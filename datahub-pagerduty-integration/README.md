# DataHub PagerDuty Integration

🚨 **Automated Incident Management for Your Data Infrastructure** 🚨

This integration bridges DataHub Cloud with PagerDuty to provide real-time alerting and incident management for critical data events. When something goes wrong with your data—schema changes, quality failures, or ownership issues—your team gets immediately notified through PagerDuty's proven alerting system.

## 🎯 Why This Integration Matters

### The Problem
Modern data teams manage hundreds of datasets across multiple platforms. When critical data issues occur:
- **Silent failures** can go unnoticed for hours or days
- **Downstream impacts** affect business decisions and customer experiences  
- **Manual monitoring** doesn't scale as data ecosystems grow
- **Communication gaps** between data teams and incident responders

### The Solution
This integration automatically monitors your DataHub Cloud instance and creates PagerDuty incidents for critical data events, ensuring:
- ⚡ **Immediate alerting** when data issues occur
- 🎯 **Targeted notifications** to the right on-call teams
- 🔄 **Automated resolution** when issues are fixed
- 📊 **Incident tracking** for post-mortem analysis and SLA monitoring

## 📋 What Events Trigger Incidents

The integration monitors these critical data events in DataHub Cloud:

### 🔴 Critical Events (Error/Critical Severity)
- **Data Quality Assertion Failures**: When data quality checks fail
- **Ingestion Pipeline Failures**: When data ingestion jobs break
- **Missing Data**: When expected datasets don't arrive

### 🟡 Warning Events (Warning Severity)  
- **Schema Changes**: When table schemas are modified unexpectedly
- **Asset Deprecations**: When critical datasets are marked as deprecated
- **Data Freshness Issues**: When data becomes stale beyond thresholds

### 🔵 Info Events (Info Severity)
- **Ownership Changes**: When dataset ownership is transferred
- **Tag Modifications**: When critical tags (like PII) are added/removed
- **Documentation Updates**: When important documentation changes

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DataHub Cloud │    │ Actions Framework│    │   PagerDuty     │
│  (fieldeng.acryl│───▶│  (Your Computer) │───▶│   Incidents     │
│      .io)       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    Metadata Events         Event Processing        Incident Management
    • Schema changes        • Event filtering        • Alert routing
    • Quality failures      • Severity mapping       • Escalation
    • Ownership changes     • Deduplication         • Auto-resolution
```

### How It Works
1. **Event Monitoring**: The Actions Framework polls DataHub Cloud via REST API using your Personal Access Token
2. **Event Processing**: Events are filtered, categorized, and mapped to appropriate severity levels
3. **Incident Creation**: Critical events trigger PagerDuty incidents with rich context and links
4. **Auto-Resolution**: When issues are resolved in DataHub, corresponding PagerDuty incidents are automatically resolved
5. **Deduplication**: Multiple events for the same issue are grouped into a single incident

## Prerequisites

- DataHub Cloud account access
- Personal Access Token from DataHub Cloud
- PagerDuty account with Events API v2 service
- Python 3.8+

## 🚀 Quick Start

### Prerequisites
- DataHub Cloud account access (`fieldeng.acryl.io`)
- Personal Access Token from DataHub Cloud  
- PagerDuty account with Events API v2 service
- Python 3.8+

### 1. Clone and Setup

```bash
git clone https://github.com/martyacryl/datahubdemos.git
cd datahubdemos/datahub-pagerduty-integration

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure DataHub Cloud Access

1. Log into DataHub Cloud at `https://fieldeng.acryl.io`
2. Navigate to **Settings** → **Access Tokens**
3. Click **Generate new token**
4. Name: "PagerDuty Integration"
5. Expiration: 1 year (recommended)
6. Copy the token - you'll need it for the `.env` file

### 3. Configure PagerDuty Service

1. Log into your PagerDuty account
2. Navigate to **Services** → **Service Directory**
3. Click **+ New Service**
4. **Service Details**:
   - Name: "DataHub Data Quality Alerts"
   - Description: "Critical data events from DataHub Cloud"
5. **Integration Settings**:
   - Select **"Use our API directly"**
   - Choose **"Events API v2"**
6. **Escalation Policy**: Assign to your data team's escalation policy
7. Click **Create Service**
8. **Copy the Integration Key** from the service details

