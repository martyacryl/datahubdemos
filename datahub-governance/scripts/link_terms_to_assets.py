#!/usr/bin/env python3
"""
Script to link glossary terms to data assets.
"""

import json
import requests
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# DataHub API configuration
DATAHUB_URL = "http://localhost:8080"  # Update with your DataHub URL
TOKEN = "YOUR_TOKEN_HERE"  # Update with your authentication token

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def link_term_to_asset(term_urn, asset_urn):
    """
    Link a glossary term to a data asset
    
    Parameters:
        term_urn (str): The URN of the glossary term
        asset_urn (str): The URN of the data asset
    
    Returns:
        bool: True if term was linked successfully, False otherwise
    """
    try:
        # Prepare the payload
        payload = {
            "urn": asset_urn,
            "aspect": {
                "glossaryTerms": {
                    "terms": [
                        {
                            "urn": term_urn
                        }
                    ]
                }
            }
        }
        
        # Link term to asset
        response = requests.post(
            f"{DATAHUB_URL}/entities?action=ingest",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully linked term {term_urn} to asset {asset_urn}")
            return True
        else:
            logger.error(f"Failed to link term to asset: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error linking term to asset: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: link_terms_to_assets.py <term_urn> <asset_urn>")
        sys.exit(1)
        
    term_urn = sys.argv[1]
    asset_urn = sys.argv[2]
    
    link_term_to_asset(term_urn, asset_urn)
