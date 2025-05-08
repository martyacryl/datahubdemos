# Best Practices for DataHub-Snowflake Integration

This guide covers recommendations and best practices for optimizing your DataHub-Snowflake integration.

## Performance Optimization

### Resource Allocation

- **Dedicated Warehouse**: Use a dedicated, right-sized warehouse for DataHub ingestion to avoid impacting production workloads
- **Warehouse Sizing**: Start with X-Small or Small warehouse for most deployments, scaling up if needed for very large Snowflake instances
- **Auto-Suspend**: Configure auto-suspend to minimize costs while ensuring the warehouse is available when needed
- **Scaling**: For large Snowflake instances, consider configuring the warehouse to scale out during ingestion

### Query Optimization

- **Filtration**: Use pattern matching to limit the scope of ingestion to relevant databases, schemas, and tables
- **Sampling**: Enable the `use_sampling` option to speed up profiling of large tables
- **Query Caching**: Leverage Snowflake's query caching by using consistent ingestion patterns
- **Timestamp-Based Filtering**: Use `profile_if_updated_since_days` to only profile recently changed tables

### Concurrency Management

- **Worker Configuration**: Adjust `max_workers` in the profiling configuration based on your warehouse size (typically 1-2× the number of warehouse nodes)
- **Avoid Warehouse Contention**: Schedule ingestion during off-peak hours to reduce impact on other Snowflake workloads
- **Query Combination**: Keep `query_combiner_enabled: true` to reduce the number of queries sent to Snowflake

## Security Best Practices

### Authentication

- **Key Pair Authentication**: Prefer key pair authentication over password-based authentication for production deployments
- **OAuth**: For enterprise environments, use OAuth with SSO to integrate with your existing identity provider
- **Credential Rotation**: Implement a regular schedule for rotating credentials and keys
- **Secrets Management**: Use a secrets manager (Kubernetes Secrets, Vault, AWS Secrets Manager) rather than embedding credentials in recipes

### Role and Access Management

- **Least Privilege**: Grant only the necessary privileges to the DataHub role
- **Dedicated User**: Use a dedicated service account for DataHub ingestion
- **Role Hierarchy**: Consider creating a role hierarchy if managing multiple environments (dev/test/prod)
- **Multi-Account Strategy**: For multi-account Snowflake environments, define a consistent RBAC strategy across accounts

## Metadata Management

### Tagging Strategy

- **Consistent Tagging**: Develop a consistent tagging strategy in Snowflake that can be leveraged by DataHub
- **Tag Hierarchy**: Organize tags hierarchically (e.g., `PII.EMAIL`, `PII.SSN`) for better categorization
- **Automated Classification**: Combine DataHub's classification features with Snowflake's to enhance metadata
- **Tag Propagation**: Decide between direct tagging (`without_lineage`) and propagated tagging (`with_lineage`) based on your needs

### Domain Organization

- **Logical Grouping**: Organize Snowflake assets into domains based on business function or data subject areas
- **Domain Mapping**: Use dataset domain patterns to map Snowflake databases and schemas to DataHub domains
- **Consistent Naming**: Establish naming conventions that make domain mapping more consistent

### Glossary Integration

- **Terminology Alignment**: Align Snowflake comments and DataHub glossary terms
- **Definition Source of Truth**: Decide whether Snowflake comments or DataHub definitions are the source of truth
- **Term to Tag Mapping**: Map DataHub glossary terms to Snowflake tags for better integration

## Ingestion Strategy

### Ingestion Frequency

- **Incremental Updates**: Use stateful ingestion for efficient incremental updates
- **Tiered Approach**: Consider different frequencies for different metadata types:
  - Schema metadata: Daily or after schema changes
  - Usage statistics: Daily
  - Lineage information: Weekly
  - Profiling: Weekly for stable tables, daily for frequently changing tables

### Scope Management

