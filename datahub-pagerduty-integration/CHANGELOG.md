# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-XX

### 🚨 BREAKING CHANGES
- **Removed support for MetadataChangeLog_v1 events** - These are not supported in DataHub Cloud
- **Updated event processing logic** - Now only processes EntityChangeEvent_v1 events
- **Changed event structure parsing** - Updated to match actual DataHub Cloud API structure

### ✅ Fixed
- **DataHub Cloud Compatibility** - Fixed all issues preventing proper DataHub Cloud integration
- **Event Type Support** - Now correctly supports only EntityChangeEvent_v1 events
- **Configuration File** - Complete rewrite of pagerduty_action.yaml with proper DataHub Cloud settings
- **Error Handling** - Added comprehensive error handling for DataHub Cloud API limitations
- **Rate Limiting** - Added proper rate limiting and retry logic for PagerDuty API
- **Documentation** - Complete rewrite of README with accurate feature descriptions

### ❌ Removed
- **False Claims** - Removed all claims about unsupported DataHub Cloud features:
  - Data Quality Assertion monitoring
  - Ingestion Pipeline failure detection
  - Missing Data alerts
  - Data Freshness monitoring
- **Unsupported Event Types** - Removed MetadataChangeLog_v1 event processing
- **Invalid Event Structure** - Removed processing of non-existent event fields

### 🔧 Technical Improvements
- **Event Processing** - Updated to use correct event structure (category, operation, modifier)
- **Severity Mapping** - Now maps actual event categories to PagerDuty severities
- **Deduplication** - Improved deduplication using entity URN and category
- **Auto-Resolution** - Updated to work with actual DataHub Cloud event structure
- **Configuration** - Added proper environment variable support and validation

### 📚 Documentation
- **Limitations Section** - Added clear documentation of what DataHub Cloud features are NOT supported
- **Supported Events** - Documented exactly which events are supported
- **Setup Instructions** - Updated with correct DataHub Cloud configuration steps
- **Troubleshooting** - Added comprehensive troubleshooting guide
- **Testing** - Added proper testing instructions and examples

### 🧪 Testing
- **Unit Tests** - Added comprehensive unit tests for all major functionality
- **Integration Tests** - Added integration testing instructions
- **Validation** - Added proper validation of DataHub Cloud connectivity

## [1.0.0] - 2024-01-XX

### 🚨 Initial Release Issues
- **Incorrect Event Types** - Claimed support for MetadataChangeLog_v1 (not supported in DataHub Cloud)
- **False Feature Claims** - Claimed support for data quality assertions and ingestion monitoring
- **Incomplete Configuration** - Missing proper DataHub Cloud configuration
- **Poor Error Handling** - No handling for DataHub Cloud API limitations
- **Inaccurate Documentation** - Documentation did not reflect actual capabilities

### 📝 Notes
This version had significant issues with DataHub Cloud compatibility and made false claims about supported features. It has been completely rewritten in version 2.0.0 to provide accurate, working integration with DataHub Cloud.
