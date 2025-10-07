# 📋 DMF Monitor Runbook
## Complete Guide for Ad Hoc, Automated, and Adding New DMFs

---

## 🚀 **AD HOC EXECUTION**

### **When to Run Ad Hoc**
- ✅ Testing before setting up automation
- ✅ Troubleshooting scheduled runs
- ✅ Manual data quality checks
- ✅ Demonstrations
- ✅ Development/testing changes

### **How to Run Ad Hoc**

**Basic Run:**
```bash
cd /path/to/snowflake-dmf-demo
python simple_automated_monitor.py
```

**With Timestamped Output:**
```bash
python simple_automated_monitor.py > adhoc_run_$(date +%Y%m%d_%H%M%S).log 2>&1
```

**Verbose Run:**
```bash
python -u simple_automated_monitor.py
```

### **Ad Hoc Run Checklist**

**Before Running:**
- [ ] Verify `.env` file has correct credentials
- [ ] Check Snowflake connection: `python -c "from snowflake_assertion_extractor import SnowflakeAssertionExtractor; print('✅ Snowflake OK')"`
- [ ] Check DataHub connection: `python -c "from datahub.ingestion.graph.client import DataHubGraph; print('✅ DataHub OK')"`

**During Run:**
- [ ] Watch for connection errors
- [ ] Note execution time (should be ~5 seconds)
- [ ] Check for SUCCESS/FAILURE status
- [ ] Verify assertion URN is created/updated

**After Run:**
- [ ] Check DataHub UI for ACTIVE assertion
- [ ] Verify evaluation history shows new run
- [ ] Review log file for any errors
- [ ] Note current DMF values and thresholds

### **Ad Hoc Troubleshooting**

**Connection Issues:**
```bash
# Test Snowflake
python -c "
from snowflake_assertion_extractor import SnowflakeAssertionExtractor
extractor = SnowflakeAssertionExtractor()
print('✅ Snowflake connection OK')
"

# Test DataHub
python -c "
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from dotenv import load_dotenv
import os
load_dotenv()
graph = DataHubGraph(config=DatahubClientConfig(server=os.getenv('DATAHUB_GMS_URL'), token=os.getenv('DATAHUB_GMS_TOKEN')))
print('✅ DataHub connection OK')
"
```

**Permission Issues:**
```bash
chmod +x simple_automated_monitor.py
```

**Environment Issues:**
```bash
# Check .env file
cat .env | grep -E "(DATAHUB|SNOWFLAKE)"
```

---

## 🤖 **AUTOMATED EXECUTION**

### **Scheduling Options**

**1. CRON Job (Recommended)**
```bash
# Edit crontab
crontab -e

# Add one of these lines:
# Every 15 minutes
*/15 * * * * cd /path/to/snowflake-dmf-demo && python simple_automated_monitor.py >> dmf_monitor_cron.log 2>&1

# Every hour
0 * * * * cd /path/to/snowflake-dmf-demo && python simple_automated_monitor.py >> dmf_monitor_cron.log 2>&1

# Daily at 9 AM
0 9 * * * cd /path/to/snowflake-dmf-demo && python simple_automated_monitor.py >> dmf_monitor_cron.log 2>&1
```

**2. Systemd Timer (Linux)**
```bash
# Create service file
sudo tee /etc/systemd/system/dmf-monitor.service > /dev/null <<EOF
[Unit]
Description=DMF Monitor
After=network.target

[Service]
Type=oneshot
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/simple_automated_monitor.py
StandardOutput=append:$(pwd)/dmf_monitor_systemd.log
StandardError=append:$(pwd)/dmf_monitor_systemd.log
EOF

# Create timer file
sudo tee /etc/systemd/system/dmf-monitor.timer > /dev/null <<EOF
[Unit]
Description=Run DMF Monitor every 15 minutes
Requires=dmf-monitor.service

[Timer]
OnCalendar=*:0/15
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable and start
sudo systemctl enable dmf-monitor.timer
sudo systemctl start dmf-monitor.timer
```

