# 📋 DMF Monitor Runbook Summary

## 🎯 **Complete Runbook Package**

You now have a comprehensive runbook for managing your DMF monitoring solution:

### **📚 Documentation Files**

| File | Purpose | When to Use |
|------|---------|-------------|
| **`DMF_MONITOR_RUNBOOK.md`** | **Complete runbook** | Full reference for all scenarios |
| **`QUICK_REFERENCE_CARD.md`** | **Quick reference** | Daily operations and troubleshooting |
| **`AUTOMATED_DMF_MONITORING.md`** | **Technical guide** | Setup and configuration details |
| **`README_AUTOMATED_SOLUTION.md`** | **Success summary** | Overview of what was accomplished |

### **🛠️ Helper Scripts**

| Script | Purpose | Usage |
|--------|---------|-------|
| **`simple_automated_monitor.py`** | **Main monitor** | `python simple_automated_monitor.py` |
| **`add_new_dmf.py`** | **Add new DMFs** | `python add_new_dmf.py` |
| **`schedule_dmf_monitor.sh`** | **Scheduling options** | `./schedule_dmf_monitor.sh` |

---

## 🚀 **AD HOC EXECUTION**

### **Quick Commands**
```bash
# Basic run
python simple_automated_monitor.py

# With logging
python simple_automated_monitor.py > adhoc_$(date +%Y%m%d_%H%M%S).log 2>&1

# Check results
tail -f dmf_monitor.log
```

### **Verification**
- **DataHub UI**: Check assertions tab for ACTIVE status
- **Logs**: Look for "Successfully reported" messages
- **Performance**: Should complete in ~5 seconds

---

## 🤖 **AUTOMATED EXECUTION**

### **CRON Setup (Recommended)**
```bash
# Edit crontab
crontab -e

# Add one of these:
*/15 * * * * cd /path/to/demo && python simple_automated_monitor.py >> dmf_monitor_cron.log 2>&1
0 9 * * * cd /path/to/demo && python simple_automated_monitor.py >> dmf_monitor_cron.log 2>&1
```

### **Monitoring**
```bash
# Check recent runs
tail -20 dmf_monitor.log

# Check for errors
grep "ERROR" dmf_monitor.log

# Check success rate
grep "Successfully reported" dmf_monitor.log | wc -l
```

---

## ➕ **ADDING NEW DMFs**

### **Step-by-Step Process**

**1. Use the Helper Script**
```bash
python add_new_dmf.py
```

**2. Add to Snowflake**
```sql
-- Example: Add completeness check
ALTER TABLE CUSTOMERS
    ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.COMPLETENESS ON (PHONE);
```

**3. Update Monitor Script**
- Add threshold to `get_threshold_for_metric()`
- Add SQL logic to `get_sql_logic_for_metric()`

**4. Test**
```bash
python simple_automated_monitor.py
```

**5. Verify**
- Check DataHub UI for new assertion
- Verify it's ACTIVE
- Review evaluation results

---

## 🔍 **TROUBLESHOOTING**

### **Connection Tests**
```bash
# Snowflake
python -c "from snowflake_assertion_extractor import SnowflakeAssertionExtractor; print('✅ Snowflake OK')"

# DataHub
python -c "from datahub.ingestion.graph.client import DataHubGraph; print('✅ DataHub OK')"
```

### **Common Issues**
- **Connection errors**: Check `.env` file credentials
- **Permission issues**: `chmod +x simple_automated_monitor.py`
- **CRON not running**: Check `systemctl status cron`
- **Assertions inactive**: Run manual execution first

---

## 📊 **MONITORING CHECKLIST**

### **Daily**
- [ ] Check logs: `tail -f dmf_monitor.log`
- [ ] Verify DataHub assertions are ACTIVE
- [ ] Check for any errors

### **Weekly**
- [ ] Review performance metrics
- [ ] Check success rate
- [ ] Analyze error patterns

### **Monthly**
- [ ] Review and update thresholds
- [ ] Check for new DMF types to add
- [ ] Rotate log files

---

## 🎯 **SUCCESS INDICATORS**

✅ **Script runs without errors**  
✅ **DataHub shows ACTIVE assertions**  
✅ **Evaluation history shows recent runs**  
✅ **Logs show "Successfully reported"**  
✅ **Execution time ~5 seconds**  
✅ **No connection errors**  

---

## 📞 **SUPPORT ESCALATION**

### **Level 1: Self-Service**
- Check runbook documentation
- Run connection tests
- Review log files
- Test manual execution

### **Level 2: Team Support**
- DataHub issues: DataHub support team
- Snowflake issues: Snowflake support team
- Script issues: Development team
- Infrastructure: DevOps team

---

## 🚀 **QUICK START GUIDE**

### **For New Users**
1. **Read**: `QUICK_REFERENCE_CARD.md`
2. **Test**: `python simple_automated_monitor.py`
3. **Schedule**: `./schedule_dmf_monitor.sh`
4. **Monitor**: Check DataHub UI and logs

### **For Adding DMFs**
1. **Run**: `python add_new_dmf.py`
2. **Follow**: Generated instructions
3. **Test**: `python simple_automated_monitor.py`
4. **Verify**: Check DataHub UI

### **For Troubleshooting**
1. **Check**: `DMF_MONITOR_RUNBOOK.md`
2. **Test**: Connection tests
3. **Review**: Log files
4. **Escalate**: If needed

---

## 📁 **File Organization**

```
snowflake-dmf-demo/
├── 📚 Documentation
│   ├── DMF_MONITOR_RUNBOOK.md          # Complete runbook
│   ├── QUICK_REFERENCE_CARD.md         # Quick reference
│   ├── AUTOMATED_DMF_MONITORING.md     # Technical guide
│   └── README_AUTOMATED_SOLUTION.md    # Success summary
├── 🛠️ Scripts
│   ├── simple_automated_monitor.py     # Main monitor
│   ├── add_new_dmf.py                  # Add new DMFs
│   └── schedule_dmf_monitor.sh         # Scheduling options
├── 📊 Logs
│   ├── dmf_monitor.log                 # Main logs
│   └── dmf_monitor_cron.log            # CRON logs
└── ⚙️ Configuration
    └── .env                            # Environment variables
```

---

## 🎉 **You're All Set!**

**You now have a complete, production-ready DMF monitoring solution with:**

✅ **Automated monitoring** that runs on schedule  
✅ **Ad hoc execution** for testing and troubleshooting  
✅ **Easy DMF addition** with helper scripts  
✅ **Comprehensive documentation** for all scenarios  
✅ **Troubleshooting guides** for common issues  
✅ **Monitoring procedures** for ongoing maintenance  

**The solution is repeatable, scalable, and ready for production deployment!** 🚀

---

**📋 Keep the runbook handy and refer to it whenever you need to:**
- Run the monitor ad hoc
- Set up automated scheduling  
- Add new DMFs
- Troubleshoot issues
- Monitor the system