### 4. Environment Configuration

```bash
# Copy the environment template
cp .env.example .env

# Edit with your actual tokens (use any text editor)
nano .env
```

Update `.env` with your tokens:
```env
# Required: Your DataHub Cloud Personal Access Token
DATAHUB_GMS_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...

# Required: PagerDuty Integration Key (Events API v2)  
PAGERDUTY_ROUTING_KEY=R012ABC34DEF5GHI67890JKL

# Optional: Environment identifier
ENVIRONMENT=production
```

### 5. Test the Integration

```bash
# Test with debug logging to see what's happening
python -m datahub_pagerduty_integration --debug

# Or use the DataHub Actions CLI directly
datahub actions -c config/pagerduty_action.yaml --debug
```

### 6. Verify It's Working

1. **Check Logs**: Look for successful connection messages
2. **Make a Test Change**: Add a tag or change ownership in DataHub Cloud
3. **Check PagerDuty**: Verify incidents are created for critical events
4. **Test Resolution**: Fix the issue in DataHub and verify auto-resolution

## 🔧 Configuration Deep Dive

### Event Filtering
The integration can be configured to monitor specific types of events. Edit `config/pagerduty_action.yaml`:

```yaml
# Monitor only critical events
filter:
  event_type: "EntityChangeEvent_v1"
  event:
    aspectName: ["schemaMetadata", "assertions", "deprecation"]
```

### Severity Mapping
Customize how DataHub events map to PagerDuty severity levels:

```yaml
action:
  config:
    severity_mapping:
      schema_change: "warning"        # Schema changes are warnings
      data_quality_failure: "error"  # Quality failures are errors  
      ingestion_failure: "critical"  # Pipeline failures are critical
      ownership_change: "info"       # Ownership changes are info
      deprecation: "warning"         # Deprecations are warnings
```

### Auto-Resolution
Configure which events should automatically resolve incidents:

```yaml
action:
  config:
    enable_auto_resolve: true
    auto_resolve_events:
      - "data_quality_restored"  # Quality checks passing again
      - "ingestion_restored"     # Pipeline working again
      - "ownership_restored"     # Ownership issues fixed
```

### Custom Fields
Add organization-specific context to incidents:

```yaml
action:
  config:
    custom_fields:
      environment: "production"
      team: "data-engineering"
      service: "datahub"
      runbook_url: "https://wiki.company.com/data-incident-response"
```

## 🧪 Testing & Validation

### Unit Testing
```bash
# Run the test suite
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src/datahub_pagerduty_integration --cov-report=html
```

### Integration Testing

#### Test 1: Basic Connectivity
```bash
# Test DataHub Cloud connection
python -c "
import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DATAHUB_GMS_TOKEN')
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('https://fieldeng.acryl.io/gms/health', headers=headers)
print(f'DataHub Health: {response.status_code}')
"

# Test PagerDuty connection
python -c "
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
routing_key = os.getenv('PAGERDUTY_ROUTING_KEY')
payload = {
    'routing_key': routing_key,
    'event_action': 'trigger',
    'payload': {
        'summary': 'Test incident from DataHub integration',
        'source': 'DataHub Test',
        'severity': 'info'
    }
}
response = requests.post('https://events.pagerduty.com/v2/enqueue', 
                        data=json.dumps(payload),
                        headers={'Content-Type': 'application/json'})
print(f'PagerDuty Test: {response.status_code} - {response.json()}')
"
```

#### Test 2: End-to-End Event Processing
```bash
# Run with debug logging and watch for events
python -m datahub_pagerduty_integration --debug

# In another terminal, make changes in DataHub Cloud:
# 1. Add a tag to a dataset
# 2. Change ownership
# 3. Add a deprecation notice
# 4. Update documentation

# Watch the logs for event processing and PagerDuty API calls
```

#### Test 3: Incident Verification
1. **Create Test Incident**: Make a change in DataHub that should trigger an incident  
2. **Check PagerDuty**: Verify the incident appears with correct details
3. **Verify Context**: Check that the incident includes:
   - Clear summary of the issue
   - Link to the DataHub entity
   - Custom fields with environment/team info
   - Appropriate severity level
4. **Test Auto-Resolution**: Fix the issue in DataHub and verify the incident resolves

