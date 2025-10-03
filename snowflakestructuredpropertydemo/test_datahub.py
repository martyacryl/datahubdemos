#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_datahub_connection():
    try:
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        
        # Test DataHub connection
        headers = {
            'Authorization': f'Bearer {datahub_token}',
            'Content-Type': 'application/json'
        }
        
        # Simple search query
        search_query = {
            "query": "*",
            "entityTypes": ["dataset"],
            "start": 0,
            "count": 1
        }
        
        response = requests.post(
            f"{datahub_gms_url}/graphql",
            json={
                "query": """
                query search($input: SearchInput!) {
                    search(input: $input) {
                        searchResults {
                            entity {
                                urn
                                type
                            }
                        }
                    }
                }
                """,
                "variables": {"input": search_query}
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"❌ DataHub GraphQL errors: {data['errors']}")
                return False
            
            search_results = data.get('data', {}).get('search', {}).get('searchResults', [])
            print(f"✅ DataHub connection successful!")
            print(f"✅ Found {len(search_results)} datasets (showing first 1)")
            
            if search_results:
                print(f"✅ Sample dataset URN: {search_results[0]['entity']['urn']}")
            
            return True
        else:
            print(f"❌ DataHub connection failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ DataHub connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_datahub_connection()
