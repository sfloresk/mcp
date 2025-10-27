# AWS HealthOmics MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with comprehensive access to AWS HealthOmics services for genomic workflow management, execution, and analysis.

## Overview

AWS HealthOmics is a purpose-built service for storing, querying, and analyzing genomic, transcriptomic, and other omics data. This MCP server enables AI assistants to interact with HealthOmics workflows through natural language, making genomic data analysis more accessible and efficient.

## Key Capabilities

This MCP server provides tools for:

### 🧬 Workflow Management
- **Create and validate workflows**: Support for WDL, CWL, and Nextflow workflow languages
- **Lint workflow definitions**: Validate WDL and CWL workflows using industry-standard linting tools
- **Version management**: Create and manage workflow versions with different configurations
- **Package workflows**: Bundle workflow definitions into deployable packages

### 🚀 Workflow Execution
- **Start and monitor runs**: Execute workflows with custom parameters and monitor progress
- **Task management**: Track individual workflow tasks and their execution status
- **Resource configuration**: Configure compute resources, storage, and caching options

### 📊 Analysis and Troubleshooting
- **Performance analysis**: Analyze workflow execution performance and resource utilization
- **Failure diagnosis**: Comprehensive troubleshooting tools for failed workflow runs
- **Log access**: Retrieve detailed logs from runs, engines, tasks, and manifests

### 🌍 Region Management
- **Multi-region support**: Get information about AWS regions where HealthOmics is available

## Available Tools

### Workflow Management Tools

1. **ListAHOWorkflows** - List available HealthOmics workflows with pagination support
2. **CreateAHOWorkflow** - Create new workflows with WDL, CWL, or Nextflow definitions from base64-encoded ZIP files or S3 URIs, with optional container registry mappings
3. **GetAHOWorkflow** - Retrieve detailed workflow information and export definitions
4. **CreateAHOWorkflowVersion** - Create new versions of existing workflows from base64-encoded ZIP files or S3 URIs, with optional container registry mappings
5. **ListAHOWorkflowVersions** - List all versions of a specific workflow
6. **LintAHOWorkflowDefinition** - Lint single WDL or CWL workflow files using miniwdl and cwltool
7. **LintAHOWorkflowBundle** - Lint multi-file WDL or CWL workflow bundles with import/dependency support
8. **PackageAHOWorkflow** - Package workflow files into base64-encoded ZIP format

### Workflow Execution Tools

1. **StartAHORun** - Start workflow runs with custom parameters and resource configuration
2. **ListAHORuns** - List workflow runs with filtering by status and date ranges
3. **GetAHORun** - Retrieve detailed run information including status and metadata
4. **ListAHORunTasks** - List tasks for specific runs with status filtering
5. **GetAHORunTask** - Get detailed information about specific workflow tasks

### Analysis and Troubleshooting Tools

1. **AnalyzeAHORunPerformance** - Analyze workflow run performance and resource utilization
2. **DiagnoseAHORunFailure** - Comprehensive diagnosis of failed workflow runs with remediation suggestions
3. **GetAHORunLogs** - Access high-level workflow execution logs and events
4. **GetAHORunEngineLogs** - Retrieve workflow engine logs (STDOUT/STDERR) for debugging
5. **GetAHORunManifestLogs** - Access run manifest logs with runtime information and metrics
6. **GetAHOTaskLogs** - Get task-specific logs for debugging individual workflow steps

### Region Management Tools

1. **GetAHOSupportedRegions** - List AWS regions where HealthOmics is available

## Instructions for AI Assistants

This MCP server enables AI assistants to help users with AWS HealthOmics genomic workflow management. Here's how to effectively use these tools:

### Understanding AWS HealthOmics

AWS HealthOmics is designed for genomic data analysis workflows. Key concepts:

- **Workflows**: Computational pipelines written in WDL, CWL, or Nextflow that process genomic data
- **Runs**: Executions of workflows with specific input parameters and data
- **Tasks**: Individual steps within a workflow run
- **Storage Types**: STATIC (fixed storage) or DYNAMIC (auto-scaling storage)

### Workflow Management Best Practices

