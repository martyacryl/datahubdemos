# pagerduty_action.py
import requests
import json
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

from datahub_actions.action.action import Action
from datahub_actions.event.event_envelope import EventEnvelope
from datahub_actions.pipeline.pipeline_context import PipelineContext

logger = logging.getLogger(__name__)

class PagerDutyAction(Action):
    """
    DataHub Action that sends incidents to PagerDuty when critical data events occur.
    
    This action integrates with PagerDuty Events API v2 to create, update, and resolve
    incidents based on DataHub Cloud EntityChangeEvent_v1 events like schema changes, 
    ownership changes, and asset deprecations.
    
    Note: This integration only supports EntityChangeEvent_v1 events from DataHub Cloud.
    Data quality assertions and other Observe features are not accessible via REST API.
    """
    
    @classmethod
    def create(cls, config_dict: dict, ctx: PipelineContext) -> "Action":
        """
        Factory method to create a PagerDutyAction instance.
        
        Expected config:
        - routing_key: PagerDuty Integration Key (Events API v2)
        - base_url: DataHub UI base URL for generating links
        - severity_mapping: Optional mapping of event categories to PagerDuty severities
        - custom_fields: Additional custom fields to include in incidents
        - enable_auto_resolve: Whether to auto-resolve incidents for certain events
        """
        return cls(config_dict, ctx)
    
    def __init__(self, config: Dict[str, Any], ctx: PipelineContext):
        super().__init__()
        self.ctx = ctx
        # Initialize PagerDuty configuration
        self.routing_key = config.get("routing_key")
        if not self.routing_key:
            raise ValueError("PagerDuty routing_key is required")
        
        self.base_url = config.get("base_url", "https://<namespace>.acryl.io")
        self.datahub_server = config.get("datahub_server", "https://<namespace>.acryl.io/gms")
        self.datahub_token = config.get("datahub_token")
        self.pagerduty_api_url = "https://events.pagerduty.com/v2/enqueue"
        
        # Severity mapping for different event categories
        self.severity_mapping = config.get("severity_mapping", {
            "TECHNICAL_SCHEMA": "warning",    # Schema changes
            "OWNER": "info",                  # Ownership changes
            "DEPRECATION": "warning",         # Asset deprecations
            "TAG": "info",                    # Tag changes
            "DOMAIN": "info",                 # Domain changes
            "GLOSSARY_TERM": "info",          # Glossary term changes
            "LIFECYCLE": "warning",           # Lifecycle changes
            "RUN": "critical"                 # Assertion failures are critical
        })
        
        # Auto-resolve configuration
        self.enable_auto_resolve = config.get("enable_auto_resolve", True)
        self.auto_resolve_operations = config.get("auto_resolve_operations", [
            "REMOVE"  # Auto-resolve when tags/terms are removed
        ])
        
        # Custom fields to include in PagerDuty incidents
        self.custom_fields = config.get("custom_fields", {})
        
        # Rate limiting and retry configuration
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1)
        
        # Validate required configuration
        if not self.datahub_token:
            raise ValueError("datahub_token is required for DataHub Cloud integration")
        
        logger.info(f"PagerDuty Action initialized for DataHub Cloud at {self.datahub_server}")
    
    def act(self, event: EventEnvelope) -> None:
        """
        Process a DataHub event and send appropriate notification to PagerDuty.
        """
        try:
            # Extract event information
            event_type = event.event_type
            event_data = event.event
            
            logger.info(f"Processing event: {event_type}")
            
            # Only process EntityChangeEvent_v1 events (DataHub Cloud supported)
            if event_type != "EntityChangeEvent_v1":
                logger.debug(f"Skipping unsupported event type: {event_type}")
                return
            
            # Determine if this is a trigger or resolve event
            action_type = self._determine_action_type(event_data)
            
            if action_type == "trigger":
                self._send_trigger_event(event_data)
            elif action_type == "resolve":
                self._send_resolve_event(event_data)
            else:
                logger.debug(f"Ignoring event category: {event_data.get('category', 'unknown')}")
                
        except Exception as e:
            logger.error(f"Failed to process event {event.event_type}: {str(e)}")
            raise
    
    def _determine_action_type(self, event_data: Dict) -> Optional[str]:
        """
        Determine whether this event should trigger or resolve a PagerDuty incident.
        """
        category = event_data.get("category", "")
        operation = event_data.get("operation", "")
        
        # Trigger on critical changes
        trigger_categories = [
            "TECHNICAL_SCHEMA",  # Schema changes
            "DEPRECATION",       # Asset deprecations
            "OWNER",             # Ownership changes
            "TAG",               # Tag changes (especially PII)
            "DOMAIN",            # Domain changes
            "LIFECYCLE",         # Lifecycle changes
            "RUN"                # Assertion failures
        ]
        
        if category in trigger_categories:
            if self._should_trigger_incident(event_data):
                return "trigger"
            elif self._should_resolve_incident(event_data):
                return "resolve"
        
        return None
    
    def _should_trigger_incident(self, event_data: Dict) -> bool:
        """
        Determine if the event data indicates a critical issue that should trigger an incident.
        """
        category = event_data.get("category", "")
        operation = event_data.get("operation", "")
        
        # Always trigger on schema changes
        if category == "TECHNICAL_SCHEMA" and operation == "MODIFY":
            return True
        
        # Trigger on deprecation
        if category == "DEPRECATION" and operation == "ADD":
            return True
        
        # Trigger on ownership changes
        if category == "OWNER" and operation in ["ADD", "MODIFY"]:
            return True
        
        # Trigger on critical tag changes (like PII)
        if category == "TAG" and operation == "ADD":
            modifier = event_data.get("modifier", "")
            if "pii" in modifier.lower() or "sensitive" in modifier.lower():
                return True
        
        # Trigger on domain changes
        if category == "DOMAIN" and operation in ["ADD", "MODIFY"]:
            return True
        
        # Trigger on assertion failures
        if category == "RUN" and operation == "COMPLETED":
            # Check if this is an assertion run event with FAILURE result
            parameters = event_data.get("parameters", {})
            run_result = parameters.get("runResult")
            if run_result == "FAILURE":
                return True
        
        return False
    
    def _should_resolve_incident(self, event_data: Dict) -> bool:
        """
        Determine if the event data indicates a resolution.
        """
        if not self.enable_auto_resolve:
            return False
            
        category = event_data.get("category", "")
        operation = event_data.get("operation", "")
        
        # Auto-resolve when deprecation is removed
        if category == "DEPRECATION" and operation == "REMOVE":
            return True
        
        # Auto-resolve when critical tags are removed
        if category == "TAG" and operation == "REMOVE":
            modifier = event_data.get("modifier", "")
            if "pii" in modifier.lower() or "sensitive" in modifier.lower():
                return True
        
        return False
    
    def _send_trigger_event(self, event_data: Dict) -> None:
        """
        Send a trigger event to PagerDuty to create an incident.
        """
        # Generate deduplication key
        entity_urn = event_data.get("entityUrn", "unknown")
        category = event_data.get("category", "unknown")
        dedup_key = f"datahub-{entity_urn}-{category}"
        
        # Determine severity
        severity = self._get_severity(event_data)
        
        # Generate summary and description
        summary = self._generate_summary(event_data)
        description = self._generate_description(event_data)
        
        # Create entity URL for DataHub Cloud
        if entity_urn != "unknown":
            # DataHub Cloud URL format
            entity_url = f"{self.base_url}/dataset/{entity_urn.replace(':', '%3A')}"
        else:
            entity_url = None
        
        # Build payload
        payload = {
            "routing_key": self.routing_key,
            "event_action": "trigger",
            "client": "DataHub",
            "client_url": entity_url,
            "dedup_key": dedup_key,
            "payload": {
                "summary": summary,
                "source": "DataHub Metadata Platform",
                "severity": severity,
                "component": self._extract_component(entity_urn),
                "class": category,
                "custom_details": {
                    "entity_urn": entity_urn,
                    "category": category,
                    "operation": event_data.get("operation", ""),
                    "modifier": event_data.get("modifier", ""),
                    "timestamp": event_data.get("auditStamp", {}).get("time", ""),
                    "actor": event_data.get("auditStamp", {}).get("actor", ""),
                    "entity_url": entity_url,
                    "description": description,
                    **self.custom_fields
                }
            }
        }
        
        self._send_to_pagerduty(payload)
    
    def _send_resolve_event(self, event_data: Dict) -> None:
        """
        Send a resolve event to PagerDuty to resolve an incident.
        """
        # Generate same deduplication key as trigger event
        entity_urn = event_data.get("entityUrn", "unknown")
        category = event_data.get("category", "unknown")
        dedup_key = f"datahub-{entity_urn}-{category}"
        
        payload = {
            "routing_key": self.routing_key,
            "event_action": "resolve",
            "dedup_key": dedup_key,
            "payload": {
                "summary": f"DataHub issue resolved for {self._extract_component(entity_urn)}",
                "source": "DataHub Metadata Platform",
                "custom_details": {
                    "entity_urn": entity_urn,
                    "category": category,
                    "resolution_time": datetime.utcnow().isoformat(),
                    "resolved_by": "DataHub Automated Resolution"
                }
            }
        }
        
        self._send_to_pagerduty(payload)
    
    def _send_to_pagerduty(self, payload: Dict) -> None:
        """
        Send the payload to PagerDuty Events API with retry logic.
        """
        for attempt in range(self.max_retries):
            try:
                headers = {
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    self.pagerduty_api_url,
                    data=json.dumps(payload),
                    headers=headers,
                    timeout=30
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', self.retry_delay))
                    logger.warning(f"Rate limited by PagerDuty API. Retrying in {retry_after} seconds.")
                    time.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Successfully sent event to PagerDuty: {result.get('message', 'Success')}")
                return
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to send event to PagerDuty (attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse PagerDuty response: {str(e)}")
                raise
    
    def _get_severity(self, event_data: Dict) -> str:
        """
        Determine the severity level for the incident.
        """
        category = event_data.get("category", "")
        
        # Use configured severity mapping
        return self.severity_mapping.get(category, "warning")
    
    def _generate_summary(self, event_data: Dict) -> str:
        """
        Generate a human-readable summary for the incident.
        """
        entity_urn = event_data.get("entityUrn", "Unknown Entity")
        category = event_data.get("category", "")
        operation = event_data.get("operation", "")
        
        component = self._extract_component(entity_urn)
        
        if category == "TECHNICAL_SCHEMA":
            return f"Schema change detected in {component}"
        elif category == "DEPRECATION":
            return f"Asset deprecated: {component}"
        elif category == "OWNER":
            return f"Ownership change in {component}"
        elif category == "TAG":
            modifier = event_data.get("modifier", "")
            tag_name = modifier.split(":")[-1] if ":" in modifier else modifier
            return f"Tag '{tag_name}' {operation.lower()}ed on {component}"
        elif category == "DOMAIN":
            return f"Domain change in {component}"
        elif category == "RUN":
            # Handle assertion run events
            parameters = event_data.get("parameters", {})
            run_result = parameters.get("runResult", "UNKNOWN")
            assertee_urn = parameters.get("asserteeUrn", "")
            run_id = parameters.get("runId", "")
            
            if run_result == "FAILURE":
                assertee_component = self._extract_component(assertee_urn) if assertee_urn else "unknown dataset"
                return f"Data Quality Assertion FAILED: {assertee_component} (Run ID: {run_id})"
            else:
                return f"Assertion run completed: {run_result}"
        else:
            return f"DataHub metadata change in {component}: {category}"
    
    def _generate_description(self, event_data: Dict) -> str:
        """
        Generate a detailed description for the incident.
        """
        entity_urn = event_data.get("entityUrn", "")
        category = event_data.get("category", "")
        operation = event_data.get("operation", "")
        modifier = event_data.get("modifier", "")
        timestamp = event_data.get("auditStamp", {}).get("time", "")
        actor = event_data.get("auditStamp", {}).get("actor", "")
        
        description = f"DataHub detected a {operation.lower()} event for {category} "
        description += f"on entity: {entity_urn}\n\n"
        description += f"Category: {category}\n"
        description += f"Operation: {operation}\n"
        
        # Add specific details for assertion events
        if category == "RUN":
            parameters = event_data.get("parameters", {})
            run_result = parameters.get("runResult", "UNKNOWN")
            assertee_urn = parameters.get("asserteeUrn", "")
            run_id = parameters.get("runId", "")
            
            description += f"Assertion Result: {run_result}\n"
            description += f"Run ID: {run_id}\n"
            description += f"Assertion URN: {entity_urn}\n"
            description += f"Dataset URN: {assertee_urn}\n"
            
            if run_result == "FAILURE":
                description += "\n🚨 **DATA QUALITY ASSERTION FAILED** 🚨\n"
                description += "This indicates a data quality issue that requires immediate attention.\n"
        else:
            if modifier:
                description += f"Modifier: {modifier}\n"
        
        description += f"Timestamp: {timestamp}\n"
        description += f"Actor: {actor}\n\n"
        description += "Please review the entity in DataHub to understand the impact."
        
        return description
    
    def _extract_component(self, entity_urn: str) -> str:
        """
        Extract a human-readable component name from the entity URN.
        """
        if not entity_urn or entity_urn == "unknown":
            return "Unknown Component"
        
        # Parse URN format: urn:li:dataset:(platform,name,env)
        try:
            parts = entity_urn.split(",")
            if len(parts) >= 2:
                # Extract dataset name or table name
                name_part = parts[1]
                return name_part.split(".")[-1] if "." in name_part else name_part
        except:
            pass
        
        return entity_urn.split(":")[-1] if ":" in entity_urn else entity_urn
    
    def close(self) -> None:
        """
        Cleanup when the action is being shut down.
        """
        logger.info("PagerDuty Action shutting down")
