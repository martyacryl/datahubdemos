#!/bin/bash
set -e

# Display help if requested
if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
  echo "DataHub Snowflake Ingestion Container"
  echo "-------------------------------------"
  echo "Available commands:"
  echo "  ingest [config_file]         - Run a standard ingestion with the specified config file"
  echo "  enhanced-ingest              - Run the enhanced ingestion with custom metadata"
  echo "  monitor [pipeline_name]      - Monitor the specified pipeline"
  echo "  cron                         - Start scheduled ingestion based on SCHEDULE environment variable"
  echo "  help                         - Display this help message"
  echo ""
  echo "Environment variables:"
  echo "  DATAHUB_GMS_URL              - DataHub GMS URL (required)"
  echo "  SNOWFLAKE_ACCOUNT            - Snowflake account identifier (required for enhanced-ingest)"
  echo "  SNOWFLAKE_USER               - Snowflake username (required for enhanced-ingest)"
  echo "  SNOWFLAKE_PASS               - Snowflake password (required for enhanced-ingest)"
  echo "  SNOWFLAKE_WAREHOUSE          - Snowflake warehouse (required for enhanced-ingest)"
  echo "  SNOWFLAKE_ROLE               - Snowflake role (required for enhanced-ingest)"
  echo "  SNOWFLAKE_DATABASES          - Comma-separated list of databases (required for enhanced-ingest)"
  echo "  SCHEDULE                     - Cron schedule for ingestion (required for cron mode)"
  echo "  SLACK_WEBHOOK                - Slack webhook URL for monitoring alerts"
  exit 0
fi

# Verify required environment variables
if [ -z "$DATAHUB_GMS_URL" ]; then
  echo "Error: DATAHUB_GMS_URL environment variable is required"
  exit 1
fi

# Command-specific behavior
case "$1" in
  "ingest")
    if [ -z "$2" ]; then
      echo "Error: Config file is required for ingestion"
      echo "Usage: ingest [config_file]"
      exit 1
    fi
    
    echo "Running ingestion with config: $2"
    datahub ingest -c "$2"
    ;;
  
  "enhanced-ingest")
    # Verify required environment variables for enhanced ingestion
    for var in SNOWFLAKE_ACCOUNT SNOWFLAKE_USER SNOWFLAKE_PASS SNOWFLAKE_WAREHOUSE SNOWFLAKE_ROLE SNOWFLAKE_DATABASES; do
      if [ -z "${!var}" ]; then
        echo "Error: $var environment variable is required for enhanced ingestion"
        exit 1
      fi
    done
    
    # Convert comma-separated databases to space-separated for command line arguments
    DATABASES=$(echo $SNOWFLAKE_DATABASES | tr ',' ' ')
    DB_ARGS=""
    for db in $DATABASES; do
      DB_ARGS="$DB_ARGS --database $db"
    done
    
    echo "Running enhanced ingestion"
    python /app/custom_snowflake_ingestion.py \
      --account-id "$SNOWFLAKE_ACCOUNT" \
      --username "$SNOWFLAKE_USER" \
      --password "$SNOWFLAKE_PASS" \
      --warehouse "$SNOWFLAKE_WAREHOUSE" \
      --role "$SNOWFLAKE_ROLE" \
      $DB_ARGS \
      --datahub-gms-url "$DATAHUB_GMS_URL"
    ;;
  
  "monitor")
    PIPELINE_ARG=""
    if [ ! -z "$2" ]; then
      PIPELINE_ARG="--pipeline-name $2"
    fi
    
    SLACK_ARG=""
    if [ ! -z "$SLACK_WEBHOOK" ]; then
      SLACK_ARG="--slack-webhook $SLACK_WEBHOOK"
    fi
    
    echo "Running ingestion monitor"
    python /app/monitor_ingestion.py \
      --datahub-gms-url "$DATAHUB_GMS_URL" \
      $PIPELINE_ARG \
      $SLACK_ARG
    ;;
  
  "cron")
    if [ -z "$SCHEDULE" ]; then
      echo "Error: SCHEDULE environment variable is required for cron mode"
      exit 1
    fi
    
    if [ -z "$CONFIG_FILE" ]; then
      echo "Error: CONFIG_FILE environment variable is required for cron mode"
      exit 1
    fi
    
    echo "Starting scheduled ingestion with schedule: $SCHEDULE"
    
    # Install and run the cron job using Python schedule
    cat > /app/cron.py << EOF
import schedule
import time
import os
import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def run_ingestion():
    logger.info("Running scheduled ingestion")
    try:
        result = subprocess.run(
            ["datahub", "ingest", "-c", os.environ.get("CONFIG_FILE")],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Ingestion completed: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ingestion failed: {e.stderr}")

# Set up the schedule
schedule.every().${SCHEDULE}.do(run_ingestion)

# Run the scheduler
logger.info("Starting scheduler")
while True:
    schedule.run_pending()
    time.sleep(60)
EOF
    
    python /app/cron.py
    ;;
  
  *)
    echo "Unknown command: $1"
    echo "Run 'help' for available commands"
    exit 1
    ;;
esac