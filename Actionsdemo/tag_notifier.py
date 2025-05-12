# Configuration for tag notification action - Cloud Version
name: "tag_notifier"

# For cloud DataHub, we need to use the REST event source instead of Kafka
source:
  type: "rest" 
  config:
    server: "https://test-environment.acryl.io"
    # Replace with your actual PAT (Personal Access Token)
    token: "token"
    # Poll interval in seconds
    polling_interval: 30

# Filter to only process tag-related events
filter:
  event_type: "EntityChangeEvent_v1"
  event:
    category: "TAG"
    operation: "ADD"

# Define the action to take
action:
  # Reference our custom action
  type: "datahubdemos.actions.tag_notifier:TagNotifierAction"
  config:
    # Notification method: log, slack, or email
    notification_method: "log"
    # List of tags considered to be PII
    pii_tags:
      - "pii"
      - "personal_information"
      - "sensitive"
      - "confidential"
      - "financial"
