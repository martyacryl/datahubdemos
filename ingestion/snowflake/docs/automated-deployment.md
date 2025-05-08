# Automated Deployment for DataHub-Snowflake Integration

This guide covers methods for automating the deployment and execution of DataHub-Snowflake ingestion pipelines in various environments.

## Docker-Based Deployment

### Using the DataHub Docker Images

The DataHub project provides official Docker images that can be used to run ingestion pipelines. Here's a sample `docker-compose.yml` file for running Snowflake ingestion:

```yaml
version: '3'
services:
  datahub-ingestion:
    image: acryldata/datahub-ingestion:latest
    environment:
      - DATAHUB_GMS_URL=http://datahub-gms:8080
      - SNOWFLAKE_USER=datahub_user
      - SNOWFLAKE_PASS=${SNOWFLAKE_PASSWORD}
    volumes:
      - ./recipes:/recipes
    command: ["datahub", "ingest", "-c", "/recipes/snowflake_ingestion.yaml"]
```

### Creating a Custom Ingestion Container

For more control, you can create a custom Dockerfile:

```dockerfile
FROM acryldata/datahub-ingestion:latest

# Install additional dependencies if needed
RUN pip install --no-cache-dir "acryl-datahub[snowflake]>=0.10.0"

# Copy your recipes
COPY ./recipes /recipes

# Set environment variables
ENV DATAHUB_GMS_URL=http://datahub-gms:8080

# Set the entrypoint
ENTRYPOINT ["datahub", "ingest", "-c"]
CMD ["/recipes/snowflake_ingestion.yaml"]
```

Build and run the container:

```bash
docker build -t custom-datahub-ingestion .
docker run -e SNOWFLAKE_USER=datahub_user -e SNOWFLAKE_PASS=password custom-datahub-ingestion
```

## Kubernetes Deployment

### Using a CronJob

To schedule regular ingestion on Kubernetes, create a CronJob manifest:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: datahub-snowflake-ingestion
spec:
  schedule: "0 1 * * *"  # Run at 1 AM every day
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: datahub-ingestion
            image: acryldata/datahub-ingestion:latest
            command: ["datahub", "ingest", "-c", "/recipes/snowflake_ingestion.yaml"]
            env:
            - name: DATAHUB_GMS_URL
              value: "http://datahub-gms-service:8080"
            - name: SNOWFLAKE_USER
              value: "datahub_user"
            - name: SNOWFLAKE_PASS
              valueFrom:
                secretKeyRef:
                  name: snowflake-credentials
                  key: password
            volumeMounts:
            - name: recipes
              mountPath: /recipes
          volumes:
          - name: recipes
            configMap:
              name: datahub-ingestion-recipes
          restartPolicy: OnFailure
```

Create a ConfigMap for your recipes:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: datahub-ingestion-recipes
data:
  snowflake_ingestion.yaml: |
    source:
      type: snowflake
      config:
        account_id: "xy12345"
        warehouse: "COMPUTE_WH"
        username: "${SNOWFLAKE_USER}"
        password: "${SNOWFLAKE_PASS}"
        role: "datahub_role"
        # ... additional configuration
    sink:
      type: datahub-rest
      config:
        server: "${DATAHUB_GMS_URL}"
```

Create a Secret for your credentials:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: snowflake-credentials
type: Opaque
data:
  password: <base64-encoded-password>
```

Apply these manifests:

```bash
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f cronjob.yaml
```

### Using Helm

If you're using Helm to deploy DataHub, you can configure ingestion sources in your values file:

```yaml
datahub-actions:
  enabled: true
  extraEnvs:
    - name: SNOWFLAKE_USER
      value: datahub_user
    - name: SNOWFLAKE_PASS
      valueFrom:
        secretKeyRef:
          name: snowflake-credentials
          key: password
  
  ingestionSchedules:
    snowflake:
      enabled: true
      schedule: "0 1 * * *"
      recipe: |
        source:
          type: snowflake
          config:
            account_id: "xy12345"
            warehouse: "COMPUTE_WH"
            username: "${SNOWFLAKE_USER}"
            password: "${SNOWFLAKE_PASS}"
            role: "datahub_role"
            # ... additional configuration
        sink:
          type: datahub-rest
          config:
            server: "http://datahub-gms:8080"
