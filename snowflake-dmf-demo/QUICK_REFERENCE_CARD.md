# 🚀 DMF Monitor Quick Reference Card

## **AD HOC RUNS**

### **Basic Run**
```bash
python simple_automated_monitor.py
```

### **With Logging**
```bash
python simple_automated_monitor.py > adhoc_$(date +%Y%m%d_%H%M%S).log 2>&1
```

### **Check Results**
- **DataHub UI**: [Quality Page](https://test-environment.acryl.io/dataset/urn:li:dataset:(urn:li:dataPlatform:snowflake,DMF_DEMO_DB.DEMO_SCHEMA.CUSTOMERS,PROD)/Quality/List)
- **Look for**: "Snowflake DMF" assertion
- **Status**: Should be ACTIVE
- **History**: Check evaluation runs

---

## **AUTOMATED SCHEDULING**

### **CRON (Every 15 minutes)**
```bash
crontab -e
# Add this line:
*/15 * * * * cd /path/to/snowflake-dmf-demo && python simple_automated_monitor.py >> dmf_monitor_cron.log 2>&1
```

### **CRON (Daily at 9 AM)**
```bash
crontab -e
# Add this line:
0 9 * * * cd /path/to/snowflake-dmf-demo && python simple_automated_monitor.py >> dmf_monitor_cron.log 2>&1
```

### **View All Options**
```bash
./schedule_dmf_monitor.sh
```

---

## **ADDING NEW DMFs**

### **1. Add to Snowflake**
```sql
ALTER TABLE CUSTOMERS
    ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.COMPLETENESS ON (PHONE);
```

### **2. Update Script**
Edit `simple_automated_monitor.py`:
- Add new metric to extraction logic
- Define threshold: `get_threshold_for_metric()`
- Add SQL logic: `get_sql_logic_for_metric()`

### **3. Test**
```bash
python simple_automated_monitor.py
```

### **4. Verify**
- Check DataHub UI for new assertion
- Verify it's ACTIVE
- Review evaluation results

---

## **TROUBLESHOOTING**

### **Test Connections**
```bash
# Snowflake
python -c "from snowflake_assertion_extractor import SnowflakeAssertionExtractor; print('✅ Snowflake OK')"

# DataHub
python -c "from datahub.ingestion.graph.client import DataHubGraph; print('✅ DataHub OK')"
```

### **Check Logs**
```bash
# Recent runs
tail -20 dmf_monitor.log

# Errors
grep "ERROR" dmf_monitor.log

# Success rate
grep "Successfully reported" dmf_monitor.log | wc -l
```

### **Check CRON**
```bash
# CRON status
systemctl status cron

# CRON logs
tail -f /var/log/cron
```

---

## **MONITORING**

### **Daily Checks**
```bash
tail -f dmf_monitor.log
```

### **Weekly Checks**
```bash
# Performance
grep "Duration:" dmf_monitor.log | tail -10

# Errors
grep -A 3 -B 3 "ERROR" dmf_monitor.log
```

### **DataHub UI**
- **URL**: [Quality Page](https://test-environment.acryl.io/dataset/urn:li:dataset:(urn:li:dataPlatform:snowflake,DMF_DEMO_DB.DEMO_SCHEMA.CUSTOMERS,PROD)/Quality/List)
- **Check**: Assertions tab
- **Look for**: "Snowflake DMF" assertions
- **Status**: Should be ACTIVE
- **History**: Recent evaluation runs

---

## **KEY FILES**

| File | Purpose |
|------|---------|
| `simple_automated_monitor.py` | **Main script** |
| `schedule_dmf_monitor.sh` | **Scheduling options** |
| `DMF_MONITOR_RUNBOOK.md` | **Complete runbook** |
| `dmf_monitor.log` | **Execution logs** |
| `.env` | **Configuration** |

---

## **SUCCESS INDICATORS**

✅ **Script runs without errors**  
✅ **DataHub shows ACTIVE assertions**  
✅ **Evaluation history shows recent runs**  
✅ **Logs show "Successfully reported"**  
✅ **Execution time ~5 seconds**  

---

## **EMERGENCY CONTACTS**

- **DataHub Issues**: DataHub support
- **Snowflake Issues**: Snowflake support  
- **Script Issues**: Development team
- **Infrastructure**: DevOps team

---

**🎯 Keep this card handy for quick reference!**
