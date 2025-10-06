#!/usr/bin/env python3
"""
DataHub Custom Assertion Ingester
Uses DataHub Python SDK to create and manage custom assertions from external sources.
Based on: https://docs.datahub.com/docs/api/tutorials/custom-assertions
"""

import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ExternalAssertion:
    """Represents an assertion from an external source (Glue, Snowflake, etc.)"""
    source_id: str  # Unique ID from source system
    entity_urn: str  # DataHub URN of the entity being monitored
    assertion_type: str  # Type of assertion (e.g., "Data Type Validation", "Custom Constraint")
    description: str  # Human-readable description
    platform: str  # Source platform (e.g., "aws-glue", "snowflake")
    field_path: Optional[str] = None  # Optional field path for field-level assertions
    external_url: Optional[str] = None  # Optional URL to source system
    logic: Optional[str] = None  # Optional SQL logic for the assertion
    properties: Optional[Dict[str, str]] = None  # Additional properties

@dataclass
class AssertionResult:
    """Represents the result of an assertion evaluation"""
    assertion_urn: str
    timestamp_millis: int
    result_type: str  # SUCCESS, FAILURE, ERROR, INIT
    properties: Optional[Dict[str, str]] = None
    external_url: Optional[str] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None

class DataHubAssertionIngester:
    """Main class for ingesting custom assertions into DataHub."""
    
    def __init__(self, datahub_gms_url: str, datahub_token: str):
        self.datahub_gms_url = datahub_gms_url.rstrip('/')
        self.datahub_token = datahub_token
        
        # Initialize DataHub Graph client
        self.graph = DataHubGraph(
            config=DatahubClientConfig(
                server=self.datahub_gms_url,
                token=self.datahub_token,
            )
        )
        
        logger.info(f"Initialized DataHub client for {self.datahub_gms_url}")
    
    def create_assertion(self, assertion: ExternalAssertion) -> Optional[str]:
        """
        Create a custom assertion in DataHub using the upsert_custom_assertion method.
        Based on: https://docs.datahub.com/docs/api/tutorials/custom-assertions#create-and-update-custom-assertions
        """
        try:
            # Generate assertion URN
            assertion_urn = f"urn:li:assertion:{assertion.source_id}"
            
            # Map platform name to URN if needed
            platform_urn = self._get_platform_urn(assertion.platform)
            
            logger.info(f"Creating assertion: {assertion_urn}")
            logger.debug(f"Assertion details: {assertion}")
            
            # Upsert the custom assertion
            result = self.graph.upsert_custom_assertion(
                urn=assertion_urn,
                entity_urn=assertion.entity_urn,
                type=assertion.assertion_type,
                description=assertion.description,
                platform_urn=platform_urn,
                field_path=assertion.field_path,
                external_url=assertion.external_url,
                logic=assertion.logic
            )
            
            if result:
                logger.info(f"Successfully created assertion: {assertion_urn}")
                return assertion_urn
            else:
                logger.error(f"Failed to create assertion: {assertion_urn}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating assertion {assertion.source_id}: {str(e)}")
            return None
    
    def report_assertion_result(self, result: AssertionResult) -> bool:
        """
        Report the result of an assertion evaluation.
        Based on: https://docs.datahub.com/docs/api/tutorials/custom-assertions#report-results-for-custom-assertions
        """
        try:
            logger.info(f"Reporting result for assertion: {result.assertion_urn}")
            logger.debug(f"Result details: {result}")
            
            # Convert properties dict to list of key-value pairs
            properties_list = []
            if result.properties:
                properties_list = [{"key": k, "value": v} for k, v in result.properties.items()]
            
            # Report the assertion result
            success = self.graph.report_assertion_result(
                urn=result.assertion_urn,
                timestamp_millis=result.timestamp_millis,
                type=result.result_type,
                properties=properties_list,
                external_url=result.external_url,
                error_type=result.error_type,
                error_message=result.error_message
            )
            
            if success:
                logger.info(f"Successfully reported result for assertion: {result.assertion_urn}")
                return True
            else:
                logger.error(f"Failed to report result for assertion: {result.assertion_urn}")
                return False
                
        except Exception as e:
            logger.error(f"Error reporting result for assertion {result.assertion_urn}: {str(e)}")
            return False
    
    def create_assertion_with_result(self, assertion: ExternalAssertion, 
                                   result_type: str = "INIT",
                                   result_properties: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Create an assertion and immediately report an initial result.
        """
        # Create the assertion
        assertion_urn = self.create_assertion(assertion)
        
        if assertion_urn:
            # Report initial result
            result = AssertionResult(
                assertion_urn=assertion_urn,
                timestamp_millis=int(time.time() * 1000),
                result_type=result_type,
                properties=result_properties,
                external_url=assertion.external_url
            )
            
            if self.report_assertion_result(result):
                return assertion_urn
        
        return None
    
    def batch_create_assertions(self, assertions: List[ExternalAssertion]) -> Dict[str, Any]:
        """
        Create multiple assertions in batch.
        """
        results = {
            'successful': [],
            'failed': [],
            'total': len(assertions)
        }
        
        logger.info(f"Processing {len(assertions)} assertions in batch")
        
        for assertion in assertions:
            assertion_urn = self.create_assertion(assertion)
            
            if assertion_urn:
                results['successful'].append({
                    'source_id': assertion.source_id,
                    'assertion_urn': assertion_urn,
                    'entity_urn': assertion.entity_urn
                })
            else:
                results['failed'].append({
                    'source_id': assertion.source_id,
                    'entity_urn': assertion.entity_urn,
                    'error': 'Failed to create assertion'
                })
        
        logger.info(f"Batch processing complete: {len(results['successful'])} successful, {len(results['failed'])} failed")
        return results
    
    def get_assertions_for_entity(self, entity_urn: str) -> List[Dict[str, Any]]:
        """
        Retrieve all assertions for a specific entity.
        Based on: https://docs.datahub.com/docs/api/tutorials/custom-assertions#retrieve-results-for-custom-assertions
        """
        try:
            # Query for assertions on the entity
            query = """
            query getEntityAssertions($urn: String!) {
                dataset(urn: $urn) {
                    assertions(start: 0, count: 1000) {
                        start
                        count
                        total
                        assertions {
                            urn
                            runEvents(status: COMPLETE, limit: 1) {
                                total
                                failed
                                succeeded
                                runEvents {
                                    timestampMillis
                                    status
                                    result {
                                        type
                                        nativeResults {
                                            key
                                            value
                                        }
                                    }
                                }
                            }
                            info {
                                type
                                customType
                                description
                                lastUpdated {
                                    time
                                    actor
                                }
                                customAssertion {
                                    entityUrn
                                    fieldPath
                                    externalUrl
                                    logic
                                }
                            }
                        }
                    }
                }
            }
            """
            
            result = self.graph.execute_graphql(query, {"urn": entity_urn})
            
            if result and 'data' in result and 'dataset' in result['data']:
                dataset = result['data']['dataset']
                if dataset and 'assertions' in dataset:
                    return dataset['assertions']['assertions']
            
            return []
            
        except Exception as e:
            logger.error(f"Error retrieving assertions for entity {entity_urn}: {str(e)}")
            return []
    
    def _get_platform_urn(self, platform_name: str) -> str:
        """Map platform name to DataHub platform URN."""
        platform_mapping = {
            'aws-glue': 'urn:li:dataPlatform:glue',
            'snowflake': 'urn:li:dataPlatform:snowflake',
            'great-expectations': 'urn:li:dataPlatform:great-expectations',
            'dbt': 'urn:li:dataPlatform:dbt',
            'custom': 'urn:li:dataPlatform:custom'
        }
        
        return platform_mapping.get(platform_name.lower(), f'urn:li:dataPlatform:{platform_name.lower()}')
    
    def validate_assertion_data(self, assertion: ExternalAssertion) -> List[str]:
        """Validate assertion data before creating."""
        errors = []
        
        if not assertion.source_id:
            errors.append("source_id is required")
        
        if not assertion.entity_urn:
            errors.append("entity_urn is required")
        
        if not assertion.assertion_type:
            errors.append("assertion_type is required")
        
        if not assertion.description:
            errors.append("description is required")
        
        if not assertion.platform:
            errors.append("platform is required")
        
        # Validate entity URN format
        if assertion.entity_urn and not assertion.entity_urn.startswith('urn:li:'):
            errors.append("entity_urn must be a valid DataHub URN")
        
        return errors

def main():
    """Example usage of the DataHub Assertion Ingester."""
    # Configuration from environment variables
    datahub_gms_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
    datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
    
    if not datahub_token:
        logger.error("DATAHUB_GMS_TOKEN environment variable is required")
        return
    
    # Create ingester
    ingester = DataHubAssertionIngester(datahub_gms_url, datahub_token)
    
    # Example assertion from Glue
    glue_assertion = ExternalAssertion(
        source_id="glue-table-constraint-001",
        entity_urn="urn:li:dataset:(urn:li:dataPlatform:glue,sample_db.users,PROD)",
        assertion_type="Data Type Validation",
        description="Validates that the 'id' column is of type INTEGER",
        platform="aws-glue",
        field_path="id",
        external_url="https://console.aws.amazon.com/glue/home?region=us-west-2#etl:tab=databases",
        logic="SELECT COUNT(*) FROM users WHERE id IS NOT NULL AND id::INTEGER IS NULL",
        properties={
            "constraint_type": "data_type",
            "expected_type": "INTEGER",
            "column_name": "id"
        }
    )
    
    # Example assertion from Snowflake
    snowflake_assertion = ExternalAssertion(
        source_id="snowflake-check-constraint-001",
        entity_urn="urn:li:dataset:(urn:li:dataPlatform:snowflake,sample_db.orders,PROD)",
        assertion_type="Custom Constraint",
        description="Validates that order_amount is greater than 0",
        platform="snowflake",
        field_path="order_amount",
        external_url="https://app.snowflake.com/console/account/123456/warehouses",
        logic="SELECT COUNT(*) FROM orders WHERE order_amount <= 0",
        properties={
            "constraint_type": "check_constraint",
            "constraint_name": "CHK_ORDER_AMOUNT_POSITIVE",
            "expression": "order_amount > 0"
        }
    )
    
    # Create assertions
    logger.info("Creating example assertions...")
    
    glue_urn = ingester.create_assertion_with_result(
        glue_assertion, 
        result_type="SUCCESS",
        result_properties={"validation_passed": "true", "records_checked": "1000"}
    )
    
    snowflake_urn = ingester.create_assertion_with_result(
        snowflake_assertion,
        result_type="FAILURE", 
        result_properties={"validation_passed": "false", "violations_found": "5"}
    )
    
    if glue_urn:
        logger.info(f"Created Glue assertion: {glue_urn}")
    
    if snowflake_urn:
        logger.info(f"Created Snowflake assertion: {snowflake_urn}")
    
    logger.info("Assertion ingestion example completed!")

if __name__ == "__main__":
    main()