- **Start Small**: Begin with core databases/schemas, then expand coverage
- **Critical Data First**: Prioritize business-critical datasets for initial ingestion
- **Feature Progressive Rollout**: Enable basic features first (schema, lineage), then add advanced features (profiling, usage)

### Environment Strategy

- **Multi-Environment Setup**: Configure separate ingestion pipelines for dev, test, and prod
- **Environment Tagging**: Use the `env` parameter to distinguish assets from different environments
- **Platform Instance**: Use `platform_instance` to distinguish between Snowflake accounts

## Monitoring and Maintenance

### Health Monitoring

- **Ingestion Reports**: Capture and analyze ingestion reports for trends and anomalies
- **Performance Metrics**: Monitor ingestion duration, number of assets extracted, and resource utilization
- **Error Tracking**: Set up alerting for ingestion failures or anomalies
- **Integration with Observability Tools**: Forward DataHub metrics to your existing monitoring stack

### Maintenance Tasks

- **Recipe Validation**: Validate configuration changes before deployment
- **Version Control**: Maintain recipes in version control
- **Change Management**: Coordinate DataHub ingestion changes with Snowflake schema changes
- **Regular Audits**: Periodically audit ingestion coverage against Snowflake metadata

## Scaling for Enterprise

### Handling Large Snowflake Environments

- **Horizontal Partitioning**: Split ingestion across multiple pipelines (e.g., by database)
- **Scheduled Windows**: Stagger ingestion to avoid resource contention
- **Metadata Prioritization**: Prioritize critical metadata over comprehensive coverage
- **Resource Scaling**: Scale DataHub resources alongside Snowflake growth

### Cross-Platform Integration

- **Unified Lineage**: Connect Snowflake lineage with other platforms (e.g., dbt, Airflow, BI tools)
- **Consistent Metadata**: Maintain consistent metadata practices across platforms
- **Integration Testing**: Test cross-platform metadata flows in lower environments before production

## Common Issues and Solutions

### Slow Ingestion

- **Issue**: Ingestion takes too long to complete
- **Solutions**:
  - Reduce scope with pattern matching
  - Increase warehouse size
  - Enable sampling for profiling
  - Use timestamp-based filtering
  - Optimize worker count

### Missing Lineage

- **Issue**: Not seeing expected lineage information
- **Solutions**:
  - Verify Snowflake edition (Enterprise or higher required)
  - Check GRANT permissions on the Snowflake database
  - Extend the time window with `ignore_start_time_lineage: true`
  - Verify SQL query patterns are supported by the parser

### Excessive Resource Usage

- **Issue**: High Snowflake credit consumption
- **Solutions**:
  - Limit profiling to essential tables
  - Use sampling for large tables
  - Schedule ingestion during off-peak hours
  - Turn off expensive profiling metrics
  - Right-size the warehouse

### Incomplete Metadata

- **Issue**: Missing tables, views, or columns
- **Solutions**:
  - Check pattern configurations
  - Verify permissions
  - Check for exclude patterns that might be too broad
  - Enable debug logging to identify skipped assets

## Case Studies and Examples

### Finance Industry Example

A financial services company implemented DataHub-Snowflake integration with these optimizations:

- Separated metadata ingestion (every 6 hours) from profiling (nightly)
- Used domain mapping to organize data by business function
- Implemented PII tagging in Snowflake that was pulled into DataHub
- Created unified lineage across Snowflake, dbt, and Tableau

### E-commerce Example

An e-commerce platform optimized their DataHub-Snowflake integration:

- Used multi-pipeline approach to handle 10,000+ tables
- Implemented automated classification for sensitive data
- Set up tiered profiling (daily for critical tables, weekly for others)
- Integrated with CI/CD for automated testing and deployment

## Next Steps

- Review our [example implementation](/examples/) for more practical examples
- Check out the [scripts](/scripts/) for automation helpers
- Contribute your own best practices back to the community