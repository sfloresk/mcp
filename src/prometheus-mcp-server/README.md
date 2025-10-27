# Prometheus MCP Server

The Prometheus MCP Server provides a robust interface for interacting with AWS Managed Prometheus, enabling users to execute PromQL queries, list metrics, and retrieve server information with AWS SigV4 authentication support.

This MCP server is designed to be fully compatible with Amazon Q developer CLI, allowing seamless integration of Prometheus monitoring capabilities into your Amazon Q workflows. You can load the server directly into Amazon Q to leverage its powerful querying and metric analysis features through the familiar Q interface.

## Features

- Execute instant PromQL queries against AWS Managed Prometheus
- Execute range queries with start time, end time, and step interval
- List all available metrics in your Prometheus instance
- Get server configuration information
- AWS SigV4 authentication for secure access
- Automatic retries with exponential backoff

## Installation

| Cursor | VS Code |
|:------:|:-------:|
| [![Install MCP Server](https://cursor.com/deeplink/mcp-install-light.svg)](https://cursor.com/en/install-mcp?name=awslabs.prometheus-mcp-server&config=eyJjb21tYW5kIjoidXZ4IGF3c2xhYnMucHJvbWV0aGV1cy1tY3Atc2VydmVyQGxhdGVzdCAtLXVybCBodHRwczovL2Fwcy13b3Jrc3BhY2VzLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tL3dvcmtzcGFjZXMvd3MtPFdvcmtzcGFjZSBJRD4gLS1yZWdpb24gPFlvdXIgQVdTIFJlZ2lvbj4gLS1wcm9maWxlIDxZb3VyIENMSSBQcm9maWxlIFtkZWZhdWx0XSBpZiBubyBwcm9maWxlIGlzIHVzZWQ%2BIiwiZW52Ijp7IkZBU1RNQ1BfTE9HX0xFVkVMIjoiREVCVUciLCJBV1NfUFJPRklMRSI6IjxZb3VyIENMSSBQcm9maWxlIFtkZWZhdWx0XSBpZiBubyBwcm9maWxlIGlzIHVzZWQ%2BIn19) | [![Install on VS Code](https://img.shields.io/badge/Install_on-VS_Code-FF9900?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=Prometheus%20MCP%20Server&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22awslabs.prometheus-mcp-server%40latest%22%2C%22--url%22%2C%22https%3A%2F%2Faps-workspaces.us-east-1.amazonaws.com%2Fworkspaces%2Fws-%3CWorkspace%20ID%3E%22%2C%22--region%22%2C%22%3CYour%20AWS%20Region%3E%22%2C%22--profile%22%2C%22%3CYour%20CLI%20Profile%20%5Bdefault%5D%20if%20no%20profile%20is%20used%3E%22%5D%2C%22env%22%3A%7B%22FASTMCP_LOG_LEVEL%22%3A%22DEBUG%22%2C%22AWS_PROFILE%22%3A%22%3CYour%20CLI%20Profile%20%5Bdefault%5D%20if%20no%20profile%20is%20used%3E%22%7D%7D) |

### Prerequisites

- Python 3.10 or higher
- AWS credentials configured with appropriate permissions
- AWS Managed Prometheus workspace



## Configuration

The server is configured through the Amazon Q MCP configuration file as shown in the Usage section below.

## Usage with Amazon Q

Here are some ways you can work with MCP across AWS, and we'll be adding support to more products including Amazon Q Developer CLI soon:

1. Create a configuration file:
```bash
mkdir -p ~/.aws/amazonq/
```

2. Add the following to `~/.aws/amazonq/mcp.json`:

### Basic Configuration
```json
{
  "mcpServers": {
    "prometheus": {
      "command": "uvx",
      "args": [
        "awslabs.prometheus-mcp-server@latest"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```
### Windows Installation

For Windows users, the MCP server configuration format is slightly different:

```json
{
  "mcpServers": {
    "awslabs.prometheus-mcp-server": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "uv",
      "args": [
        "tool",
        "run",
        "--from",
        "awslabs.prometheus-mcp-server@latest",
        "awslabs.prometheus-mcp-server.exe"
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


### Configuration with Optional Arguments
```json
{
  "mcpServers": {
    "prometheus": {
      "command": "uvx",
      "args": [
        "awslabs.prometheus-mcp-server@latest",
        "--url",
        "https://aps-workspaces.<AWS Region>.amazonaws.com/workspaces/ws-<Workspace ID>",
        "--region",
        "<Your AWS Region>",
        "--profile",
        "<Your CLI Profile>"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

3. In Amazon Q, you can now use the Prometheus MCP server to query your metrics.

## Available Tools

1. **GetAvailableWorkspaces**
   - List all available Prometheus workspaces in the specified region
   - Parameters: region (optional)
   - Returns: List of workspaces with IDs, aliases, and status

2. **ExecuteQuery**
   - Execute instant PromQL queries against Prometheus
   - Parameters: workspace_id (required), query (required), time (optional), region (optional)

3. **ExecuteRangeQuery**
   - Execute PromQL queries over a time range
   - Parameters: workspace_id (required), query, start time, end time, step interval, region (optional)

4. **ListMetrics**
   - Retrieve all available metric names from Prometheus
   - Parameters: workspace_id (required), region (optional)
   - Returns: Sorted list of metric names

5. **GetServerInfo**
   - Retrieve server configuration details
   - Parameters: workspace_id (required), region (optional)
   - Returns: URL, region, profile, and service information

## Example Queries

```python
# Get available workspaces
workspaces = await get_available_workspaces()
for ws in workspaces['workspaces']:
    print(f"ID: {ws['workspace_id']}, Alias: {ws['alias']}, Status: {ws['status']}")

# Execute an instant query
result = await execute_query(
    workspace_id="ws-12345678-abcd-1234-efgh-123456789012",
    query="up"
)

# Execute a range query
data = await execute_range_query(
    workspace_id="ws-12345678-abcd-1234-efgh-123456789012",
    query="rate(node_cpu_seconds_total[5m])",
    start="2023-01-01T00:00:00Z",
    end="2023-01-01T01:00:00Z",
    step="1m"
)

# List available metrics
metrics = await list_metrics(
    workspace_id="ws-12345678-abcd-1234-efgh-123456789012"
)

# Get server information
info = await get_server_info(
    workspace_id="ws-12345678-abcd-1234-efgh-123456789012"
)
```

## Troubleshooting

Common issues and solutions:

1. **AWS Credentials Not Found**
   - Check ~/.aws/credentials
   - Set AWS_PROFILE environment variable
   - Verify IAM permissions

2. **Connection Errors**
   - Verify Prometheus URL is correct
   - Check network connectivity
   - Ensure AWS VPC access is configured correctly

3. **Authentication Failures**
   - Verify AWS credentials are current
   - Check system clock synchronization
   - Ensure correct AWS region is specified

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
