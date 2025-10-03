#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def verify_structured_property():
    try:
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        
        headers = {
            'Authorization': f'Bearer {datahub_token}',
            'Content-Type': 'application/json'
        }
        
        # Query to check if structured property exists
        query = """
        query getStructuredProperty($urn: String!) {
            structuredProperty(urn: $urn) {
                name
                displayName
                description
                type
                definition {
                    entityTypes
                    valueType
                }
            }
        }
        """
        
        response = requests.post(
            f"{datahub_gms_url}/graphql",
            json={
                "query": query,
                "variables": {"urn": "urn:li:structuredProperty:retention_period"}
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return False
            
            property_data = data.get('data', {}).get('structuredProperty')
            if property_data:
                print("✅ Structured property 'retention_period' found!")
                print(f"   Name: {property_data['name']}")
                print(f"   Display Name: {property_data['displayName']}")
                print(f"   Type: {property_data['type']}")
                print(f"   Entity Types: {property_data['definition']['entityTypes']}")
                return True
            else:
                print("❌ Structured property 'retention_period' not found")
                return False
        else:
            print(f"❌ Failed to query structured property: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying structured property: {str(e)}")
        return False

if __name__ == "__main__":
    verify_structured_property()
