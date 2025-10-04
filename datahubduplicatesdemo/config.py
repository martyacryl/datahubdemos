#!/usr/bin/env python3
"""
Configuration management for the DataHub Duplicate Detector
"""

import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DuplicateDetectorConfig:
    """Configuration class for the duplicate detector."""
    
    # DataHub Configuration
    datahub_gms_url: str = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
    datahub_token: str = os.getenv('DATAHUB_GMS_TOKEN', '')
    
    # Detection Configuration
    entity_types: List[str] = None
    detection_types: List[str] = None
    
    # Similarity Thresholds
    name_similarity_threshold: float = float(os.getenv('NAME_SIMILARITY_THRESHOLD', '0.8'))
    schema_similarity_threshold: float = float(os.getenv('SCHEMA_SIMILARITY_THRESHOLD', '0.7'))
    content_similarity_threshold: float = float(os.getenv('CONTENT_SIMILARITY_THRESHOLD', '0.9'))
    
    # Detection Rules
    min_assets_for_duplicate: int = int(os.getenv('MIN_ASSETS_FOR_DUPLICATE', '2'))
    case_sensitive: bool = os.getenv('CASE_SENSITIVE', 'false').lower() == 'true'
    
    # Common suffixes/prefixes to ignore
    ignore_common_suffixes: List[str] = None
    ignore_common_prefixes: List[str] = None
    
    def __post_init__(self):
        """Initialize derived fields after object creation."""
        if self.entity_types is None:
            entity_types_str = os.getenv('ENTITY_TYPES', 'dataset,chart,dashboard,dataFlow,dataJob')
            self.entity_types = [t.strip() for t in entity_types_str.split(',')]
        
        if self.detection_types is None:
            detection_types_str = os.getenv('DETECTION_TYPES', 'name,schema,description')
            self.detection_types = [t.strip() for t in detection_types_str.split(',')]
        
        if self.ignore_common_suffixes is None:
            self.ignore_common_suffixes = [
                '_backup', '_old', '_temp', '_tmp', '_test', '_dev', '_staging',
                '_v1', '_v2', '_v3', '_new', '_copy', '_duplicate', '_archive',
                '_bak', '_orig', '_previous', '_legacy'
            ]
        
        if self.ignore_common_prefixes is None:
            self.ignore_common_prefixes = [
                'backup_', 'old_', 'temp_', 'tmp_', 'test_', 'dev_', 'staging_',
                'archive_', 'bak_', 'orig_', 'previous_', 'legacy_'
            ]
    
    def validate(self) -> List[str]:
        """Validate the configuration and return any errors."""
        errors = []
        
        if not self.datahub_token:
            errors.append("DATAHUB_GMS_TOKEN is required")
        
        if not self.datahub_gms_url:
            errors.append("DATAHUB_GMS_URL is required")
        
        if not self.entity_types:
            errors.append("At least one entity type must be specified")
        
        if not self.detection_types:
            errors.append("At least one detection type must be specified")
        
        if not (0 <= self.name_similarity_threshold <= 1):
            errors.append("NAME_SIMILARITY_THRESHOLD must be between 0 and 1")
        
        if not (0 <= self.schema_similarity_threshold <= 1):
            errors.append("SCHEMA_SIMILARITY_THRESHOLD must be between 0 and 1")
        
        if not (0 <= self.content_similarity_threshold <= 1):
            errors.append("CONTENT_SIMILARITY_THRESHOLD must be between 0 and 1")
        
        if self.min_assets_for_duplicate < 2:
            errors.append("MIN_ASSETS_FOR_DUPLICATE must be at least 2")
        
        return errors
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            'datahub_gms_url': self.datahub_gms_url,
            'entity_types': self.entity_types,
            'detection_types': self.detection_types,
            'name_similarity_threshold': self.name_similarity_threshold,
            'schema_similarity_threshold': self.schema_similarity_threshold,
            'content_similarity_threshold': self.content_similarity_threshold,
            'min_assets_for_duplicate': self.min_assets_for_duplicate,
            'case_sensitive': self.case_sensitive,
            'ignore_common_suffixes': self.ignore_common_suffixes,
            'ignore_common_prefixes': self.ignore_common_prefixes
        }

def get_config() -> DuplicateDetectorConfig:
    """Get the configuration instance."""
    return DuplicateDetectorConfig()
