#!/bin/bash
# File: datahub/ingestion/create_pat.sh
# Purpose: Create a Personal Access Token for DataHub ingestion

# Set variables for DataHub access
DATAHUB_URL="https://test-environment.acryl.io"
DATAHUB_USERNAME=""  # Set your DataHub username
DATAHUB_PASSWORD=""  # Set your DataHub password

# Prompt for credentials if not set
if [ -z "$DATAHUB_USERNAME" ]; then
  read -p "Enter your DataHub username: " DATAHUB_USERNAME
fi

if [ -z "$DATAHUB_PASSWORD" ]; then
  read -s -p "Enter your DataHub password: " DATAHUB_PASSWORD
  echo
fi

# Authenticate and get JWT token
echo "Authenticating with DataHub..."
RESPONSE=$(curl -s -X POST "$DATAHUB_URL/authenticate" \
  -H "Content-Type: application/json" \
  -d '{"username":"'"$DATAHUB_USERNAME"'","password":"'"$DATAHUB_PASSWORD"'"}')

JWT_TOKEN=$(echo $RESPONSE | grep -o '"token":"[^"]*' | sed 's/"token":"//')

if [ -z "$JWT_TOKEN" ]; then
  echo "Failed to authenticate. Check your credentials."
  exit 1
fi

# Create a Personal Access Token (PAT)
echo "Creating Personal Access Token..."
PAT_RESPONSE=$(curl -s -X POST "$DATAHUB_URL/openapi/personaltokens" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "name": "snowflake-finserv-integration",
    "description": "Token for Snowflake Financial Services integration",
    "expiresAt": null
  }')

PAT_TOKEN=$(echo $PAT_RESPONSE | grep -o '"token":"[^"]*' | sed 's/"token":"//')

if [ -z "$PAT_TOKEN" ]; then
  echo "Failed to create PAT. Response: $PAT_RESPONSE"
  exit 1
fi

# Output the PAT to a file
echo "export DATAHUB_PAT=\"$PAT_TOKEN\"" > .env
echo "export DATAHUB_GMS_URL=\"$DATAHUB_URL\"" >> .env

echo "Personal Access Token created and saved to .env file."
echo "Run 'source .env' to load the token into your environment."
