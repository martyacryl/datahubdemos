# DataHub Duplicate Asset Detector - Complete User Guide

This comprehensive guide walks you through every step to set up and use the DataHub Duplicate Asset Detector, including verification at each stage.

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- [ ] Python 3.8+ installed
- [ ] Access to DataHub GMS with appropriate permissions
- [ ] Valid DataHub Personal Access Token
- [ ] Basic understanding of DataHub concepts (datasets, charts, dashboards)

## 🚀 Step-by-Step Implementation

### Step 1: Environment Setup

#### 1.1 Navigate to the Project Directory
```bash
cd /Users/mstjohn/Documents/GitHub/datahubdemos/datahubduplicatesdemo
```

#### 1.2 Create Environment File
```bash
# Copy the example file
cp env.example .env

# Edit with your actual values
nano .env
```

#### 1.3 Configure Your Credentials
Edit `.env` with your actual values:
```bash
# DataHub Configuration
DATAHUB_GMS_URL=https://test-environment.acryl.io/gms
DATAHUB_GMS_TOKEN=your_actual_datahub_token_here

# Detection Configuration
ENTITY_TYPES=dataset,chart,dashboard,dataFlow,dataJob
DETECTION_TYPES=name,schema,description

# Advanced Configuration (optional)
NAME_SIMILARITY_THRESHOLD=0.8
SCHEMA_SIMILARITY_THRESHOLD=0.7
MIN_ASSETS_FOR_DUPLICATE=2
CASE_SENSITIVE=false
```

#### 1.4 Verify Environment Variables
```bash
# Load and check your environment variables
source .env
echo "DataHub URL: $DATAHUB_GMS_URL"
echo "Entity Types: $ENTITY_TYPES"
echo "Detection Types: $DETECTION_TYPES"
```

**✅ Verification:** You should see your actual values printed without any empty variables.

### Step 2: Install Dependencies

#### 2.1 Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2.2 Install Required Packages
```bash
pip install -r requirements.txt
```

#### 2.3 Verify Installation
```bash
# Test imports
python3 -c "import requests, json, os; print('✅ All packages installed successfully')"
```

**✅ Verification:** You should see "All packages installed successfully" without any import errors.

### Step 3: Test DataHub Connection

#### 3.1 Run Connection Test
```bash
python test_connection.py
```

#### 3.2 Verify Connection Test Output
You should see output like:
```
INFO:__main__:Testing connection to DataHub at: https://test-environment.acryl.io/gms
INFO:__main__:Testing basic asset search...
INFO:__main__:✅ Found 150 assets (showing first 5)
INFO:__main__: 1. customer_data (dataset) - snowflake
INFO:__main__: 2. sales_dashboard (dashboard) - looker
INFO:__main__: 3. revenue_chart (chart) - tableau
INFO:__main__:Testing entity type filtering...
INFO:__main__:✅ Found 120 datasets
INFO:__main__:✅ Found 15 charts
INFO:__main__:✅ Found 10 dashboards
INFO:__main__:✅ DataHub connection test successful!
INFO:__main__:Testing detection algorithms...
INFO:__main__:Testing name similarity calculation...
INFO:__main__:  'customer_data' vs 'customer_data_v2': 0.95
INFO:__main__:  'user_table' vs 'users_table': 0.89
INFO:__main__:Testing schema similarity calculation...
INFO:__main__:  Schema similarity: 0.75
INFO:__main__:✅ Detection algorithms test successful!
INFO:__main__:🎉 All tests passed! The duplicate detector is ready to use.
```

**✅ Verification:** Look for:
- "DataHub connection test successful!"
- Number of assets found (should be > 0)
- "All tests passed! The duplicate detector is ready to use."

### Step 4: Run Basic Duplicate Detection

#### 4.1 Run Basic Detection
```bash
python run_detector.py
```

