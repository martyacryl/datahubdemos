# DataHub Duplicate Detector - Quick Reference

## 🚀 Quick Start Commands

### Setup
```bash
cd datahubduplicatesdemo
cp env.example .env
# Edit .env with your credentials
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### Test & Run
```bash
python test_connection.py                    # Test connection
python run_detector.py                      # Basic detection
./run_detector.sh                          # One-click runner
```

## ⚡ Common Commands

### Basic Detection
```bash
python run_detector.py                                    # All entity types, all detection types
python run_detector.py --entity-types dataset            # Only datasets
python run_detector.py --detection-types name            # Only name-based detection
```

### Advanced Detection
```bash
python run_detector.py --name-threshold 0.9              # Higher name similarity
python run_detector.py --schema-threshold 0.8            # Higher schema similarity
python run_detector.py --min-assets 3                    # Require 3+ assets for duplicate
```

### Output Options
```bash
python run_detector.py --format json                     # JSON only
python run_detector.py --output-dir ./my_reports         # Custom output directory
python run_detector.py --dry-run                         # No reports generated
python run_detector.py --verbose                         # Detailed logging
```

## 🔍 Detection Types

| Type | Description | Best For |
|------|-------------|----------|
| `name` | Similar asset names | Tables, charts, dashboards |
| `schema` | Similar field structures | Datasets only |
| `description` | Similar descriptions | Any asset type |

## ⚙️ Configuration

### Environment Variables (.env)
```bash
DATAHUB_GMS_URL=https://your-instance.acryl.io/gms
DATAHUB_GMS_TOKEN=your_token_here
ENTITY_TYPES=dataset,chart,dashboard
DETECTION_TYPES=name,schema,description
NAME_SIMILARITY_THRESHOLD=0.8
SCHEMA_SIMILARITY_THRESHOLD=0.7
MIN_ASSETS_FOR_DUPLICATE=2
```

### Command Line Overrides
```bash
--entity-types dataset,chart
--detection-types name,schema
--name-threshold 0.9
--schema-threshold 0.8
--min-assets 3
```

## 📊 Output Files

| File | Format | Description |
|------|--------|-------------|
| `duplicate_report_*.md` | Markdown | Human-readable report |
| `duplicate_findings_*.json` | JSON | Machine-readable data |

## 🎯 Common Scenarios

### Find Duplicate Tables
```bash
python run_detector.py --entity-types dataset --detection-types name,schema
```

### Find Duplicate Dashboards
```bash
python run_detector.py --entity-types dashboard --detection-types name,description
```

### High Precision Detection
```bash
python run_detector.py --name-threshold 0.95 --schema-threshold 0.9 --min-assets 2
```

### Broad Detection
```bash
python run_detector.py --name-threshold 0.7 --schema-threshold 0.6 --min-assets 2
```

## 🔧 Troubleshooting

### No Assets Found
```bash
python test_connection.py  # Check connection
```

### Too Many False Positives
```bash
python run_detector.py --name-threshold 0.9 --schema-threshold 0.8
```

### Missing Obvious Duplicates
```bash
python run_detector.py --name-threshold 0.7 --schema-threshold 0.6
```

### Performance Issues
```bash
python run_detector.py --entity-types dataset --detection-types name
```

## 📈 Verification Steps

1. **Test Connection**: `python test_connection.py`
2. **Run Detection**: `python run_detector.py`
3. **Check Reports**: `ls -la reports/`
4. **Verify in UI**: Search for assets by URN in DataHub
5. **Adjust Config**: Modify thresholds based on results

## 🐳 Docker Usage

```bash
docker-compose up --build
```

## 📝 Success Indicators

✅ Connection test passes  
✅ Detection runs without errors  
✅ Reports generated successfully  
✅ Findings make sense in DataHub UI  
✅ Configuration can be adjusted  
