import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class DataHubConfig:
    server: str = "http://localhost:8080"
    token: Optional[str] = None
    gms_url: Optional[str] = None

@dataclass
class GeneratorConfig:
    output_file: str = "generated_metadata.json"
    include_finance: bool = True
    include_engineering: bool = True
    include_data_science: bool = True
    num_tables_per_domain: int = 5
    num_dashboards_per_domain: int = 3
    include_lineage: bool = True

class Config:
    def __init__(self):
        self.datahub = DataHubConfig()
        self.generator = GeneratorConfig()
    
    def print_config(self):
        print("🔧 Configuration loaded successfully!")