1. **Creating Workflows**:
   - **From local files**: Use `PackageAHOWorkflow` to bundle workflow files, then use the base64-encoded ZIP with `CreateAHOWorkflow`
   - **From S3**: Store your workflow definition ZIP file in S3 and reference it using the `definition_uri` parameter
   - Validate workflows with appropriate language syntax (WDL, CWL, Nextflow)
   - Include parameter templates to guide users on required inputs
   - Choose the appropriate method based on your workflow storage preferences

2. **S3 URI Support**:
   - Both `CreateAHOWorkflow` and `CreateAHOWorkflowVersion` support S3 URIs as an alternative to base64-encoded ZIP files
   - **Benefits of S3 URIs**:
     - Better for large workflow definitions (no base64 encoding overhead)
     - Easier integration with CI/CD pipelines that store artifacts in S3
     - Reduced memory usage during workflow creation
     - Direct reference to existing S3-stored workflow definitions
   - **Requirements**:
     - S3 URI must start with `s3://`
     - The S3 bucket must be in the same region as the HealthOmics service
     - Appropriate S3 permissions must be configured for the HealthOmics service
   - **Usage**: Specify either `definition_zip_base64` OR `definition_uri`, but not both

3. **Version Management**:
   - Create new versions for workflow updates rather than modifying existing ones
   - Use descriptive version names that indicate changes or improvements
   - List versions to help users choose the appropriate one
   - Both base64 ZIP and S3 URI methods are supported for version creation

### Workflow Execution Guidance

1. **Starting Runs**:
   - Always specify required parameters: workflow_id, role_arn, name, output_uri
   - Choose appropriate storage type (DYNAMIC recommended for most cases)
   - Use meaningful run names for easy identification
   - Configure caching when appropriate to save costs and time

2. **Monitoring Runs**:
   - Use `ListAHORuns` with status filters to track active workflows
   - Check individual run details with `GetAHORun` for comprehensive status
   - Monitor tasks with `ListAHORunTasks` to identify bottlenecks

### Troubleshooting Failed Runs

When workflows fail, follow this diagnostic approach:

1. **Start with DiagnoseAHORunFailure**: This comprehensive tool provides:
   - Failure reasons and error analysis
   - Failed task identification
   - Log summaries and recommendations
   - Actionable troubleshooting steps

2. **Access Specific Logs**:
   - **Run Logs**: High-level workflow events and status changes
   - **Engine Logs**: Workflow engine STDOUT/STDERR for system-level issues
   - **Task Logs**: Individual task execution details for specific failures
   - **Manifest Logs**: Resource utilization and workflow summary information

3. **Performance Analysis**:
   - Use `AnalyzeAHORunPerformance` to identify resource bottlenecks
   - Review task resource utilization patterns
   - Optimize workflow parameters based on analysis results

### Workflow Linting and Validation

The MCP server includes built-in workflow linting capabilities for validating WDL and CWL workflows before deployment:

1. **Lint Workflow Definitions**:
   - **Single files**: Use `LintAHOWorkflowDefinition` for individual workflow files
   - **Multi-file bundles**: Use `LintAHOWorkflowBundle` for workflows with imports and dependencies
   - **Syntax errors**: Catch parsing issues before deployment
   - **Missing components**: Identify missing inputs, outputs, or steps
   - **Runtime requirements**: Ensure tasks have proper runtime specifications
   - **Import resolution**: Validate imports and dependencies between files
   - **Best practices**: Get warnings about potential improvements

2. **Supported Formats**:
   - **WDL**: Uses miniwdl for comprehensive validation
   - **CWL**: Uses cwltool for standards-compliant validation

3. **No Additional Installation Required**:
   Both miniwdl and cwltool are included as dependencies and available immediately after installing the MCP server.

### Common Use Cases

1. **Workflow Development**:
   ```
   User: "Help me create a new genomic variant calling workflow"
   → Option A: Use PackageAHOWorkflow to bundle files, then CreateAHOWorkflow with base64 ZIP
   → Option B: Upload workflow ZIP to S3, then CreateAHOWorkflow with S3 URI
   → Validate syntax and parameters
   → Choose method based on workflow size and storage preferences
   ```

