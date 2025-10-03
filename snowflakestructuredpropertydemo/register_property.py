#!/usr/bin/env python3
"""
Register the retention period structured property in DataHub
"""

import json
import os
import requests
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_structured_property(datahub_gms_url: str, datahub_token: str):
    """Register the retention period structured property in DataHub."""
    
    # Load the property schema
    with open('retention_property_schema.json', 'r') as f:
        property_schema = json.load(f)
    
    # Prepare the mutation
    mutation = """
    mutation createStructuredProperty($input: CreateStructuredPropertyInput!) {
        createStructuredProperty(input: $input)
    }
    """
    
    variables = {
        "input": {
            "name": property_schema["name"],
            "displayName": property_schema["displayName"],
            "description": property_schema["description"],
            "type": property_schema["type"],
            "definition": {
                "entityTypes": ["dataset"],
                "valueType": property_schema["type"],
                "fields": property_schema["fields"]
            }
        }
    }
    
    # Make the request
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {datahub_token}',
        'Content-Type': 'application/json'
    })
    
    try:
        response = session.post(
            f"{datahub_gms_url}/graphql",
            json={
                "query": mutation,
                "variables": variables
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Error creating structured property: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        if 'errors' in data:
            logger.error(f"GraphQL errors: {data['errors']}")
            return False
        
        logger.info("Successfully created structured property: retention_period")
        return True
        
    except Exception as e:
        logger.error(f"Error creating structured property: {str(e)}")
        return False

def main():
    datahub_gms_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
    datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
    
    if not datahub_token:
        logger.error("DATAHUB_GMS_TOKEN environment variable is required")
        sys.exit(1)
    
    success = register_structured_property(datahub_gms_url, datahub_token)
    if success:
        logger.info("Structured property registration completed successfully")
    else:
        logger.error("Failed to register structured property")
        sys.exit(1)

if __name__ == "__main__":
    main()
