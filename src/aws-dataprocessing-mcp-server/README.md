# Amazon Data Processing MCP Server

The AWS DataProcessing MCP server provides AI code assistants with comprehensive data processing tools and real-time pipeline visibility across AWS Glue and Amazon EMR-EC2. This integration equips large language models (LLMs) with essential data engineering capabilities and contextual awareness, enabling AI code assistants to streamline data processing workflows through intelligent guidance — from initial data discovery and cataloging through complex ETL pipeline orchestration and big data analytics optimization.

Integrating the DataProcessing MCP server into AI code assistants transforms data engineering workflows across all phases, from simplifying data catalog management with automated schema discovery and data quality validation. Additionally, it streamlines ETL job creation with intelligent code generation and best practice recommendations. It accelerates big data processing through automated EMR cluster provisioning and workload optimization. Finally, it enhances troubleshooting through intelligent debugging tools and operational insights. All of this simplifies complex data operations through natural language interactions in AI code assistants.


## Key features

### AWS Glue Integration

* Data Catalog Management: Enables users to explore, create, and manage databases, tables, and partitions through natural language requests, automatically translating them into appropriate AWS Glue Data Catalog operations.
* Interactive Sessions: Provides interactive development environment for Spark and Ray workloads, enabling data exploration, debugging, and iterative development through managed Jupyter-like sessions.
* Workflows and Triggers: Orchestrates complex ETL activities through visual workflows and automated triggers, supporting scheduled, conditional, and event-based execution patterns.
* Commons: Enables users to create and manage usage profiles, security configurations, catalog encryption settings and resource policies, which provide users with the ability to manage the configuration and encryption of several Glue resources like ETL jobs, catalogs, etc.
* ETL Job Orchestration: Provides the ability to create, monitor, and manage Glue ETL jobs with automatic script generation, job scheduling, and workflow coordination based on user-defined data transformation requirements.
* Crawler Management: Enables intelligent data discovery through automated crawler configuration, scheduling, and metadata extraction from various data sources.

### Amazon EMR Integration

* Cluster Management: Enables users to create, configure, monitor, and terminate EMR clusters with comprehensive control over instance types, applications, and configurations through natural language requests.
* Instance Management: Provides the ability to add, modify, and monitor instance fleets and instance groups within EMR clusters, supporting both on-demand and spot instances with auto-scaling capabilities.
* Step Execution: Orchestrates data processing workflows through EMR steps, allowing users to submit, monitor, and manage Hadoop, Spark, and other application jobs on running clusters.
* Security Configuration: Manages EMR security settings including encryption, authentication, and authorization policies to ensure secure data processing environments.

### Amazon Athena Integration

* Query Execution: Enables users to execute, monitor, and manage SQL queries with comprehensive control over query lifecycle, including starting queries, retrieving results, monitoring performance statistics, and canceling running queries through natural language requests.
* Named Query Management: Provides the ability to create, update, retrieve, and delete saved SQL queries, enabling users to build reusable query libraries with proper organization and team collaboration capabilities.
* Data Catalog Operations: Manages Athena data catalogs with support for multiple catalog types (LAMBDA, GLUE, HIVE, FEDERATED), enabling users to create, configure, and maintain data source connections for cross-platform querying.
* Database and Table Discovery: Facilitates data exploration through comprehensive database and table metadata retrieval, allowing users to discover available data sources, understand schema structures, and navigate data catalogs efficiently.
* Workgroup Administration: Orchestrates query execution environments through workgroup management, providing cost control, access management, and query result configuration with support for different user groups and organizational policies.

## Prerequisites