**3. Docker Container**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN echo '*/15 * * * * cd /app && python simple_automated_monitor.py' | crontab -
CMD ["cron", "-f"]
```

### **Automated Monitoring Checklist**

**Setup Phase:**
- [ ] Test ad hoc run first
- [ ] Choose scheduling method
- [ ] Set up logging directory
- [ ] Configure log rotation
- [ ] Set up monitoring/alerting

**Ongoing Monitoring:**
- [ ] Check logs daily: `tail -f dmf_monitor.log`
- [ ] Monitor success rate: `grep "Successfully reported" dmf_monitor.log | wc -l`
- [ ] Check for errors: `grep "ERROR" dmf_monitor.log`
- [ ] Verify DataHub assertions are ACTIVE
- [ ] Review execution times (should be consistent)

### **Automated Troubleshooting**

**Check CRON Status:**
```bash
# View CRON logs
tail -f /var/log/cron

# Check if CRON is running
systemctl status cron

# Test CRON environment
*/15 * * * * cd /path/to/demo && /usr/bin/python3 simple_automated_monitor.py
```

**Check Systemd Status:**
```bash
# Check timer status
systemctl status dmf-monitor.timer

# Check service status
systemctl status dmf-monitor.service

# View logs
journalctl -u dmf-monitor.service -f
```

**Log Analysis:**
```bash
# Recent runs
tail -20 dmf_monitor.log

# Error analysis
grep -A 5 -B 5 "ERROR" dmf_monitor.log

# Success rate
grep "Successfully reported" dmf_monitor.log | tail -10

# Performance analysis
grep "Duration:" dmf_monitor.log | tail -10
```

---

## ➕ **ADDING NEW DMFs**

### **Step 1: Add DMF to Snowflake**

**In Snowflake, add new DMF:**
```sql
-- Example: Add completeness check
ALTER TABLE CUSTOMERS
    ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.COMPLETENESS ON (PHONE);

-- Example: Add freshness check
ALTER TABLE CUSTOMERS
    ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.FRESHNESS ON (UPDATED_DATE);

-- Example: Add null count check
ALTER TABLE CUSTOMERS
    ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (ADDRESS);
```

### **Step 2: Update the Monitor Script**

**Edit `simple_automated_monitor.py`:**

**Add new DMF types to the extraction logic:**
```python
def extract_dmf_data():
    """Extract current DMF data from Snowflake."""
    logger.info("📊 Extracting DMF data from Snowflake...")
    
    try:
        extractor = SnowflakeAssertionExtractor()
        assertions = extractor.extract_assertions()
        
        # Process and organize DMF data
        dmf_data = {}
        for assertion in assertions:
            metric_name = assertion.get('properties', {}).get('metric_name', 'Unknown')
            current_value = assertion.get('properties', {}).get('value', 0)
            column_name = assertion.get('properties', {}).get('column_name', 'N/A')
            
            if metric_name not in dmf_data:
                dmf_data[metric_name] = {
                    'current_value': int(current_value) if current_value is not None else 0,
                    'column_name': column_name,
                    'database': assertion.get('properties', {}).get('database_name'),
                    'schema': assertion.get('properties', {}).get('schema_name'),
                    'table': assertion.get('properties', {}).get('table_name'),
                    'measurement_time': assertion.get('properties', {}).get('measurement_time')
                }
        
        logger.info(f"✅ Extracted {len(dmf_data)} DMF metrics")
        for metric, data in dmf_data.items():
            logger.info(f"   {metric}: {data['current_value']} (column: {data['column_name']})")
        
        return dmf_data
        
    except Exception as e:
        logger.error(f"❌ Failed to extract DMF data: {str(e)}")
        return {}
