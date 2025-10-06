#!/usr/bin/env python3
"""
Create Sample DMFs in Snowflake
This script creates sample tables and DMFs for customers who don't have any.
"""

import os
import logging
from dotenv import load_dotenv
import snowflake.connector

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_dmfs():
    """Create sample tables and DMFs in Snowflake."""
    
    # Get Snowflake configuration
    account = os.getenv('SNOWFLAKE_ACCOUNT')
    user = os.getenv('SNOWFLAKE_USER')
    password = os.getenv('SNOWFLAKE_PASSWORD')
    warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
    database = os.getenv('SNOWFLAKE_DATABASE', 'DEMO_DB')
    schema = os.getenv('SNOWFLAKE_SCHEMA', 'DEMO_SCHEMA')
    
    if not all([account, user, password, warehouse]):
        logger.error("❌ Missing required Snowflake credentials in .env file")
        return False
    
    try:
        # Connect to Snowflake
        logger.info("🔌 Connecting to Snowflake...")
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema
        )
        cursor = conn.cursor()
        
        logger.info(f"✅ Connected to Snowflake: {database}.{schema}")
        
        # Create demo database and schema if they don't exist
        logger.info("📁 Creating demo database and schema...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        cursor.execute(f"USE DATABASE {database}")
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        cursor.execute(f"USE SCHEMA {schema}")
        
        # Create sample customers table
        logger.info("📊 Creating sample CUSTOMERS table...")
        cursor.execute("""
            CREATE OR REPLACE TABLE CUSTOMERS (
                CUSTOMER_ID NUMBER PRIMARY KEY,
                FIRST_NAME VARCHAR(50),
                LAST_NAME VARCHAR(50),
                EMAIL VARCHAR(100),
                PHONE VARCHAR(20),
                CREATED_DATE DATE,
                STATUS VARCHAR(20)
            )
        """)
        
        # Insert sample data with some intentional nulls for testing
        logger.info("📝 Inserting sample data...")
        cursor.execute("""
            INSERT INTO CUSTOMERS VALUES
            (1, 'John', 'Doe', 'john.doe@email.com', '555-0101', '2024-01-15', 'ACTIVE'),
            (2, 'Jane', 'Smith', 'jane.smith@email.com', '555-0102', '2024-01-16', 'ACTIVE'),
            (3, 'Bob', 'Johnson', NULL, '555-0103', '2024-01-17', 'ACTIVE'),
            (4, 'Alice', 'Brown', 'alice.brown@email.com', NULL, '2024-01-18', 'ACTIVE'),
            (5, 'Charlie', 'Wilson', 'charlie.wilson@email.com', '555-0105', '2024-01-19', 'INACTIVE'),
            (6, 'Diana', 'Davis', NULL, '555-0106', '2024-01-20', 'ACTIVE'),
            (7, 'Eve', 'Miller', 'eve.miller@email.com', '555-0107', '2024-01-21', 'ACTIVE'),
            (8, 'Frank', 'Garcia', 'frank.garcia@email.com', '555-0108', '2024-01-22', 'ACTIVE'),
            (9, 'Grace', 'Martinez', NULL, '555-0109', '2024-01-23', 'ACTIVE'),
            (10, 'Henry', 'Anderson', 'henry.anderson@email.com', '555-0110', '2024-01-24', 'ACTIVE')
        """)
        
        # Create DMFs
        logger.info("🔧 Creating Data Metric Functions (DMFs)...")
        
        # DMF 1: Monitor null values in EMAIL column
        cursor.execute("""
            ALTER TABLE CUSTOMERS
                MODIFY DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (EMAIL)
                ADD EXPECTATION email_null_check CHECK (VALUE <= 2)
        """)
        logger.info("   ✅ Created DMF: email_null_check (NULL_COUNT on EMAIL)")
        
        # DMF 2: Monitor data freshness
        cursor.execute("""
            ALTER TABLE CUSTOMERS
                MODIFY DATA METRIC FUNCTION SNOWFLAKE.CORE.FRESHNESS ON (CREATED_DATE)
                ADD EXPECTATION data_freshness_check CHECK (VALUE <= 7)
        """)
        logger.info("   ✅ Created DMF: data_freshness_check (FRESHNESS on CREATED_DATE)")
        
        # DMF 3: Monitor data volume
        cursor.execute("""
            ALTER TABLE CUSTOMERS
                MODIFY DATA METRIC FUNCTION SNOWFLAKE.CORE.VOLUME ON (CUSTOMER_ID)
                ADD EXPECTATION data_volume_check CHECK (VALUE >= 5)
        """)
        logger.info("   ✅ Created DMF: data_volume_check (VOLUME on CUSTOMER_ID)")
        
        # Verify the DMFs were created
        logger.info("🔍 Verifying DMFs...")
        cursor.execute("""
            SELECT 
                TABLE_NAME,
                COLUMN_NAME,
                METRIC_FUNCTION_NAME,
                EXPECTATION_NAME,
                EXPECTATION_EXPRESSION
            FROM SNOWFLAKE.LOCAL.DATA_QUALITY_MONITORING_RESULTS_RAW
            WHERE TABLE_NAME = 'CUSTOMERS'
            AND EXPECTATION_NAME IS NOT NULL
            ORDER BY CREATED_ON DESC
        """)
        
        dmf_results = cursor.fetchall()
        logger.info(f"✅ Found {len(dmf_results)} DMFs in Snowflake:")
        
        for row in dmf_results:
            logger.info(f"   • {row[2]} on {row[1]} - {row[3]}: {row[4]}")
        
        # Test the DMFs
        logger.info("🧪 Testing DMF evaluations...")
        cursor.execute("""
            SELECT *
            FROM TABLE(SYSTEM$EVALUATE_DATA_QUALITY_EXPECTATIONS(
                REF_ENTITY_NAME => 'DEMO_DB.DEMO_SCHEMA.CUSTOMERS'))
        """)
        
        evaluation_results = cursor.fetchall()
        logger.info(f"✅ DMF evaluation results: {len(evaluation_results)} expectations evaluated")
        
        cursor.close()
        conn.close()
        
        logger.info("🎉 Sample DMFs created successfully!")
        logger.info("📊 Created:")
        logger.info("   • CUSTOMERS table with sample data")
        logger.info("   • 3 Data Metric Functions (DMFs)")
        logger.info("   • Data quality expectations")
        logger.info("")
        logger.info("🚀 You can now run the demo:")
        logger.info("   ./run_quick_demo.sh")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating sample DMFs: {str(e)}")
        return False

def main():
    """Main function."""
    print("🏔️  Creating Sample DMFs in Snowflake")
    print("=====================================")
    print("This script will create sample tables and DMFs for testing.")
    print("")
    
    if create_sample_dmfs():
        print("\n✅ Sample DMFs created successfully!")
        print("You can now run the demo with: ./run_quick_demo.sh")
        return 0
    else:
        print("\n❌ Failed to create sample DMFs.")
        print("Please check your Snowflake credentials and try again.")
        return 1

if __name__ == "__main__":
    exit(main())
