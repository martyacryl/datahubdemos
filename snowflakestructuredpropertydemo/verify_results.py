#!/usr/bin/env python3
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def verify_retention_properties():
    try:
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        
        headers = {
            'Authorization': f'Bearer {datahub_token}',
            'Content-Type': 'application/json'
        }
        
        # Query to find assets with retention properties
        query = """
        query search($input: SearchInput!) {
            search(input: $input) {
                searchResults {
                    entity {
                        urn
                        type
                        ... on Dataset {
                            structuredProperties {
                                structuredProperty {
                                    name
                                }
                                values {
                                    value
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        # Search for datasets with retention_period property
        search_input = {
            "query": "structuredProperties:retention_period",
            "entityTypes": ["dataset"],
            "start": 0,
            "count": 10
        }
        
        response = requests.post(
            f"{datahub_gms_url}/graphql",
            json={
                "query": query,
                "variables": {"input": search_input}
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return False
            
            search_results = data.get('data', {}).get('search', {}).get('searchResults', [])
            print(f"✅ Found {len(search_results)} datasets with retention properties")
            
            for result in search_results[:3]:  # Show first 3
                entity = result['entity']
                urn = entity['urn']
                properties = entity.get('structuredProperties', [])
                
                print(f"\n📊 Dataset: {urn}")
                for prop in properties:
                    if prop['structuredProperty']['name'] == 'retention_period':
                        value = json.loads(prop['values'][0]['value'])
                        print(f"   Retention Time: {value.get('retention_time')} days")
                        print(f"   Retention Unit: {value.get('retention_unit')}")
                        print(f"   Enabled: {value.get('is_retention_enabled')}")
                        print(f"   Last Updated: {value.get('last_updated')}")
            
            return True
        else:
            print(f"❌ Failed to query results: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying results: {str(e)}")
        return False

if __name__ == "__main__":
    verify_retention_properties()
