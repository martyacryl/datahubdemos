#!/bin/bash
# Script to run DataHub Actions for cloud environment

# Check if token is set
if [ -z "$DATAHUB_TOKEN" ]; then
  echo "Error: DATAHUB_TOKEN environment variable is not set"
  echo "Please set it with: export DATAHUB_TOKEN=your_personal_access_token"
  exit 1
fi

# Display current configuration
echo "=== DataHub Actions Setup ==="
echo "DataHub Cloud URL: https://test-environment.acryl.io"
echo "PAT Token: ${DATAHUB_TOKEN:0:5}... (first 5 characters shown)"
echo

# Ask which action to run
echo "Which action would you like to run?"
echo "1) Tag Notifier"
echo "2) Quality Monitor"
echo "3) Both actions in separate processes"
echo "q) Quit"
read -p "Select an option [1/2/3/q]: " option

case $option in
  1)
    echo "Starting Tag Notifier action..."
    datahub actions run --action-file datahubdemos/configs/tag_notifier_cloud.yaml
    ;;
  2)
    echo "Starting Quality Monitor action..."
    datahub actions run --action-file datahubdemos/configs/quality_monitor_cloud.yaml
    ;;
  3)
    echo "Starting both actions in separate processes..."
    datahub actions run --action-file datahubdemos/configs/tag_notifier_cloud.yaml > tag_notifier.log 2>&1 &
    TAG_PID=$!
    echo "Tag Notifier started with PID: $TAG_PID"
    
    datahub actions run --action-file datahubdemos/configs/quality_monitor_cloud.yaml > quality_monitor.log 2>&1 &
    QUALITY_PID=$!
    echo "Quality Monitor started with PID: $QUALITY_PID"
    
    echo "Actions are running in background. Check logs with:"
    echo "  tail -f tag_notifier.log"
    echo "  tail -f quality_monitor.log"
    ;;
  q|Q)
    echo "Exiting..."
    exit 0
    ;;
  *)
    echo "Invalid option. Exiting."
    exit 1
    ;;
esac