#### 4.2 Monitor the Output
You should see output like:
```
INFO:__main__:DataHub Duplicate Asset Detector
INFO:__main__:================================
INFO:__main__:Starting duplicate detection...
INFO:__main__:Entity types: ['dataset', 'chart', 'dashboard']
INFO:__main__:Detection types: ['name', 'schema', 'description']
INFO:__main__:Name similarity threshold: 0.8
INFO:__main__:Schema similarity threshold: 0.7
INFO:__main__:Minimum assets for duplicate: 2
INFO:duplicate_detector:Searching for assets in DataHub...
INFO:duplicate_detector:Found 150 assets to analyze
INFO:duplicate_detector:Detecting name-based duplicates...
INFO:duplicate_detector:Found 5 name-based duplicates
INFO:duplicate_detector:Detecting schema-based duplicates...
INFO:duplicate_detector:Found 3 schema-based duplicates
INFO:duplicate_detector:Detecting description-based duplicates...
INFO:duplicate_detector:Found 2 description-based duplicates
INFO:duplicate_detector:Total duplicate findings: 10
INFO:__main__:Detection completed. Found 10 duplicate groups.
INFO:__main__:Markdown report saved to: ./reports/duplicate_report_20241003_143022.md
INFO:__main__:JSON report saved to: ./reports/duplicate_findings_20241003_143022.json
```

#### 4.3 Verify Detection Results
Look for:
- Number of assets found and analyzed
- Number of duplicates found by type
- Report files generated successfully
- No error messages

**✅ Verification:** You should see:
- "Detection completed. Found X duplicate groups."
- Report files created in `./reports/` directory
- No error messages

### Step 5: Review Detection Reports

#### 5.1 Check Generated Reports
```bash
ls -la reports/
```

**✅ Verification:** You should see files like:
- `duplicate_report_YYYYMMDD_HHMMSS.md`
- `duplicate_findings_YYYYMMDD_HHMMSS.json`

#### 5.2 Review Markdown Report
```bash
# View the markdown report
cat reports/duplicate_report_*.md | head -50
```

**✅ Verification:** You should see:
- Report header with timestamp and total findings
- Summary section with counts by type and confidence
- Detailed findings with asset information

#### 5.3 Review JSON Report
```bash
# View the JSON report structure
cat reports/duplicate_findings_*.json | head -20
```

**✅ Verification:** You should see:
- Valid JSON structure
- Asset metadata and similarity scores
- Confidence levels and reasoning

### Step 6: Advanced Detection Options

#### 6.1 Run Detection with Custom Parameters
```bash
# Detect only datasets with name-based duplicates
python run_detector.py --entity-types dataset --detection-types name --name-threshold 0.9

# Detect with higher sensitivity
python run_detector.py --name-threshold 0.7 --schema-threshold 0.6 --min-assets 2

# Dry run (no reports generated)
python run_detector.py --dry-run --verbose
```

#### 6.2 Verify Custom Parameters
**✅ Verification:** Check that:
- Only specified entity types are processed
- Similarity thresholds are applied correctly
- Dry run shows findings without generating files

### Step 7: Verify Findings in DataHub UI

#### 7.1 Open DataHub UI
1. Navigate to your DataHub instance in a web browser
2. Log in with your credentials

#### 7.2 Check Specific Assets
For each finding in the report:
1. **Copy the URN** from the report
2. **Search for the asset** in DataHub UI
3. **Verify the asset exists** and matches the report
4. **Check the asset details** (name, type, platform, description)

#### 7.3 Verify Duplicate Relationships
1. **Compare asset names** - they should be similar as reported
2. **Check asset schemas** (for datasets) - fields should overlap as indicated
3. **Read descriptions** - they should be similar for description-based duplicates

**✅ Verification:** You should be able to:
- Find all assets mentioned in the report
- Confirm the similarity relationships
- Verify the confidence levels make sense

### Step 8: Test Different Detection Scenarios

#### 8.1 Test Name-Based Detection
```bash
# Run with high name similarity threshold
python run_detector.py --detection-types name --name-threshold 0.95 --verbose
```

**✅ Verification:** Should find only very similar names (95%+ similarity)

#### 8.2 Test Schema-Based Detection
```bash
# Run schema detection only on datasets
python run_detector.py --entity-types dataset --detection-types schema --schema-threshold 0.8
```

**✅ Verification:** Should find datasets with 80%+ schema overlap

#### 8.3 Test Description-Based Detection
```bash
# Run description detection with lower threshold
python run_detector.py --detection-types description --verbose
```

