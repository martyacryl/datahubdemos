"""
DataHub Action that monitors data quality assertion events.
"""
from datahub_actions.action.action import Action
from datahub_actions.event.event_envelope import EventEnvelope
from datahub_actions.pipeline.pipeline_context import PipelineContext
import logging
import json

logger = logging.getLogger(__name__)

class QualityMonitorAction(Action):
    """
    Action that monitors data quality assertion events and logs warnings for failures.
    """
    @classmethod
    def create(cls, config_dict, ctx: PipelineContext) -> "Action":
        """Factory method to create the action"""
        # Get configuration with defaults
        severity_threshold = config_dict.get("severity_threshold", "ERROR")
        send_alerts = config_dict.get("send_alerts", False)
        
        return cls(ctx, severity_threshold, send_alerts)

    def __init__(self, ctx: PipelineContext, severity_threshold: str, send_alerts: bool):
        self.ctx = ctx
        self.severity_threshold = severity_threshold
        self.send_alerts = send_alerts
        logger.info(f"QualityMonitorAction initialized with severity threshold: {severity_threshold}")
        logger.info(f"Alert sending is {'enabled' if send_alerts else 'disabled'}")

    def act(self, event: EventEnvelope) -> None:
        """Process the event and monitor quality assertions"""
        event_data = event.event
        
        # Skip non-assertion events
        if event.event_type != "AssertionRunEvent_v1":
            return
            
        # Extract assertion information
        try:
            dataset_urn = event_data.get("datasetUrn", "")
            assertion_urn = event_data.get("assertionUrn", "")
            assertion_status = event_data.get("runStatus", "UNKNOWN")
            result = event_data.get("result", {})
            
            # Process based on assertion status
            if assertion_status == "COMPLETE":
                self._process_assertion_result(dataset_urn, assertion_urn, result)
            elif assertion_status == "FAILURE":
                logger.error(f"Assertion run failed for {assertion_urn} on {dataset_urn}: {result.get('message', 'No details')}")
                if self.send_alerts:
                    self._send_alert(dataset_urn, assertion_urn, "Assertion run failed", result)
                    
        except Exception as e:
            logger.error(f"Error processing assertion event: {e}")
    
    def _process_assertion_result(self, dataset_urn, assertion_urn, result):
        """Process the assertion result and take appropriate action"""
        success = result.get("success", False)
        
        if not success:
            severity = result.get("severity", "UNKNOWN")
            message = result.get("message", "Assertion failed without details")
            
            # Log with appropriate level based on severity
            if severity == "ERROR" or severity == "CRITICAL":
                logger.error(f"Quality check failed for {dataset_urn}: {message}")
                if self.send_alerts and self._is_above_threshold(severity):
                    self._send_alert(dataset_urn, assertion_urn, message, result)
            elif severity == "WARNING":
                logger.warning(f"Quality check warning for {dataset_urn}: {message}")
                if self.send_alerts and self._is_above_threshold(severity):
                    self._send_alert(dataset_urn, assertion_urn, message, result)
            else:
                logger.info(f"Quality check info for {dataset_urn}: {message}")
    
    def _is_above_threshold(self, severity):
        """Check if the severity is at or above the configured threshold"""
        severity_levels = {"INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
        return severity_levels.get(severity, 0) >= severity_levels.get(self.severity_threshold, 0)
    
    def _send_alert(self, dataset_urn, assertion_urn, message, details):
        """Send alert about failed assertion"""
        alert_message = f"Data Quality Alert: {message}\nDataset: {dataset_urn}\nAssertion: {assertion_urn}"
        
        # This is a mock implementation - in reality, you'd integrate with your alerting system
        logger.info(f"Would send alert: {alert_message}")
        logger.debug(f"Alert details: {json.dumps(details)}")
    
    def close(self) -> None:
        """Clean up resources"""
        logger.info("QualityMonitorAction shutting down")