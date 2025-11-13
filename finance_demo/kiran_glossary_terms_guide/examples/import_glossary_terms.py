#!/usr/bin/env python3
"""
Import Glossary Terms from YAML
=================================

This script imports glossary terms from glossary_terms.yaml into DataHub Cloud.
It creates glossary nodes (term groups) and glossary terms with proper relationships.

Usage:
    python import_glossary_terms.py

Requirements:
    - Set DATAHUB_PAT environment variable
    - Or update the server and token in the script
    - Install: pip install acryl-datahub[datahub-rest]
"""

import os
import yaml
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    GlossaryTermInfoClass,
    GlossaryNodeInfoClass,
    ChangeTypeClass,
)
from datahub.emitter.mcp import MetadataChangeProposalWrapper

# Configuration
SERVER = os.getenv("DATAHUB_GMS_SERVER", "https://your-instance.acryl.io/gms")
TOKEN = os.getenv("DATAHUB_PAT", "")

if not TOKEN:
    print("❌ ERROR: DATAHUB_PAT environment variable not set!")
    print("   Set it with: export DATAHUB_PAT=your_token")
    exit(1)

def create_glossary_node(emitter, node_id, name, description):
    """Create a glossary node (term group)"""
    node_urn = f"urn:li:glossaryNode:{node_id}"
    
    node_info = GlossaryNodeInfoClass(
        definition=description,
        name=name,
    )
    
    mcp = MetadataChangeProposalWrapper(
        entityType="glossaryNode",
        changeType=ChangeTypeClass.UPSERT,
        entityUrn=node_urn,
        aspect=node_info,
    )
    
    try:
        emitter.emit_mcp(mcp)
        print(f"   ✅ Created glossary node: {name}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create glossary node {name}: {e}")
        return False

def create_glossary_term(emitter, term_id, name, description, parent_node_urn=None):
    """Create a glossary term"""
    term_urn = f"urn:li:glossaryTerm:{term_id}"
    
    term_info = GlossaryTermInfoClass(
        definition=description,
        name=name,
        termSource="MANUAL",
    )
    
    # Add parent node if specified
    if parent_node_urn:
        term_info.parentNode = parent_node_urn
    
    mcp = MetadataChangeProposalWrapper(
        entityType="glossaryTerm",
        changeType=ChangeTypeClass.UPSERT,
        entityUrn=term_urn,
        aspect=term_info,
    )
    
    try:
        emitter.emit_mcp(mcp)
        print(f"      ✅ Created glossary term: {name}")
        return True
    except Exception as e:
        print(f"      ❌ Failed to create glossary term {name}: {e}")
        return False

def main():
    """Main function to import glossary from YAML"""
    print("=" * 60)
    print("📚 Importing Glossary Terms into DataHub")
    print("=" * 60)
    print(f"📡 Target: {SERVER}")
    print("")
    
    # Initialize emitter
    emitter = DatahubRestEmitter(SERVER, TOKEN)
    
    # Load YAML file (look in same directory as script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_file = os.path.join(script_dir, "glossary_terms.yaml")
    
    if not os.path.exists(yaml_file):
        print(f"❌ ERROR: YAML file not found: {yaml_file}")
        print(f"   Make sure glossary_terms.yaml is in the same directory as this script")
        exit(1)
    
    with open(yaml_file, 'r') as f:
        glossary_data = yaml.safe_load(f)
    
    total_nodes = 0
    total_terms = 0
    
    # Step 1: Create glossary nodes (term groups)
    print("📁 Step 1: Creating Glossary Nodes (Term Groups)...")
    print("")
    
    for node in glossary_data.get("glossary_nodes", []):
        node_id = node["id"]
        name = node["name"]
        description = node.get("description", "")
        
        if create_glossary_node(emitter, node_id, name, description):
            total_nodes += 1
    
    # Wait a bit for nodes to be created
    import time
    time.sleep(1)
    
    print("")
    print("📖 Step 2: Creating Glossary Terms...")
    print("")
    
    # Step 2: Create glossary terms
    for node in glossary_data.get("glossary_nodes", []):
        node_id = node["id"]
        node_name = node["name"]
        parent_node_urn = f"urn:li:glossaryNode:{node_id}"
        
        print(f"   Creating terms in '{node_name}' group:")
        
        for term in node.get("terms", []):
            term_id = term["id"]
            term_name = term["name"]
            term_description = term.get("description", "")
            
            # Build full description with additional details if available
            full_description = term_description
            
            if "formula" in term:
                full_description += f"\n\nFormula: {term['formula']}"
            
            if "calculation" in term:
                full_description += f"\n\nCalculation: {term['calculation']}"
            
            if "examples" in term:
                examples_text = "\n".join([f"  - {ex}" for ex in term["examples"]])
                full_description += f"\n\nExamples:\n{examples_text}"
            
            if "data_type" in term:
                full_description += f"\n\nData Type: {term['data_type']}"
            
            if create_glossary_term(emitter, term_id, term_name, full_description, parent_node_urn):
                total_terms += 1
    
    print("")
    print("=" * 60)
    print("✅ SUCCESS: Glossary Terms Imported!")
    print("=" * 60)
    print(f"   📁 Created {total_nodes} glossary nodes (term groups)")
    print(f"   📖 Created {total_terms} glossary terms")
    print("")
    print("💡 Next Steps:")
    print("   1. Verify terms in DataHub UI: Glossary section")
    print("   2. Add meta properties to your dbt models (see README.md)")
    print("   3. Configure meta mappings in your ingestion recipe")
    print("   4. Run dbt ingestion to automatically apply terms to models")
    print("")

if __name__ == "__main__":
    main()