2. **Production Execution**:
   ```
   User: "Run my alignment workflow on these FASTQ files"
   → Use StartAHORun with appropriate parameters
   → Monitor with ListAHORuns and GetAHORun
   → Track task progress with ListAHORunTasks
   ```

3. **Troubleshooting**:
   ```
   User: "My workflow failed, what went wrong?"
   → Use DiagnoseAHORunFailure for comprehensive analysis
   → Access specific logs based on failure type
   → Provide actionable remediation steps
   ```

4. **Performance Optimization**:
   ```
   User: "How can I make my workflow run faster?"
   → Use AnalyzeAHORunPerformance to identify bottlenecks
   → Review resource utilization patterns
   → Suggest optimization strategies
   ```

5. **Workflow Validation**:
   ```
   User: "Check if my WDL workflow is valid"
   → Use LintAHOWorkflowDefinition for single files
   → Use LintAHOWorkflowBundle for multi-file workflows with imports
   → Check for missing inputs, outputs, or runtime requirements
   → Validate import resolution and dependencies
   → Get detailed error messages and warnings
   ```

### Important Considerations

- **IAM Permissions**: Ensure proper IAM roles with HealthOmics permissions
- **Regional Availability**: Use `GetAHOSupportedRegions` to verify service availability
- **Cost Management**: Monitor storage and compute costs, especially with STATIC storage
- **Data Security**: Follow genomic data handling best practices and compliance requirements
- **Resource Limits**: Be aware of service quotas and limits for concurrent runs

### Error Handling

When tools return errors:
- Check AWS credentials and permissions
- Verify resource IDs (workflow_id, run_id, task_id) are valid
- Ensure proper parameter formatting and required fields
- Use diagnostic tools to understand failure root causes
- Provide clear, actionable error messages to users

## Installation

| Cursor | VS Code |
|:------:|:-------:|
| [![Install MCP Server](https://cursor.com/deeplink/mcp-install-light.svg)](https://cursor.com/en/install-mcp?name=awslabs.aws-healthomics-mcp-server&config=eyJjb21tYW5kIjoidXZ4IGF3c2xhYnMuYXdzLWhlYWx0aG9taWNzLW1jcC1zZXJ2ZXJAbGF0ZXN0IiwiZW52Ijp7IkFXU19SRUdJT04iOiJ1cy1lYXN0LTEiLCJBV1NfUFJPRklMRSI6InlvdXItcHJvZmlsZSIsIkZBU1RNQ1BfTE9HX0xFVkVMIjoiV0FSTklORyJ9fQ%3D%3D) | [![Install on VS Code](https://img.shields.io/badge/Install_on-VS_Code-FF9900?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=AWS%20HealthOmics%20MCP%20Server&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22awslabs.aws-healthomics-mcp-server%40latest%22%5D%2C%22env%22%3A%7B%22AWS_REGION%22%3A%22us-east-1%22%2C%22AWS_PROFILE%22%3A%22your-profile%22%2C%22FASTMCP_LOG_LEVEL%22%3A%22WARNING%22%7D%7D) |

Install using uvx:

```bash
uvx awslabs.aws-healthomics-mcp-server
```

Or install from source:

```bash
git clone <repository-url>
cd mcp/src/aws-healthomics-mcp-server
uv sync
uv run -m awslabs.aws_healthomics_mcp_server.server
```

## Configuration

### Environment Variables

- `AWS_REGION` - AWS region for HealthOmics operations (default: us-east-1)
- `AWS_PROFILE` - AWS profile for authentication
- `FASTMCP_LOG_LEVEL` - Server logging level (default: WARNING)
- `HEALTHOMICS_DEFAULT_MAX_RESULTS` - Default maximum number of results for paginated API calls (default: 10)

#### Testing Configuration Variables

The following environment variables are primarily intended for testing scenarios, such as integration testing against mock service endpoints:

- `HEALTHOMICS_SERVICE_NAME` - Override the AWS service name used by the HealthOmics client (default: omics)
  - **Use case**: Testing against mock services or alternative implementations
  - **Validation**: Cannot be empty or whitespace-only; falls back to default with warning if invalid
  - **Example**: `export HEALTHOMICS_SERVICE_NAME=omics-mock`

- `HEALTHOMICS_ENDPOINT_URL` - Override the endpoint URL used by the HealthOmics client
  - **Use case**: Integration testing against local mock services or alternative endpoints
  - **Validation**: Must begin with `http://` or `https://`; ignored with warning if invalid
  - **Example**: `export HEALTHOMICS_ENDPOINT_URL=http://localhost:8080`
  - **Note**: Only affects the HealthOmics client; other AWS services use default endpoints

> **Important**: These testing configuration variables should only be used in development and testing environments. In production, always use the default AWS HealthOmics service endpoints for security and reliability.

### AWS Credentials

This server requires AWS credentials with appropriate permissions for HealthOmics operations. Configure using:

1. AWS CLI: `aws configure`
2. Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
3. IAM roles (recommended for EC2/Lambda)
4. AWS profiles: Set `AWS_PROFILE` environment variable

### Required IAM Permissions

The following IAM permissions are required:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "omics:ListWorkflows",
                "omics:CreateWorkflow",
                "omics:GetWorkflow",
                "omics:CreateWorkflowVersion",
                "omics:ListWorkflowVersions",
                "omics:StartRun",
                "omics:ListRuns",
                "omics:GetRun",
                "omics:ListRunTasks",
                "omics:GetRunTask",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
                "logs:GetLogEvents"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": "arn:aws:iam::*:role/HealthOmicsExecutionRole*"
        }
    ]
}
```

## Usage with MCP Clients

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "aws-healthomics": {
      "command": "uvx",
      "args": ["awslabs.aws-healthomics-mcp-server"],
      "env": {
        "AWS_REGION": "us-east-1",
        "AWS_PROFILE": "your-profile",
        "HEALTHOMICS_DEFAULT_MAX_RESULTS": "10"
      }
    }
  }
}
```

