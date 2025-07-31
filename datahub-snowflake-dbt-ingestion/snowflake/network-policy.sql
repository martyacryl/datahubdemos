-- ==============================================
-- NETWORK POLICY CONFIGURATION
-- ==============================================
-- Execute if your Snowflake account has network policies restricting IP access

-- Check existing network policies
SHOW NETWORK POLICIES;

-- Option 1: Modify existing network policy to include DataHub IP
-- Replace 'YOUR_EXISTING_POLICY' with your actual policy name
-- Replace 'YOUR_DATAHUB_IP' with your DataHub server's public IP address

-- ALTER NETWORK POLICY YOUR_EXISTING_POLICY SET ALLOWED_IP_LIST = (
--     '192.168.1.100',        -- existing allowed IPs
--     '203.0.113.50',         -- existing allowed IPs  
--     'YOUR_DATAHUB_IP'       -- DataHub server IP
-- );

-- Option 2: Create dedicated DataHub network policy
-- CREATE NETWORK POLICY DATAHUB_ACCESS_POLICY
--     ALLOWED_IP_LIST = ('YOUR_DATAHUB_IP');

-- Option 3: Apply network policy to DataHub user specifically
-- ALTER USER DATAHUB_USER SET NETWORK_POLICY = 'DATAHUB_ACCESS_POLICY';

-- Option 4: Create policy allowing a subnet/range
-- CREATE NETWORK POLICY DATAHUB_SUBNET_POLICY
--     ALLOWED_IP_LIST = ('203.0.113.0/24');  -- Allow entire subnet

/*
==============================================
FIND YOUR PUBLIC IP
==============================================
To find your DataHub server's public IP address:

1. From the DataHub server, run:
   curl ifconfig.me

2. Or check "What's my IP" from the server's browser

3. For cloud deployments:
   - AWS: Check EC2 instance public IP or NAT Gateway IP
   - GCP: Check Compute Engine external IP
   - Azure: Check VM public IP address

4. Add this IP to the network policy using the commands above
==============================================
*/