### Performance Testing
```bash
# Monitor memory and CPU usage
python -m datahub_pagerduty_integration --debug &
PID=$!

# Monitor resource usage
top -p $PID

# Or use more detailed monitoring
python -m py-spy top --pid $PID
```

## 🔍 Code Structure & Implementation Details

### Core Components

#### `src/datahub_pagerduty_integration/pagerduty_action.py`
The main integration logic that:
- **Extends DataHub's Action base class** to handle metadata events
- **Filters events** based on criticality and type
- **Maps DataHub events** to PagerDuty incidents with appropriate severity
- **Handles deduplication** using entity URNs to prevent spam
- **Manages auto-resolution** when issues are fixed
- **Formats rich incident details** with links and context

Key methods:
- `act()`: Processes each DataHub event
- `_should_trigger_incident()`: Determines if an event warrants an incident
- `_send_trigger_event()`: Creates PagerDuty incidents
- `_send_resolve_event()`: Resolves incidents automatically

#### `src/datahub_pagerduty_integration/runner.py`
The runtime orchestrator that:
- **Loads environment variables** from `.env` file
- **Validates configuration** and required tokens
- **Launches the DataHub Actions CLI** with proper parameters
- **Handles graceful shutdown** and error recovery

#### `config/pagerduty_action.yaml`
DataHub Actions configuration that:
- **Defines event sources** (DataHub Cloud REST API)
- **Configures polling intervals** for checking new events
- **Sets up event filtering** to focus on critical events only
- **Maps action parameters** like routing keys and severity levels

### Event Processing Flow

```python
# Simplified event processing logic
def act(self, event: EventEnvelope) -> None:
    """Process a DataHub event and potentially send to PagerDuty"""
    
    # 1. Extract event metadata
    event_type = event.event_type
    entity_urn = event.event.get("entityUrn")
    aspect_name = event.event.get("aspectName")
    
    # 2. Determine criticality
    if self._should_trigger_incident(event.event):
        # 3. Create rich incident context
        incident_data = {
            "summary": self._generate_summary(event),
            "source": "DataHub Cloud",
            "severity": self._get_severity(event),
            "component": self._extract_component(entity_urn),
            "custom_details": {
                "entity_url": f"https://fieldeng.acryl.io/dataset/{entity_urn}",
                "aspect_name": aspect_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # 4. Send to PagerDuty
        self._send_to_pagerduty(incident_data)
```

### Deduplication Strategy

The integration uses intelligent deduplication to prevent alert spam:

```python
# Generate consistent deduplication key
dedup_key = f"datahub-{entity_urn}-{aspect_name}"
```

This ensures:
- **Multiple events** for the same entity/aspect are grouped
- **Incident updates** rather than new incidents for ongoing issues
- **Clean resolution** when the underlying issue is fixed

### Error Handling & Resilience

The integration includes robust error handling:
- **Retry logic** for transient API failures
- **Circuit breaker** patterns for PagerDuty API rate limiting
- **Dead letter queue** for events that can't be processed
- **Graceful degradation** when services are unavailable

## 🚀 Deployment Options

### Development & Testing
For local development and testing:
```bash
# Run interactively with debug logging
python -m datahub_pagerduty_integration --debug

# Run in background
nohup python -m datahub_pagerduty_integration > logs/integration.log 2>&1 &
```

### Production Server Deployment
For 24/7 monitoring, deploy on a server:

```bash
# Copy to server
scp -r datahub-pagerduty-integration user@server:/opt/

# Install as systemd service
sudo cp scripts/datahub-pagerduty.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable datahub-pagerduty
sudo systemctl start datahub-pagerduty

# Check status
sudo systemctl status datahub-pagerduty
sudo journalctl -u datahub-pagerduty -f
```

### Docker Deployment
```bash
# Build image
docker build -t datahub-pagerduty .

# Run container
docker run -d \
  --name datahub-pagerduty \
  --env-file .env \
  --restart unless-stopped \
  -v $(pwd)/logs:/app/logs \
  datahub-pagerduty

# Check logs
docker logs -f datahub-pagerduty
```

### Cloud Deployment (AWS/GCP/Azure)
The integration can be deployed on any cloud platform:

- **AWS**: EC2 instance, ECS container, or Lambda function
- **GCP**: Compute Engine, Cloud Run, or Cloud Functions  
- **Azure**: Virtual Machine, Container Instances, or Functions