* [Install Python 3.10+](https://www.python.org/downloads/release/python-3100/)
* [Install the `uv` package manager](https://docs.astral.sh/uv/getting-started/installation/)
* [Install and configure the AWS CLI with credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)

## Setup

Add these IAM policies to the IAM role or user that you use to manage your Glue, EMR-EC2 or Athena resources.

### Read-Only Operations Policy

For read operations, the following permissions are required:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "glue:GetDatabase*",
        "glue:GetTable*",
        "glue:GetPartition*",
        "glue:GetCrawler*",
        "glue:GetConnection*",
        "glue:GetDatabases",
        "glue:GetTables",
        "glue:ListCrawlers",
        "glue:SearchTables",
        "glue:GetJobRun",
        "glue:GetJobRuns",
        "glue:GetJob",
        "glue:GetJobs",
        "glue:GetJobBookmark",
        "glue:GetUsageProfile",
        "glue:GetSecurityConfiguration",
        "glue:GetDataCatalogEncryptionSettings",
        "glue:GetResourcePolicy",
        "glue:GetSession",
        "glue:ListSessions",
        "glue:GetStatement",
        "glue:ListStatements",
        "glue:GetSession",
        "glue:ListSessions",
        "glue:GetStatement",
        "glue:ListStatements",
        "glue:GetWorkflow",
        "glue:ListWorkflows",
        "glue:GetTrigger",
        "glue:GetTriggers",
        "cloudwatch:GetMetricData",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "emr:DescribeCluster",
        "emr:ListClusters",
        "emr:DescribeStep",
        "emr:ListSteps",
        "emr:ListInstances",
        "emr:GetManagedScalingPolicy",
        "emr:DescribeStudio",
        "emr:ListStudios",
        "emr:DescribeNotebookExecution",
        "emr:ListNotebookExecutions",
        "athena:BatchGetQueryExecution",
        "athena:GetQueryExecution",
        "athena:GetQueryResults",
        "athena:GetQueryRuntimeStatistics",
        "athena:ListQueryExecutions",
        "athena:BatchGetNamedQuery",
        "athena:GetNamedQuery",
        "athena:ListNamedQueries",
        "athena:GetDataCatalog",
        "athena:ListDataCatalogs",
        "athena:GetDatabase",
        "athena:GetTableMetadata",
        "athena:ListDatabases",
        "athena:ListTableMetadata",
        "athena:GetWorkGroup",
        "athena:ListWorkGroups",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

### Write Operations Policy

For write operations, we recommend the following IAM policies:

* AWSGlueServiceRole: Enables Glue service operations including job execution, crawler runs, and data catalog modifications

**Important Security Note**: Users should exercise caution when --allow-write and --allow-sensitive-data-access modes are enabled with these broad permissions, as this combination grants significant privileges to the MCP server. Only enable these flags when necessary and in trusted environments.

**Resource Management Limitation**: The DataProcessing MCP Server can only update or delete resources that were originally created through it. Resources created by other means cannot be modified or deleted using the DataProcessing MCP Server.


## Installation

| Cursor | VS Code |
|:------:|:-------:|
| [![Install MCP Server](https://cursor.com/deeplink/mcp-install-light.svg)](https://cursor.com/en-US/install-mcp?name=awslabs.aws-dataprocessing-mcp-server&config=eyJjb21tYW5kIjoidXZ4IGF3c2xhYnMuYXdzLWRhdGFwcm9jZXNzaW5nLW1jcC1zZXJ2ZXJAbGF0ZXN0IC0tYWxsb3ctd3JpdGUiLCJlbnYiOnsiRkFTVE1DUF9MT0dfTEVWRUwiOiJFUlJPUiIsIkFXU19SRUdJT04iOiJ1cy1lYXN0LTEifSwiYXV0b0FwcHJvdmUiOltdLCJkaXNhYmxlZCI6ZmFsc2UsInRyYW5zcG9ydFR5cGUiOiJzdGRpbyJ9) | [![Install on VS Code](https://img.shields.io/badge/Install_on-VS_Code-FF9900?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=AWS%20Data%20Processing%20MCP%20Server&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22awslabs.aws-dataprocessing-mcp-server%40latest%22%2C%22--allow-write%22%5D%2C%22env%22%3A%7B%22FASTMCP_LOG_LEVEL%22%3A%22ERROR%22%2C%22AWS_REGION%22%3A%22us-east-1%22%7D%2C%22autoApprove%22%3A%5B%5D%2C%22disabled%22%3Afalse%2C%22transportType%22%3A%22stdio%22%7D) |

## Quickstart

This quickstart guide walks you through the steps to configure the Amazon Data Processing MCP Server for use with both the [Cursor](https://www.cursor.com/en/downloads) IDE and the [Amazon Q Developer CLI](https://github.com/aws/amazon-q-developer-cli). By following these steps, you'll setup your development environment to leverage the Data Processing MCP Server's tools for managing your Glue, EMR and Athena resources.

**Set up Cursor**

1. Open Cursor.
2. Click the gear icon (⚙️) in the top right to open the settings panel, click **MCP**, **Add new global MCP server**.
3. Paste your MCP server definition. For example, this example shows how to configure the Data Processing MCP Server, including enabling mutating actions by adding the `--allow-write` flag to the server arguments:

```
{
  "mcpServers": {
    "aws.dp-mcp": {
      "autoApprove": [],
      "disabled": false,
      "command": "uvx",
      "args": [
        "awslabs.aws-dataprocessing-mcp-server@latest",
        "--allow-write"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "AWS_REGION": "us-east-1"
      },
      "transportType": "stdio"
    }
  }
}
```

### Windows Installation

For Windows users, the MCP server configuration format is slightly different:

```json
{
  "mcpServers": {
    "awslabs.aws-dataprocessing-mcp-server": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "uv",
      "args": [
        "tool",
        "run",
        "--from",
        "awslabs.aws-dataprocessing-mcp-server@latest",
        "awslabs.aws-dataprocessing-mcp-server.exe"
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

After a few minutes, you should see a green indicator if your MCP server definition is valid.

4. Open a chat panel in Cursor (e.g., `Ctrl/⌘ + L`).  In your Cursor chat window, enter your prompt. For example, "Look at all the tables from my account federated across GDC"

**Set up the Amazon Q Developer CLI**

1. Install the [Amazon Q Developer CLI](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line-installing.html) .
2. The Q Developer CLI supports MCP servers for tools and prompts out-of-the-box. Edit your Q developer CLI's MCP configuration file named mcp.json following [these instructions](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line-mcp-configuration.html). For example:

```
{
  "mcpServers": {
    "aws.dp-mcp": {
      "command": "uvx",
      "args": ["awslabs.aws-dataprocessing-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "autoApprove": [],
      "disabled": false
    }
  }
}
```

3. Verify your setup by running the `/tools` command in the Q Developer CLI to see the available Data Processing MCP tools.

Note that this is a basic quickstart. You can enable additional capabilities, such as [running MCP servers in containers](https://github.com/awslabs/mcp?tab=readme-ov-file#running-mcp-servers-in-containers) or combining more MCP servers like the [AWS Documentation MCP Server](https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server/) into a single MCP server definition. To view an example, see the [Installation and Setup](https://github.com/awslabs/mcp?tab=readme-ov-file#installation-and-setup) guide in AWS MCP Servers on GitHub. To view a real-world implementation with application code in context with an MCP server, see the [Server Developer](https://modelcontextprotocol.io/quickstart/server) guide in Anthropic documentation.

## Configurations

### Arguments

The `args` field in the MCP server definition specifies the command-line arguments passed to the server when it starts. These arguments control how the server is executed and configured. For example:

```
{
  "mcpServers": {
    "aws.dp-mcp": {
      "command": "uvx",
      "args": [
        "awslabs.aws-dataprocessing-mcp-server@latest",
        "--allow-write",
        "--allow-sensitive-data-access"
      ],
      "env": {
        "AWS_PROFILE": "your-profile",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

#### `awslabs.aws-dataprocessing-mcp-server@latest` (required)

Specifies the latest package/version specifier for the MCP client config.

* Enables MCP server startup and tool registration.

#### `--allow-write` (optional)

Enables write access mode, which allows mutating operations (e.g., create, update, delete resources)

* Default: false (The server runs in read-only mode by default)
* Example: Add `--allow-write` to the `args` list in your MCP server definition.

#### `--allow-sensitive-data-access` (optional)

Enables access to sensitive data such as logs, events, and Kubernetes Secrets.

* Default: false (Access to sensitive data is restricted by default)
* Example: Add `--allow-sensitive-data-access` to the `args` list in your MCP server definition.

### Environment variables

The `env` field in the MCP server definition allows you to configure environment variables that control the behavior of the DataProcessing MCP server.  For example:

```
{
  "mcpServers": {
    "aws.dp-mcp": {
      "command": "uvx",
      "args": [
        "awslabs.aws-dataprocessing-mcp-server@latest",
        "--allow-write",
        "--allow-sensitive-data-access"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "AWS_PROFILE": "my-profile",
        "AWS_REGION": "us-west-2",
        "CUSTOM_TAGS": "true"  // Skip adding and verifying MCP-managed tags
      }
    }
  }
}
```

#### `FASTMCP_LOG_LEVEL` (optional)

Sets the logging level verbosity for the server.

* Valid values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
* Default: "WARNING"
* Example: `"FASTMCP_LOG_LEVEL": "ERROR"`

#### `AWS_PROFILE` (optional)

Specifies the AWS profile to use for authentication.

* Default: None (If not set, uses default AWS credentials).
* Example: `"AWS_PROFILE": "my-profile"`

#### `AWS_REGION` (optional)

Specifies the AWS region where Glue,EMR clusters or Athena are managed, which will be used for all AWS service operations.

* Default: None (If not set, uses default AWS region).
* Example: `"AWS_REGION": "us-west-2"`

#### `CUSTOM_TAGS` (optional)

Controls whether the MCP server adds and verifies MCP-managed tags on resources.

* When set to 'true', the server will:
  * Skip adding default MCP tags to resources during creation
  * Skip verifying that resources have MCP-managed tags during operations
* Default: None (If not set, MCP tags are added and verified)
* Example: `"CUSTOM_TAGS": "true"`
* **Important**: Enabling this option means resources won't be tagged as MCP-managed. This is done at the owner's consent and responsibility, as it bypasses the built-in resource management safeguards.

## Tools

### Glue Data Catalog Handler Tools

| Tool Name | Description | Key Operations | Requirements |
|-----------|-------------|----------------|--------------|
| manage_aws_glue_databases | Manage AWS Glue Data Catalog databases | create-database, delete-database, get-database, list-databases, update-database | --allow-write flag for create/delete/update operations, appropriate AWS permissions |
| manage_aws_glue_tables | Manage AWS Glue Data Catalog tables | create-table, delete-table, get-table, list-tables, update-table, search-tables | --allow-write flag for create/delete/update operations, database must exist, appropriate AWS permissions |
| manage_aws_glue_connections | Manage AWS Glue Data Catalog connections | create-connection, delete-connection, get-connection, list-connections, update-connection | --allow-write flag for create/delete/update operations, appropriate AWS permissions |
| manage_aws_glue_partitions | Manage AWS Glue Data Catalog partitions | create-partition, delete-partition, get-partition, list-partitions, update-partition | --allow-write flag for create/delete/update operations, database and table must exist, appropriate AWS permissions |
| manage_aws_glue_catalog | Manage AWS Glue Data Catalog | create-catalog, delete-catalog, get-catalog, list-catalogs, import-catalog-to-glue | --allow-write flag for create/delete/import operations, appropriate AWS permissions |

### Glue Interactive Sessions Handler Tools

| Tool Name | Description | Key Operations | Requirements |
|-----------|-------------|----------------|--------------|
| manage_aws_glue_sessions | Manage AWS Glue Interactive Sessions for Spark and Ray workloads | create-session, delete-session, get-session, list-sessions, stop-session | --allow-write flag for create/delete/stop operations, appropriate AWS permissions |
| manage_aws_glue_statements | Execute and manage code statements within Glue Interactive Sessions | run-statement, cancel-statement, get-statement, list-statements | --allow-write flag for run/cancel operations, active session required |

### Glue Workflows and Triggers Handler Tools

| Tool Name | Description | Key Operations | Requirements |
|-----------|-------------|----------------|--------------|
| manage_aws_glue_workflows | Orchestrate complex ETL activities through visual workflows | create-workflow, delete-workflow, get-workflow, list-workflows, start-workflow-run | --allow-write flag for create/delete/start operations, appropriate AWS permissions |
| manage_aws_glue_triggers | Automate workflow and job execution with scheduled or event-based triggers | create-trigger, delete-trigger, get-trigger, get-triggers, start-trigger, stop-trigger | --allow-write flag for create/delete/start/stop operations, appropriate AWS permissions |


### EMR Cluster Handler Tools

| Tool Name | Description | Key Operations | Requirements |
|-----------|-------------|----------------|--------------|
| manage_aws_emr_clusters | Manage Amazon EMR clusters with comprehensive control over cluster lifecycle | create-cluster, describe-cluster, modify-cluster, modify-cluster-attributes, terminate-clusters, list-clusters, create-security-configuration, delete-security-configuration, describe-security-configuration, list-security-configurations | --allow-write flag for create/modify/terminate operations, appropriate AWS permissions |

### EMR Instance Handler Tools

| Tool Name | Description | Key Operations | Requirements |
|-----------|-------------|----------------|--------------|
| manage_aws_emr_ec2_instances | Manage Amazon EMR EC2 instances with both read and write operations | add-instance-fleet, add-instance-groups, modify-instance-fleet, modify-instance-groups, list-instance-fleets, list-instances, list-supported-instance-types | --allow-write flag for add/modify operations, appropriate AWS permissions |

### EMR Steps Handler Tools

| Tool Name | Description | Key Operations | Requirements |
|-----------|-------------|----------------|--------------|
| manage_aws_emr_ec2_steps | Manage Amazon EMR steps for processing data on EMR clusters | add-steps, cancel-steps, describe-step, list-steps | --allow-write flag for add/cancel operations, appropriate AWS permissions |

### Athena Query Handler Tools

| Tool Name | Description | Key Operations | Requirements |
|-----------|-------------|----------------|--------------|
| manage_aws_athena_query_executions | Execute and manage AWS Athena SQL queries | batch-get-query-execution, get-query-execution, get-query-results, get-query-runtime-statistics, list-query-executions, start-query-execution, stop-query-execution | --allow-write flag for start/stop operations, appropriate AWS permissions |
| manage_aws_athena_named_queries | Manage saved SQL queries in AWS Athena | batch-get-named-query, create-named-query, delete-named-query, get-named-query, list-named-queries, update-named-query | --allow-write flag for create/delete/update operations, appropriate AWS permissions |


### Athena Data Catalog Handler Tools

| Tool Name | Description | Key Operations | Requirements |
|-----------|-------------|----------------|--------------|
| manage_aws_athena_data_catalogs | Manage AWS Athena data catalogs | create-data-catalog, delete-data-catalog, get-data-catalog, list-data-catalogs, update-data-catalog | --allow-write flag for create/delete/update operations, appropriate AWS permissions |
| manage_aws_athena_databases_and_tables | Manage AWS Athena databases and tables | get-database, get-table-metadata, list-databases, list-table-metadata | Appropriate AWS permissions for Athena database operations |

### Athena WorkGroup Handler Tools

| Tool Name | Description | Key Operations | Requirements |
|-----------|-------------|----------------|--------------|
| manage_aws_athena_workgroups | Manage AWS Athena workgroups | create-work-group, delete-work-group, get-work-group, list-work-groups, update-work-group | --allow-write flag for create/delete/update operations, appropriate AWS permissions |

### Glue Commons Handler Tools

| Tool Name | Description                                                                 | Key Operations | Requirements                                                                        |
|-----------|-----------------------------------------------------------------------------|----------------|-------------------------------------------------------------------------------------|
| manage_aws_glue_usage_profiles | Manage AWS Glue Usage Profiles for resource allocation and cost management  | create-profile, delete-profile, get-profile, update-profile | --allow-write flag for create/delete/update operations, appropriate AWS permissions |
| manage_aws_glue_security_configurations | Manage AWS Glue Security Configurations for data encryption                 | create-security-configuration, delete-security-configuration, get-security-configuration | --allow-write flag for create/delete operations, appropriate AWS permissions        |
| manage_aws_glue_encryption | Manage AWS Glue catalog encryption settings                                 | get-catalog-encryption-settings, put-catalog-encryption-settings | --allow-write flag for put operations, appropriate AWS permissions                  |
| manage_aws_glue_resource_policies | Manage resource policies for AWS Glue catalogs, databases and tables | get-resource-policy, put-resource-policy, delete-resource-policy | --allow-write flag for put/delete operations, appropriate AWS permissions           |

### Glue ETL Handler Tools

| Tool Name | Description | Key Operations | Requirements |
|-----------|-------------|----------------|--------------|
| manage_aws_glue_jobs | Manage AWS Glue ETL jobs and job runs | create-job, delete-job, get-job, get-jobs, update-job, start-job-run, stop-job-run, get-job-run, get-job-runs, batch-stop-job-run, get-job-bookmark, reset-job-bookmark | --allow-write flag for create/delete/update/start/stop operations, appropriate AWS permissions |

### Glue Crawler Handler Tools

| Tool Name | Description | Key Operations | Requirements |
|-----------|-------------|----------------|--------------|
| manage_aws_glue_crawlers | Manage AWS Glue crawlers to discover and catalog data sources | create-crawler, delete-crawler, get-crawler, get-crawlers, start-crawler, stop-crawler, batch-get-crawlers, list-crawlers, update-crawler | --allow-write flag for create/delete/start/stop/update operations, appropriate AWS permissions |
| manage_aws_glue_classifiers | Manage AWS Glue classifiers to determine data formats and schemas | create-classifier, delete-classifier, get-classifier, get-classifiers, update-classifier | --allow-write flag for create/delete/update operations, appropriate AWS permissions |
| manage_aws_glue_crawler_management | Manage AWS Glue crawler schedules and monitor performance metrics | get-crawler-metrics, start-crawler-schedule, stop-crawler-schedule, update-crawler-schedule | --allow-write flag for schedule operations, appropriate AWS permissions |


### Common Resource Handler Tools

#### IAM Management Tools

| Tool Name | Description | Key Operations | Requirements |
|-----------|-------------|----------------|--------------|
| add_inline_policy | Add a new inline policy to an IAM role | Create inline policies with custom permissions for data processing services | --allow-write flag, role must exist, policy name must be unique |
| get_policies_for_role | Get all policies attached to an IAM role | Retrieve managed and inline policies, assume role policy document, role metadata | Role must exist, valid AWS credentials |
| create_data_processing_role | Create a new IAM role for data processing services | Create roles for Glue/EMR/Athena with trust relationships, attach managed policies, add inline policies | --allow-write flag, unique role name, valid service type (glue/emr/athena) |
| get_roles_for_service | Get all IAM roles that can be assumed by a specific AWS service | List roles with trust relationships for Glue/EMR/Athena services, filter by service principal | Valid AWS credentials, service type parameter |

#### S3 Management Tools

| Tool Name | Description | Key Operations | Requirements |
|-----------|-------------|----------------|--------------|
| list_s3_buckets | List S3 buckets with 'glue' in their name and usage statistics | List buckets by region, show object counts, last modified dates, idle time analysis | Valid AWS credentials, S3:ListAllMyBuckets permission |
| upload_to_s3 | Upload Python code content directly to S3 buckets | Upload scripts for Glue jobs, EMR steps, or other data processing code | --allow-write flag, bucket must exist, S3 write permissions |
| analyze_s3_usage_for_data_processing | Analyze S3 bucket usage patterns for data processing services | Identify buckets used by Glue/EMR/Athena, detect idle buckets, usage recommendations | Valid AWS credentials, permissions for Glue/EMR/Athena service APIs |

## Version

Current MCP server version: 0.1.0
