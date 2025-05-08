#!/usr/bin/env python
"""
This script runs a DataHub ingestion pipeline for Snowflake metadata.
It supports both basic and advanced configurations, with options for
environment-specific settings.
"""

import os
import sys
import json
import logging
import argparse
import datetime
from typing import Dict, Any, Optional

from datahub.ingestion.run.pipeline import Pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> Dict[str, Any]:
    """Load the ingestion configuration from a JSON file."""
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load configuration from {config_path}: {e}")
        sys.exit(1)

def override_config(config: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Apply overrides to the configuration."""
    for section in ["source", "sink"]:
        if section in overrides and section in config:
            if "config" in overrides[section] and "config" in config[section]:
                config[section]["config"].update(overrides[section]["config"])
    
    if "pipeline_name" in overrides:
        config["pipeline_name"] = overrides["pipeline_name"]
    
    return config

def run_ingestion(config: Dict[str, Any], dry_run: bool = False) -> Optional[Dict[str, Any]]:
    """Run the ingestion pipeline with the given configuration."""
    if dry_run:
        logger.info("Dry run mode. Configuration:")
        logger.info(json.dumps(config, indent=2))
        return None
    
    logger.info(f"Starting ingestion with pipeline: {config.get('pipeline_name', 'unnamed')}")
    
    try:
        pipeline = Pipeline.create(config)
        pipeline.run()
        report = pipeline.get_report()
        
        logger.info(f"Ingestion completed. Summary: {report.ingestion_summary()}")
        return report.as_obj()
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="DataHub Snowflake Ingestion Runner")
    parser.add_argument("--config", required=True, help="Path to the ingestion configuration file")
    parser.add_argument("--env", help="Environment (dev, test, prod)")
    parser.add_argument("--platform-instance", help="Snowflake platform instance name")
    parser.add_argument("--dry-run", action="store_true", help="Validate config without running ingestion")
    parser.add_argument("--output", help="Path to write the ingestion report")
    
    args = parser.parse_args()
    
    # Load the base configuration
    config = load_config(args.config)
    
    # Apply environment-specific overrides
    overrides = {}
    
    # Environment override
    if args.env:
        if "source" not in overrides:
            overrides["source"] = {"config": {}}
        overrides["source"]["config"]["env"] = args.env
        overrides["pipeline_name"] = f"{config.get('pipeline_name', 'snowflake_ingestion')}_{args.env}"
    
    # Platform instance override
    if args.platform_instance:
        if "source" not in overrides:
            overrides["source"] = {"config": {}}
        overrides["source"]["config"]["platform_instance"] = args.platform_instance
    
    # Apply the overrides
    config = override_config(config, overrides)
    
    # Substitute environment variables
    config_str = json.dumps(config)
    for key, value in os.environ.items():
        if key.startswith("SNOWFLAKE_") or key.startswith("DATAHUB_"):
            placeholder = f"${{{key}}}"
            config_str = config_str.replace(placeholder, value)
    
    config = json.loads(config_str)
    
    # Run the ingestion
    report = run_ingestion(config, args.dry_run)
    
    # Write the report if requested
    if report and args.output:
        try:
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Ingestion report written to {args.output}")
        except Exception as e:
            logger.error(f"Failed to write report to {args.output}: {e}")

if __name__ == "__main__":
    main()