For serverless deployments, consider using cron-triggered functions that run the integration periodically.

## 📊 Monitoring & Observability

### Application Logs
```bash
# View real-time logs
tail -f logs/datahub_pagerduty.log

# Search for errors
grep -i error logs/datahub_pagerduty.log

# Monitor API calls
grep -i "pagerduty\|datahub" logs/datahub_pagerduty.log
```

### Health Checks
```bash
# Check if the integration is running
ps aux | grep datahub_pagerduty

# Check DataHub Cloud connectivity
curl -H "Authorization: Bearer $DATAHUB_GMS_TOKEN" \
     https://fieldeng.acryl.io/gms/health

# Check PagerDuty Events API
curl -X POST https://events.pagerduty.com/v2/enqueue \
     -H "Content-Type: application/json" \
     -d '{"routing_key":"test","event_action":"trigger","payload":{"summary":"health check"}}'
```

### Metrics & Alerting
Consider implementing these metrics:
- **Events processed per hour**
- **PagerDuty API success rate**  
- **DataHub API response times**
- **Integration uptime**

## 🛠️ Troubleshooting

### Common Issues

#### Authentication Errors
```
ERROR: Failed to authenticate with DataHub Cloud
```
**Solutions:**
- Verify your Personal Access Token is correct
- Check token expiration date in DataHub Cloud
- Ensure token has required permissions
- Regenerate token if necessary

#### PagerDuty API Errors
```
ERROR: Failed to send event to PagerDuty: 400 Client Error
```
**Solutions:**
- Verify PagerDuty routing key is correct
- Check PagerDuty service configuration
- Ensure Events API v2 is enabled
- Test API manually with curl

#### No Events Being Processed
```
INFO: No events received in the last 5 minutes
```
**Solutions:**
- Check DataHub Cloud connectivity
- Verify event filtering rules aren't too restrictive
- Enable debug logging to see event flow
- Make test changes in DataHub Cloud

#### Memory/Performance Issues
```
WARNING: High memory usage detected
```
**Solutions:**
- Restart the integration service
- Check for memory leaks in logs
- Adjust polling intervals
- Monitor system resources

### Debug Mode
Enable detailed logging to troubleshoot issues:
```bash
# Maximum verbosity
python -m datahub_pagerduty_integration --debug

# Log API requests and responses
export DATAHUB_DEBUG=true
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

### Getting Help

1. **Check Logs**: Always start with the application logs
2. **Test Connectivity**: Verify both DataHub and PagerDuty APIs work
3. **Review Configuration**: Double-check tokens and settings
4. **GitHub Issues**: Report bugs or request features
5. **DataHub Community**: Ask questions in DataHub Slack
6. **PagerDuty Support**: For PagerDuty-specific issues

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/datahubdemos.git
cd datahubdemos/datahub-pagerduty-integration

# Create development environment
python -m venv dev-env
source dev-env/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test categories
python -m pytest tests/test_pagerduty_action.py -v
python -m pytest tests/integration/ -v
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code  
flake8 src/ tests/

# Type checking
mypy src/
```

### Submitting Changes
1. Create a feature branch: `git checkout -b feature/new-feature`
2. Make changes and add tests
3. Run the test suite and ensure all tests pass
4. Submit a pull request with a clear description

## 📚 Additional Resources

### Documentation
- [DataHub Actions Framework](https://datahubproject.io/docs/actions)
- [PagerDuty Events API v2](https://developer.pagerduty.com/docs/events-api-v2)
- [DataHub Cloud Documentation](https://docs.acryl.io)

### Related Projects
- [DataHub Slack Integration](https://github.com/datahub-project/datahub/tree/master/docs/actions/actions/slack)
- [DataHub Microsoft Teams Integration](https://github.com/datahub-project/datahub/tree/master/docs/actions/actions/teams)

### Community
- [DataHub Slack Community](https://datahubspace.slack.com)
- [PagerDuty Community](https://community.pagerduty.com)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **DataHub Team** for building the Actions Framework
- **PagerDuty** for their robust Events API
- **Open Source Community** for inspiration and best practices

---

**Made with ❤️ by the Data Engineering Team**

*For questions or support, please open an issue or contact the maintainers.*