```

**Add threshold logic for new DMFs:**
```python
def get_threshold_for_metric(metric_name):
    """Get threshold for different DMF types."""
    thresholds = {
        'INVALID_EMAIL_COUNT': 0,
        'NULL_COUNT': 0,
        'COMPLETENESS': 0.95,  # 95% completeness
        'FRESHNESS': 24,       # 24 hours
        'UNIQUENESS': 0,       # 0 duplicates
        'VALIDITY': 0          # 0 invalid records
    }
    return thresholds.get(metric_name, 0)

def create_or_update_assertion(graph, metric_name, dmf_data):
    """Create or update assertion for any DMF type."""
    dataset_urn = f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{dmf_data['database']}.{dmf_data['schema']}.{dmf_data['table']},PROD)"
    assertion_urn = f"urn:li:assertion:snowflake-dmf-{metric_name.lower().replace('_', '-')}"
    
    # Get threshold for this metric type
    threshold = get_threshold_for_metric(metric_name)
    
    # Create SQL logic based on metric type
    sql_logic = get_sql_logic_for_metric(metric_name, dmf_data)
    
    try:
        res = graph.upsert_custom_assertion(
            urn=assertion_urn,
            entity_urn=dataset_urn,
            type="Snowflake DMF",
            description=f"Snowflake DMF: {metric_name} should be <= {threshold} (current: {dmf_data['current_value']})",
            platform_urn="urn:li:dataPlatform:snowflake",
            field_path=dmf_data['column_name'] if dmf_data['column_name'] != 'N/A' else None,
            external_url=f"https://app.snowflake.com/console/account/{os.getenv('SNOWFLAKE_ACCOUNT')}/warehouses",
            logic=sql_logic
        )
        
        if res is not None:
            logger.info(f"✅ Created/updated assertion: {assertion_urn}")
            return assertion_urn, threshold
        else:
            logger.error(f"❌ Failed to create/update assertion: {assertion_urn}")
            return None, None
            
    except Exception as e:
        logger.error(f"❌ Failed to create/update assertion: {str(e)}")
        return None, None

def get_sql_logic_for_metric(metric_name, dmf_data):
    """Generate SQL logic for different DMF types."""
    table_ref = f"{dmf_data['database']}.{dmf_data['schema']}.{dmf_data['table']}"
    column = dmf_data['column_name']
    
    sql_templates = {
        'INVALID_EMAIL_COUNT': f"SELECT COUNT(*) FROM {table_ref} WHERE {column} NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{{2,}}$'",
        'NULL_COUNT': f"SELECT COUNT(*) FROM {table_ref} WHERE {column} IS NULL",
        'COMPLETENESS': f"SELECT (COUNT(*) - COUNT({column})) / COUNT(*) FROM {table_ref}",
        'FRESHNESS': f"SELECT DATEDIFF('hour', MAX({column}), CURRENT_TIMESTAMP()) FROM {table_ref}",
        'UNIQUENESS': f"SELECT COUNT(*) - COUNT(DISTINCT {column}) FROM {table_ref}",
        'VALIDITY': f"SELECT COUNT(*) FROM {table_ref} WHERE {column} IS NOT NULL AND {column} = ''"
    }
    
    return sql_templates.get(metric_name, f"SELECT COUNT(*) FROM {table_ref} WHERE {column} IS NULL")
```

### **Step 3: Test New DMF**

**Test the updated script:**
```bash
# Test with new DMF
python simple_automated_monitor.py

# Check logs for new metric
grep "Extracted.*DMF metrics" dmf_monitor.log

