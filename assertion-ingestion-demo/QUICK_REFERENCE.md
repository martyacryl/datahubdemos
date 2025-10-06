# DataHub External Assertion Ingestion - Quick Reference

## 🚀 Quick Start Commands

### 1. Setup
```bash
# Copy environment template
cp env.example .env

# Edit configuration
nano .env  # or your preferred editor

# Run the ingestion
./run_ingestion.sh
```

### 2. Test Connection
```bash
python test_datahub_connection.py
```

### 3. Run Specific Sources
```bash
# Glue only
python ingest_all_assertions.py --glue-only

# Snowflake only
python ingest_all_assertions.py --snowflake-only

# Dry run (no actual ingestion)
python ingest_all_assertions.py --dry-run
```

## 🔧 Configuration Quick Reference

### Required Environment Variables
```bash
DATAHUB_GMS_URL=https://your-account-id.acryl.io/gms
DATAHUB_GMS_TOKEN=your_pat_token_here
```

### Optional: AWS Glue
```bash
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-west-2
GLUE_DATABASE_NAME=your_glue_database
```

### Optional: Snowflake
```bash
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
```

## 📊 Common Use Cases

### 1. Ingest All Available Assertions
```bash
./run_ingestion.sh
```

### 2. Test with Dry Run
```bash
python ingest_all_assertions.py --dry-run --verbose
```

### 3. Ingest Only Glue Assertions
```bash
python ingest_all_assertions.py --glue-only
```

### 4. Ingest Only Snowflake Assertions
```bash
python ingest_all_assertions.py --snowflake-only
```

### 5. Custom Configuration
```bash
python ingest_all_assertions.py --glue-database my_glue_db --snowflake-database my_snowflake_db
```

## 🔍 Verification Commands

### Check DataHub Connection
```bash
python test_datahub_connection.py
```

### View Ingestion Reports
```bash
ls -la reports/
cat reports/ingestion_report_*.json
```

### Check Logs
```bash
tail -f logs/assertion_ingestion.log
```

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify your PAT token is correct
   - Check DataHub GMS URL format: `https://account-id.acryl.io/gms`

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Permission Errors**
   - Ensure your PAT has assertion creation permissions
   - Check AWS/Snowflake credentials

4. **Connection Timeout**
   - Verify network connectivity
   - Check DataHub GMS URL accessibility

### Debug Mode
```bash
python ingest_all_assertions.py --verbose --debug
```

## 📁 File Structure
```
assertion-ingestion-demo/
├── datahub_assertion_ingester.py    # Main DataHub integration
├── glue_assertion_extractor.py      # AWS Glue extractor
├── snowflake_assertion_extractor.py # Snowflake extractor
├── ingest_all_assertions.py         # Main orchestration script
├── test_datahub_connection.py       # Connection test
├── run_ingestion.sh                 # Easy run script
├── requirements.txt                 # Python dependencies
├── env.example                      # Environment template
├── docker-compose.yml               # Docker setup (optional)
├── README.md                        # Full documentation
├── USER_GUIDE.md                    # Detailed user guide
└── QUICK_REFERENCE.md               # This file
```

## 🎯 Next Steps

1. **Configure your environment** - Edit `.env` with your credentials
2. **Test connection** - Run `python test_datahub_connection.py`
3. **Run ingestion** - Execute `./run_ingestion.sh`
4. **Verify results** - Check DataHub UI for new assertions
5. **Schedule automation** - Set up cron job or CI/CD pipeline

## 📞 Support

- Check the full [USER_GUIDE.md](USER_GUIDE.md) for detailed instructions
- Review [README.md](README.md) for project overview
- Check logs in `logs/` directory for detailed error information