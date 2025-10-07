#!/usr/bin/env python3
"""
Add New DMF - Helper script to add new Data Metric Functions
This script helps you add new DMFs to your monitoring setup
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_header():
    """Print script header."""
    print("=" * 70)
    print("➕ Add New DMF - Helper Script")
    print("=" * 70)
    print("This script helps you add new Data Metric Functions to your monitoring")
    print("=" * 70)

def get_dmf_templates():
    """Get common DMF templates."""
    return {
        'INVALID_EMAIL_COUNT': {
            'description': 'Count of invalid email addresses',
            'threshold': 0,
            'sql_template': "SELECT COUNT(*) FROM {table} WHERE {column} NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{{2,}}$'"
        },
        'NULL_COUNT': {
            'description': 'Count of null values',
            'threshold': 0,
            'sql_template': "SELECT COUNT(*) FROM {table} WHERE {column} IS NULL"
        },
        'COMPLETENESS': {
            'description': 'Percentage of non-null values',
            'threshold': 0.95,
            'sql_template': "SELECT (COUNT(*) - COUNT({column})) / COUNT(*) FROM {table}"
        },
        'FRESHNESS': {
            'description': 'Hours since last update',
            'threshold': 24,
            'sql_template': "SELECT DATEDIFF('hour', MAX({column}), CURRENT_TIMESTAMP()) FROM {table}"
        },
        'UNIQUENESS': {
            'description': 'Count of duplicate values',
            'threshold': 0,
            'sql_template': "SELECT COUNT(*) - COUNT(DISTINCT {column}) FROM {table}"
        },
        'VALIDITY': {
            'description': 'Count of invalid values',
            'threshold': 0,
            'sql_template': "SELECT COUNT(*) FROM {table} WHERE {column} IS NOT NULL AND {column} = ''"
        }
    }

def generate_snowflake_sql(dmf_type, table_name, column_name, database=None, schema=None):
    """Generate Snowflake SQL to add DMF."""
    database = database or os.getenv('SNOWFLAKE_DATABASE', 'DMF_DEMO_DB')
    schema = schema or os.getenv('SNOWFLAKE_SCHEMA', 'DEMO_SCHEMA')
    
    # Map DMF types to Snowflake functions
    snowflake_functions = {
        'INVALID_EMAIL_COUNT': 'SNOWFLAKE.CORE.INVALID_EMAIL_COUNT',
        'NULL_COUNT': 'SNOWFLAKE.CORE.NULL_COUNT',
        'COMPLETENESS': 'SNOWFLAKE.CORE.COMPLETENESS',
        'FRESHNESS': 'SNOWFLAKE.CORE.FRESHNESS',
        'UNIQUENESS': 'SNOWFLAKE.CORE.UNIQUENESS',
        'VALIDITY': 'SNOWFLAKE.CORE.VALIDITY'
    }
    
    function_name = snowflake_functions.get(dmf_type, 'SNOWFLAKE.CORE.NULL_COUNT')
    
    sql = f"""
-- Add {dmf_type} DMF to {table_name}.{column_name}
ALTER TABLE {database}.{schema}.{table_name}
    ADD DATA METRIC FUNCTION {function_name} ON ({column_name});
"""
    return sql.strip()

def generate_python_code(dmf_type, table_name, column_name):
    """Generate Python code to add to the monitor script."""
    templates = get_dmf_templates()
    template = templates.get(dmf_type, templates['NULL_COUNT'])
    
    python_code = f"""
# Add to get_threshold_for_metric() function:
'{dmf_type}': {template['threshold']},

# Add to get_sql_logic_for_metric() function:
'{dmf_type}': f"{template['sql_template'].format(table='{{table_ref}}', column='{{column}}')}",
"""
    return python_code.strip()

def main():
    """Main function to help add new DMFs."""
    print_header()
    
    print("\n📋 Available DMF Types:")
    templates = get_dmf_templates()
    for i, (dmf_type, info) in enumerate(templates.items(), 1):
        print(f"{i}. {dmf_type}: {info['description']}")
    
    print("\n🔧 Configuration:")
    database = os.getenv('SNOWFLAKE_DATABASE', 'DMF_DEMO_DB')
    schema = os.getenv('SNOWFLAKE_SCHEMA', 'DEMO_SCHEMA')
    print(f"   Database: {database}")
    print(f"   Schema: {schema}")
    
    print("\n📝 To add a new DMF:")
    print("1. Choose a DMF type from the list above")
    print("2. Run the generated Snowflake SQL")
    print("3. Add the generated Python code to simple_automated_monitor.py")
    print("4. Test with: python simple_automated_monitor.py")
    
    print("\n" + "=" * 70)
    print("🎯 Example: Adding INVALID_EMAIL_COUNT to CUSTOMERS.EMAIL")
    print("=" * 70)
    
    # Example
    dmf_type = 'INVALID_EMAIL_COUNT'
    table_name = 'CUSTOMERS'
    column_name = 'EMAIL'
    
    print(f"\n1️⃣ Snowflake SQL:")
    snowflake_sql = generate_snowflake_sql(dmf_type, table_name, column_name, database, schema)
    print(snowflake_sql)
    
    print(f"\n2️⃣ Python Code to add to simple_automated_monitor.py:")
    python_code = generate_python_code(dmf_type, table_name, column_name)
    print(python_code)
    
    print(f"\n3️⃣ Test the new DMF:")
    print("python simple_automated_monitor.py")
    
    print(f"\n4️⃣ Verify in DataHub:")
    print("Check the Assertions tab for the new DMF assertion")
    
    print("\n" + "=" * 70)
    print("💡 Tips:")
    print("- Test in development first")
    print("- Check Snowflake documentation for available DMF functions")
    print("- Verify thresholds make sense for your data")
    print("- Monitor logs after adding new DMFs")
    print("=" * 70)

if __name__ == "__main__":
    main()