# Verify new assertion in DataHub
# Go to DataHub UI and check for new assertion
```

### **Step 4: Add Multiple Tables**

**For multiple tables, modify the script:**
```python
def run_monitoring_cycle():
    """Run monitoring for multiple tables."""
    tables_to_monitor = [
        {'database': 'DMF_DEMO_DB', 'schema': 'DEMO_SCHEMA', 'table': 'CUSTOMERS'},
        {'database': 'DMF_DEMO_DB', 'schema': 'DEMO_SCHEMA', 'table': 'ORDERS'},
        {'database': 'DMF_DEMO_DB', 'schema': 'DEMO_SCHEMA', 'table': 'PRODUCTS'}
    ]
    
    for table_config in tables_to_monitor:
        logger.info(f"📊 Monitoring table: {table_config['table']}")
        # Extract DMF data for this table
        # Create/update assertions
        # Report results
```

### **Adding New DMFs Checklist**

**Snowflake Setup:**
- [ ] Add DMF to Snowflake table
- [ ] Verify DMF is collecting data
- [ ] Check DMF results in Snowflake UI

**Script Updates:**
- [ ] Add new metric to extraction logic
- [ ] Define threshold for new metric
- [ ] Add SQL logic template
- [ ] Test script with new DMF

**DataHub Verification:**
- [ ] Check new assertion appears in DataHub
- [ ] Verify assertion is ACTIVE
- [ ] Review evaluation results
- [ ] Confirm properties are correct

**Production Deployment:**
- [ ] Test in development environment
- [ ] Deploy to production
- [ ] Monitor logs for new metric
- [ ] Set up alerts for new DMF failures

---

## 📊 **MONITORING & MAINTENANCE**

### **Daily Checks**
```bash
# Check recent runs
tail -20 dmf_monitor.log

# Check for errors
grep "ERROR" dmf_monitor.log | tail -5

# Check success rate
grep "Successfully reported" dmf_monitor.log | wc -l
```

### **Weekly Checks**
```bash
# Performance analysis
grep "Duration:" dmf_monitor.log | awk '{print $NF}' | sort -n

# Error analysis
grep -A 3 -B 3 "ERROR" dmf_monitor.log

# DataHub UI check
# Verify all assertions are ACTIVE
# Review evaluation history
```

### **Monthly Checks**
```bash
# Log rotation
sudo logrotate -f /etc/logrotate.d/dmf-monitor

# Performance trends
grep "Duration:" dmf_monitor.log | tail -100 | awk '{print $NF}' | sort -n

# Review and update thresholds
# Check for new DMF types to add
```

---

## 🚨 **EMERGENCY PROCEDURES**

### **Script Not Running**
1. Check CRON/systemd status
2. Verify environment variables
3. Test manual execution
4. Check log files for errors
5. Restart service if needed

### **DataHub Connection Issues**
1. Verify credentials in `.env`
2. Check DataHub instance status
3. Test connection manually
4. Review network connectivity

### **Snowflake Connection Issues**
1. Verify Snowflake credentials
2. Check warehouse status
3. Test connection manually
4. Review network connectivity

### **Assertions Not Active**
1. Run manual execution
2. Check DataHub UI
3. Verify assertion URNs
4. Review evaluation history

---

## 📞 **SUPPORT CONTACTS**

- **DataHub Issues**: DataHub support team
- **Snowflake Issues**: Snowflake support team
- **Script Issues**: Development team
- **Infrastructure Issues**: DevOps team

---

## 📚 **QUICK REFERENCE**

**Ad Hoc Run:**
```bash
python simple_automated_monitor.py
```

**Check Status:**
```bash
tail -f dmf_monitor.log
```

**View Scheduling Options:**
```bash
./schedule_dmf_monitor.sh
```

**Test Connections:**
```bash
python -c "from snowflake_assertion_extractor import SnowflakeAssertionExtractor; print('✅ Snowflake OK')"
python -c "from datahub.ingestion.graph.client import DataHubGraph; print('✅ DataHub OK')"
```

**DataHub UI:**
- Go to: Datasets → CUSTOMERS → Assertions tab
- Look for: "Snowflake DMF" assertions
- Check: Status should be ACTIVE

---

**🎯 This runbook covers all scenarios: ad hoc runs, automated scheduling, and adding new DMFs over time!**
