# Amazon ECS MCP Server

[![PyPI version](https://img.shields.io/pypi/v/awslabs.ecs-mcp-server.svg)](https://pypi.org/project/awslabs.ecs-mcp-server/)

An MCP server for containerizing applications, deploying applications to Amazon Elastic Container Service (ECS), troubleshooting ECS deployments, and managing ECS resources. This server enables AI assistants to help users with the full lifecycle of containerized applications on AWS.

## Features

- **Containerization Guidance**: Provides best practices and guidance for containerizing web applications
- **ECS Deployment**: Deploy containerized applications to AWS ECS using Fargate
- **Load Balancer Integration**: Automatically configure Application Load Balancers (ALBs) for web traffic
- **Infrastructure as Code**: Generate and apply CloudFormation templates for ECS infrastructure
- **URL Management**: Return public ALB URLs for immediate access to deployed applications
- **Circuit Breaker**: Implement deployment circuit breaker with automatic rollback
- **Container Insights**: Enable enhanced container insights for monitoring
- **VPC Endpoints**: Configure VPC endpoints for secure access to AWS services without internet exposure
- **Security Best Practices**: Implement AWS security best practices for container deployments
- **Resource Management**: List and explore ECS resources such as task definitions, services, clusters, and tasks
- **ECR Integration**: View repositories and container images in Amazon ECR
- **AWS Knowledge Integration**: Access up-to-date AWS documentation through the integrated AWS Knowledge MCP Server proxy which includes knowledge on ECS and new features released that models may not be aware of

Customers can use the `containerize_app` tool to help them containerize their applications with best practices and deploy them to Amazon ECS. The `create_ecs_infrastructure` tool automates infrastructure deployment using CloudFormation, while `get_deployment_status` returns the status of deployments and provide the URL of the set up Application Load Balancer. When resources are no longer needed, the `delete_ecs_infrastructure` tool allows for easy cleanup and removal of all deployed components.

Customers can list and view their ECS resources (clusters, services, tasks, task definitions) and access their ECR resources (container images) using the `ecs_resource_management` tool. When running into ECS deployment issues, they can use the `ecs_troubleshooting_tool` to diagnose and resolve common problems.

## Installation

### Prerequisites

Before installing the ECS MCP Server, ensure you have the following prerequisites installed:

1. **Docker or Finch**: Required for containerization and local testing
   - [Docker](https://docs.docker.com/get-docker/) for container management
   - [Finch](https://github.com/runfinch/finch) as a Docker alternative

2. **UV**: Required for package management and running MCP servers
   - Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/)

### Installation Steps

```bash
# Install using uv
uv pip install awslabs.ecs-mcp-server

# Or install using pip
pip install awslabs.ecs-mcp-server
```

You can also run the MCP server directly from a local clone of the GitHub repository:

```bash
# Clone the awslabs repository
git clone https://github.com/awslabs/mcp.git

# Run the server directly using uv
uv --directory /path/to/ecs-mcp-server/src/ecs-mcp-server/awslabs/ecs_mcp_server run main.py
```

To setup your preferred MCP client (ie. Amazon Q Developer CLI, Cline, Cursor, VS Code, etc.) with the ECS MCP Server, proceed to the [Configuration](#configuration) section.

## Usage Environments

The ECS MCP Server is currently in development and is designed for the following environments:

- **Development and Prototyping**: Ideal for local application development, testing containerization approaches, and rapidly iterating on deployment configurations.
- **Learning and Exploration**: Excellent for users who want to learn about containerization, ECS, and AWS infrastructure.
- **Testing and Staging**: Suitable for integration testing and pre-production validation in non-critical environments.

**Not Recommended For**:
- **Production Workloads**: As this tool is still in active development, it is not suited for production deployments or business-critical applications.
- **Regulated or Sensitive Workloads**: Not suitable for applications handling sensitive data or subject to regulatory compliance requirements.

**Important Note on Troubleshooting Tools**: Even the troubleshooting tools should be used with caution in production environments. Always set `ALLOW_SENSITIVE_DATA=false` and `ALLOW_WRITE=false` flags when connecting to production accounts to prevent accidental exposure of sensitive information or unintended infrastructure modifications.

## Production Considerations

While the ECS MCP Server is primarily designed for development, testing, and non-critical environments, certain components can be considered for controlled production use with appropriate safeguards.

### Allowlisted Actions for Production

The following operations are read-only and relatively safe for production environments when used with appropriate IAM permissions. Note: they can return sensitive information, so ensure `ALLOW_SENSITIVE_DATA=false` is set in production configurations.

| Tool | Operation | Production Safety |
|------|-----------|-------------------|
| `ecs_resource_management` | List operations (clusters, services, tasks) | ✅ Safe - Read-only |
| `ecs_resource_management` | Describe operations (clusters, services, tasks) | ✅ Safe - Read-only |
| `ecs_troubleshooting_tool` | `fetch_service_events` | ✅ Safe - Read-only |
| `ecs_troubleshooting_tool` | `get_ecs_troubleshooting_guidance` | ✅ Safe - Read-only |
| `get_deployment_status` | Status checking | ✅ Safe - Read-only |
| `aws_knowledge_aws___search_documentation` | AWS documentation search | ✅ Safe - Read-only |
| `aws_knowledge_aws___read_documentation` | AWS documentation reading | ✅ Safe - Read-only |
| `aws_knowledge_aws___recommend` | AWS documentation recommendations | ✅ Safe - Read-only |

The following operations modify resources and should be used with extreme caution in production:

| Tool | Operation | Production Safety |
|------|-----------|-------------------|
| `create_ecs_infrastructure` | Creating resources | ⚠️ High Risk - Creates infrastructure |
| `delete_ecs_infrastructure` | Deleting resources | 🛑 Dangerous - Deletes infrastructure |
| `containerize_app` | Generate container configs | 🟡 Medium Risk - Local changes only |
| `ecs_resource_management` | Create operations (clusters, services, tasks) | ⚠️ High Risk - Creates resources |
| `ecs_resource_management` | Update operations (services, tasks, settings) | ⚠️ High Risk - Modifies resources |
| `ecs_resource_management` | Delete operations (clusters, services, tasks) | 🛑 Dangerous - Deletes resources |
| `ecs_resource_management` | Run/Start/Stop task operations | ⚠️ High Risk - Affects running workloads |

### When to Consider Production Use

The ECS MCP Server may be appropriate for production environments in the following scenarios:

1. **Read-only monitoring**: Using resource management tools with read-only IAM policies
2. **Troubleshooting non-critical issues**: Using diagnostic tools to gather logs and status information
3. **Sandbox or isolated environments**: Using deployment tools in production-like environments that are isolated from core services

### When to Avoid Production Use

Avoid using ECS MCP Server in production for:

1. Critical business infrastructure
2. Applications handling sensitive customer data
3. High-throughput or high-availability services
4. Regulated workloads with compliance requirements
5. Infrastructure lacking proper backup and disaster recovery procedures

## Configuration

| Cursor | VS Code |
|:------:|:-------:|
| [![Install MCP Server](https://cursor.com/deeplink/mcp-install-light.svg)](https://cursor.com/en/install-mcp?name=awslabs.ecs-mcp-server&config=eyJjb21tYW5kIjoidXZ4IC0tZnJvbSBhd3NsYWJzLWVjcy1tY3Atc2VydmVyIGVjcy1tY3Atc2VydmVyIiwiZW52Ijp7IkFXU19QUk9GSUxFIjoieW91ci1hd3MtcHJvZmlsZSIsIkFXU19SRUdJT04iOiJ5b3VyLWF3cy1yZWdpb24iLCJGQVNUTUNQX0xPR19MRVZFTCI6IkVSUk9SIiwiRkFTVE1DUF9MT0dfRklMRSI6Ii9wYXRoL3RvL2Vjcy1tY3Atc2VydmVyLmxvZyIsIkFMTE9XX1dSSVRFIjoiZmFsc2UiLCJBTExPV19TRU5TSVRJVkVfREFUQSI6ImZhbHNlIn19) | [![Install on VS Code](https://img.shields.io/badge/Install_on-VS_Code-FF9900?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=ECS%20MCP%20Server&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22awslabs-ecs-mcp-server%22%2C%22ecs-mcp-server%22%5D%2C%22env%22%3A%7B%22AWS_PROFILE%22%3A%22your-aws-profile%22%2C%22AWS_REGION%22%3A%22your-aws-region%22%2C%22FASTMCP_LOG_LEVEL%22%3A%22ERROR%22%2C%22FASTMCP_LOG_FILE%22%3A%22%2Fpath%2Fto%2Fecs-mcp-server.log%22%2C%22ALLOW_WRITE%22%3A%22false%22%2C%22ALLOW_SENSITIVE_DATA%22%3A%22false%22%7D%7D) |

Add the ECS MCP Server to your MCP client configuration:

```json
{
  "mcpServers": {
    "awslabs.ecs-mcp-server": {
      "command": "uvx",
      "args": ["--from", "awslabs-ecs-mcp-server", "ecs-mcp-server"],
      "env": {
        "AWS_PROFILE": "your-aws-profile", // Optional - uses your local AWS configuration if not specified
        "AWS_REGION": "your-aws-region", // Optional - uses your local AWS configuration if not specified
        "FASTMCP_LOG_LEVEL": "ERROR",
        "FASTMCP_LOG_FILE": "/path/to/ecs-mcp-server.log",
        "ALLOW_WRITE": "false",
        "ALLOW_SENSITIVE_DATA": "false"
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
    "awslabs.ecs-mcp-server": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "uv",
      "args": [
        "tool",
        "run",
        "--from",
        "awslabs.ecs-mcp-server@latest",
        "ecs-mcp-server.exe"
      ],
     "env": {
        "AWS_PROFILE": "your-aws-profile", // Optional - uses your local AWS configuration if not specified
        "AWS_REGION": "your-aws-region", // Optional - uses your local AWS configuration if not specified
        "FASTMCP_LOG_LEVEL": "ERROR",
        "FASTMCP_LOG_FILE": "/path/to/ecs-mcp-server.log",
        "ALLOW_WRITE": "false",
        "ALLOW_SENSITIVE_DATA": "false"
      }
    }
  }
}
```


If running from a local repository, configure the MCP client like this:

```json
{
  "mcpServers": {
    "awslabs.ecs-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ecs-mcp-server/src/ecs-mcp-server/awslabs/ecs_mcp_server",
        "run",
        "main.py"
      ],
      "env": {
        "AWS_PROFILE": "your-aws-profile",
        "AWS_REGION": "your-aws-region",
        "FASTMCP_LOG_LEVEL": "DEBUG",
        "FASTMCP_LOG_FILE": "/path/to/ecs-mcp-server.log",
        "ALLOW_WRITE": "false",
        "ALLOW_SENSITIVE_DATA": "false"
      }
    }
  }
}
```

## Updating the MCP Server

The ECS MCP Server is regularly updated with new features, bug fixes, and improvements. Here's how to get the latest updates:

### Automatic Updates (Default Behavior)

If you installed via PyPI (recommended), updates are automatic:

- **PyPI Installation**: The MCP client automatically downloads the latest version when the server is restarted
- **No action required**: Simply restart your MCP client to get the latest updates

### Manual Updates

If you want to manually update to ensure you have the latest version:

```bash
uv pip install --upgrade awslabs.ecs-mcp-server
```

### Local Repository Updates

If you're running from a cloned repository, update by pulling the latest changes:

```bash
# Navigate to your cloned repository
cd /path/to/mcp

# Pull the latest changes
git pull origin main

# The MCP server will automatically use the updated code on next restart
```

## Security Controls

The ECS MCP Server includes security controls in your MCP client configuration to prevent accidental changes to infrastructure and limit access to sensitive data:

### ALLOW_WRITE

Controls whether write operations (creating or deleting infrastructure) are allowed.

```bash
# Enable write operations
"ALLOW_WRITE": "true"

# Disable write operations (default)
"ALLOW_WRITE": "false"
```

### ALLOW_SENSITIVE_DATA

Controls whether tools that return logs and detailed resource information are allowed.

```bash
# Enable access to sensitive data
"ALLOW_SENSITIVE_DATA": "true"

# Disable access to sensitive data (default)
"ALLOW_SENSITIVE_DATA": "false"
```

### IAM Best Practices

We strongly recommend creating dedicated IAM roles with least-privilege permissions when using the ECS MCP Server:

1. **Create a dedicated IAM role** specifically for ECS MCP Server operations
2. **Apply least-privilege permissions** by attaching only the necessary policies based on your use case
3. **Use scoped-down resource policies** whenever possible
4. **Apply a permission boundary** to limit the maximum permissions

For detailed example IAM policies tailored for different ECS MCP Server use cases (read-only monitoring, troubleshooting, deployment, and service-specific access), see [EXAMPLE_IAM_POLICIES.md](https://github.com/awslabs/mcp/blob/main/src/ecs-mcp-server/EXAMPLE_IAM_POLICIES.md).


## MCP Tools

### Deployment Tools

These tools help you containerize applications and deploy them to Amazon ECS with proper infrastructure setup and monitoring.

- **containerize_app**: Generates Dockerfile and container configurations for web applications
- **create_ecs_infrastructure**: Creates AWS infrastructure needed to deploy your containerized application using ECS. This includes:
  - Application Load Balancer (ALB) with public-facing endpoints
  - Network security groups with appropriate inbound/outbound rules
  - IAM roles and policies with least-privilege permissions
  - VPC configurations with public and private subnets (if needed)
  - S3 Gateway endpoint associations for ECR image pulls
  - ECS cluster with capacity provider settings
  - Task definition with CPU/memory allocations and container configs
  - Service configuration with desired count and auto-scaling policies
  - Health check configuration and deployment circuit breakers
- **get_deployment_status**: Gets the status of an ECS deployment and returns the ALB URL
- **delete_ecs_infrastructure**: Deletes the AWS infrastructure created by the ECS MCP Server

### Troubleshooting Tool

The troubleshooting tool helps diagnose and resolve common ECS deployment issues stemming from infrastructure, service, task, and network configuration.

- **ecs_troubleshooting_tool**: Consolidated tool with the following actions:
  - **get_ecs_troubleshooting_guidance**: Initial assessment and troubleshooting path recommendation
  - **fetch_cloudformation_status**: Infrastructure-level diagnostics for CloudFormation stacks
  - **fetch_service_events**: Service-level diagnostics for ECS services
  - **fetch_task_failures**: Task-level diagnostics for ECS task failures
  - **fetch_task_logs**: Application-level diagnostics through CloudWatch logs
  - **detect_image_pull_failures**: Specialized tool for detecting container image pull failures
  - **fetch_network_configuration**: Network-level diagnostics for ECS deployments including VPC, subnets, security groups, and load balancers

### Resource Management

This tool provides comprehensive access to Amazon ECS resources to help you monitor, understand, and manage your deployment environment.

- **ecs_resource_management**: Execute operations on ECS resources with a consistent interface:
  - **Read Operations** (always available):
    - Clusters: List all clusters, describe specific cluster details
    - Services: List services in a cluster, describe service configuration
    - Tasks: List running or stopped tasks, describe task details and status
    - Task Definitions: List task definition families, describe specific task definition revisions
    - Container Instances: List container instances, describe instance health and capacity
    - Capacity Providers: List and describe capacity providers associated with clusters
    - ECR repositories and container images
  - **Write Operations** (requires ALLOW_WRITE=true):
    - Create resources: Create clusters, services, task sets, and capacity providers
    - Update resources: Update service configurations, task protection settings, and cluster settings
    - Delete resources: Delete clusters, services, task definitions, and capacity providers
    - Register/Deregister: Register and deregister task definitions and container instances
    - Task Management: Run tasks, start tasks, stop tasks, and execute commands on running tasks
    - Tag Management: Tag and untag resources

The resource management tool enforces permission checks for write operations. Operations that modify resources require the ALLOW_WRITE environment variable to be set to true.

### AWS Documentation Tools

The ECS MCP Server integrates with the [AWS Knowledge MCP Server](https://github.com/awslabs/mcp/tree/main/src/aws-knowledge-mcp-server) to provide access to up-to-date AWS documentation, including ECS-specific knowledge about new features recently launched that models may not be aware of.

Note: these tools are duplicative if you have the AWS Knowledge MCP Server already configured in your MCP client. For the below knowledge tools, the ECS MCP Server adds extra guidance to the tool descriptions to help LLMs use the tools for ECS contexts.

- **aws_knowledge_aws___search_documentation**: Search across all AWS documentation including the latest AWS docs, API references, Blogs posts, Architectural references, and Well-Architected best practices.

- **aws_knowledge_aws___read_documentation**: Fetch and convert AWS documentation pages to markdown format.

- **aws_knowledge_aws___recommend**: Get content recommendations for AWS documentation pages.

## Example Prompts

### Containerization and Deployment

- "Containerize this Node.js app and deploy it to AWS"
- "Deploy this Flask application to Amazon ECS"
- "Create an ECS deployment for this web application with auto-scaling"
- "Set up a containerized environment for this Django app on Amazon ECS"
- "List all my ECS clusters"
- "Show me details for my-cluster"

### Troubleshooting

- "Help me troubleshoot my ECS deployment"
- "My ECS tasks keep failing, can you diagnose the issue?"
- "The ALB health check is failing for my ECS service"
- "Why can't I access my deployed application?"
- "Check what's wrong with my CloudFormation stack"

### Resource Management

- "Show me my ECS clusters"
- "List all running tasks in my ECS cluster"
- "Describe my ECS service configuration"
- "Get information about my task definition"
- "Create a new ECS cluster"
- "Update my service configuration"
- "Register a new task definition"
- "Delete an unused task definition"
- "Run a task in my cluster"
- "Stop a running task"

### AWS Documentation and Knowledge

- "What are the best practices for ECS deployments?"
- "How do I set up blue-green deployments in ECS?"
- "Get recommendations for ECS security best practices"

## Requirements

- Python 3.10+
- AWS credentials with permissions for ECS, ECR, CloudFormation, and related services
- Docker (for local containerization testing)

## License

This project is licensed under the Apache-2.0 License.