**✅ Verification:** Should find assets with similar descriptions

### Step 9: Validate Detection Quality

#### 9.1 Check False Positives
Review the findings and identify any false positives:
- Assets that are similar but not actually duplicates
- Different versions that should be kept separate
- Assets with similar names but different purposes

#### 9.2 Check False Negatives
Look for obvious duplicates that weren't detected:
- Assets with slightly different naming patterns
- Assets with similar purposes but different descriptions
- Assets that might need different similarity thresholds

#### 9.3 Adjust Configuration
Based on your findings, adjust the configuration:
```bash
# Edit .env file with new thresholds
nano .env

# Or use command line parameters
python run_detector.py --name-threshold 0.85 --schema-threshold 0.75
```

**✅ Verification:** Re-run detection and verify improved results

### Step 10: Production Usage

#### 10.1 Set Up Regular Detection
Create a cron job or scheduled task:
```bash
# Add to crontab for daily detection
0 2 * * * cd /path/to/datahubduplicatesdemo && ./run_detector.sh > detection.log 2>&1
```

#### 10.2 Set Up Monitoring
Monitor the detection results:
```bash
# Check detection logs
tail -f detection.log

# Check report generation
ls -la reports/ | tail -10
```

#### 10.3 Set Up Alerts
Configure alerts for:
- High number of duplicates found
- Detection failures
- New duplicate patterns

**✅ Verification:** Regular detection runs successfully and generates reports

## 🔧 Troubleshooting Common Issues

### Issue 1: No Assets Found
**Symptoms:** "No assets found in DataHub"
**Solutions:**
1. Check DataHub GMS URL and token
2. Verify entity types are correct
3. Check if assets exist in DataHub UI
4. Test with broader search query

### Issue 2: Connection Errors
**Symptoms:** "DataHub connection test failed"
**Solutions:**
1. Verify DATAHUB_GMS_TOKEN is correct
2. Check network connectivity
3. Ensure DataHub instance is accessible
4. Verify token has appropriate permissions

### Issue 3: High False Positive Rate
**Symptoms:** Too many similar but non-duplicate assets
**Solutions:**
1. Increase similarity thresholds
2. Add more suffixes/prefixes to ignore
3. Use more specific entity types
4. Enable case-sensitive matching

### Issue 4: Missing Obvious Duplicates
**Symptoms:** Known duplicates not detected
**Solutions:**
1. Decrease similarity thresholds
2. Check asset metadata quality
3. Use different detection types
4. Verify asset naming patterns

### Issue 5: Performance Issues
**Symptoms:** Slow detection or timeouts
**Solutions:**
1. Reduce number of entity types
2. Use smaller batch sizes
3. Filter by specific queries
4. Run detection during off-peak hours

## 📊 Success Criteria

You've successfully set up the duplicate detector when:
- [ ] Connection test passes
- [ ] Detection runs without errors
- [ ] Reports are generated successfully
- [ ] Findings make sense when verified in DataHub UI
- [ ] Configuration can be adjusted for your needs
- [ ] Regular detection can be scheduled

## 🎯 Best Practices

### Configuration
- Start with default thresholds and adjust based on results
- Use specific entity types for focused detection
- Regularly review and update ignored suffixes/prefixes
- Test configuration changes with dry runs

### Monitoring
- Set up regular detection schedules
- Monitor detection logs for errors
- Review findings regularly for quality
- Track duplicate trends over time

### Maintenance
- Update similarity thresholds based on findings
- Add new entity types as needed
- Clean up old reports periodically
- Document configuration changes

## 📞 Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review the detection logs for error messages
3. Test with different configuration parameters
4. Verify your DataHub setup and permissions
5. Check the README.md for additional information

## 🔄 Next Steps

After successful setup:
1. **Regular Detection**: Set up automated detection schedules
2. **Custom Rules**: Add organization-specific detection rules
3. **Integration**: Integrate with your data governance workflows
4. **Monitoring**: Set up alerts and monitoring for detection results
5. **Optimization**: Continuously improve detection accuracy based on results

The duplicate detector is now ready to help you identify and manage duplicate assets across your DataHub instance!
