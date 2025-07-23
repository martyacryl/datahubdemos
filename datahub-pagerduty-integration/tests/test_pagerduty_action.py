import pytest
from unittest.mock import Mock, patch
from src.datahub_pagerduty_integration.pagerduty_action import PagerDutyAction

class TestPagerDutyAction:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.config = {
            "routing_key": "test_routing_key",
            "datahub_token": "test-token",
            "base_url": "https://<namespace>.acryl.io"
        }
        self.ctx = Mock()
        self.action = PagerDutyAction(self.config, self.ctx)
    
    def test_init(self):
        """Test PagerDutyAction initialization"""
        assert self.action.routing_key == "test_routing_key"
        assert self.action.base_url == "https://<namespace>.acryl.io"
    
    def test_init_missing_routing_key(self):
        """Test that PagerDutyAction raises error when routing_key is missing."""
        config = {"datahub_token": "test-token"}
        with pytest.raises(ValueError, match="routing_key is required"):
            PagerDutyAction(config, self.ctx)
    
    def test_init_missing_datahub_token(self):
        """Test that PagerDutyAction raises error when datahub_token is missing."""
        config = {"routing_key": "test-key"}
        with pytest.raises(ValueError, match="datahub_token is required"):
            PagerDutyAction(config, self.ctx)
    
    def test_should_trigger_incident_schema_change(self):
        """Test that schema changes trigger incidents."""
        event_data = {
            "category": "TECHNICAL_SCHEMA",
            "operation": "MODIFY"
        }
        assert self.action._should_trigger_incident(event_data) is True
    
    def test_should_trigger_incident_deprecation(self):
        """Test that deprecations trigger incidents."""
        event_data = {
            "category": "DEPRECATION",
            "operation": "ADD"
        }
        assert self.action._should_trigger_incident(event_data) is True
    
    def test_should_trigger_incident_pii_tag(self):
        """Test that PII tag additions trigger incidents."""
        event_data = {
            "category": "TAG",
            "operation": "ADD",
            "modifier": "urn:li:tag:PII"
        }
        assert self.action._should_trigger_incident(event_data) is True
    
    def test_should_not_trigger_incident_normal_tag(self):
        """Test that normal tag additions don't trigger incidents."""
        event_data = {
            "category": "TAG",
            "operation": "ADD",
            "modifier": "urn:li:tag:normal"
        }
        assert self.action._should_trigger_incident(event_data) is False
    
    def test_should_resolve_incident_deprecation_removed(self):
        """Test that deprecation removal resolves incidents."""
        event_data = {
            "category": "DEPRECATION",
            "operation": "REMOVE"
        }
        assert self.action._should_resolve_incident(event_data) is True
    
    def test_should_resolve_incident_pii_tag_removed(self):
        """Test that PII tag removal resolves incidents."""
        event_data = {
            "category": "TAG",
            "operation": "REMOVE",
            "modifier": "urn:li:tag:PII"
        }
        assert self.action._should_resolve_incident(event_data) is True
    
    def test_get_severity_mapping(self):
        """Test severity mapping for different categories."""
        assert self.action._get_severity({"category": "TECHNICAL_SCHEMA"}) == "warning"
        assert self.action._get_severity({"category": "OWNERSHIP"}) == "info"
        assert self.action._get_severity({"category": "DEPRECATION"}) == "warning"
        assert self.action._get_severity({"category": "UNKNOWN"}) == "warning"  # default
    
    def test_extract_component_from_urn(self):
        """Test component extraction from entity URN."""
        urn = "urn:li:dataset:(platform,db.schema.table,PROD)"
        assert self.action._extract_component(urn) == "table"
        
        urn = "urn:li:dataset:(platform,simple_name,PROD)"
        assert self.action._extract_component(urn) == "simple_name"
        
        urn = "urn:li:dataset:simple"
        assert self.action._extract_component(urn) == "simple"
    
    def test_generate_summary(self):
        """Test summary generation for different event types."""
        event_data = {
            "entityUrn": "urn:li:dataset:(platform,test.table,PROD)",
            "category": "TECHNICAL_SCHEMA",
            "operation": "MODIFY"
        }
        summary = self.action._generate_summary(event_data)
        assert "Schema change detected in table" in summary
    
    @patch('requests.post')
    def test_send_to_pagerduty_success(self, mock_post):
        """Test successful PagerDuty API call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Event processed"}
        mock_post.return_value = mock_response
        
        payload = {"test": "data"}
        self.action._send_to_pagerduty(payload)
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['headers']['Content-Type'] == 'application/json'
