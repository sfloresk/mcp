# CloudWatch Application Signals MCP Server

An MCP (Model Context Protocol) server that provides tools for monitoring and analyzing AWS services using [AWS Application Signals](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Application-Signals.html).

This server enables AI assistants like Claude, GitHub Copilot, and Amazon Q to help you monitor service health, analyze performance metrics, track SLO compliance, and investigate issues using distributed tracing.

## Key Features

1. Monitor overall service health, diagnose root causes, and recommend actionable fixes with the built-in APM expertise.
2. Generate business insights from telemetry data through natural language queries.

## Prerequisites

1. [Sign-Up for an AWS account](https://aws.amazon.com/free/?trk=78b916d7-7c94-4cab-98d9-0ce5e648dd5f&sc_channel=ps&ef_id=Cj0KCQjwxJvBBhDuARIsAGUgNfjOZq8r2bH2OfcYfYTht5v5I1Bn0lBKiI2Ii71A8Gk39ZU5cwMLPkcaAo_CEALw_wcB:G:s&s_kwcid=AL!4422!3!432339156162!e!!g!!aws%20sign%20up!9572385111!102212379327&gad_campaignid=9572385111&gbraid=0AAAAADjHtp99c5A9DUyUaUQVhVEoi8of3&gclid=Cj0KCQjwxJvBBhDuARIsAGUgNfjOZq8r2bH2OfcYfYTht5v5I1Bn0lBKiI2Ii71A8Gk39ZU5cwMLPkcaAo_CEALw_wcB)
2. [Enable Application Signals](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Application-Monitoring-Sections.html) for your applications
3. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
4. Install Python using `uv python install 3.10`

### Available Tools

1. **`list_monitored_services`** - List all services monitored by AWS Application Signals
   - Get an overview of all monitored services
   - See service names, types, and key attributes
   - Identify the services monitored by Application Signals

2. **`get_service_detail`** - Get detailed information about a specific service
   - Get Service key properties such as Hosting environment, list of APIs,etc
   - Get the list of ApplicationSignals metrics available on service
   - Find associated log groups

3. **`list_slis`** - List all SLOs and SLIs status for all services
   - List the configured SLOs and across all services
   - Find out all breached SLIs and status

4. **`get_slo`** - Gets the details configuration for a specific SLO
   - Return the relevant metrics info, SLO threshold

5. **`search_transaction_spans`** - Queries OTel Spans data via Transaction Search
   - Query OTel Spans to root cause the potential problems
   - Generate business performance insights summaries

6. **`query_sampled_traces`** - Queries AWS X-Ray traces to gain deeper insights
   - Find the impact from the tracing dependency view
   - Return the exact error stack for LLM to suggest the actionable fixes

7. **`query_service_metrics`** - Queries Application Signals metrics for root causing service performance issues
   - Query Application Signals RED metrics to correlate the relevant OTel Spans/Traces for troubleshooting

## Installation

### Installing via Cursor

To install CloudWatch Application Signals MCP Server for Cursor automatically:

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-light.svg)](https://cursor.com/install-mcp?name=awslabs.cloudwatch-appsignals-mcp-server&config=eyJhdXRvQXBwcm92ZSI6W10sImRpc2FibGVkIjpmYWxzZSwidGltZW91dCI6NjAsImNvbW1hbmQiOiJ1dnggYXdzbGFicy5jbG91ZHdhdGNoLWFwcHNpZ25hbHMtbWNwLXNlcnZlckBsYXRlc3QiLCJlbnYiOnsiQVdTX1BST0ZJTEUiOiJbVGhlIEFXUyBQcm9maWxlIE5hbWUgdG8gdXNlIGZvciBBV1MgYWNjZXNzXSIsIkFXU19SRUdJT04iOiJbVGhlIEFXUyByZWdpb24gdG8gcnVuIGluXSIsIkZBU1RNQ1BfTE9HX0xFVkVMIjoiRVJST1IifSwidHJhbnNwb3J0VHlwZSI6InN0ZGlvIn0%3D)

### Installing via `uv`

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *awslabs.cloudwatch-appsignals-mcp-server*.

### Installing for Amazon Q (Preview)

- Start Amazon Q Developer CLI from [here](https://github.com/aws/amazon-q-developer-cli).
- Add the following configuration in `~/.aws/amazonq/mcp.json` file.
```json
{
  "mcpServers": {
    "awslabs.cloudwatch-appsignals-mcp-server": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "command": "uvx",
      "args": [
        "awslabs.cloudwatch-appsignals-mcp-server@latest"
      ],
      "env": {
        "AWS_ACCESS_KEY_ID": "[AWS Access Key ID]",
        "AWS_SECRET_ACCESS_KEY": "[AWS Access Key]",
        "AWS_REGION": "[AWS Region]",
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "transportType": "stdio"
    }
  }
}
```

### Installing via Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  When installing a development or unpublished server, add the `--directory` flag:

  ```json
  {
    "mcpServers": {
      "awslabs.cloudwatch-appsignals-mcp-server": {
        "command": "uvx",
        "args": ["--from", "/absolute/path/to/cloudwatch-appsignals-mcp-server", "awslabs.cloudwatch-appsignals-mcp-server"]
      }
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>

  ```json
  {
    "mcpServers": {
      "awslabs.cloudwatch-appsignals-mcp-server": {
        "command": "uvx",
        "args": ["awslabs.cloudwatch-appsignals-mcp-server@latest"]
      }
    }
  }
  ```
</details>

### Build and install docker image locally on the same host of your LLM client

1. `git clone https://github.com/awslabs/mcp.git`
2. Go to sub-directory 'src/cloudwatch-appsignals-mcp-server/'
3. Run 'docker build -t awslabs/cloudwatch-appsignals-mcp-server:latest .'

### Add or update your LLM client's config with following:
```json
{
  "mcpServers": {
    "awslabs.cloudwatch-appsignals-mcp-server": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "AWS_ACCESS_KEY_ID=[your data]",
        "-e", "AWS_SECRET_ACCESS_KEY=[your data]",
        "-e", "AWS_REGION=[your data]",
        "awslabs/cloudwatch-appsignals-mcp-server:latest"
      ]
    }
  }
}
```

### Debugging

You can use the MCP inspector to debug the server. For `uvx` installations:

```bash
npx @modelcontextprotocol/inspector uvx awslabs.cloudwatch-appsignals-mcp-server
```

Or if you've installed the package in a specific directory:

```bash
cd /path/to/cloudwatch-appsignals-mcp-server
npx @modelcontextprotocol/inspector uv run awslabs.cloudwatch-appsignals-mcp-server
```

## Usage Examples

### Example 1: Getting Started with Service Monitoring
```
User: "What services are being monitored by Application Signals?"
Assistant: I'll check what services are currently being monitored by AWS Application Signals.

[Uses list_monitored_services tool]

I found 3 services being monitored:

• Service: api-gateway-service
  Type: AWS::ApiGateway::RestApi
  Key Attributes:
    Name: api-gateway-service
    Type: AWS::ApiGateway::RestApi
    Environment: production

• Service: order-service
  Type: AWS::ECS::Service
  Key Attributes:
    Name: order-service
    Type: AWS::ECS::Service
    Environment: production
    Platform: ECS

• Service: payment-lambda
  Type: AWS::Lambda::Function
  Key Attributes:
    Name: payment-lambda
    Type: AWS::Lambda::Function
    Environment: production
```

### Example 2: Investigating Service Details
```
User: "Tell me more about the order-service"
Assistant: I'll get detailed information about the order-service.

[Uses get_service_detail tool]

Here are the details for order-service:

Key Attributes:
  Name: order-service
  Type: AWS::ECS::Service
  Environment: production

Additional Attributes:
  Platform: ECS
  Application: ecommerce-app
  Telemetry.SDK: opentelemetry-1.9.0

Metric References (15 total):
  • AWS/ApplicationSignals/Latency
    Type: GAUGE
    Dimensions: Service=order-service, Operation=GetOrder

  • AWS/ApplicationSignals/ErrorRate
    Type: GAUGE
    Dimensions: Service=order-service, Operation=CreateOrder

Log Group References (2 total):
  • /aws/ecs/order-service
  • /aws/application-signals/order-service
```

## Configuration

### Required AWS Permissions

The server requires the following AWS IAM permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "application-signals:ListServices",
        "application-signals:GetService",
        "application-signals:ListServiceLevelObjectives",
        "application-signals:GetServiceLevelObjective",
        "application-signals:BatchGetServiceLevelObjectiveBudgetReport",
        "cloudwatch:GetMetricData",
        "logs:GetQueryResults",
        "logs:StartQuery",
        "logs:StopQuery",
        "xray:GetTraceSummaries",
        "xray:BatchGetTraces"
      ],
      "Resource": "*"
    }
  ]
}
```

### Environment Variables

- `AWS_REGION` - AWS region (defaults to us-east-1)
- `MCP_CLOUDWATCH_APPSIGNALS_LOG_LEVEL` - Logging level (defaults to INFO)

### AWS Credentials

This server uses the standard AWS credential chain via boto3. It will automatically use credentials from:
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc.)
- AWS credentials file (`~/.aws/credentials`)
- AWS config file (`~/.aws/config`)
- IAM roles (when running on EC2, ECS, Lambda, etc.)
- And other standard AWS credential providers

No additional credential configuration is needed beyond your standard AWS setup.

## Development

This server is part of the AWS Labs MCP collection. For development and contribution guidelines, please see the main repository documentation.

## License

This project is licensed under the Apache License, Version 2.0. See the LICENSE file for details.
