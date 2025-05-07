# DataHub Cloud Actions Framework Demo

This guide provides instructions for using the DataHub Actions Framework with your DataHub Cloud account at https://test-environment.acryl.io/.

## Setup for Cloud Deployment

When working with DataHub Cloud, there are a few key differences compared to self-hosted DataHub:

1. You need to use a REST event source instead of Kafka
2. You must authenticate using a Personal Access Token (PAT)
3. Event polling occurs via API rather than direct Kafka consumption

## Configuration

The updated configuration files for cloud usage are:
- `tag_notifier_cloud.yaml`
- `quality_monitor_cloud.yaml`

## Authentication Setup

1. Generate a Personal Access Token (PAT) from your DataHub Cloud account:
   - Log in to https://test-environment.acryl.io/
   - Navigate to Settings → Personal Access Tokens
   - Create a new token with appropriate permissions
   - Copy the token value

2. Set the token as an environment variable:
   ```bash
   export DATAHUB_TOKEN="your_personal_access_token_here"
   ```

## Running the Actions

```bash
# Run the Tag Notifier action
datahub actions run --action-file datahubdemos/configs/tag_notifier_cloud.yaml

# Run the Quality Monitor action
datahub actions run --action-file datahubdemos/configs/quality_monitor_cloud.yaml
```

## Troubleshooting

If you encounter issues:

1. Verify your token has the necessary permissions
2. Check that your token is correctly set in the environment variable
3. Increase logging verbosity for debugging:
   ```bash
   datahub actions run --action-file datahubdemos/configs/tag_notifier_cloud.yaml --verbose
   ```
4. Ensure you have network connectivity to the cloud instance

## REST Source Parameters

The REST event source has additional configuration options that may be useful:

```yaml
source:
  type: "rest"
  config:
    server: "https://test-environment.acryl.io"
    token: "${DATAHUB_TOKEN}"
    # Optional parameters
    polling_interval: 30  # Seconds between polls (default: 30)
    timeout: 10           # Request timeout in seconds (default: 10)
    retry_count: 3        # Number of retries (default: 3)
    retry_interval: 5     # Seconds between retries (default: 5)
```

Adjust these parameters as needed for your specific use case.