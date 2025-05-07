#!/usr/bin/env python
"""
DataHub Metadata Testing Demo - Main Script

This script demonstrates how to create, run, and evaluate metadata tests (assertions)
on datasets in DataHub.
"""

import os
import sys
import json
import time
import logging
import argparse
from typing import Dict, List, Optional, Any
import requests
from tqdm import tqdm
from tabulate import tabulate
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DataHubMetadataTest:
    """
    Class to demonstrate DataHub metadata testing functionality.
    """
    
    def __init__(self, server_url: str, token: str):
        """Initialize with DataHub server URL and token."""
        self.server_url = server_url
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        logger.info(f"Initialized DataHub client for {server_url}")
    
    def search_datasets(self, query: str = "*", limit: int = 5) -> List[Dict]:
        """
        Search for datasets in DataHub.
        
        Args:
            query: Search query string
            limit: Maximum number of datasets to return
            
        Returns:
            List of dataset information
        """
        logger.info(f"Searching for datasets with query: {query}")
        
        url = f"{self.server_url}/api/graphql"
        
        graphql_query = """
        query search($input: SearchInput!) {
            search(input: $input) {
                start
                count
                total
                searchResults {
                    entity {
                        urn
                        type
                        ... on Dataset {
                            name
                            platform {
                                name
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "input": {
                "type": "DATASET",
                "query": query,
                "start": 0,
                "count": limit,
                "filters": []
            }
        }
        
        try:
            response = requests.post(
                url, 
                headers=self.headers, 
                json={"query": graphql_query, "variables": variables}
            )
            
            if response.status_code != 200:
                logger.error(f"Error searching datasets: {response.text}")
                return []
            
            data = response.json()
            search_results = data.get("data", {}).get("search", {}).get("searchResults", [])
            
            datasets = []
            for result in search_results:
                entity = result.get("entity", {})
                datasets.append({
                    "urn": entity.get("urn"),
                    "name": entity.get("name", entity.get("urn", "").split(":")[-1]),
                    "platform": entity.get("platform", {}).get("name", "unknown")
                })
            
            logger.info(f"Found {len(datasets)} datasets")
            return datasets
            
        except Exception as e:
            logger.error(f"Exception searching datasets: {e}")
            return []
    
    def create_test(self, dataset_urn: str, test_config: Dict) -> Optional[str]:
        """
        Create a metadata test on a dataset.
        
        Args:
            dataset_urn: The URN of the dataset
            test_config: Test configuration
            
        Returns:
            The URN of the created test, or None if failed
        """
        test_type = test_config.get("type", "unknown")
        logger.info(f"Creating {test_type} test on dataset: {dataset_urn}")
        
        url = f"{self.server_url}/api/graphql"
        
        # Map test type to the corresponding assertion definition type
        assertion_type = {
            "schema_completeness": "SCHEMA_FIELD_DOCS_EXIST",
            "ownership": "ENTITY_OWNER_EXISTS",
            "freshness": "DATASET_FRESHNESS"
        }.get(test_type, "CUSTOM")
        
        # Extract test parameters
        parameters = test_config.get("parameters", {})
        
        graphql_mutation = """
        mutation createAssertion($input: CreateAssertionInput!) {
            createAssertion(input: $input) {
                urn
            }
        }
        """
        
        variables = {
            "input": {
                "datasetUrn": dataset_urn,
                "type": assertion_type,
                "enabled": True,
                "properties": {
                    "name": test_config.get("name", f"{test_type.title()} Test"),
                    "description": test_config.get("description", f"Validates {test_type} of the dataset"),
                    "documentationUrl": test_config.get("documentationUrl", ""),
                    "severity": test_config.get("severity", "WARNING"),
                    "parameters": parameters
                }
            }
        }
        
        try:
            response = requests.post(
                url, 
                headers=self.headers, 
                json={"query": graphql_mutation, "variables": variables}
            )
            
            if response.status_code != 200:
                logger.error(f"Error creating test: {response.text}")
                return None
            
            data = response.json()
            assertion_urn = data.get("data", {}).get("createAssertion", {}).get("urn")
            
            if assertion_urn:
                logger.info(f"Successfully created test: {assertion_urn}")
                return assertion_urn
            else:
                logger.warning(f"Test creation response didn't contain URN: {data}")
                return None
            
        except Exception as e:
            logger.error(f"Exception creating test: {e}")
            return None
    
    def run_test(self, assertion_urn: str) -> Dict:
        """
        Run a metadata test (assertion).
        
        Args:
            assertion_urn: The URN of the test to run
            
        Returns:
            Dictionary with test results
        """
        logger.info(f"Running test: {assertion_urn}")
        
        url = f"{self.server_url}/api/graphql"
        
        graphql_mutation = """
        mutation runAssertion($input: RunAssertionInput!) {
            runAssertion(input: $input) {
                runId
            }
        }
        """
        
        variables = {
            "input": {
                "urn": assertion_urn
            }
        }
        
        try:
            # Start the test run
            response = requests.post(
                url, 
                headers=self.headers, 
                json={"query": graphql_mutation, "variables": variables}
            )
            
            if response.status_code != 200:
                logger.error(f"Error running test: {response.text}")
                return {"status": "ERROR", "message": f"Failed to run test: {response.text}"}
            
            data = response.json()
            run_id = data.get("data", {}).get("runAssertion", {}).get("runId")
            
            if not run_id:
                logger.warning(f"Test run response didn't contain runId: {data}")
                return {"status": "ERROR", "message": "Failed to get test run ID"}
            
            # Wait for the test to complete and get results
            return self._wait_for_test_result(assertion_urn, run_id)
            
        except Exception as e:
            logger.error(f"Exception running test: {e}")
            return {"status": "ERROR", "message": f"Exception: {str(e)}"}
    
    def _wait_for_test_result(self, assertion_urn: str, run_id: str, max_attempts: int = 10) -> Dict:
        """
        Wait for a test run to complete and get the results.
        
        Args:
            assertion_urn: URN of the test
            run_id: ID of the test run
            max_attempts: Maximum number of attempts to check status
            
        Returns:
            Dictionary with test results
        """
        url = f"{self.server_url}/api/graphql"
        
        graphql_query = """
        query assertionRunByUrn($urn: String!, $runId: String!) {
            assertionRunByUrn(urn: $urn, runId: $runId) {
                runId
                runStatus
                result {
                    type
                    success
                    message
                    severity
                }
                runEvents {
                    timestamp
                    eventType
                    eventText
                }
            }
        }
        """
        
        variables = {
            "urn": assertion_urn,
            "runId": run_id
        }
        
        for attempt in range(max_attempts):
            try:
                response = requests.post(
                    url, 
                    headers=self.headers, 
                    json={"query": graphql_query, "variables": variables}
                )
                
                if response.status_code != 200:
                    logger.error(f"Error checking test result: {response.text}")
                    time.sleep(2)
                    continue
                
                data = response.json()
                run_data = data.get("data", {}).get("assertionRunByUrn", {})
                
                # Check if run is complete
                status = run_data.get("runStatus")
                if status == "COMPLETE":
                    result = run_data.get("result", {})
                    events = run_data.get("runEvents", [])
                    
                    return {
                        "status": status,
                        "success": result.get("success", False),
                        "message": result.get("message", "No message provided"),
                        "severity": result.get("severity", "UNKNOWN"),
                        "events": events
                    }
                elif status == "FAILURE":
                    return {
                        "status": status,
                        "success": False,
                        "message": "Test run failed",
                        "events": run_data.get("runEvents", [])
                    }
                
                # Not complete yet, wait and try again
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Exception checking test result: {e}")
                time.sleep(2)
        
        return {
            "status": "TIMEOUT",
            "success": False,
            "message": f"Test did not complete after {max_attempts} attempts"
        }
    
    def get_test_configs(self) -> Dict[str, Dict]:
        """
        Load test configurations from files.
        
        Returns:
            Dictionary mapping test types to their configurations
        """
        configs = {}
        config_dir = "test_configs"
        
        try:
            for filename in os.listdir(config_dir):
                if filename.endswith(".json"):
                    with open(os.path.join(config_dir, filename), "r") as f:
                        config = json.load(f)
                        test_type = config.get("type")
                        if test_type:
                            configs[test_type] = config
        except Exception as e:
            logger.error(f"Error loading test configs: {e}")
        
        return configs
    
    def run_demo(self, query: str = "*", limit: int = 3) -> None:
        """
        Run the complete metadata testing demo.
        
        Args:
            query: Search query to find datasets
            limit: Maximum number of datasets to test
        """
        # Step 1: Find datasets to test
        datasets = self.search_datasets(query=query, limit=limit)
        
        if not datasets:
            logger.error(f"No datasets found matching query: {query}")
            return
        
        print(f"\nFound {len(datasets)} datasets to test:")
        table_data = [[i+1, d.get("name"), d.get("platform")] for i, d in enumerate(datasets)]
        print(tabulate(table_data, headers=["#", "Dataset", "Platform"], tablefmt="pretty"))
        
        # Step 2: Load test configurations
        test_configs = self.get_test_configs()
        
        if not test_configs:
            logger.error("No test configurations found")
            return
        
        print(f"\nLoaded {len(test_configs)} test types:")
        for test_type, config in test_configs.items():
            print(f"  - {config.get('name', test_type.title())}: {config.get('description', 'No description')}")
        
        # Step 3: Create and run tests on each dataset
        results = []
        
        for dataset in tqdm(datasets, desc="Testing datasets"):
            dataset_urn = dataset.get("urn")
            dataset_name = dataset.get("name")
            
            print(f"\n\nTesting dataset: {dataset_name}")
            
            for test_type, config in test_configs.items():
                print(f"\n  Running {test_type} test...")
                
                # Create the test
                assertion_urn = self.create_test(dataset_urn, config)
                
                if not assertion_urn:
                    print(f"    ❌ Failed to create test")
                    results.append({
                        "dataset": dataset_name,
                        "test": config.get("name", test_type.title()),
                        "status": "ERROR",
                        "success": False,
                        "message": "Failed to create test"
                    })
                    continue
                
                # Run the test
                test_result = self.run_test(assertion_urn)
                
                # Store and display result
                result_entry = {
                    "dataset": dataset_name,
                    "test": config.get("name", test_type.title()),
                    "status": test_result.get("status", "UNKNOWN"),
                    "success": test_result.get("success", False),
                    "message": test_result.get("message", "No message provided")
                }
                results.append(result_entry)
                
                if result_entry["success"]:
                    print(f"    ✅ Test passed: {result_entry['message']}")
                else:
                    print(f"    ❌ Test failed: {result_entry['message']}")
        
        # Step 4: Show summary of results
        print("\n\n=== Test Results Summary ===")
        
        table_data = []
        for r in results:
            status = "✅ PASSED" if r.get("success") else "❌ FAILED"
            table_data.append([
                r.get("dataset"),
                r.get("test"),
                status,
                r.get("message")
            ])
        
        print(tabulate(table_data, headers=["Dataset", "Test", "Status", "Message"], tablefmt="pretty"))
        
        # Calculate statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get("success"))
        failed_tests = total_tests - passed_tests
        
        print(f"\nTotal tests run: {total_tests}")
        print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        
        # Save results to file
        results_file = f"test_results_{int(time.time())}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nDetailed results saved to {results_file}")


def main():
    """Main function to run the demo."""
    parser = argparse.ArgumentParser(description="DataHub Metadata Testing Demo")
    parser.add_argument("--server", default=os.getenv("DATAHUB_GMS_URL", "https://test-environment.acryl.io"),
                       help="DataHub GMS URL")
    parser.add_argument("--token", default=os.getenv("DATAHUB_TOKEN"),
                       help="DataHub Personal Access Token (PAT)")
    parser.add_argument("--query", default="*",
                       help="Search query to find datasets (default: *)")
    parser.add_argument("--limit", type=int, default=3,
                       help="Maximum number of datasets to test (default: 3)")
    
    args = parser.parse_args()
    
    if not args.token:
        logger.error("DataHub token is required. Set DATAHUB_TOKEN environment variable or use --token")
        sys.exit(1)
    
    # Create and run the demo
    demo = DataHubMetadataTest(args.server, args.token)
    demo.run_demo(args.query, args.limit)

if __name__ == "__main__":
    main()