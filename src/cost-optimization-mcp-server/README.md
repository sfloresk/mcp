# Cost optimization MCP Server

MCP server for generating insights for cost and usage report

## Features

### Query trusted advisor findings

- Get detailed breakdown of your AWS trusted advisor findings

### Query cost and usage report via athena

- Ask questions about your AWS costs in plain English, no complex query languages required

### Generate cost reports and insights

- Generate comprehensive cost reports based on findings and query results


## Prerequisites

1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
2. Install Python using `uv python install 3.10`
3. Install dependencies: `uv sync`

## Installation

For Amazon Q Developer CLI MCP, add the following `awslabs.cost-optimization-mcp-server` entry to `~/.aws/amazonq/mcp.json`:

```json
{
  "mcpServers": {
    "awslabs.cost-optimization-mcp-server": {
        "command": "[REPLACE_FOR_ABSOLUTE_PATH_FOR_UV_BIN]/uv",
        "args": [
            "--directory",
            "[REPLACE_FOR_ABSOLUTE_PATH_FOR_MCP_PROJECT]/src/cost-optimization-mcp-server/awslabs/cost_optimization_mcp_server",
            "run",
            "server.py"
        ],
        "env": {
            "FASTMCP_LOG_LEVEL": "INFO",
            "AWS_PROFILE": "[REPLACE_WITH_AWS_PROFILE]",
            "AWS_CUR_DB_NAME": "[REPLACE_WITH_AWS_CUR_DATABASE_NAME]",
            "AWS_CUR_TABLE_NAME": "[REPLACE_WITH_AWS_CUR_TABLE_NAME]",
            "AWS_ATHENA_RESULTS_BUCKET": "[REPLACE_WITH_S3_ARN]",
            "AWS_DEFAULT_REGION": "[REPLACE_WITH_AWS_REGION]"
        },
        "disabled": false,
        "autoApprove": []
    }
  }
}
```

### AWS Authentication

The MCP server uses the AWS profile specified in the `AWS_PROFILE` environment variable. If not provided, it defaults to the "default" profile in your AWS configuration file.
