#!/usr/bin/env python3
"""
Enhanced runner script for the DataHub Duplicate Detector
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
from duplicate_detector import DataHubDuplicateDetector
from config import get_config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='DataHub Duplicate Asset Detector')
    
    parser.add_argument('--entity-types', 
                       help='Comma-separated list of entity types to analyze (default: dataset,chart,dashboard)',
                       default='dataset,chart,dashboard')
    
    parser.add_argument('--detection-types',
                       help='Comma-separated list of detection types (default: name,schema,description)',
                       default='name,schema,description')
    
    parser.add_argument('--name-threshold',
                       type=float,
                       help='Name similarity threshold (default: 0.8)',
                       default=0.8)
    
    parser.add_argument('--schema-threshold',
                       type=float,
                       help='Schema similarity threshold (default: 0.7)',
                       default=0.7)
    
    parser.add_argument('--min-assets',
                       type=int,
                       help='Minimum number of assets to consider a duplicate group (default: 2)',
                       default=2)
    
    parser.add_argument('--output-dir',
                       help='Output directory for reports (default: ./reports)',
                       default='./reports')
    
    parser.add_argument('--format',
                       choices=['markdown', 'json', 'both'],
                       help='Output format (default: both)',
                       default='both')
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Enable verbose logging')
    
    parser.add_argument('--dry-run',
                       action='store_true',
                       help='Run detection without generating reports')
    
    return parser.parse_args()

def setup_output_directory(output_dir: str):
    """Create output directory if it doesn't exist."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")

def run_detection(args):
    """Run the duplicate detection process."""
    try:
        # Get configuration
        config = get_config()
        
        # Override config with command line arguments
        config.entity_types = [t.strip() for t in args.entity_types.split(',')]
        config.detection_types = [t.strip() for t in args.detection_types.split(',')]
        config.name_similarity_threshold = args.name_threshold
        config.schema_similarity_threshold = args.schema_threshold
        config.min_assets_for_duplicate = args.min_assets
        
        # Validate configuration
        errors = config.validate()
        if errors:
            logger.error("Configuration errors:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        # Create detector
        detector = DataHubDuplicateDetector(config.datahub_gms_url, config.datahub_token)
        
        # Override detector config
        detector.config.name_similarity_threshold = config.name_similarity_threshold
        detector.config.schema_similarity_threshold = config.schema_similarity_threshold
        detector.config.min_assets_for_duplicate = config.min_assets_for_duplicate
        
        logger.info("Starting duplicate detection...")
        logger.info(f"Entity types: {config.entity_types}")
        logger.info(f"Detection types: {config.detection_types}")
        logger.info(f"Name similarity threshold: {config.name_similarity_threshold}")
        logger.info(f"Schema similarity threshold: {config.schema_similarity_threshold}")
        logger.info(f"Minimum assets for duplicate: {config.min_assets_for_duplicate}")
        
        # Run detection
        findings = detector.detect_duplicates(config.entity_types, config.detection_types)
        
        logger.info(f"Detection completed. Found {len(findings)} duplicate groups.")
        
        if args.dry_run:
            logger.info("Dry run mode - no reports generated")
            return True
        
        # Generate reports
        setup_output_directory(args.output_dir)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if args.format in ['markdown', 'both']:
            report_file = os.path.join(args.output_dir, f"duplicate_report_{timestamp}.md")
            detector.generate_report(findings, report_file)
            logger.info(f"Markdown report saved to: {report_file}")
        
        if args.format in ['json', 'both']:
            json_file = os.path.join(args.output_dir, f"duplicate_findings_{timestamp}.json")
            detector.export_findings_json(findings, json_file)
            logger.info(f"JSON report saved to: {json_file}")
        
        # Print summary
        if findings:
            print("\n" + "="*60)
            print("DUPLICATE DETECTION SUMMARY")
            print("="*60)
            
            by_type = {}
            by_confidence = {}
            
            for finding in findings:
                by_type[finding.similarity_type] = by_type.get(finding.similarity_type, 0) + 1
                by_confidence[finding.confidence] = by_confidence.get(finding.confidence, 0) + 1
            
            print(f"Total duplicate groups found: {len(findings)}")
            print(f"By type: {by_type}")
            print(f"By confidence: {by_confidence}")
            
            # Show top findings
            print("\nTop findings:")
            for i, finding in enumerate(findings[:5], 1):
                primary_info = detector.extract_asset_info(finding.primary_asset)
                print(f"  {i}. {finding.similarity_type.title()} - {finding.confidence.upper()} confidence")
                print(f"     Primary: {primary_info['name']} ({primary_info['type']})")
                print(f"     Duplicates: {len(finding.duplicate_assets)}")
                print(f"     Similarity: {finding.similarity_score:.2%}")
                print()
        else:
            print("\n✅ No duplicates found!")
        
        return True
        
    except Exception as e:
        logger.error(f"Detection failed: {str(e)}")
        return False

def main():
    """Main function."""
    args = parse_arguments()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("DataHub Duplicate Asset Detector")
    logger.info("=" * 40)
    
    success = run_detection(args)
    
    if success:
        logger.info("✅ Detection completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Detection failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
