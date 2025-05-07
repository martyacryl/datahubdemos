# Configuration for tag notification action - Cloud Version
name: "tag_notifier"

# For cloud DataHub, we need to use the REST event source instead of Kafka
source:
  type: "rest" 
  config:
    server: "https://test-environment.acryl.io"
    # Replace with your actual PAT (Personal Access Token)
    token: "eyJhbGciOiJIUzI1NiJ9.eyJhY3RvclR5cGUiOiJVU0VSIiwiYWN0b3JJZCI6Im1hcnR5LnN0am9obkBhY3J5bC5pbyIsInR5cGUiOiJQRVJTT05BTCIsInZlcnNpb24iOiIyIiwianRpIjoiMzBlZTRiOTUtYjg4Ny00ZjgzLWI0YWItNTQxMzlmMTQwNTQ1Iiwic3ViIjoibWFydHkuc3Rqb2huQGFjcnlsLmlvIiwiaXNzIjoiZGF0YWh1Yi1tZXRhZGF0YS1zZXJ2aWNlIn0.UG_Ge9EBtpBdyHhWcantlGCoZLJZgX9E7u49GCeF6CY"
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