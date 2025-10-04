#!/usr/bin/env python3
"""
DataHub Duplicate Asset Detector
Finds duplicated tables, views, stored procedures, and other assets in DataHub.
"""

import json
import logging
import os
import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import requests
from dataclasses import dataclass
from difflib import SequenceMatcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DuplicateFinding:
    """Represents a duplicate finding with details about the assets and similarity."""
    asset_type: str
    similarity_type: str
    similarity_score: float
    primary_asset: Dict[str, Any]
    duplicate_assets: List[Dict[str, Any]]
    reason: str
    confidence: str  # high, medium, low

@dataclass
class DetectionConfig:
    """Configuration for duplicate detection."""
    name_similarity_threshold: float = 0.8
    schema_similarity_threshold: float = 0.7
    content_similarity_threshold: float = 0.9
    min_assets_for_duplicate: int = 2
    case_sensitive: bool = False
    ignore_common_suffixes: List[str] = None
    ignore_common_prefixes: List[str] = None

class DataHubDuplicateDetector:
    """Main class for detecting duplicate assets in DataHub."""
    
    def __init__(self, datahub_gms_url: str, datahub_token: str):
        self.datahub_gms_url = datahub_gms_url.rstrip('/')
        self.datahub_token = datahub_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {datahub_token}',
            'Content-Type': 'application/json'
        })
        self.config = DetectionConfig()
        
        # Common suffixes/prefixes to ignore
        self.config.ignore_common_suffixes = [
            '_backup', '_old', '_temp', '_tmp', '_test', '_dev', '_staging',
            '_v1', '_v2', '_v3', '_new', '_copy', '_duplicate'
        ]
        self.config.ignore_common_prefixes = [
            'backup_', 'old_', 'temp_', 'tmp_', 'test_', 'dev_', 'staging_'
        ]
    
    def search_assets(self, entity_types: List[str] = None, query: str = "*", 
                     start: int = 0, count: int = 1000) -> List[Dict[str, Any]]:
        """Search for assets in DataHub."""
        try:
            if entity_types is None:
                entity_types = ["dataset", "chart", "dashboard", "dataFlow", "dataJob"]
            
            search_query = {
                "query": query,
                "entityTypes": entity_types,
                "start": start,
                "count": count
            }
            
            response = self.session.post(
                f"{self.datahub_gms_url}/graphql",
                json={
                    "query": """
                    query search($input: SearchInput!) {
                        search(input: $input) {
                            searchResults {
                                entity {
                                    urn
                                    type
                                    ... on Dataset {
                                        name
                                        platform {
                                            name
                                        }
                                        properties {
                                            name
                                            description
                                        }
                                        schemaMetadata {
                                            fields {
                                                fieldPath
                                                type
                                                description
                                            }
                                        }
                                        upstreamLineage {
                                            upstreams {
                                                dataset {
                                                    urn
                                                }
                                            }
                                        }
                                        downstreamLineage {
                                            downstreams {
                                                dataset {
                                                    urn
                                                }
                                            }
                                        }
                                    }
                                    ... on Chart {
                                        name
                                        platform {
                                            name
                                        }
                                        properties {
                                            name
                                            description
                                        }
                                    }
                                    ... on Dashboard {
                                        name
                                        platform {
                                            name
                                        }
                                        properties {
                                            name
                                            description
                                        }
                                    }
                                    ... on DataFlow {
                                        name
                                        platform {
                                            name
                                        }
                                        properties {
                                            name
                                            description
                                        }
                                    }
                                    ... on DataJob {
                                        name
                                        platform {
                                            name
                                        }
                                        properties {
                                            name
                                            description
                                        }
                                    }
                                }
                            }
                        }
                    }
                    """,
                    "variables": {"input": search_query}
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Error searching DataHub: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            if 'errors' in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return []
            
            search_results = data.get('data', {}).get('search', {}).get('searchResults', [])
            return [result['entity'] for result in search_results]
            
        except Exception as e:
            logger.error(f"Error searching assets: {str(e)}")
            return []
    
    def normalize_name(self, name: str) -> str:
        """Normalize asset name for comparison."""
        if not name:
            return ""
        
        # Convert to lowercase if not case sensitive
        if not self.config.case_sensitive:
            name = name.lower()
        
        # Remove common suffixes
        for suffix in self.config.ignore_common_suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break
        
        # Remove common prefixes
        for prefix in self.config.ignore_common_prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
                break
        
        # Remove special characters and normalize spaces
        name = re.sub(r'[_\-\s]+', '_', name)
        name = name.strip('_')
        
        return name
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two asset names."""
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        if norm1 == norm2:
            return 1.0
        
        # Use SequenceMatcher for fuzzy matching
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        return similarity
    
    def calculate_schema_similarity(self, schema1: List[Dict], schema2: List[Dict]) -> float:
        """Calculate similarity between two schemas."""
        if not schema1 or not schema2:
            return 0.0
        
        # Extract field names and types
        fields1 = {(field.get('fieldPath', ''), field.get('type', '')) for field in schema1}
        fields2 = {(field.get('fieldPath', ''), field.get('type', '')) for field in schema2}
        
        if not fields1 or not fields2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(fields1.intersection(fields2))
        union = len(fields1.union(fields2))
        
        return intersection / union if union > 0 else 0.0
    
    def extract_asset_info(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant information from an asset for comparison."""
        info = {
            'urn': asset.get('urn', ''),
            'type': asset.get('type', ''),
            'name': '',
            'platform': '',
            'description': '',
            'schema': [],
            'properties': {}
        }
        
        # Extract name and platform based on asset type
        if asset.get('type') == 'dataset':
            info['name'] = asset.get('name', '')
            platform = asset.get('platform', {})
            info['platform'] = platform.get('name', '') if platform else ''
            info['description'] = asset.get('properties', {}).get('description', '')
            info['schema'] = asset.get('schemaMetadata', {}).get('fields', [])
        else:
            # For other asset types
            info['name'] = asset.get('name', '')
            platform = asset.get('platform', {})
            info['platform'] = platform.get('name', '') if platform else ''
            info['description'] = asset.get('properties', {}).get('description', '')
        
        info['properties'] = asset.get('properties', {})
        return info
    
    def detect_name_duplicates(self, assets: List[Dict[str, Any]]) -> List[DuplicateFinding]:
        """Detect assets with similar names."""
        findings = []
        
        # Group assets by platform and type
        grouped_assets = defaultdict(list)
        for asset in assets:
            info = self.extract_asset_info(asset)
            key = f"{info['platform']}_{info['type']}"
            grouped_assets[key].append((info['name'], asset))
        
        # Check for duplicates within each group
        for group_name, asset_list in grouped_assets.items():
            for i, (name1, asset1) in enumerate(asset_list):
                duplicates = [asset1]
                
                for j, (name2, asset2) in enumerate(asset_list[i+1:], i+1):
                    similarity = self.calculate_name_similarity(name1, name2)
                    
                    if similarity >= self.config.name_similarity_threshold:
                        duplicates.append(asset2)
                
                if len(duplicates) >= self.config.min_assets_for_duplicate:
                    # Determine confidence
                    if similarity >= 0.95:
                        confidence = "high"
                    elif similarity >= 0.8:
                        confidence = "medium"
                    else:
                        confidence = "low"
                    
                    finding = DuplicateFinding(
                        asset_type=asset1.get('type', ''),
                        similarity_type="name",
                        similarity_score=similarity,
                        primary_asset=duplicates[0],
                        duplicate_assets=duplicates[1:],
                        reason=f"Similar names: {name1} vs {[self.extract_asset_info(a)['name'] for a in duplicates[1:]]}",
                        confidence=confidence
                    )
                    findings.append(finding)
        
        return findings
    
    def detect_schema_duplicates(self, assets: List[Dict[str, Any]]) -> List[DuplicateFinding]:
        """Detect datasets with similar schemas."""
        findings = []
        
        # Filter to only datasets
        datasets = [asset for asset in assets if asset.get('type') == 'dataset']
        
        for i, asset1 in enumerate(datasets):
            info1 = self.extract_asset_info(asset1)
            schema1 = info1['schema']
            
            if not schema1:
                continue
            
            duplicates = [asset1]
            
            for j, asset2 in enumerate(datasets[i+1:], i+1):
                info2 = self.extract_asset_info(asset2)
                schema2 = info2['schema']
                
                if not schema2:
                    continue
                
                similarity = self.calculate_schema_similarity(schema1, schema2)
                
                if similarity >= self.config.schema_similarity_threshold:
                    duplicates.append(asset2)
            
            if len(duplicates) >= self.config.min_assets_for_duplicate:
                # Calculate average similarity
                avg_similarity = sum(
                    self.calculate_schema_similarity(
                        self.extract_asset_info(duplicates[0])['schema'],
                        self.extract_asset_info(dup)['schema']
                    ) for dup in duplicates[1:]
                ) / len(duplicates[1:])
                
                # Determine confidence
                if avg_similarity >= 0.9:
                    confidence = "high"
                elif avg_similarity >= 0.7:
                    confidence = "medium"
                else:
                    confidence = "low"
                
                finding = DuplicateFinding(
                    asset_type="dataset",
                    similarity_type="schema",
                    similarity_score=avg_similarity,
                    primary_asset=duplicates[0],
                    duplicate_assets=duplicates[1:],
                    reason=f"Similar schemas with {avg_similarity:.2%} field overlap",
                    confidence=confidence
                )
                findings.append(finding)
        
        return findings
    
    def detect_description_duplicates(self, assets: List[Dict[str, Any]]) -> List[DuplicateFinding]:
        """Detect assets with similar descriptions."""
        findings = []
        
        # Group assets by type
        grouped_assets = defaultdict(list)
        for asset in assets:
            info = self.extract_asset_info(asset)
            if info['description']:
                grouped_assets[info['type']].append((info['description'], asset))
        
        # Check for duplicates within each group
        for asset_type, asset_list in grouped_assets.items():
            for i, (desc1, asset1) in enumerate(asset_list):
                duplicates = [asset1]
                
                for j, (desc2, asset2) in enumerate(asset_list[i+1:], i+1):
                    similarity = SequenceMatcher(None, desc1.lower(), desc2.lower()).ratio()
                    
                    if similarity >= 0.8:  # High threshold for description similarity
                        duplicates.append(asset2)
                
                if len(duplicates) >= self.config.min_assets_for_duplicate:
                    finding = DuplicateFinding(
                        asset_type=asset_type,
                        similarity_type="description",
                        similarity_score=similarity,
                        primary_asset=duplicates[0],
                        duplicate_assets=duplicates[1:],
                        reason=f"Similar descriptions with {similarity:.2%} text overlap",
                        confidence="medium" if similarity >= 0.9 else "low"
                    )
                    findings.append(finding)
        
        return findings
    
    def detect_duplicates(self, entity_types: List[str] = None, 
                         detection_types: List[str] = None) -> List[DuplicateFinding]:
        """Main method to detect all types of duplicates."""
        if detection_types is None:
            detection_types = ["name", "schema", "description"]
        
        logger.info("Searching for assets in DataHub...")
        assets = self.search_assets(entity_types)
        logger.info(f"Found {len(assets)} assets to analyze")
        
        all_findings = []
        
        if "name" in detection_types:
            logger.info("Detecting name-based duplicates...")
            name_findings = self.detect_name_duplicates(assets)
            all_findings.extend(name_findings)
            logger.info(f"Found {len(name_findings)} name-based duplicates")
        
        if "schema" in detection_types:
            logger.info("Detecting schema-based duplicates...")
            schema_findings = self.detect_schema_duplicates(assets)
            all_findings.extend(schema_findings)
            logger.info(f"Found {len(schema_findings)} schema-based duplicates")
        
        if "description" in detection_types:
            logger.info("Detecting description-based duplicates...")
            desc_findings = self.detect_description_duplicates(assets)
            all_findings.extend(desc_findings)
            logger.info(f"Found {len(desc_findings)} description-based duplicates")
        
        logger.info(f"Total duplicate findings: {len(all_findings)}")
        return all_findings
    
    def generate_report(self, findings: List[DuplicateFinding], 
                       output_file: str = None) -> str:
        """Generate a detailed report of duplicate findings."""
        report = []
        report.append("# DataHub Duplicate Asset Detection Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Findings: {len(findings)}")
        report.append("")
        
        # Group findings by type
        by_type = defaultdict(list)
        by_confidence = defaultdict(list)
        
        for finding in findings:
            by_type[finding.similarity_type].append(finding)
            by_confidence[finding.confidence].append(finding)
        
        # Summary
        report.append("## Summary")
        report.append(f"- Name-based duplicates: {len(by_type['name'])}")
        report.append(f"- Schema-based duplicates: {len(by_type['schema'])}")
        report.append(f"- Description-based duplicates: {len(by_type['description'])}")
        report.append("")
        report.append(f"- High confidence: {len(by_confidence['high'])}")
        report.append(f"- Medium confidence: {len(by_confidence['medium'])}")
        report.append(f"- Low confidence: {len(by_confidence['low'])}")
        report.append("")
        
        # Detailed findings
        for finding in findings:
            report.append(f"## {finding.similarity_type.title()} Duplicate - {finding.confidence.upper()} Confidence")
            report.append(f"**Similarity Score:** {finding.similarity_score:.2%}")
            report.append(f"**Reason:** {finding.reason}")
            report.append("")
            
            # Primary asset
            primary_info = self.extract_asset_info(finding.primary_asset)
            report.append(f"### Primary Asset")
            report.append(f"- **Name:** {primary_info['name']}")
            report.append(f"- **Type:** {primary_info['type']}")
            report.append(f"- **Platform:** {primary_info['platform']}")
            report.append(f"- **URN:** {primary_info['urn']}")
            if primary_info['description']:
                report.append(f"- **Description:** {primary_info['description'][:200]}...")
            report.append("")
            
            # Duplicate assets
            report.append(f"### Duplicate Assets ({len(finding.duplicate_assets)})")
            for i, dup_asset in enumerate(finding.duplicate_assets, 1):
                dup_info = self.extract_asset_info(dup_asset)
                report.append(f"#### Duplicate {i}")
                report.append(f"- **Name:** {dup_info['name']}")
                report.append(f"- **Type:** {dup_info['type']}")
                report.append(f"- **Platform:** {dup_info['platform']}")
                report.append(f"- **URN:** {dup_info['urn']}")
                if dup_info['description']:
                    report.append(f"- **Description:** {dup_info['description'][:200]}...")
                report.append("")
            
            report.append("---")
            report.append("")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            logger.info(f"Report saved to {output_file}")
        
        return report_text
    
    def export_findings_json(self, findings: List[DuplicateFinding], 
                           output_file: str) -> None:
        """Export findings to JSON format."""
        findings_data = []
        
        for finding in findings:
            finding_data = {
                'asset_type': finding.asset_type,
                'similarity_type': finding.similarity_type,
                'similarity_score': finding.similarity_score,
                'confidence': finding.confidence,
                'reason': finding.reason,
                'primary_asset': self.extract_asset_info(finding.primary_asset),
                'duplicate_assets': [self.extract_asset_info(asset) for asset in finding.duplicate_assets],
                'total_duplicates': len(finding.duplicate_assets) + 1
            }
            findings_data.append(finding_data)
        
        with open(output_file, 'w') as f:
            json.dump(findings_data, f, indent=2)
        
        logger.info(f"Findings exported to {output_file}")

def main():
    """Main function to run the duplicate detector."""
    # Configuration from environment variables
    datahub_gms_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
    datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
    
    if not datahub_token:
        logger.error("DATAHUB_GMS_TOKEN environment variable is required")
        return
    
    # Create detector
    detector = DataHubDuplicateDetector(datahub_gms_url, datahub_token)
    
    # Configure detection
    entity_types = os.getenv('ENTITY_TYPES', 'dataset,chart,dashboard').split(',')
    detection_types = os.getenv('DETECTION_TYPES', 'name,schema,description').split(',')
    
    # Run detection
    logger.info("Starting duplicate detection...")
    findings = detector.detect_duplicates(entity_types, detection_types)
    
    # Generate reports
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"duplicate_report_{timestamp}.md"
    json_file = f"duplicate_findings_{timestamp}.json"
    
    detector.generate_report(findings, report_file)
    detector.export_findings_json(findings, json_file)
    
    logger.info(f"Detection completed. Found {len(findings)} duplicate groups.")
    logger.info(f"Reports generated: {report_file}, {json_file}")

if __name__ == "__main__":
    main()