#!/usr/bin/env python3
import os
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_snowflake_connection():
    try:
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA', 'INFORMATION_SCHEMA')
        )
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        result = cursor.fetchone()
        
        print(f"✅ Snowflake connection successful!")
        print(f"✅ Found {result[0]} base tables in INFORMATION_SCHEMA")
        
        # Test retention data query
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' 
            AND RETENTION_TIME IS NOT NULL
        """)
        retention_count = cursor.fetchone()
        print(f"✅ Found {retention_count[0]} tables with retention data")
        
        # Show sample retention data
        cursor.execute("""
            SELECT TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, RETENTION_TIME
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' 
            AND RETENTION_TIME IS NOT NULL
            LIMIT 3
        """)
        sample_data = cursor.fetchall()
        
        if sample_data:
            print(f"✅ Sample retention data:")
            for row in sample_data:
                print(f"   {row[0]}.{row[1]}.{row[2]} -> {row[3]} days")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Snowflake connection failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    test_snowflake_connection()
