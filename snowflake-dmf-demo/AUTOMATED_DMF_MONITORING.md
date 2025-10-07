# 🤖 Automated DMF Monitoring - Snowflake to DataHub Integration

This guide shows you how to set up **repeatable, automated monitoring** of Snowflake Data Metric Functions (DMFs) with automatic reporting to DataHub.

## 🎯 What This Achieves

✅ **Automatically extracts** DMF data from Snowflake  
✅ **Creates/updates** custom assertions in DataHub  
✅ **Reports evaluation results** to make assertions ACTIVE  
✅ **Runs on a schedule** (cron, systemd, cloud schedulers)  
✅ **Provides comprehensive logging** for monitoring  
✅ **Handles errors gracefully** with proper error handling  

## 🚀 Quick Start

### 1. Test the Monitor Manually

```bash
# Test the automated monitor
python simple_automated_monitor.py
```

### 2. Set Up Scheduling

```bash
# View scheduling options
./schedule_dmf_monitor.sh
```

### 3. Choose Your Scheduling Method

**Recommended: CRON Job (every 15 minutes)**
```bash
# Add to crontab (crontab -e)
*/15 * * * * cd /path/to/snowflake-dmf-demo && python simple_automated_monitor.py >> dmf_monitor_cron.log 2>&1
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `simple_automated_monitor.py` | **Main automated monitor script** |
| `schedule_dmf_monitor.sh` | **Scheduling options and setup guide** |
| `snowflake_assertion_extractor.py` | **Snowflake DMF extraction logic** |
| `dmf_monitor.log` | **Automated monitor logs** |
| `.env` | **Environment configuration** |

## 🔧 How It Works

### 1. **Extract DMF Data**
- Connects to Snowflake using your credentials
- Queries `SNOWFLAKE.LOCAL.DATA_QUALITY_MONITORING_RESULTS`
- Extracts current DMF values (e.g., INVALID_EMAIL_COUNT)

### 2. **Create/Update Assertion**
- Uses DataHub Graph API to create custom assertion
- Sets up proper metadata and SQL logic
- Links to Snowflake console for external access

### 3. **Report Results**
- Determines SUCCESS/FAILURE based on thresholds
- Reports evaluation results to DataHub
- Makes the assertion ACTIVE with current data

### 4. **Logging & Monitoring**
- Comprehensive logging to file and console
- Performance metrics (duration, success/failure)
- Error handling with detailed error messages

## 📊 Example Output

```
🤖 Simple Automated DMF Monitor
================================================================================
Automatically monitors Snowflake DMFs and reports to DataHub
Uses the proven approach that worked in our manual tests
================================================================================

🚀 Starting automated DMF monitoring cycle...
✅ DataHub Graph client initialized
📊 Extracting current DMF data from Snowflake...
✅ Current DMF value: 1
📝 Creating/updating assertion: urn:li:assertion:snowflake-dmf-simple-assertion
✅ Created/updated assertion: urn:li:assertion:snowflake-dmf-simple-assertion
📊 Reporting assertion result: FAILURE
   Current value: 1, Expected: <= 0
✅ Successfully reported assertion result: FAILURE
🎉 Automated monitoring cycle completed!
   Duration: 5.30 seconds
   DMF Value: 1
   Result: FAILURE
   Assertion: urn:li:assertion:snowflake-dmf-simple-assertion

🎉 Automated DMF monitoring completed successfully!
Check DataHub for updated assertion results.
The assertion should now be ACTIVE with the latest evaluation.
```

## 🕐 Scheduling Options

### 1. **CRON Jobs** (Recommended)
```bash
# Every 15 minutes
*/15 * * * * cd /path/to/demo && python simple_automated_monitor.py >> dmf_monitor_cron.log 2>&1

# Every hour
0 * * * * cd /path/to/demo && python simple_automated_monitor.py >> dmf_monitor_cron.log 2>&1

# Daily at 9 AM
0 9 * * * cd /path/to/demo && python simple_automated_monitor.py >> dmf_monitor_cron.log 2>&1
```

### 2. **Systemd Timer** (Linux)
```bash
# Create service and timer files
sudo systemctl enable dmf-monitor.timer
sudo systemctl start dmf-monitor.timer
```

### 3. **Docker Container**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN echo '*/15 * * * * cd /app && python simple_automated_monitor.py' | crontab -
CMD ["cron", "-f"]
```

### 4. **Cloud Schedulers**
- **AWS EventBridge** → Lambda function
- **Google Cloud Scheduler** → Cloud Function  
- **Azure Logic Apps** → Recurring workflow
- **Apache Airflow** → DAG with PythonOperator

## 📋 Configuration

### Environment Variables (.env)
```bash
# DataHub Configuration
DATAHUB_GMS_URL=https://your-datahub-instance.acryl.io
DATAHUB_GMS_TOKEN=your-datahub-token

# Snowflake Configuration  
SNOWFLAKE_ACCOUNT=your-account
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_DATABASE=DMF_DEMO_DB
SNOWFLAKE_SCHEMA=DEMO_SCHEMA
SNOWFLAKE_WAREHOUSE=your-warehouse
```

