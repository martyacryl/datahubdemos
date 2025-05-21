#!/bin/bash
# File: datahub/metadata/apply_metadata.sh
# Purpose: Apply custom metadata to DataHub entities using the DataHub REST API

# Check if environment variables are set
if [ -z "$DATAHUB_PAT" ]; then
  if [ -f ../.env ]; then
    echo "Loading environment variables from ../.env file..."
    source ../.env
  else
    echo "Error: DATAHUB_PAT environment variable not set."
    echo "Please run '../ingestion/create_pat.sh' first or set it manually."
    exit 1
  fi
fi

DATAHUB_URL=${DATAHUB_GMS_URL:-"https://test-environment.acryl.io"}

# Function to create a domain
create_domain() {
  local domain_id=$1
  local domain_name=$2
  local domain_description=$3
  
  echo "Creating domain: $domain_name..."
  
  curl -s -X POST "$DATAHUB_URL/api/v2/domain" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DATAHUB_PAT" \
    -d '{
      "id": "'"$domain_id"'",
      "name": "'"$domain_name"'",
      "description": "'"$domain_description"'",
      "properties": {
        "name": "'"$domain_name"'",
        "description": "'"$domain_description"'"
      }
    }' > /dev/null
}

# Create domains from domains.json
echo "Creating domains..."
jq -c '.domains[]' domains.json | while read -r domain; do
  id=$(echo $domain | jq -r '.id')
  name=$(echo $domain | jq -r '.name')
  description=$(echo $domain | jq -r '.description')
  create_domain "$id" "$name" "$description"
done

echo "Metadata application complete!"
