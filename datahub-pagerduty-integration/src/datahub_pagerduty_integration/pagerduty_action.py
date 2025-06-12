# pagerduty_action.py
import requests
import json
import logging
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
    incidents based on DataHub metadata events like schema changes, data quality failures,
    ownership changes, and asset deprecations.
    """
    
    @classmethod
    def create(cls, config_dict: dict, ctx: PipelineContext) -> "Action":
        """
        Factory method to create a PagerDutyAction instance.
        
        Expected config:
        - routing_key: PagerDuty Integration Key (Events API v2)
        - base_url: DataHub UI base URL for generating links
        - severity_mapping: Optional mapping of event types to PagerDuty severities
        - custom_fields: Additional custom fields to include in incidents
        - enable_auto_resolve: Whether to auto-resolve incidents for certain events
        """
        return cls(config_dict, ctx)
    
    def __init__(self, config: Dict[str, Any], ctx: PipelineContext):
        super().__init__()
        self.ctx = ctx
        self.routing_key = config.get("routing_key")
        self.base_url = config.get("base_url", "https://fieldeng.acryl.io")
        self.datahub_server = config.get("datahub_server", "https://fieldeng.acryl.io/gms")
        self.datahub_token = config.get("datahub_token")
        self.pagerduty_api_url = "https://events.pagerduty.com/v2/enqueue"
        
        # Severity mapping for different event types
        self.severity_mapping = config.get("severity_mapping", {
            "schema_change": "warning",
            "ownership_change": "info", 
            "deprecation": "warning",
            "data_quality_failure": "error",
            "ingestion_failure": "critical",
            "tag_change": "info"
        })
        
        # Auto-resolve configuration
        self.enable_auto_resolve = config.get("enable_auto_resolve", True)
        self.auto_resolve_events = config.get("auto_resolve_events", [
            "ownership_restored",
            "data_quality_restored",
            "ingestion_restored"
        ])
        
        # Custom fields to include in PagerDuty incidents
        self.custom_fields = config.get("custom_fields", {})
        
        # Validate required configuration
        if not self.routing_key:
            raise ValueError("routing_key is required for PagerDuty integration")
        
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
            
            # Determine if this is a trigger or resolve event
            action_type = self._determine_action_type(event_type, event_data)
            
            if action_type == "trigger":
                self._send_trigger_event(event_type, event_data)
            elif action_type == "resolve":
                self._send_resolve_event(event_type, event_data)
            else:
                logger.debug(f"Ignoring event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Failed to process event {event.event_type}: {str(e)}")
            raise
    
    def _determine_action_type(self, event_type: str, event_data: Dict) -> Optional[str]:
        """
        Determine whether this event should trigger or resolve a PagerDuty incident.
        """
        # Map DataHub event types to PagerDuty actions
        trigger_events = [
            "EntityChangeEvent_v1",  # Schema changes
            "MetadataChangeLog_v1",  # Ownership, tags, deprecation changes
        ]
        
        # Check if this event type should trigger an incident
        if event_type in trigger_events:
            # Further filter based on event content
            if self._should_trigger_incident(event_data):
                return "trigger"
            elif self._should_resolve_incident(event_data):
                return "resolve"
        
        return None
    
    def _should_trigger_incident(self, event_data: Dict) -> bool:
        """
        Determine if the event data indicates a critical issue that should trigger an incident.
        """
        # Example logic - customize based on your needs
        change_type = event_data.get("changeType", "")
        aspect_name = event_data.get("aspectName", "")
        
        # Trigger on critical changes
        critical_changes = [
            "schemaMetadata",  # Schema changes
            "deprecation",     # Asset deprecations
            "datasetProperties", # Dataset property changes
            "ownership"        # Ownership changes
        ]
        
        # Check for data quality failures or ingestion issues
        if "assertion" in aspect_name.lower() and change_type == "UPSERT":
            assertion_result = event_data.get("aspect", {}).get("result", {})
            if assertion_result.get("type") == "FAILURE":
                return True
        
        # Check for deprecation events
        if aspect_name == "deprecation" and change_type == "UPSERT":
            deprecation = event_data.get("aspect", {})
            if deprecation.get("deprecated", False):
                return True
        
        # Check for schema changes
        if aspect_name == "schemaMetadata" and change_type == "UPSERT":
            return True
        
        return False
    
    def _should_resolve_incident(self, event_data: Dict) -> bool:
        """
        Determine if the event data indicates a resolution.
        """
        if not self.enable_auto_resolve:
            return False
            
        change_type = event_data.get("changeType", "")
        aspect_name = event_data.get("aspectName", "")
        
        # Auto-resolve on successful assertions
        if "assertion" in aspect_name.lower() and change_type == "UPSERT":
            assertion_result = event_data.get("aspect", {}).get("result", {})
            if assertion_result.get("type") == "SUCCESS":
                return True
        
        # Auto-resolve when deprecation is removed
        if aspect_name == "deprecation" and change_type == "DELETE":
            return True
        
        return False
    
    def _send_trigger_event(self, event_type: str, event_data: Dict) -> None:
        """
        Send a trigger event to PagerDuty to create an incident.
        """
        # Generate deduplication key
        entity_urn = event_data.get("entityUrn", "unknown")
        aspect_name = event_data.get("aspectName", "unknown")
        dedup_key = f"datahub-{entity_urn}-{aspect_name}"
        
        # Determine severity
        severity = self._get_severity(event_type, event_data)
        
        # Generate summary and description
        summary = self._generate_summary(event_type, event_data)
        description = self._generate_description(event_type, event_data)
        
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
                "class": event_type,
                "custom_details": {
                    "entity_urn": entity_urn,
                    "aspect_name": aspect_name,
                    "change_type": event_data.get("changeType", ""),
                    "timestamp": event_data.get("systemMetadata", {}).get("lastObserved", ""),
                    "entity_url": entity_url,
                    "description": description,
                    **self.custom_fields
                }
            }
        }
        
        self._send_to_pagerduty(payload)
    
    def _send_resolve_event(self, event_type: str, event_data: Dict) -> None:
        """
        Send a resolve event to PagerDuty to resolve an incident.
        """
        # Generate same deduplication key as trigger event
        entity_urn = event_data.get("entityUrn", "unknown")
        aspect_name = event_data.get("aspectName", "unknown")
        dedup_key = f"datahub-{entity_urn}-{aspect_name}"
        
        payload = {
            "routing_key": self.routing_key,
            "event_action": "resolve",
            "dedup_key": dedup_key,
            "payload": {
                "summary": f"DataHub issue resolved for {self._extract_component(entity_urn)}",
                "source": "DataHub Metadata Platform",
                "custom_details": {
                    "entity_urn": entity_urn,
                    "resolution_time": datetime.utcnow().isoformat(),
                    "resolved_by": "DataHub Automated Resolution"
                }
            }
        }
        
        self._send_to_pagerduty(payload)
    
    def _send_to_pagerduty(self, payload: Dict) -> None:
        """
        Send the payload to PagerDuty Events API.
        """
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
            
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully sent event to PagerDuty: {result.get('message', 'Success')}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send event to PagerDuty: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PagerDuty response: {str(e)}")
            raise
    
    def _get_severity(self, event_type: str, event_data: Dict) -> str:
        """
        Determine the severity level for the incident.
        """
        aspect_name = event_data.get("aspectName", "")
        
        # Map aspect names to severities
        if "assertion" in aspect_name.lower():
            return "error"
        elif aspect_name == "deprecation":
            return "warning"
        elif aspect_name == "schemaMetadata":
            return "warning"
        elif aspect_name == "ownership":
            return "info"
        
        return "warning"  # Default severity
    
    def _generate_summary(self, event_type: str, event_data: Dict) -> str:
        """
        Generate a human-readable summary for the incident.
        """
        entity_urn = event_data.get("entityUrn", "Unknown Entity")
        aspect_name = event_data.get("aspectName", "")
        change_type = event_data.get("changeType", "")
        
        component = self._extract_component(entity_urn)
        
        if aspect_name == "schemaMetadata":
            return f"Schema change detected in {component}"
        elif aspect_name == "deprecation":
            return f"Asset deprecated: {component}"
        elif aspect_name == "ownership":
            return f"Ownership change in {component}"
        elif "assertion" in aspect_name.lower():
            return f"Data quality assertion failed for {component}"
        else:
            return f"DataHub metadata change in {component}: {aspect_name}"
    
    def _generate_description(self, event_type: str, event_data: Dict) -> str:
        """
        Generate a detailed description for the incident.
        """
        entity_urn = event_data.get("entityUrn", "")
        aspect_name = event_data.get("aspectName", "")
        change_type = event_data.get("changeType", "")
        timestamp = event_data.get("systemMetadata", {}).get("lastObserved", "")
        
        description = f"DataHub detected a {change_type.lower()} event for {aspect_name} "
        description += f"on entity: {entity_urn}\n\n"
        description += f"Event Type: {event_type}\n"
        description += f"Timestamp: {timestamp}\n"
        description += f"Change Type: {change_type}\n"
        description += f"Aspect: {aspect_name}\n\n"
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
        logger.info("PagerDuty Action shutting down")# PASTE THE PAGERDUTY ACTION PYTHON CODE HERE
# This is where you will paste the PagerDuty Action implementation
