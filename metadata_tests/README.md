# DataHub Metadata Testing Demo

A simple demonstration of how to create and run metadata tests (assertions) in DataHub.

## Overview

This demo shows how to:
1. Create metadata tests on datasets in DataHub
2. Run those tests to validate metadata quality
3. View the test results

## Prerequisites

- Access to a DataHub instance (cloud or self-hosted)
- DataHub Personal Access Token (PAT)
- Python 3.8+

## Setup

1. Install dependencies:
pip install -r requirements.txt
2. Set up your environment variables:
export DATAHUB_GMS_URL=<your-datahub-gms-url>
export DATAHUB_TOKEN=<your-datahub-pat>

## Running the Demo

To run the complete demo:

```bash
python run_demo.py
This will:

Search for datasets in your DataHub instance
Create metadata tests on those datasets
Run the tests and show the results


4. Save the file:
   - If you're using nano, press `Ctrl+O` to write the file, then `Enter` to confirm, then `Ctrl+X` to exit
   - If you're using another editor, save using that editor's save command

5. Verify the file was created correctly:
   ```bash
   cat metadata_tests/README.md