#### Testing Configuration Example

For integration testing against mock services:

```json
{
  "mcpServers": {
    "aws-healthomics-test": {
      "command": "uvx",
      "args": ["awslabs.aws-healthomics-mcp-server"],
      "env": {
        "AWS_REGION": "us-east-1",
        "AWS_PROFILE": "test-profile",
        "HEALTHOMICS_SERVICE_NAME": "omics-mock",
        "HEALTHOMICS_ENDPOINT_URL": "http://localhost:8080",
        "FASTMCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Other MCP Clients

Configure according to your client's documentation, using:
- Command: `uvx`
- Args: `["awslabs.aws-healthomics-mcp-server"]`
- Environment variables as needed

### Windows Installation

For Windows users, the MCP server configuration format is slightly different:

```json
{
  "mcpServers": {
    "awslabs.aws-healthomics-mcp-server": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "uv",
      "args": [
        "tool",
        "run",
        "--from",
        "awslabs.aws-healthomics-mcp-server@latest",
        "awslabs.aws-healthomics-mcp-server.exe"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "AWS_PROFILE": "your-aws-profile",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

#### Windows Testing Configuration

For testing scenarios on Windows:

```json
{
  "mcpServers": {
    "awslabs.aws-healthomics-mcp-server-test": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "uv",
      "args": [
        "tool",
        "run",
        "--from",
        "awslabs.aws-healthomics-mcp-server@latest",
        "awslabs.aws-healthomics-mcp-server.exe"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "DEBUG",
        "AWS_PROFILE": "test-profile",
        "AWS_REGION": "us-east-1",
        "HEALTHOMICS_SERVICE_NAME": "omics-mock",
        "HEALTHOMICS_ENDPOINT_URL": "http://localhost:8080"
      }
    }
  }
}
```

## Development

### Setup

```bash
git clone <repository-url>
cd aws-healthomics-mcp-server
uv sync
```

### Testing

```bash
# Run tests with coverage
uv run pytest --cov --cov-branch --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_server.py -v
```

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Type checking
uv run pyright
```

## Contributing

Contributions are welcome! Please see the [contributing guidelines](https://github.com/awslabs/mcp/blob/main/CONTRIBUTING.md) for more information.

## License

This project is licensed under the Apache-2.0 License. See the [LICENSE](https://github.com/awslabs/mcp/blob/main/LICENSE) file for details.
