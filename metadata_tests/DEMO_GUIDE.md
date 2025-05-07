# DataHub Metadata Testing Demo Guide

This guide will walk you through running the DataHub Metadata Testing Demo step by step.

## Directory Structure

```
datahub-metadata-test-demo/
├── README.md                         # Overview documentation
├── DEMO_GUIDE.md                     # This guide
├── requirements.txt                  # Python dependencies
├── run_demo.py                       # Main demo script
└── test_configs/                     # Test configuration templates
    ├── schema_completeness_test.json # Schema test config
    ├── ownership_test.json           # Ownership test config
    └── freshness_test.json           # Freshness test config
```

## Setup Instructions

1. **Create the Directory Structure**

   You can use the provided `setup.sh` script to create the directory structure:

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   Or manually create the structure:

   ```bash
   mkdir -p datahub-metadata-test-demo/test_configs
   ```

2. **Install Dependencies**

   ```bash
   cd datahub-metadata-test-demo
   pip install -r requirements.txt
   ```

3. **Set Environment Variables**

   ```bash
   export DATAHUB_GMS_URL=https://test-environment.acryl.io  # Your DataHub URL
   export DATAHUB_TOKEN=your_personal_access_token
   ```

## Running the Demo

1. **Run the Demo Script**

   ```bash
   python run_demo.py
   ```

   This will:
   - Search for datasets in your DataHub instance
   - Create metadata tests on those datasets
   - Run the tests and display the results

2. **Customizing the Demo**

   You can customize the demo with these command-line arguments:

   ```bash
   # Test specific datasets matching a query
   python run_demo.py --query "sales"

   # Limit the number of datasets to test
   python run_demo.py --limit 5

   # Specify DataHub URL and token explicitly
   python run_demo.py --server https://your-datahub-url --token your_token
   ```

## What to Expect

1. **Dataset Discovery**:
   - The script will search for datasets in your DataHub instance
   - It will display a table of found datasets

2. **Test Creation**:
   - For each dataset, the script will create three metadata tests:
   - Schema Completeness Test (checks field descriptions)
   - Ownership Test (checks if datasets have owners)
   - Freshness Test (checks how recently data was updated)

3. **Test Execution**:
   - The script will run each test and display the results in real-time
   - You'll see which tests pass and which fail

4. **Summary Results**:
   - At the end, you'll see a summary table of all test results
   - The script will save detailed results to a JSON file

## Expected Outcomes

The demo will show you:

1. **Passing Tests**: Datasets that have complete metadata (descriptions, owners, recent updates)
2. **Failing Tests**: Datasets with metadata issues that need attention
3. **Test Metrics**: The overall health of your metadata

## Troubleshooting

If you encounter any issues:

- **API Errors**: Check that your DataHub token is valid and has permissions
- **No Datasets Found**: Try adjusting your search query or check your DataHub instance
- **Tests Not Running**: Ensure your DataHub version supports the assertion API (requires 0.10.0+)

## Next Steps

After running the demo, you can:

1. Fix metadata issues identified by the tests
2. Create additional test configurations for other metadata aspects
3. Schedule regular test runs to monitor metadata quality
4. Integrate with your data quality workflows

## Demo Video

For a visual guide on how to run the demo and what to expect, check out our demo video (not included with this package).