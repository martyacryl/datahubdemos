#!/usr/bin/env python
"""
This script monitors DataHub ingestion jobs and sends alerts when issues are detected.
It can be used to set up a monitoring system for your DataHub-Snowflake ingestion pipelines.
"""

import os
import sys
import json
import logging
import argparse
import datetime
import requests
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

class IngestionMonitor:
    """Monitor DataHub ingestion jobs and alert on issues."""
    
    def __init__(
        self,
        datahub_gms_url: str,
        slack_webhook_url: Optional[str] = None,
        email_recipients: Optional[List[str]] = None,
        source_type: str = "snowflake"
    ):
        self.datahub_gms_url = datahub_gms_url
        self.slack_webhook_url = slack_webhook_url
        self.email_recipients = email_recipients
        self.source_type = source_type
    
    def get_latest_runs(self, pipeline_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get the latest ingestion runs from DataHub."""
        try:
            url = f"{self.datahub_gms_url}/runs"
            if pipeline_name:
                url += f"?pipeline={pipeline_name}"
            
            response = requests.get(url)
            response.raise_for_status()
            
            runs = response.json().get("runs", [])
            return [run for run in runs if run.get("source", {}).get("type") == self.source_type]
        except Exception as e:
            logger.error(f"Failed to get ingestion runs: {e}")
            return []
    
    def analyze_run(self, run: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an ingestion run for issues."""
        analysis = {
            "pipeline_name": run.get("pipelineName", "unknown"),
            "start_time": run.get("startTimeMs", 0),
            "end_time": run.get("endTimeMs", 0),
            "status": "success",
            "issues": [],
            "stats": {},
        }
        
        # Check overall success
        if not run.get("success", False):
            analysis["status"] = "failure"
            analysis["issues"].append("Pipeline run failed")
        
        # Analyze report
        report = run.get("report", {})
        
        # Check for failed entities
        for entity_type, counts in report.get("counts", {}).items():
            failed = counts.get("failures", 0)
            if failed > 0:
                analysis["status"] = "warning"
                analysis["issues"].append(f"Failed to ingest {failed} {entity_type} entities")
            
            # Collect stats
            analysis["stats"][entity_type] = {
                "success": counts.get("success", 0),
                "failure": failed
            }
        
        # Check for specific errors
        if "errors" in report and report["errors"]:
            analysis["status"] = "failure"
            for error in report["errors"][:5]:  # Limit to first 5 errors
                analysis["issues"].append(error)
        
        return analysis
    
    def send_alert(self, analysis: Dict[str, Any]):
        """Send an alert about ingestion issues."""
        if analysis["status"] == "success":
            return
        
        # Format the message
        message = f"DataHub Ingestion Alert: {analysis['status'].upper()} for {analysis['pipeline_name']}\n"
        message += f"Start time: {datetime.datetime.fromtimestamp(analysis['start_time']/1000)}\n"
        
        if analysis["issues"]:
            message += "\nIssues:\n"
            for issue in analysis["issues"]:
                message += f"- {issue}\n"
        
        if analysis["stats"]:
            message += "\nStats:\n"
            for entity_type, counts in analysis["stats"].items():
                message += f"- {entity_type}: {counts['success']} succeeded, {counts['failure']} failed\n"
        
        # Send to Slack if configured
        if self.slack_webhook_url:
            self._send_slack_alert(message, analysis)
        
        # Send email if configured
        if self.email_recipients:
            self._send_email_alert(message, analysis)
    
    def _send_slack_alert(self, message: str, analysis: Dict[str, Any]):
        """Send an alert to Slack."""
        try:
            color = "#ff0000" if analysis["status"] == "failure" else "#ffcc00"
            
            payload = {
                "attachments": [
                    {
                        "fallback": message,
                        "color": color,
                        "title": f"DataHub Ingestion Alert: {analysis['pipeline_name']}",
                        "text": message,
                        "ts": int(datetime.datetime.now().timestamp())
                    }
                ]
            }
            
            response = requests.post(
                self.slack_webhook_url,
                json=payload
            )
            response.raise_for_status()
            logger.info("Slack alert sent successfully")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def _send_email_alert(self, message: str, analysis: Dict[str, Any]):
        """Send an email alert (implementation depends on your email service)."""
        # This is a placeholder - implement using your preferred email service
        # Examples: SMTP, Amazon SES, SendGrid, etc.
        logger.info(f"Would send email to {self.email_recipients} with message: {message}")

def main():
    parser = argparse.ArgumentParser(description="DataHub Ingestion Monitor")
    parser.add_argument("--datahub-gms-url", required=True, help="DataHub GMS URL")
    parser.add_argument("--pipeline-name", help="Specific pipeline to monitor")
    parser.add_argument("--slack-webhook", help="Slack webhook URL for alerts")
    parser.add_argument("--email", action="append", help="Email recipients for alerts")
    
    args = parser.parse_args()
    
    monitor = IngestionMonitor(
        datahub_gms_url=args.datahub_gms_url,
        slack_webhook_url=args.slack_webhook,
        email_recipients=args.email,
    )
    
    runs = monitor.get_latest_runs(args.pipeline_name)
    
    if not runs:
        logger.warning("No ingestion runs found")
        return
    
    for run in runs:
        analysis = monitor.analyze_run(run)
        
        if analysis["status"] != "success":
            monitor.send_alert(analysis)
        else:
            logger.info(f"Ingestion successful for {analysis['pipeline_name']}")

if __name__ == "__main__":
    main()