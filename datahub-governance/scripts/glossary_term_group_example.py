#!/usr/bin/env python3
"""
Example script to create and manage term groups in DataHub.
This demonstrates how to create term groups and add terms to these groups.
"""

import json
import requests
import logging
from urllib.parse import quote

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

def create_glossary_node(glossary_id="main", node_type="node"):
    """
    Create a glossary node (term group is created as a 'node')
    
    Parameters:
        glossary_id (str): The ID of the glossary (default: "main")
        node_type (str): The type of node ("term" or "node", default: "node")
    
    Returns:
        str: The URN of the created glossary node
    """
    try:
        # Create glossary node
        response = requests.post(
            f"{DATAHUB_URL}/glossary/{glossary_id}/{node_type}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            node_urn = data.get("urn")
            logger.info(f"Successfully created glossary {node_type}: {node_urn}")
            return node_urn
        else:
            logger.error(f"Failed to create glossary {node_type}: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error creating glossary {node_type}: {str(e)}")
        return None

def update_term_group(group_urn, group_data):
    """
    Update a term group with provided data
    
    Parameters:
        group_urn (str): The URN of the term group
        group_data (dict): The group data to update
    
    Returns:
        bool: True if group was updated successfully, False otherwise
    """
    try:
        # Extract the group name from the URN
        group_parts = group_urn.split(":")
        if len(group_parts) >= 4:
            group_id = group_parts[3]
        else:
            logger.error(f"Invalid group URN format: {group_urn}")
            return False
        
        # Prepare the payload for group update
        payload = {
            "name": group_data.get("name", ""),
            "description": group_data.get("description", "")
        }
        
        # Add custom properties if provided
        if "customProperties" in group_data:
            payload["customProperties"] = group_data["customProperties"]
        
        # Update the group
        response = requests.put(
            f"{DATAHUB_URL}/glossaryNodes/{quote(group_id)}",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully updated term group: {group_data.get('name')}")
            
            # Set group owners if provided
            if "owners" in group_data:
                set_owners(group_urn, group_data["owners"])
            
            return True
        else:
            logger.error(f"Failed to update term group: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error updating term group: {str(e)}")
        return False

def set_owners(entity_urn, owners):
    """
    Set owners for an entity
    
    Parameters:
        entity_urn (str): The entity URN
        owners (list): List of owner objects with owner URN and type
    
    Returns:
        bool: True if owners were set successfully, False otherwise
    """
    try:
        # Prepare the ownership payload
        payload = {
            "urn": entity_urn,
            "aspect": {
                "ownership": {
                    "owners": owners
                }
            }
        }
        
        # Set entity owners
        response = requests.post(
            f"{DATAHUB_URL}/entities?action=ingest",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully set owners for entity: {entity_urn}")
            return True
        else:
            logger.error(f"Failed to set entity owners: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error setting entity owners: {str(e)}")
        return False

def create_term(glossary_id="main"):
    """
    Create a glossary term
    
    Parameters:
        glossary_id (str): The ID of the glossary (default: "main")
    
    Returns:
        str: The URN of the created term
    """
    return create_glossary_node(glossary_id, "term")

def update_term(term_urn, term_data):
    """
    Update a glossary term with provided data
    
    Parameters:
        term_urn (str): The URN of the glossary term
        term_data (dict): The term data to update
    
    Returns:
        bool: True if term was updated successfully, False otherwise
    """
    try:
        # Extract the term name from the URN
        term_parts = term_urn.split(":")
        if len(term_parts) >= 4:
            term_id = term_parts[3]
        else:
            logger.error(f"Invalid term URN format: {term_urn}")
            return False
        
        # Prepare the payload for term update
        payload = {
            "name": term_data.get("name", ""),
            "description": term_data.get("description", ""),
            "termSource": term_data.get("termSource", "INTERNAL")
        }
        
        # Add custom properties if provided
        if "customProperties" in term_data:
            payload["customProperties"] = term_data["customProperties"]
        
        # Update the term
        response = requests.put(
            f"{DATAHUB_URL}/glossaryTerms/{quote(term_id)}",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully updated glossary term: {term_data.get('name')}")
            
            # Set term owners if provided
            if "owners" in term_data:
                set_owners(term_urn, term_data["owners"])
            
            return True
        else:
            logger.error(f"Failed to update glossary term: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error updating glossary term: {str(e)}")
        return False

def add_term_to_group(term_urn, group_urn):
    """
    Add a term to a term group
    
    Parameters:
        term_urn (str): The URN of the glossary term
        group_urn (str): The URN of the term group
    
    Returns:
        bool: True if term was added to group successfully, False otherwise
    """
    try:
        # Prepare the payload
        payload = {
            "urn": term_urn,
            "aspect": {
                "parentNodes": {
                    "nodes": [
                        {
                            "urn": group_urn
                        }
                    ]
                }
            }
        }
        
        # Add term to group
        response = requests.post(
            f"{DATAHUB_URL}/entities?action=ingest",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully added term {term_urn} to group {group_urn}")
            return True
        else:
            logger.error(f"Failed to add term to group: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error adding term to group: {str(e)}")
        return False

def add_term_to_parent_term(child_term_urn, parent_term_urn):
    """
    Add a term as a child of another term
    
    Parameters:
        child_term_urn (str): The URN of the child glossary term
        parent_term_urn (str): The URN of the parent glossary term
    
    Returns:
        bool: True if term was added as child successfully, False otherwise
    """
    return add_term_to_group(child_term_urn, parent_term_urn)

if __name__ == "__main__":
    # Create a new term group (node)
    finance_group_urn = create_glossary_node(glossary_id="main", node_type="node")
    
    if finance_group_urn:
        # Example term group data
        finance_group_data = {
            "name": "Financial Metrics",
            "description": "Terms related to financial performance and metrics",
            "owners": [
                {
                    "owner": "urn:li:corpuser:finance_team_lead",
                    "type": "DATAOWNER"
                }
            ],
            "customProperties": {
                "department": "Finance",
                "dataClassification": "Confidential"
            }
        }
        
        # Update the term group with data
        success = update_term_group(finance_group_urn, finance_group_data)
        
        if success:
            # Create terms for the group
            terms_to_create = [
                {
                    "name": "Revenue",
                    "description": "Total income generated from business activities and sales before any expenses are deducted.",
                    "termSource": "INTERNAL",
                    "owners": [
                        {
                            "owner": "urn:li:corpuser:finance_team_lead",
                            "type": "DATAOWNER"
                        }
                    ],
                    "customProperties": {
                        "formula": "Sum of all income from sales and services",
                        "reporting_frequency": "Monthly"
                    }
                },
                {
                    "name": "EBITDA",
                    "description": "Earnings Before Interest, Taxes, Depreciation, and Amortization. A measure of a company's overall financial performance.",
                    "termSource": "INTERNAL",
                    "owners": [
                        {
                            "owner": "urn:li:corpuser:finance_team_lead",
                            "type": "DATAOWNER"
                        }
                    ],
                    "customProperties": {
                        "formula": "Revenue - Expenses (excluding interest, taxes, depreciation, amortization)",
                        "reporting_frequency": "Quarterly"
                    }
                },
                {
                    "name": "Gross Profit Margin",
                    "description": "A financial metric used to assess a company's financial health and business model by revealing the proportion of money left over from revenues after accounting for the cost of goods sold.",
                    "termSource": "INTERNAL",
                    "owners": [
                        {
                            "owner": "urn:li:corpuser:finance_team_lead",
                            "type": "DATAOWNER"
                        }
                    ],
                    "customProperties": {
                        "formula": "(Revenue - COGS) / Revenue",
                        "reporting_frequency": "Quarterly"
                    }
                }
            ]
            
            # Create and add terms to the group
            for term_data in terms_to_create:
                # Create the term
                term_urn = create_term()
                if term_urn:
                    # Update the term with data
                    update_term(term_urn, term_data)
                    # Add the term to the financial metrics group
                    add_term_to_group(term_urn, finance_group_urn)
            
            # Create a sub-term under EBITDA
            adjusted_ebitda_urn = create_term()
            if adjusted_ebitda_urn:
                adjusted_ebitda_data = {
                    "name": "Adjusted EBITDA",
                    "description": "EBITDA adjusted for one-time or unusual items that are not part of normal business operations.",
                    "termSource": "INTERNAL",
                    "owners": [
                        {
                            "owner": "urn:li:corpuser:finance_team_lead",
                            "type": "DATAOWNER"
                        }
                    ]
                }
                # Update the term with data
                update_term(adjusted_ebitda_urn, adjusted_ebitda_data)
                
                # Find the EBITDA term URN
                # In a real scenario, you would search for the term or store the URN when creating it
                # For this example, we'll assume we know the EBITDA term's URN
                ebitda_term_urn = "urn:li:glossaryTerm:ebitda"  # This should be replaced with the actual URN
                
                # Add Adjusted EBITDA as a child term of EBITDA
                add_term_to_parent_term(adjusted_ebitda_urn, ebitda_term_urn)
            
            print("Term group and terms created successfully!")