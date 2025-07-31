# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### Python Version Error
```
Error: Python version not compatible
```
**Solution:**
- Install Python 3.9 or higher
- Create virtual environment: `python3 -m venv venv`
- Activate environment: `source venv/bin/activate`

#### DataHub CLI Installation Failed
```
Error: Failed building wheel for acryl-datahub
```
**Solution:**
```bash
# Upgrade pip and install build tools
pip install --upgrade pip wheel setuptools

# Install with specific flags
pip install --upgrade 'acryl-datahub[snowflake,dbt]' --no-cache-dir
```

### Connection Issues

#### Snowflake Connection Failed
```
Error: 250001: Could not connect to Snowflake backend
```
**Solutions:**
1. **Check credentials:** Verify username, password, account ID
2. **Check account format:** Use format like `xy12345.us-east-1`
3. **Network policy:** Add DataHub IP to Snowflake network policy
4. **Test connection manually:**
   ```bash
   snowsql -a your-account -u your-username -d your-database
   ```

#### DataHub Server Not Accessible
```
Error: Connection refused to localhost:8080
```
**Solutions:**
1. **Start DataHub:** `./docker/quickstart.sh`
2. **Check port:** Ensure port 8080 is not blocked
3. **Check Docker:** `docker ps` to see running containers
4. **Check logs:** `docker logs datahub-gms-1`

### Permission Issues

#### Insufficient Privileges in Snowflake
```
Error: SQL execution failed: Insufficient privileges
```
**Solutions:**
1. **Run permission script:** Execute `snowflake/setup-permissions.sql`
2. **Check role grants:** `SHOW GRANTS TO ROLE DATAHUB_ROLE;`
3. **Verify user role:** `DESCRIBE USER DATAHUB_USER;`
4. **Test as DataHub user:**
   ```sql
   USE ROLE DATAHUB_ROLE;
   SHOW DATABASES;
   ```

#### Network Policy Restrictions
```
Error: IP address not allowed
```
**Solutions:**
1. **Find your IP:** `curl ifconfig.me`
2. **Update network policy:** See `snowflake/network-policy.sql`
3. **Test connectivity:** `telnet your-account.snowflakecomputing.com 443`

### dbt Issues

#### dbt Artifacts Not Found
```
Error: manifest.json not found
```
**Solutions:**
1. **Generate artifacts:**
   ```bash
   cd /path/to/dbt/project
   dbt compile
   dbt docs generate
   ```
2. **Check path:** Verify `DBT_PROJECT_ROOT` in `.env` file
3. **Check permissions:** Ensure read access to target directory

#### dbt Platform Mismatch
```
Error: Platform mismatch between dbt and warehouse
```
**Solutions:**
1. **Check target_platform:** Must be "snowflake"
2. **Verify dbt profile:** Ensure dbt connects to Snowflake
3. **Check platform_instance:** Should match between configs

## Debug Commands

### Verbose Logging
```bash
# Enable debug logging
datahub ingest -c config.yml --debug

# Save logs to file
datahub ingest -c config.yml --debug 2>&1 | tee ingestion.log
```

### Dry Run Testing
```bash
# Test configuration without ingesting
datahub ingest -c config.yml --dry-run

# Preview what will be ingested
datahub ingest -c config.yml --preview
```

### Connection Testing
```bash
# Test DataHub connectivity
datahub check localhost:8080

# Test Snowflake connection (with snowsql)
snowsql -a $SNOWFLAKE_ACCOUNT -u $SNOWFLAKE_USERNAME
```
