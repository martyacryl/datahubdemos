#!/usr/bin/env python3
"""
Generate complete setup_complete.sql with:
- 35 issuers (instead of 10)
- 75 bonds (instead of 10)
- 400-500 transactions (instead of 30)
- Opaque codes: E/T/1/0/Y/N for tax-exempt flags
- Opaque segment codes: 001/002/E/T/X
"""

import random

# States and regions
states = {
    'CA': 'W', 'NY': 'NE', 'TX': 'S', 'FL': 'S', 'IL': 'MW',
    'MA': 'NE', 'GA': 'S', 'NC': 'S', 'VA': 'S', 'MI': 'MW',
    'PA': 'NE', 'OH': 'MW', 'NJ': 'NE', 'CT': 'NE', 'WA': 'W',
    'AZ': 'W', 'CO': 'W', 'OR': 'W', 'TN': 'S', 'MD': 'NE',
    'IN': 'MW', 'WI': 'MW', 'MN': 'MW', 'MO': 'MW', 'SC': 'S',
    'AL': 'S', 'LA': 'S', 'KY': 'S', 'NV': 'W', 'UT': 'W'
}

# Opaque codes: E,1,Y = exempt; T,0,N = taxable
exempt_codes = ['E', '1', 'Y']
taxable_codes = ['T', '0', 'N']
all_codes = exempt_codes + taxable_codes

# Read the existing file structure
with open('setup_complete.sql', 'r') as f:
    content = f.read()

# Split into sections
parts = content.split('-- Insert Issuer Dimension Data (Bronze)')
if len(parts) < 2:
    print("Error: Could not find issuer section")
    exit(1)

header = parts[0]
rest = parts[1]

# Generate 35 issuers
issuer_sql = "INSERT INTO BRZ_001.ISS_5510 (ISS_ID, ISS_NAME, ISS_TYPE, STATE_CD, MUN_NAME, RAW_INFO)\n"
state_list = list(states.keys())
for i in range(1, 36):
    state = random.choice(state_list)
    code = random.choice(all_codes)
    issuer_sql += f"SELECT 'ISS{i:03d}', 'Issuer {i} {state}', '{code}', '{state}', 'State/City {i}', PARSE_JSON('{{\"type\": \"issuer\", \"code\": \"{code}\"}}')\n"
    if i < 35:
        issuer_sql += "UNION ALL\n"
issuer_sql += ";\n\n"

# Find bond section
bond_parts = rest.split('-- Insert Bond Reference Data (Bronze)')
if len(bond_parts) < 2:
    print("Error: Could not find bond section")
    exit(1)

# Generate 75 bonds
bond_sql = "INSERT INTO BRZ_001.REF_7832 (BND_ID, CUSIP, ISIN, MAT_DATE, CPN_RATE, CR_RT, ISS_TYPE, RAW_DESC)\n"
for i in range(1, 76):
    issuer_type = random.choice(all_codes)
    cusip = f"{123456780 + i:09d}"
    isin = f"US{123456780 + i:012d}"
    years = random.choice([3, 5, 7, 10, 12, 15, 20])
    coupon = round(random.uniform(2.0, 4.5), 3)
    rating = random.choice(['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-'])
    bond_sql += f"SELECT 'BND{i:03d}', '{cusip}', '{isin}', DATEADD(year, {years}, CURRENT_DATE()), {coupon:.3f}, '{rating}', '{issuer_type}', PARSE_JSON('{{\"desc\": \"{years}-year bond\", \"code\": \"{issuer_type}\"}}')\n"
    if i < 75:
        bond_sql += "UNION ALL\n"
bond_sql += ";\n\n"

# Find transaction section
txn_parts = bond_parts[1].split('-- Insert Transaction Data (Bronze)')
if len(txn_parts) < 2:
    print("Error: Could not find transaction section")
    exit(1)

# Generate 400 transactions
txn_sql = "INSERT INTO BRZ_001.TX_0421 (TX_ID, TD_DATE, STL_DATE, PRN_AMT, ISS_ID, BND_ID, TRD_TYPE, CUSIP, RAW_DATA)\n"
trade_types = ['B', 'S', '1', '2']  # B/1 = Buy, S/2 = Sell
for i in range(1, 401):
    days_ago = random.randint(1, 60)
    issuer_num = random.randint(1, 35)
    bond_num = random.randint(1, 75)
    trade_type = random.choice(trade_types)
    amount = round(random.uniform(500000, 5000000), 2)
    cusip = f"{123456780 + bond_num:09d}"
    txn_sql += f"SELECT 'TX{i:03d}', DATEADD(day, -{days_ago}, CURRENT_DATE()), DATEADD(day, -{days_ago - 2}, CURRENT_DATE()), {amount:.2f}, 'ISS{issuer_num:03d}', 'BND{bond_num:03d}', '{trade_type}', '{cusip}', PARSE_JSON('{{\"trade_id\": \"T{i:03d}\", \"code\": \"{trade_type}\"}}')\n"
    if i < 400:
        txn_sql += "UNION ALL\n"
txn_sql += ";\n\n"

# Find dynamic tables section
dt_parts = txn_parts[1].split('-- ============================================================================\n-- STEP 6: CREATE DYNAMIC TABLES')
if len(dt_parts) < 2:
    print("Error: Could not find dynamic tables section")
    exit(1)

# Reconstruct file
new_content = header + "-- Insert Issuer Dimension Data (Bronze) - 35 issuers with opaque codes\n" + issuer_sql + "-- Insert Bond Reference Data (Bronze) - 75 bonds with opaque codes\n" + bond_sql + "-- Insert Transaction Data (Bronze) - 400 transactions with opaque codes\n" + txn_sql + "-- ============================================================================\n-- STEP 6: CREATE DYNAMIC TABLES" + dt_parts[1]

# Write the updated file
with open('setup_complete.sql', 'w') as f:
    f.write(new_content)

print("Generated setup_complete.sql with 35 issuers, 75 bonds, 400 transactions")
