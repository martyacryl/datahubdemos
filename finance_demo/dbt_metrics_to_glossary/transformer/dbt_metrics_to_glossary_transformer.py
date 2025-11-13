"""
dbt Metrics to Glossary Terms Transformer for DataHub

This transformer extracts dbt metrics from the dbt manifest.json file
(obtained from dbt Cloud API or local file) and automatically creates
glossary terms in DataHub. It then applies those terms to the datasets
that the metrics reference.

Usage:
    Add to your DataHub ingestion recipe:
    
    transformers:
      - type: "transformer.dbt_metrics_to_glossary_transformer.DbtMetricsToGlossary"
        config:
          create_glossary_terms: true
          apply_to_datasets: true
          apply_to_columns: false
          term_name_prefix: "Metric"
          semantics: PATCH
"""

# CRITICAL: Print to stdout immediately when module loads
print("=" * 80, flush=True)
print("dbt_metrics_to_glossary_transformer.py: MODULE IS BEING LOADED!", flush=True)
print("=" * 80, flush=True)

import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Sequence, Union

try:
    from datahub.configuration.common import ConfigModel, TransformerSemantics
    from datahub.ingestion.api.common import PipelineContext, RecordEnvelope
    from datahub.ingestion.transformer.base_transformer import BaseTransformer
    from datahub.emitter.mcp import MetadataChangeProposalWrapper
    from datahub.metadata.schema_classes import (
        GlossaryTermInfoClass,
        GlossaryTermAssociationClass,
    )
    from datahub.ingestion.api.workunit import MetadataWorkUnit
    print("SUCCESS: All DataHub imports succeeded", flush=True)
except Exception as e:
    print(f"ERROR: Failed to import DataHub modules: {e}", flush=True)
    import traceback
    traceback.print_exc()
    raise

logger = logging.getLogger(__name__)
logger.info("=" * 80)
logger.info("dbt_metrics_to_glossary_transformer.py: Module loaded, logger initialized")
logger.info("=" * 80)
print("dbt_metrics_to_glossary_transformer.py: Logger initialized", flush=True)


class DbtMetricsToGlossaryConfig(ConfigModel):
    """Configuration for the dbt Metrics to Glossary transformer."""

    # Path to dbt manifest.json (optional - will try to find it automatically)
    manifest_path: Optional[str] = None
    
    # Whether to create glossary terms from metrics
    create_glossary_terms: bool = True
    
    # Whether to apply terms to datasets that metrics reference
    apply_to_datasets: bool = True
    
    # Whether to apply terms to columns that metrics reference
    apply_to_columns: bool = False
    
    # Prefix for glossary term names
    term_name_prefix: str = "Metric"
    
    # Parent glossary term URN (optional - to organize metrics under a parent term)
    parent_term_urn: Optional[str] = None
    
    # How to handle existing aspect values
    semantics: TransformerSemantics = TransformerSemantics.PATCH


