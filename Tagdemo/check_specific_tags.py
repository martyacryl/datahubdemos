#!/usr/bin/env python

import requests

# Configuration - modify these values
GMS_URL = "https://test-environment.acryl.io/gms"  # Note: using HTTPS
TOKEN = "token"  # Replace with your token

def check_tag(tag_name):
    """
    Check if a specific tag exists using the entities endpoint.
    """
    # Construct tag URN
    tag_urn = f"urn:li:tag:{tag_name}"
    
    # Headers for the request
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    
    # URL for entity retrieval
    url = f"{GMS_URL}/entities/{tag_urn}"
    
    print(f"Checking tag: {tag_name}")
    print(f"URL: {url}")
    
    try:
        # Make GET request to retrieve the entity
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print(f"Tag '{tag_name}' exists!")
            data = response.json()
            print(f"Details: {data}")
            return True
        else:
            print(f"Failed to find tag '{tag_name}': Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"Error checking tag '{tag_name}': {e}")
        return False

def main():
    # Tags to check
    tags_to_check = ["PII", "Deprecated", "Important", "Tested", "Experimental"]
    
    # Check each tag
    found_tags = []
    for tag_name in tags_to_check:
        print("-" * 50)
        if check_tag(tag_name):
            found_tags.append(tag_name)
        print()
    
    # Summary
    print("=" * 50)
    print(f"Found {len(found_tags)} out of {len(tags_to_check)} tags:")
    for tag in found_tags:
        print(f"- {tag}")

if __name__ == "__main__":
    main()
