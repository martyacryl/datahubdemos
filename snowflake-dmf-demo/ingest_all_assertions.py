#!/usr/bin/env python3
"""
Main script to ingest assertions from all sources (Glue and Snowflake) into DataHub.
"""

import logging
import os
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

from datahub_assertion_ingester import DataHubAssertionIngester, ExternalAssertion
from glue_assertion_extractor import GlueAssertionExtractor
from snowflake_assertion_extractor import SnowflakeAssertionExtractor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Ingest external assertions into DataHub')
    
    parser.add_argument('--sources', 
                       help='Comma-separated list of sources to ingest (glue,snowflake)',
                       default='glue,snowflake')
    
    parser.add_argument('--glue-database',
                       help='Glue database name (overrides env var)',
                       default=None)
    
    parser.add_argument('--snowflake-database',
                       help='Snowflake database name (overrides env var)',
                       default=None)
    
    parser.add_argument('--snowflake-schema',
                       help='Snowflake schema name (overrides env var)',
                       default=None)
    
    parser.add_argument('--dry-run',
                       action='store_true',
                       help='Extract assertions but do not ingest into DataHub')
    
    parser.add_argument('--output-file',
                       help='Output file for extracted assertions (JSON format)',
                       default=None)
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Enable verbose logging')
    
    return parser.parse_args()

def extract_glue_assertions(database_name: str, dry_run: bool = False) -> List[Dict[str, Any]]:
    """Extract assertions from AWS Glue."""
    try:
        logger.info(f"Extracting assertions from Glue database: {database_name}")
        
        extractor = GlueAssertionExtractor()
        assertions = extractor.extract_assertions(database_name)
        
        logger.info(f"Extracted {len(assertions)} assertions from Glue")
        return assertions
        
    except Exception as e:
        logger.error(f"Error extracting Glue assertions: {str(e)}")
        return []

def extract_snowflake_assertions(database_name: str, schema_name: str = None, dry_run: bool = False) -> List[Dict[str, Any]]:
    """Extract assertions from Snowflake."""
    try:
        logger.info(f"Extracting assertions from Snowflake database: {database_name}, schema: {schema_name}")
        
        extractor = SnowflakeAssertionExtractor()
        assertions = extractor.extract_assertions(database_name, schema_name)
        
        logger.info(f"Extracted {len(assertions)} assertions from Snowflake")
        return assertions
        
    except Exception as e:
        logger.error(f"Error extracting Snowflake assertions: {str(e)}")
        return []

def convert_to_external_assertions(assertions: List[Dict[str, Any]]) -> List[ExternalAssertion]:
    """Convert extracted assertions to ExternalAssertion objects."""
    external_assertions = []
    
    for assertion in assertions:
        try:
            external_assertion = ExternalAssertion(
                source_id=assertion['source_id'],
                entity_urn=assertion['entity_urn'],
                assertion_type=assertion['assertion_type'],
                description=assertion['description'],
                platform=assertion['platform'],
                field_path=assertion.get('field_path'),
                external_url=assertion.get('external_url'),
                logic=assertion.get('logic'),
                properties=assertion.get('properties')
            )
            external_assertions.append(external_assertion)
        except Exception as e:
            logger.error(f"Error converting assertion {assertion.get('source_id', 'unknown')}: {str(e)}")
            continue
    
    return external_assertions

def ingest_assertions_to_datahub(assertions: List[ExternalAssertion], dry_run: bool = False) -> Dict[str, Any]:
    """Ingest assertions into DataHub."""
    if dry_run:
        logger.info(f"Dry run mode: Would ingest {len(assertions)} assertions")
        return {'dry_run': True, 'count': len(assertions)}
    
    try:
        # Initialize DataHub ingester
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        
        if not datahub_token:
            logger.error("DATAHUB_GMS_TOKEN environment variable is required")
            return {'error': 'Missing DataHub token'}
        
        ingester = DataHubAssertionIngester(datahub_gms_url, datahub_token)
        
        # Batch create assertions
        results = ingester.batch_create_assertions(assertions)
        
        logger.info(f"Ingested {len(results['successful'])} assertions successfully")
        if results['failed']:
            logger.warning(f"Failed to ingest {len(results['failed'])} assertions")
        
        return results
        
    except Exception as e:
        logger.error(f"Error ingesting assertions to DataHub: {str(e)}")
        return {'error': str(e)}

def main():
    """Main function to orchestrate assertion ingestion."""
    args = parse_arguments()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("DataHub External Assertion Ingestion")
    logger.info("=" * 50)
    
    # Parse sources
    sources = [s.strip() for s in args.sources.split(',')]
    logger.info(f"Processing sources: {sources}")
    
    all_assertions = []
    extraction_results = {}
    
    # Extract assertions from each source
    if 'glue' in sources:
        glue_database = args.glue_database or os.getenv('GLUE_DATABASE_NAME')
        if not glue_database:
            logger.error("Glue database name is required (set GLUE_DATABASE_NAME env var or use --glue-database)")
            return 1
        
        glue_assertions = extract_glue_assertions(glue_database, args.dry_run)
        all_assertions.extend(glue_assertions)
        extraction_results['glue'] = {
            'count': len(glue_assertions),
            'database': glue_database
        }
    
    if 'snowflake' in sources:
        snowflake_database = args.snowflake_database or os.getenv('SNOWFLAKE_DATABASE')
        snowflake_schema = args.snowflake_schema or os.getenv('SNOWFLAKE_SCHEMA')
        
        if not snowflake_database:
            logger.error("Snowflake database name is required (set SNOWFLAKE_DATABASE env var or use --snowflake-database)")
            return 1
        
        snowflake_assertions = extract_snowflake_assertions(snowflake_database, snowflake_schema, args.dry_run)
        all_assertions.extend(snowflake_assertions)
        extraction_results['snowflake'] = {
            'count': len(snowflake_assertions),
            'database': snowflake_database,
            'schema': snowflake_schema
        }
    
    logger.info(f"Total assertions extracted: {len(all_assertions)}")
    
    # Save to file if requested
    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(all_assertions, f, indent=2)
        logger.info(f"Assertions saved to: {args.output_file}")
    
    # Convert to ExternalAssertion objects
    external_assertions = convert_to_external_assertions(all_assertions)
    logger.info(f"Converted {len(external_assertions)} assertions to ExternalAssertion objects")
    
    # Ingest into DataHub
    if not args.dry_run:
        ingestion_results = ingest_assertions_to_datahub(external_assertions, args.dry_run)
        
        if 'error' in ingestion_results:
            logger.error(f"Ingestion failed: {ingestion_results['error']}")
            return 1
        
        # Print summary
        print("\n" + "=" * 60)
        print("ASSERTION INGESTION SUMMARY")
        print("=" * 60)
        
        for source, results in extraction_results.items():
            print(f"{source.title()}: {results['count']} assertions extracted")
        
        print(f"\nTotal assertions: {len(all_assertions)}")
        
        if 'successful' in ingestion_results:
            print(f"Successfully ingested: {len(ingestion_results['successful'])}")
            if ingestion_results['failed']:
                print(f"Failed to ingest: {len(ingestion_results['failed'])}")
        
        print(f"Ingestion completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("\n" + "=" * 60)
        print("DRY RUN SUMMARY")
        print("=" * 60)
        print(f"Would extract and ingest {len(all_assertions)} assertions")
        for source, results in extraction_results.items():
            print(f"{source.title()}: {results['count']} assertions")
    
    return 0

if __name__ == "__main__":
    exit(main())