class DbtMetricsToGlossary(BaseTransformer):
    """Transformer that extracts dbt metrics from manifest and creates glossary terms."""

    ctx: PipelineContext
    config: DbtMetricsToGlossaryConfig
    metrics: Dict[str, Dict[str, Any]] = {}
    model_to_dataset_map: Dict[str, Dict[str, Any]] = {}  # model_name -> model_data
    dataset_urn_cache: Dict[str, str] = {}  # model_name -> dataset_urn
    glossary_term_mcps: List[MetadataChangeProposalWrapper] = []

    def __init__(self, config: DbtMetricsToGlossaryConfig, ctx: PipelineContext):
        super().__init__()
        self.ctx = ctx
        self.config = config
        self.manifest_loaded = False
        # Don't load manifest immediately - wait for workunits to ensure manifest is available
        logger.info("DbtMetricsToGlossary transformer initialized")
        logger.info(f"Transformer config: create_glossary_terms={config.create_glossary_terms}, term_name_prefix={config.term_name_prefix}")

    @classmethod
    def create(cls, config_dict: dict, ctx: PipelineContext) -> "DbtMetricsToGlossary":
        config = DbtMetricsToGlossaryConfig.parse_obj(config_dict)
        return cls(config, ctx)

    def entity_types(self) -> List[str]:
        """Return the entity types this transformer applies to."""
        return ["dataset", "dataFlow", "dataJob"]

    def get_aspects_to_transform(self) -> List[str]:
        """Return the aspects this transformer operates on."""
        return [
            "datasetSnapshot",
            "dataFlowSnapshot",
            "dataJobSnapshot",
            "glossaryTerms",
        ]

    def _find_manifest_path(self) -> Optional[Path]:
        """Try to find the dbt manifest.json file."""
        logger.info("=" * 80)
        logger.info("SEARCHING FOR MANIFEST.JSON...")
        logger.info("=" * 80)
        
        # Check config path first
        if self.config.manifest_path:
            path = Path(self.config.manifest_path)
            if path.exists():
                logger.info(f"✓ Found manifest at configured path: {path}")
                return path
            else:
                logger.warning(f"✗ Configured manifest path does not exist: {path}")
        
        # Try common locations relative to current working directory
        common_paths = [
            Path("target/manifest.json"),
            Path("dbt_project/target/manifest.json"),
            Path.cwd() / "target" / "manifest.json",
            Path.cwd() / "dbt_project" / "target" / "manifest.json",
        ]
        
        logger.info(f"Checking common paths (cwd: {Path.cwd()})...")
        for path in common_paths:
            if path.exists():
                logger.info(f"✓ Found manifest at: {path}")
                return path
        
        # Try to get from context if available (dbt Cloud ingestion)
        if hasattr(self.ctx, 'dbt_manifest_path'):
            manifest_path = Path(self.ctx.dbt_manifest_path)
            if manifest_path.exists():
                logger.info(f"✓ Found manifest from context: {manifest_path}")
                return manifest_path
        
        # Try DataHub Cloud temporary directories (dbt-cloud source downloads manifest here)
        import tempfile
        import glob
        
        logger.info("Searching in /tmp/datahub/ingest/**/manifest.json...")
        # Check specific temp locations where dbt-cloud source might store manifest
        # The dbt-cloud source downloads artifacts to /tmp/datahub/ingest/{exec_id}/...
        temp_locations = [
            "/tmp/datahub/ingest/**/manifest.json",
            "/tmp/datahub/**/manifest.json",
            str(Path(tempfile.gettempdir()) / "datahub" / "ingest" / "**" / "manifest.json"),
            str(Path(tempfile.gettempdir()) / "datahub" / "**" / "manifest.json"),
        ]
        
        # Search in temp directories - be aggressive!
        all_matches = []
        for pattern in temp_locations:
            try:
                logger.info(f"  Searching pattern: {pattern}")
                matches = glob.glob(pattern, recursive=True)
                logger.info(f"    Found {len(matches)} match(es)")
                all_matches.extend(matches)
            except Exception as e:
                logger.warning(f"    Error searching pattern {pattern}: {e}")
                pass
        
        # Remove duplicates and check each match
        seen = set()
        for match_str in all_matches:
            if match_str in seen:
                continue
            seen.add(match_str)
            match = Path(match_str)
            if match.exists() and match.is_file():
                # Prefer datahub/ingest paths
                if "datahub" in str(match) and "ingest" in str(match):
                    logger.info(f"✓ Found manifest in temp directory: {match}")
                    return match
        
        # Use first valid match if no preferred one found
        for match_str in all_matches:
            match = Path(match_str)
            if match.exists() and match.is_file():
                logger.info(f"✓ Found manifest in temp directory: {match}")
                return match
        
        # Try environment variable
        if "DBT_MANIFEST_PATH" in os.environ:
            env_path = Path(os.environ["DBT_MANIFEST_PATH"])
            if env_path.exists():
                logger.info(f"✓ Found manifest from environment variable: {env_path}")
                return env_path
        
        # Last resort: try to find any manifest.json in /tmp/datahub
        logger.warning("Could not find manifest in standard locations. Searching /tmp/datahub more broadly...")
        try:
            for root, dirs, files in os.walk("/tmp"):
                # Only search in datahub directories
                if "datahub" not in root:
                    dirs[:] = []  # Don't recurse
                    continue
                if "manifest.json" in files:
                    manifest_path = Path(root) / "manifest.json"
                    logger.info(f"✓ Found manifest in /tmp: {manifest_path}")
                    return manifest_path
        except Exception as e:
            logger.warning(f"Error walking /tmp: {e}")
        
        logger.error("=" * 80)
        logger.error("✗ COULD NOT FIND MANIFEST.JSON")
        logger.error("=" * 80)
        return None

    def _load_metrics_from_manifest(self):
        """Load metrics from dbt manifest.json."""
        logger.info("=" * 80)
        logger.info("LOADING METRICS FROM MANIFEST.JSON...")
        logger.info("=" * 80)
        
        manifest_path = self._find_manifest_path()
        
        if not manifest_path:
            logger.error("=" * 80)
            logger.error("✗ Could not find dbt manifest.json. Metrics will not be extracted.")
            logger.error("=" * 80)
            logger.error("Note: When using dbt-cloud source, the manifest is downloaded automatically.")
            logger.error("Searching in /tmp/datahub/ingest/**/manifest.json")
            logger.error("If manifest is not found, you may need to set manifest_path in the transformer config.")
            return
        
        try:
            logger.info(f"✓ Loading manifest from: {manifest_path}")
            logger.info(f"  File size: {manifest_path.stat().st_size} bytes")
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Extract metrics from manifest
            # dbt metrics are stored in manifest['metrics']
            logger.info(f"✓ Manifest loaded successfully")
            logger.info(f"  Manifest contains {len(manifest)} top-level keys")
            logger.info(f"  Top-level keys: {list(manifest.keys())[:20]}")
            
            # Check for semantic models first (metrics depend on semantic models)
            if 'semantic_models' in manifest:
                semantic_models = manifest['semantic_models']
                logger.info(f"✓ Found {len(semantic_models)} semantic model(s) in manifest")
                for sem_model_name in list(semantic_models.keys())[:5]:  # Show first 5
                    logger.info(f"    - Semantic model: {sem_model_name}")
                if len(semantic_models) > 5:
                    logger.info(f"    ... and {len(semantic_models) - 5} more")
            else:
                logger.warning("✗ No 'semantic_models' key found in manifest.json")
            
            # Extract metrics - THIS IS THE KEY PART
            if 'metrics' in manifest:
                metrics_dict = manifest['metrics']
                logger.info("=" * 80)
                logger.info(f"✓✓✓ FOUND {len(metrics_dict)} METRIC(S) IN MANIFEST ✓✓✓")
                logger.info("=" * 80)
                
                for metric_name, metric_data in metrics_dict.items():
                    self.metrics[metric_name] = metric_data
                    logger.info(f"  ✓ Loaded metric: {metric_name}")
                    # Log metric details for debugging
                    metric_type = metric_data.get('type', 'unknown')
                    metric_label = metric_data.get('label', metric_name)
                    logger.info(f"    Type: {metric_type}, Label: {metric_label}")
            else:
                logger.error("=" * 80)
                logger.error("✗✗✗ NO 'metrics' KEY FOUND IN MANIFEST.JSON ✗✗✗")
                logger.error("=" * 80)
                logger.error("This usually means:")
                logger.error("  1. The dbt Cloud job didn't parse the metrics YAML files")
                logger.error("  2. The job needs to be run/triggered to generate a new manifest")
                logger.error("  3. Check dbt Cloud job logs for parsing errors")
                logger.error("  4. Make sure your metrics YAML files are in the dbt project")
                logger.error("=" * 80)
            
            # Also extract model information for mapping
            if 'nodes' in manifest:
                node_count = 0
                for node_name, node_data in manifest['nodes'].items():
                    if node_data.get('resource_type') == 'model':
                        model_name = node_data.get('name')
                        if model_name:
                            # Store model info for later mapping to dataset URNs
                            self.model_to_dataset_map[model_name] = node_data
                            node_count += 1
                logger.info(f"✓ Loaded {node_count} model(s) for mapping")
            
            logger.info("=" * 80)
            logger.info(f"SUMMARY: Loaded {len(self.metrics)} metric(s) from manifest")
            logger.info(f"SUMMARY: Loaded {len(self.model_to_dataset_map)} model(s) for mapping")
            logger.info("=" * 80)
            
            if len(self.metrics) == 0:
                logger.error("=" * 80)
                logger.error("✗✗✗ ERROR: No metrics found in manifest! ✗✗✗")
                logger.error("=" * 80)
                logger.error("TROUBLESHOOTING STEPS:")
                logger.error("1. Go to dbt Cloud → Orchestration → Jobs → Job ID 961293")
                logger.error("2. Click 'Run Now' to trigger the job")
                logger.error("3. Wait for job to complete successfully")
                logger.error("4. The job must run 'dbt parse' to include metrics in manifest.json")
                logger.error("5. Then run DataHub ingestion again")
                logger.error("=" * 80)
            else:
                logger.info("=" * 80)
                logger.info(f"✓✓✓ SUCCESS: Found {len(self.metrics)} metrics in manifest! ✓✓✓")
                logger.info("=" * 80)
        
        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"✗✗✗ ERROR loading manifest: {str(e)} ✗✗✗")
            logger.error("=" * 80)
            import traceback
            logger.error(traceback.format_exc())

    def _clean_term_name(self, name: str) -> str:
        """Clean metric name for use in glossary term URN."""
        # Replace spaces and special characters with underscores
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Remove multiple consecutive underscores
        clean_name = re.sub(r'_+', '_', clean_name)
        # Remove leading/trailing underscores
        clean_name = clean_name.strip('_')
        return clean_name

    def _create_term_urn(self, metric_name: str) -> str:
        """Create glossary term URN from metric name."""
        # Clean metric name for URN
        clean_name = self._clean_term_name(metric_name)
        term_name = f"{self.config.term_name_prefix}_{clean_name}"
        return f"urn:li:glossaryTerm:{term_name}"

    def _create_glossary_term_mcp(self, metric_name: str, metric_data: Dict[str, Any]) -> MetadataChangeProposalWrapper:
        """Create a glossary term MCP for a metric."""
        term_urn = self._create_term_urn(metric_name)
        
        # Extract metric information
        label = metric_data.get('label', metric_name.replace('_', ' ').title())
        description = metric_data.get('description', f"dbt metric: {metric_name}")
        
        # Build comprehensive description
        full_description = f"{description}\n\n"
        full_description += f"**Metric Type:** {metric_data.get('type', 'simple')}\n"
        
        # Add type-specific information
        type_params = metric_data.get('type_params', {})
        if 'measure' in type_params:
            full_description += f"**Measure:** {type_params['measure']}\n"
        if 'numerator' in type_params:
            full_description += f"**Numerator:** {type_params['numerator']}\n"
        if 'denominator' in type_params:
            full_description += f"**Denominator:** {type_params['denominator']}\n"
        
        # Add model reference
        model_ref = metric_data.get('model')
        if model_ref:
            # Extract model name from ref() syntax if present
            if isinstance(model_ref, str):
                match = re.search(r"ref\(['\"]([^'\"]+)['\"]\)", model_ref)
                if match:
                    model_name = match.group(1)
                else:
                    model_name = model_ref
            else:
                model_name = str(model_ref)
            full_description += f"**Model:** {model_name}\n"
        
        # Add dimensions if available
        dimensions = metric_data.get('dimensions', [])
        if dimensions:
            full_description += f"**Dimensions:** {', '.join(dimensions)}\n"
        
        # Add time grains if available
        time_grains = metric_data.get('time_grains', [])
        if time_grains:
            full_description += f"**Time Grains:** {', '.join(time_grains)}\n"
        
        # Create glossary term
        term_info = GlossaryTermInfoClass(
            name=label,
            description=full_description,
            termSource="INTERNAL",
        )
        
        if self.config.parent_term_urn:
            term_info.parentNode = self.config.parent_term_urn
        
        mcp = MetadataChangeProposalWrapper(
            entityUrn=term_urn,
            aspect=term_info
        )
        
        logger.info(f"Created glossary term MCP: {term_urn} for metric {metric_name}")
        return mcp

    def _extract_model_name_from_ref(self, model_ref: Any) -> Optional[str]:
        """Extract model name from dbt ref() syntax."""
        if isinstance(model_ref, str):
            # Try to extract from ref() syntax
            match = re.search(r"ref\(['\"]([^'\"]+)['\"]\)", model_ref)
            if match:
                return match.group(1)
            # If no ref() syntax, assume it's already a model name
            return model_ref
        return str(model_ref) if model_ref else None

    def _find_dataset_urn_for_model(self, model_name: str, platform: str = "snowflake") -> Optional[str]:
        """Find dataset URN for a dbt model."""
        # Check cache first
        if model_name in self.dataset_urn_cache:
            return self.dataset_urn_cache[model_name]
        
        # Try to get from model mapping
        if model_name in self.model_to_dataset_map:
            model_data = self.model_to_dataset_map[model_name]
            # Extract database, schema, table from model data
            database = model_data.get('database', 'FINANCE_ANALYTICS')
            schema = model_data.get('schema', 'SILVER')
            table = model_name
            
            # Construct dataset URN
            # Format: urn:li:dataset:(urn:li:dataPlatform:{platform},{database}.{schema}.{table},PROD)
            dataset_urn = f"urn:li:dataset:(urn:li:dataPlatform:{platform},{database}.{schema}.{table},PROD)"
            self.dataset_urn_cache[model_name] = dataset_urn
            return dataset_urn
        
        # If not found, try to construct from common patterns
        # This is a fallback - may need adjustment based on your setup
        logger.warning(f"Could not find model {model_name} in manifest. Using fallback URN construction.")
        dataset_urn = f"urn:li:dataset:(urn:li:dataPlatform:{platform},FINANCE_ANALYTICS.SILVER.{model_name},PROD)"
        self.dataset_urn_cache[model_name] = dataset_urn
        return dataset_urn

    def _get_platform_from_context(self) -> str:
        """Try to get target platform from ingestion context."""
        # Try to get from source config if available
        if hasattr(self.ctx, 'source_config'):
            if hasattr(self.ctx.source_config, 'target_platform'):
                return self.ctx.source_config.target_platform
        return "snowflake"  # Default

    def transform(self, workunits):
        """Transform workunits."""
        # Don't load manifest here - wait until handle_end_of_stream when dbt-cloud source is done
        # Just pass through - we'll create MCPs in handle_end_of_stream
        logger.debug(f"Transform called with {len(workunits) if isinstance(workunits, list) else 1} workunit(s)")
        if isinstance(workunits, list):
            return workunits
        return [workunits]
    
    def _try_extract_metrics_from_workunits(self, workunits):
        """Try to extract metrics from workunits if manifest wasn't found."""
        # This is a fallback - try to find manifest in workunit metadata
        try:
            workunit_list = workunits if isinstance(workunits, list) else [workunits]
            for wu in workunit_list:
                if hasattr(wu, 'metadata') and wu.metadata:
                    # Check if workunit has manifest path in metadata
                    if hasattr(wu.metadata, 'manifest_path'):
                        manifest_path = Path(wu.metadata.manifest_path)
                        if manifest_path.exists():
                            logger.info(f"Found manifest path in workunit: {manifest_path}")
                            self._load_metrics_from_path(manifest_path)
                            return
        except Exception as e:
            logger.debug(f"Could not extract metrics from workunits: {e}")
    
    def _load_metrics_from_path(self, manifest_path: Path):
        """Load metrics from a specific manifest path."""
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            if 'metrics' in manifest:
                for metric_name, metric_data in manifest['metrics'].items():
                    self.metrics[metric_name] = metric_data
                    logger.info(f"Loaded metric from workunit manifest: {metric_name}")
            
            if 'nodes' in manifest:
                for node_name, node_data in manifest['nodes'].items():
                    if node_data.get('resource_type') == 'model':
                        model_name = node_data.get('name')
                        if model_name:
                            self.model_to_dataset_map[model_name] = node_data
        except Exception as e:
            logger.error(f"Error loading metrics from workunit manifest: {e}")

    def transform_aspect(
        self, entity_urn: str, aspect_name: str, aspect: Optional[Any]
    ) -> Optional[Any]:
        """Transform aspects."""
        # We'll handle everything in handle_end_of_stream
        # But we can also try to extract dataset URNs from workunits here
        try:
            # If this is a dataset snapshot, try to extract model name
            if aspect and hasattr(aspect, 'urn'):
                urn_str = str(aspect.urn)
                # Try to extract model name from dataset URN
                # Format: urn:li:dataset:(urn:li:dataPlatform:snowflake,DB.SCHEMA.TABLE,PROD)
                match = re.search(r',([^.]+)\.([^.]+)\.([^,]+),', urn_str)
                if match:
                    database, schema, table = match.groups()
                    # Store mapping if we have model info
                    if table in self.model_to_dataset_map:
                        self.dataset_urn_cache[table] = urn_str
        except Exception as e:
            logger.debug(f"Could not extract model info from aspect: {str(e)}")
        
        return aspect

    def handle_end_of_stream(
        self,
    ) -> Sequence[MetadataChangeProposalWrapper]:
        """Create glossary terms and associations after processing."""
        logger.info("=" * 80)
        logger.info("=" * 80)
        logger.info("DbtMetricsToGlossary.handle_end_of_stream() CALLED!")
        logger.info("=" * 80)
        logger.info("=" * 80)
        print("=" * 80, flush=True)
        print("DbtMetricsToGlossary.handle_end_of_stream() CALLED!", flush=True)
        print("=" * 80, flush=True)
        
        all_mcps = []
        
        # Load manifest NOW (after dbt-cloud source has finished downloading it)
        if not self.manifest_loaded:
            logger.info("=" * 80)
            logger.info("Loading manifest from dbt-cloud source (after source processing complete)...")
            logger.info("=" * 80)
            print("Loading manifest from dbt-cloud source...", flush=True)
            self._load_metrics_from_manifest()
            self.manifest_loaded = True
        else:
            logger.info("Manifest already loaded, skipping reload")
        
        if not self.config.create_glossary_terms:
            logger.warning("create_glossary_terms is False - skipping term creation")
            return all_mcps
        
        if not self.metrics:
            logger.error("=" * 80)
            logger.error("✗✗✗ NO METRICS FOUND ✗✗✗")
            logger.error("=" * 80)
            logger.error("This could mean:")
            logger.error("  1. The manifest.json doesn't contain a 'metrics' key")
            logger.error("  2. Your dbt job didn't parse the metrics YAML files")
            logger.error("  3. The manifest wasn't found in /tmp/datahub/ingest/**/manifest.json")
            logger.error("  4. The transformer couldn't find the manifest file")
            logger.error("=" * 80)
            return all_mcps
        
        logger.info("=" * 80)
        logger.info(f"✓✓✓ CREATING GLOSSARY TERMS FOR {len(self.metrics)} METRICS ✓✓✓")
        logger.info("=" * 80)
        print(f"Creating glossary terms for {len(self.metrics)} metrics", flush=True)
        
        platform = self._get_platform_from_context()
        logger.info(f"Using platform: {platform}")
        
        for metric_name, metric_data in self.metrics.items():
            try:
                logger.info(f"Processing metric: {metric_name}")
                # Create glossary term
                term_mcp = self._create_glossary_term_mcp(metric_name, metric_data)
                all_mcps.append(term_mcp)
                logger.info(f"  ✓ Created glossary term MCP for: {metric_name}")
                
                # Create term associations if configured
                if self.config.apply_to_datasets:
                    # Try to find the model reference in the metric data
                    # Metrics can reference models in different ways:
                    # 1. Direct model reference: metric_data.get('model')
                    # 2. Through semantic model: metric_data.get('semantic_model') -> semantic_model -> model
                    # 3. Through type_params: metric_data.get('type_params', {}).get('model')
                    
                    model_ref = None
                    # Try direct model reference first
                    if 'model' in metric_data:
                        model_ref = metric_data.get('model')
                    # Try through semantic_model
                    elif 'semantic_model' in metric_data:
                        semantic_model_name = metric_data.get('semantic_model')
                        logger.info(f"  Metric uses semantic model: {semantic_model_name}")
                        # We'd need to look up the semantic model to get the model, but for now skip
                        model_ref = None
                    # Try through type_params
                    elif 'type_params' in metric_data:
                        type_params = metric_data.get('type_params', {})
                        if 'model' in type_params:
                            model_ref = type_params.get('model')
                    
                    if model_ref:
                        model_name = self._extract_model_name_from_ref(model_ref)
                        if model_name:
                            logger.info(f"  Found model reference: {model_name}")
                            # Find dataset URN for this model
                            dataset_urn = self._find_dataset_urn_for_model(model_name, platform)
                            if dataset_urn:
                                term_urn = self._create_term_urn(metric_name)
                                association_mcp = MetadataChangeProposalWrapper(
                                    entityUrn=dataset_urn,
                                    aspect=GlossaryTermAssociationClass(term=term_urn)
                                )
                                all_mcps.append(association_mcp)
                                logger.info(f"  ✓ Created term association: {term_urn} -> {dataset_urn}")
                            else:
                                logger.warning(f"  ✗ Could not find dataset URN for model: {model_name}")
                        else:
                            logger.warning(f"  ✗ Could not extract model name from: {model_ref}")
                    else:
                        logger.info(f"  No model reference found for metric: {metric_name}")
            
            except Exception as e:
                logger.error(f"✗ Error processing metric {metric_name}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        
        logger.info("=" * 80)
        logger.info(f"✓✓✓ CREATED {len(all_mcps)} MCPs TOTAL ✓✓✓")
        logger.info(f"  - {len(self.metrics)} glossary term(s)")
        logger.info(f"  - {len(all_mcps) - len(self.metrics)} association(s)")
        logger.info("=" * 80)
        print(f"Created {len(all_mcps)} MCPs total", flush=True)
        
        return all_mcps

