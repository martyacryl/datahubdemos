FROM acryldata/datahub-ingestion:latest

# Install additional dependencies
RUN pip install --no-cache-dir \
    'snowflake-connector-python>=3.0.0' \
    'acryl-datahub[snowflake]>=0.10.0' \
    'slackclient>=2.9.0' \
    'schedule>=1.1.0'

# Set up working directory
WORKDIR /app

# Copy scripts
COPY *.py /app/
COPY entrypoint.sh /app/

# Copy examples as templates
COPY ../examples/*.json /app/templates/

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]