```

## Airflow Integration

### Using the DataHub Airflow Operator

DataHub provides native Airflow integration. Here's how to set up Snowflake ingestion using Airflow:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datahub.integrations.airflow.operators import DatahubIngestionOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
}

dag = DAG(
    'datahub_snowflake_ingestion',
    default_args=default_args,
    description='Ingest Snowflake metadata into DataHub',
    schedule_interval='0 1 * * *',
    start_date=days_ago(1),
    tags=['datahub', 'snowflake'],
)

ingest_task = DatahubIngestionOperator(
    task_id='ingest_snowflake_metadata',
    config_file='/path/to/recipes/snowflake_ingestion.yaml',
    datahub_conn_id='datahub_rest_default',
    dag=dag,
)
```

### Using the DataHub Lineage Backend

You can also enable DataHub's Airflow lineage backend to automatically track task and dataset lineage:

```python
# In your airflow.cfg
[lineage]
backend = datahub.integrations.airflow.DatahubAirflowLineageBackend
datahub_conn_id = datahub_rest_default
cluster = "prod"
capture_ownership_info = true
capture_tags_info = true
```

## CI/CD Integration

### GitOps Workflow with GitHub Actions

Create a GitHub Actions workflow for validating and deploying ingestion recipes:

```yaml
name: DataHub Ingestion Pipeline

on:
  push:
    branches: [ main ]
    paths:
      - 'recipes/**'
  pull_request:
    branches: [ main ]
    paths:
      - 'recipes/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install "acryl-datahub[snowflake]>=0.10.0"
      
      - name: Validate recipes
        run: |
          for recipe in recipes/*.yaml; do
            echo "Validating $recipe"
            datahub check recipe $recipe
          done
  
  deploy:
    needs: validate
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install "acryl-datahub[snowflake]>=0.10.0"
      
      - name: Deploy to Kubernetes
        uses: Azure/k8s-set-context@v1
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG }}
      
      - name: Update ConfigMap
        run: |
          kubectl create configmap datahub-ingestion-recipes --from-file=recipes/ -o yaml --dry-run=client | kubectl apply -f -
```

### GitLab CI Pipeline

For GitLab, create a `.gitlab-ci.yml` file:

```yaml
image: python:3.10

stages:
  - validate
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"

cache:
  paths:
    - .pip-cache/

before_script:
  - pip install "acryl-datahub[snowflake]>=0.10.0"

validate:
  stage: validate
  script:
    - for recipe in recipes/*.yaml; do
        echo "Validating $recipe";
        datahub check recipe $recipe;
      done

deploy:
  stage: deploy
  only:
    - main
  script:
    - mkdir -p ~/.kube
    - echo "$KUBE_CONFIG" > ~/.kube/config
    - kubectl create configmap datahub-ingestion-recipes --from-file=recipes/ -o yaml --dry-run=client | kubectl apply -f -
  environment:
    name: production
```

## Monitoring and Alerting

### Using DataHub's Ingestion Report

Each ingestion run produces a report that can be used for monitoring. You can capture this report and send it to your monitoring system:

```python
from datahub.ingestion.run.pipeline import Pipeline

pipeline = Pipeline.create(
    {
        "source": {
            "type": "snowflake",
            "config": {
                # ... your Snowflake config
            }
        },
        "sink": {
            "type": "datahub-rest",
            "config": {
                "server": "http://localhost:8080"
            }
        }
    }
)

pipeline.run()
report = pipeline.get_report()

# Example: Send the report to Slack
import requests
import json

webhook_url = "https://hooks.slack.com/services/XXX/YYY/ZZZ"
payload = {
    "text": f"DataHub Snowflake Ingestion Report: {report.ingestion_summary()}"
}
requests.post(webhook_url, data=json.dumps(payload))
```

### Using Prometheus and Grafana

If you're running DataHub on Kubernetes, you can use Prometheus and Grafana for monitoring:

1. Set up Prometheus to scrape DataHub metrics
2. Create a Grafana dashboard to visualize ingestion metrics
3. Set up alerts for failed ingestion runs

## Next Steps

- For best practices, see [Best Practices](best-practices.md)
- For example implementations, check the [`scripts/`](/scripts/) directory