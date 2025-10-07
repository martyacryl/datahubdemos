#!/bin/bash
# Schedule DMF Monitor - Automated Snowflake to DataHub Integration
# This script provides different scheduling options for the DMF monitor

echo "🤖 DMF Monitor Scheduling Options"
echo "=================================="
echo ""

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/simple_automated_monitor.py"

echo "📁 Monitor script location: $MONITOR_SCRIPT"
echo ""

# Check if the monitor script exists
if [ ! -f "$MONITOR_SCRIPT" ]; then
    echo "❌ Monitor script not found: $MONITOR_SCRIPT"
    exit 1
fi

# Make the script executable
chmod +x "$MONITOR_SCRIPT"

echo "🔧 Scheduling Options:"
echo ""

echo "1. 🕐 CRON JOB (Recommended for production)"
echo "   Add this line to your crontab (crontab -e):"
echo "   # Run DMF monitor every 15 minutes"
echo "   */15 * * * * cd $SCRIPT_DIR && python $MONITOR_SCRIPT >> dmf_monitor_cron.log 2>&1"
echo ""

echo "2. 🕐 CRON JOB - Every hour"
echo "   # Run DMF monitor every hour"
echo "   0 * * * * cd $SCRIPT_DIR && python $MONITOR_SCRIPT >> dmf_monitor_cron.log 2>&1"
echo ""

echo "3. 🕐 CRON JOB - Every 6 hours"
echo "   # Run DMF monitor every 6 hours"
echo "   0 */6 * * * cd $SCRIPT_DIR && python $MONITOR_SCRIPT >> dmf_monitor_cron.log 2>&1"
echo ""

echo "4. 🕐 CRON JOB - Daily at 9 AM"
echo "   # Run DMF monitor daily at 9 AM"
echo "   0 9 * * * cd $SCRIPT_DIR && python $MONITOR_SCRIPT >> dmf_monitor_cron.log 2>&1"
echo ""

echo "5. 🚀 SYSTEMD TIMER (Linux systems)"
echo "   Create /etc/systemd/system/dmf-monitor.service:"
echo "   [Unit]"
echo "   Description=DMF Monitor"
echo "   After=network.target"
echo ""
echo "   [Service]"
echo "   Type=oneshot"
echo "   User=your-username"
echo "   WorkingDirectory=$SCRIPT_DIR"
echo "   ExecStart=/usr/bin/python3 $MONITOR_SCRIPT"
echo "   StandardOutput=append:$SCRIPT_DIR/dmf_monitor_systemd.log"
echo "   StandardError=append:$SCRIPT_DIR/dmf_monitor_systemd.log"
echo ""
echo "   Create /etc/systemd/system/dmf-monitor.timer:"
echo "   [Unit]"
echo "   Description=Run DMF Monitor every 15 minutes"
echo "   Requires=dmf-monitor.service"
echo ""
echo "   [Timer]"
echo "   OnCalendar=*:0/15"
echo "   Persistent=true"
echo ""
echo "   [Install]"
echo "   WantedBy=timers.target"
echo ""
echo "   Then run:"
echo "   sudo systemctl enable dmf-monitor.timer"
echo "   sudo systemctl start dmf-monitor.timer"
echo ""

echo "6. 🐳 DOCKER CONTAINER (with cron)"
echo "   Create Dockerfile:"
echo "   FROM python:3.9-slim"
echo "   WORKDIR /app"
echo "   COPY requirements.txt ."
echo "   RUN pip install -r requirements.txt"
echo "   COPY . ."
echo "   RUN echo '*/15 * * * * cd /app && python simple_automated_monitor.py' | crontab -"
echo "   CMD [\"cron\", \"-f\"]"
echo ""

echo "7. ☁️  CLOUD SCHEDULERS"
echo "   - AWS EventBridge: Create rule to trigger Lambda function"
echo "   - Google Cloud Scheduler: Schedule Cloud Function"
echo "   - Azure Logic Apps: Create recurring workflow"
echo "   - Apache Airflow: Create DAG with PythonOperator"
echo ""

echo "8. 🧪 TEST RUN (Manual execution)"
echo "   Run this command to test the monitor:"
echo "   cd $SCRIPT_DIR && python $MONITOR_SCRIPT"
echo ""

echo "📋 Setup Instructions:"
echo "1. Ensure your .env file is properly configured"
echo "2. Test the monitor manually first: python $MONITOR_SCRIPT"
echo "3. Choose a scheduling method above"
echo "4. Monitor the logs for any issues"
echo "5. Check DataHub UI for assertion updates"
echo ""

echo "📊 Monitoring & Logs:"
echo "- Log file: $SCRIPT_DIR/dmf_monitor.log"
echo "- Cron log: $SCRIPT_DIR/dmf_monitor_cron.log (if using cron)"
echo "- Systemd log: $SCRIPT_DIR/dmf_monitor_systemd.log (if using systemd)"
echo ""

echo "🔍 Troubleshooting:"
echo "- Check .env file has correct credentials"
echo "- Verify Snowflake connection"
echo "- Verify DataHub connection"
echo "- Check log files for errors"
echo "- Test manual execution first"
echo ""

echo "✅ Ready to schedule your DMF monitor!"
echo "Choose a method above and follow the instructions."