### Customization Options

**Thresholds**: Modify in `simple_automated_monitor.py`
```python
# Current threshold logic
result_type = "SUCCESS" if current_value <= 0 else "FAILURE"
```

**DMF Metrics**: Add more metrics in the extraction logic
```python
# Add more DMF types
if metric_name not in dmf_data:
    dmf_data[metric_name] = {
        'current_value': int(current_value),
        'threshold': get_threshold_for_metric(metric_name)
    }
```

## 📊 Monitoring & Logs

### Log Files
- **`dmf_monitor.log`**: Main monitor logs
- **`dmf_monitor_cron.log`**: CRON execution logs  
- **`dmf_monitor_systemd.log`**: Systemd execution logs

### Log Analysis
```bash
# View recent logs
tail -f dmf_monitor.log

# Check for errors
grep "ERROR" dmf_monitor.log

# Monitor success rate
grep "Successfully reported" dmf_monitor.log | wc -l
```

## 🔍 Troubleshooting

### Common Issues

**1. Connection Errors**
```bash
# Test Snowflake connection
python -c "from snowflake_assertion_extractor import SnowflakeAssertionExtractor; print('✅ Snowflake OK')"

# Test DataHub connection  
python -c "from datahub.ingestion.graph.client import DataHubGraph; print('✅ DataHub OK')"
```

**2. Missing Environment Variables**
```bash
# Check .env file
cat .env | grep -E "(DATAHUB|SNOWFLAKE)"
```

**3. Permission Issues**
```bash
# Make scripts executable
chmod +x simple_automated_monitor.py
chmod +x schedule_dmf_monitor.sh
```

**4. CRON Issues**
```bash
# Check CRON logs
tail -f /var/log/cron

# Test CRON environment
*/15 * * * * cd /path/to/demo && /usr/bin/python3 simple_automated_monitor.py
```

## 🎯 DataHub UI Verification

After running the automated monitor:

1. **Go to DataHub** → Datasets → CUSTOMERS table
2. **Check Assertions tab** → Look for "Snowflake DMF" assertion
3. **Verify Status**: Should show as ACTIVE
4. **Check Evaluation History**: Should show recent runs
5. **Review Properties**: Current values, thresholds, timestamps

## 🚀 Production Deployment

### 1. **Environment Setup**
```bash
# Create production environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. **Security**
```bash
# Secure .env file
chmod 600 .env

# Use environment variables instead of .env in production
export DATAHUB_GMS_URL="https://your-instance.acryl.io"
export DATAHUB_GMS_TOKEN="your-token"
```

### 3. **Monitoring**
```bash
# Set up log rotation
sudo logrotate -f /etc/logrotate.d/dmf-monitor

# Set up alerts for failures
grep "ERROR" dmf_monitor.log | mail -s "DMF Monitor Error" admin@company.com
```

### 4. **Scaling**
- **Multiple Tables**: Modify script to loop through multiple tables
- **Multiple Databases**: Add database iteration logic
- **Parallel Processing**: Use multiprocessing for large datasets
- **Load Balancing**: Distribute across multiple instances

## 📈 Advanced Features

### 1. **Multiple DMF Types**
```python
# Add support for different DMF types
dmf_thresholds = {
    'INVALID_EMAIL_COUNT': 0,
    'NULL_COUNT': 0,
    'FRESHNESS': 24,  # hours
    'COMPLETENESS': 0.95  # percentage
}
```

### 2. **Alerting Integration**
```python
# Add Slack/Teams notifications
def send_alert(message):
    # Slack webhook or Teams webhook
    pass
```

### 3. **Historical Tracking**
```python
# Store historical data
def store_historical_data(metric_name, value, timestamp):
    # Database or file storage
    pass
```

## 🎉 Success Metrics

✅ **Automated Execution**: Runs without manual intervention  
✅ **Active Assertions**: DataHub shows ACTIVE status  
✅ **Real-time Updates**: Latest DMF values reflected  
✅ **Error Handling**: Graceful failure handling  
✅ **Comprehensive Logging**: Full audit trail  
✅ **Scalable**: Easy to extend to more tables/metrics  

## 📚 References

- [DataHub Custom Assertions API](https://docs.datahub.com/docs/api/tutorials/custom-assertions)
- [Snowflake Data Metric Functions](https://docs.snowflake.com/en/sql-reference/functions-data-metric)
- [DataHub Python SDK](https://datahub.readthedocs.io/en/latest/metadata-ingestion/)

---

**🎯 You now have a complete, repeatable solution for monitoring Snowflake DMFs and reporting to DataHub!**

The automated monitor will:
1. **Extract** current DMF values from Snowflake
2. **Create/update** assertions in DataHub  
3. **Report** evaluation results to make assertions ACTIVE
4. **Run on schedule** for continuous monitoring
5. **Provide logs** for troubleshooting and monitoring

**Next steps**: Choose your scheduling method and deploy to production! 🚀
