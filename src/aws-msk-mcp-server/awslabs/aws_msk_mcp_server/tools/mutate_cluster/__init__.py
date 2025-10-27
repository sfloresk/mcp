# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Infrastructure Management API Module

This module provides functions to manage infrastructure aspects of MSK clusters.
"""

import json
from typing import Optional

import boto3
from botocore.config import Config
from awslabs.aws_msk_mcp_server import __version__
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..common_functions import check_mcp_generated_tag
from .batch_associate_scram_secret import batch_associate_scram_secret
from .batch_disassociate_scram_secret import batch_disassociate_scram_secret
from .create_cluster_v2 import create_cluster_v2
from .put_cluster_policy import put_cluster_policy
from .reboot_broker import reboot_broker
from .update_broker_count import update_broker_count
from .update_broker_storage import update_broker_storage
from .update_broker_type import update_broker_type
from .update_cluster_configuration import update_cluster_configuration
from .update_monitoring import update_monitoring
from .update_security import update_security


def register_module(mcp: FastMCP) -> None:
    @mcp.tool(name='create_cluster', description='Creates a new MSK cluster.')
    def create_cluster_tool(
        region: str = Field(..., description="AWS region (e.g., 'us-east-1', 'eu-west-1')"),
        cluster_name: str = Field(
            ...,
            description='The name of the cluster (must be 1-64 characters, alphanumeric and hyphens only)',
        ),
        cluster_type: str = Field(
            'PROVISIONED', description='Type of cluster to create (PROVISIONED or SERVERLESS)'
        ),
        kwargs: str = Field(
            '{}', description='JSON string containing additional arguments based on cluster type'
        ),
    ):
        """
        Creates a new MSK cluster.

        IMPORTANT: Follow this step-by-step process to create an MSK cluster:

        Step 1: Ask the user for the AWS region (e.g., "us-east-1", "eu-west-1")

        Step 2: Ask the user for the cluster name (must be 1-64 characters, alphanumeric and hyphens only)

        Step 3: Ask the user to choose the cluster type (PROVISIONED or SERVERLESS)

        Step 4: Gather the required information based on the cluster type:

        For PROVISIONED clusters:
        - Subnet IDs (at least 3 in different Availability Zones)
        - Security group IDs
        - Instance type (e.g., kafka.m5.large)
        - Kafka version (ALWAYS use get_global_info tool with info_type="kafka_versions" to retrieve available versions)
        - Number of broker nodes
        - Storage volume size

        For SERVERLESS clusters:
        - VPC configuration details

        Resource Identification Guide:

        1. For subnet IDs:
           - Use this EXACT AWS CLI command with the user's region:
             `aws ec2 describe-subnets --region <region> --query "Subnets[*].[SubnetId,VpcId,AvailabilityZone,CidrBlock]" --output table`
           - Or direct the user to AWS Console: VPC > Subnets
           - Note: At least 3 subnet IDs in different Availability Zones are required for high availability

        2. For security group IDs:
           - Use this EXACT AWS CLI command with the user's region:
             `aws ec2 describe-security-groups --region <region> --query "SecurityGroups[*].[GroupId,GroupName,Description]" --output table`
           - Or direct the user to AWS Console: EC2 > Security Groups
           - Note: Security groups must allow Kafka ports (9092, 9094, 2181)

        3. For Kafka version:
           - ALWAYS use the get_global_info tool with info_type="kafka_versions" and the user's region:
             Example: get_global_info(region="us-east-1", info_type="kafka_versions")

        Args:
            cluster_name (str): The name of the cluster (must be 1-64 characters, alphanumeric and hyphens only)
            cluster_type (str): Type of cluster to create (PROVISIONED or SERVERLESS)
            region (str): AWS region (e.g., "us-east-1", "eu-west-1")
            kwargs (str): JSON string containing additional arguments based on cluster type:
                For PROVISIONED (all of these are required):
                    broker_node_group_info (dict): Information about the broker nodes
                        - InstanceType (str): The type of Amazon EC2 instance (e.g., "kafka.m5.large")
                        - ClientSubnets (list): A list of valid subnet IDs (at least 3 recommended)
                        - SecurityGroups (list): A list of valid security group IDs
                        - StorageInfo (dict, optional): Storage settings
                            - EbsStorageInfo (dict): EBS storage settings
                                - VolumeSize (int): The size in GiB (100-16384)
                    kafka_version (str): Apache Kafka version (e.g., "2.8.1", "3.3.1")
                    number_of_broker_nodes (int): Number of broker nodes (must match the number of subnets)
                    client_authentication (dict, optional): Authentication settings
                    encryption_info (dict, optional): Encryption settings
                    enhanced_monitoring (str, optional): Monitoring level
                    open_monitoring (dict, optional): Prometheus monitoring settings
                    logging_info (dict, optional): Log delivery settings
                    configuration_info (dict, optional): Cluster configuration
                    storage_mode (str, optional): Storage tier mode
                    tags (dict, optional): Resource tags
                For SERVERLESS (required):
                    vpc_configs (list): VPC configuration
                    client_authentication (dict, optional): Authentication settings
                    tags (dict, optional): Resource tags

                Example for PROVISIONED: '{"broker_node_group_info": {"InstanceType": "kafka.m5.large", "ClientSubnets": ["subnet-0a1b2c3d", "subnet-1a2b3c4d", "subnet-2a3b4c5d"], "SecurityGroups": ["sg-0a1b2c3d"], "StorageInfo": {"EbsStorageInfo": {"VolumeSize": 100}}}, "kafka_version": "2.8.1", "number_of_broker_nodes": 3}'

                Example for SERVERLESS: '{"vpc_configs": [{"SubnetIds": ["subnet-0a1b2c3d", "subnet-1a2b3c4d", "subnet-2a3b4c5d"], "SecurityGroupIds": ["sg-0a1b2c3d"]}]}'

        Returns:
            dict: Result of the cluster creation operation containing:
                - ClusterArn (str): The Amazon Resource Name (ARN) of the cluster
                - ClusterName (str): The name of the cluster
                - State (str): The state of the cluster (e.g., CREATING)
                - ClusterType (str): The type of the cluster (PROVISIONED or SERVERLESS)
                - CreationTime (datetime): The time when the cluster was created
                - CurrentVersion (str): The current version of the cluster
                - Tags (dict, optional): Tags attached to the cluster

        Note:
            After creating a cluster, you should follow up with a tag_resource tool call
            to add the "MCP Generated" tag to the created resource.
            Example:
            tag_resource_tool(resource_arn=response["ClusterArn"], tags={"MCP Generated": "true"})
        """
        # Create a boto3 client
        client = boto3.client(
            'kafka',
            region_name=region,
            config=Config(user_agent_extra=f'awslabs/mcp/aws-msk-mcp-server/{__version__}'),
        )

        # Handle kwargs whether it's a string or a dictionary
        if kwargs:
            if isinstance(kwargs, str):
                try:
                    kwargs_dict = json.loads(kwargs)
                except json.JSONDecodeError:
                    kwargs_dict = {}
            else:
                # If kwargs is already a dictionary, use it directly
                kwargs_dict = kwargs
        else:
            kwargs_dict = {}

        return create_cluster_v2(cluster_name, cluster_type, client=client, **kwargs_dict)

    @mcp.tool(
        name='update_broker_storage', description='Updates broker storage size in an MSK cluster.'
    )
    def update_broker_storage_tool(
        region: str = Field(..., description='AWS region'),
        cluster_arn: str = Field(
            ..., description='The Amazon Resource Name (ARN) that uniquely identifies the cluster'
        ),
        current_version: str = Field(..., description='The version of cluster to update from'),
        target_broker_ebs_volume_info: str = Field(
            ...,
            description='List of dictionaries describing the target volume size and broker IDs',
        ),
    ):
        """
        Updates the storage size of brokers in an MSK cluster.

        Args:
            cluster_arn (str): The Amazon Resource Name (ARN) that uniquely identifies the cluster
            current_version (str): The version of cluster to update from
            target_broker_ebs_volume_info (list): List of dictionaries describing the target volume size and broker IDs
                Example: [
                    {
                        "KafkaBrokerNodeId": "ALL",
                        "VolumeSizeGB": 1100,
                        "ProvisionedThroughput": {
                            "Enabled": True,
                            "VolumeThroughput": 250
                        }
                    }
                ]
            region (str): AWS region

        Returns:
            dict: Result of the update operation containing:
                - ClusterArn (str): The Amazon Resource Name (ARN) of the cluster
                - ClusterOperationArn (str): The ARN of the cluster operation that was created

        Note:
            This operation can ONLY be performed on resources tagged with "MCP Generated".
            Ensure the resource has this tag before attempting to update it.
        """
        # Create a boto3 client
        client = boto3.client(
            'kafka',
            region_name=region,
            config=Config(user_agent_extra=f'awslabs/mcp/aws-msk-mcp-server/{__version__}'),
        )

        # Check if the resource has the "MCP Generated" tag
        if not check_mcp_generated_tag(cluster_arn, client):
            raise ValueError(
                f"Resource {cluster_arn} does not have the 'MCP Generated' tag. "
                "This operation can only be performed on resources tagged with 'MCP Generated'."
            )

        return update_broker_storage(
            cluster_arn, current_version, target_broker_ebs_volume_info, client
        )

    @mcp.tool(
        name='update_broker_type', description='Updates broker instance type in an MSK cluster.'
    )
    def update_broker_type_tool(
        region: str = Field(..., description='AWS region'),
        cluster_arn: str = Field(
            ..., description='The Amazon Resource Name (ARN) that uniquely identifies the cluster'
        ),
        current_version: str = Field(
            ..., description='The cluster version that you want to change'
        ),
        target_instance_type: str = Field(
            ..., description='The Amazon MSK broker type that you want all brokers to be'
        ),
    ):
        """
        Updates the broker type in an MSK cluster.

        Args:
            cluster_arn (str): The Amazon Resource Name (ARN) that uniquely identifies the cluster
            current_version (str): The cluster version that you want to change
            target_instance_type (str): The Amazon MSK broker type that you want all brokers to be
                Example: "kafka.m5.large", "kafka.m5.xlarge", "kafka.m5.2xlarge"
            region (str): AWS region

        Returns:
            dict: Result of the update operation containing ClusterArn and ClusterOperationArn

        Note:
            This operation can ONLY be performed on resources tagged with "MCP Generated".
            Ensure the resource has this tag before attempting to update it.
        """
        # Create a boto3 client
        client = boto3.client(
            'kafka',
            region_name=region,
            config=Config(user_agent_extra=f'awslabs/mcp/aws-msk-mcp-server/{__version__}'),
        )

        # Check if the resource has the "MCP Generated" tag
        if not check_mcp_generated_tag(cluster_arn, client):
            raise ValueError(
                f"Resource {cluster_arn} does not have the 'MCP Generated' tag. "
                "This operation can only be performed on resources tagged with 'MCP Generated'."
            )

        return update_broker_type(cluster_arn, current_version, target_instance_type, client)

    @mcp.tool(
        name='update_cluster_configuration',
        description='Updates cluster configuration for an MSK cluster.',
    )
    def update_cluster_configuration_tool(
        region: str = Field(..., description='AWS region'),
        cluster_arn: str = Field(
            ..., description='The Amazon Resource Name (ARN) that uniquely identifies the cluster'
        ),
        configuration_arn: str = Field(
            ..., description='The Amazon Resource Name (ARN) of the configuration to use'
        ),
        configuration_revision: int = Field(
            ..., description='The revision of the configuration to use'
        ),
        current_version: str = Field(
            ..., description='The version of the cluster that you want to update'
        ),
    ):
        """
        Updates the configuration of an MSK cluster.

        Args:
            cluster_arn (str): The Amazon Resource Name (ARN) that uniquely identifies the cluster
            configuration_arn (str): The Amazon Resource Name (ARN) of the configuration to use
            configuration_revision (int): The revision of the configuration to use
            current_version (str): The version of the cluster that you want to update
            region (str): AWS region

        Returns:
            dict: Result of the update operation containing ClusterArn and ClusterOperationArn

        Note:
            This operation can ONLY be performed on resources tagged with "MCP Generated".
            Ensure the resource has this tag before attempting to update it.
        """
        # Create a boto3 client
        client = boto3.client(
            'kafka',
            region_name=region,
            config=Config(user_agent_extra=f'awslabs/mcp/aws-msk-mcp-server/{__version__}'),
        )

        # Check if the resource has the "MCP Generated" tag
        if not check_mcp_generated_tag(cluster_arn, client):
            raise ValueError(
                f"Resource {cluster_arn} does not have the 'MCP Generated' tag. "
                "This operation can only be performed on resources tagged with 'MCP Generated'."
            )

        return update_cluster_configuration(
            cluster_arn, configuration_arn, configuration_revision, current_version, client
        )

    @mcp.tool(
        name='update_monitoring', description='Updates monitoring settings for an MSK cluster.'
    )
    def update_monitoring_tool(
        region: str = Field(..., description='AWS region'),
        cluster_arn: str = Field(
            ..., description='The Amazon Resource Name (ARN) that uniquely identifies the cluster'
        ),
        current_version: str = Field(
            ..., description='The version of the cluster that you want to update'
        ),
        enhanced_monitoring: str = Field(
            ..., description='Specifies the level of monitoring for the MSK cluster'
        ),
        open_monitoring: Optional[dict] = Field(
            None, description='The settings for open monitoring with Prometheus'
        ),
        logging_info: Optional[dict] = Field(
            None, description='The settings for broker logs delivery'
        ),
    ):
        """
        Updates the monitoring settings of an MSK cluster.

        Args:
            cluster_arn (str): The Amazon Resource Name (ARN) that uniquely identifies the cluster
            current_version (str): The version of the cluster that you want to update
            enhanced_monitoring (str): Specifies the level of monitoring for the MSK cluster.
                Options: DEFAULT, PER_BROKER, PER_TOPIC_PER_BROKER, PER_TOPIC_PER_PARTITION
            open_monitoring (dict, optional): The settings for open monitoring with Prometheus
                Example: {
                    "Prometheus": {
                        "JmxExporter": {"EnabledInBroker": True},
                        "NodeExporter": {"EnabledInBroker": True}
                    }
                }
            logging_info (dict, optional): The settings for broker logs delivery
                Example: {
                    "BrokerLogs": {
                        "CloudWatchLogs": {"Enabled": True, "LogGroup": "my-log-group"},
                        "Firehose": {"Enabled": True, "DeliveryStream": "my-stream"},
                        "S3": {"Enabled": True, "Bucket": "my-bucket", "Prefix": "logs/"}
                    }
                }
            region (str): AWS region

        Returns:
            dict: Result of the update operation containing ClusterArn and ClusterOperationArn

        Note:
            This operation can ONLY be performed on resources tagged with "MCP Generated".
            Ensure the resource has this tag before attempting to update it.
        """
        # Create a boto3 client
        client = boto3.client(
            'kafka',
            region_name=region,
            config=Config(user_agent_extra=f'awslabs/mcp/aws-msk-mcp-server/{__version__}'),
        )

        # Check if the resource has the "MCP Generated" tag
        if not check_mcp_generated_tag(cluster_arn, client):
            raise ValueError(
                f"Resource {cluster_arn} does not have the 'MCP Generated' tag. "
                "This operation can only be performed on resources tagged with 'MCP Generated'."
            )

        kwargs = {}
        if open_monitoring:
            kwargs['open_monitoring'] = open_monitoring
        if logging_info:
            kwargs['logging_info'] = logging_info

        return update_monitoring(
            cluster_arn, current_version, enhanced_monitoring, client=client, **kwargs
        )

    @mcp.tool(name='update_security', description='Updates security settings for an MSK cluster.')
    def update_security_tool(
        region: str = Field(..., description='AWS region'),
        cluster_arn: str = Field(
            ..., description='The Amazon Resource Name (ARN) that uniquely identifies the cluster'
        ),
        current_version: str = Field(
            ..., description='The version of the cluster that you want to update'
        ),
        client_authentication: Optional[dict] = Field(
            None, description='Client authentication settings'
        ),
        encryption_info: Optional[dict] = Field(None, description='Encryption settings'),
    ):
        """
        Updates the security settings of an MSK cluster.

        Args:
            cluster_arn (str): The Amazon Resource Name (ARN) that uniquely identifies the cluster
            current_version (str): The version of the cluster that you want to update
            client_authentication (dict, optional): Client authentication settings
                Example: {
                    "Sasl": {
                        "Scram": {"Enabled": True},
                        "Iam": {"Enabled": True}
                    },
                    "Tls": {"Enabled": True, "CertificateAuthorityArnList": ["arn:aws:acm:..."]}
                }
            encryption_info (dict, optional): Encryption settings
                Example: {
                    "EncryptionInTransit": {
                        "InCluster": True,
                        "ClientBroker": "TLS"
                    },
                    "EncryptionAtRest": {
                        "DataVolumeKMSKeyId": "alias/aws/kafka"
                    }
                }
            region (str): AWS region

        Returns:
            dict: Result of the update operation containing ClusterArn and ClusterOperationArn

        Note:
            This operation can ONLY be performed on resources tagged with "MCP Generated".
            Ensure the resource has this tag before attempting to update it.
        """
        # Create a boto3 client
        client = boto3.client(
            'kafka',
            region_name=region,
            config=Config(user_agent_extra=f'awslabs/mcp/aws-msk-mcp-server/{__version__}'),
        )

        # Check if the resource has the "MCP Generated" tag
        if not check_mcp_generated_tag(cluster_arn, client):
            raise ValueError(
                f"Resource {cluster_arn} does not have the 'MCP Generated' tag. "
                "This operation can only be performed on resources tagged with 'MCP Generated'."
            )

        kwargs = {}
        if client_authentication:
            kwargs['client_authentication'] = client_authentication
        if encryption_info:
            kwargs['encryption_info'] = encryption_info

        return update_security(cluster_arn, current_version, client=client, **kwargs)

    @mcp.tool(
        name='put_cluster_policy', description='Attaches a resource policy to an MSK cluster.'
    )
    def put_cluster_policy_tool(
        region: str = Field(description='AWS region'),
        cluster_arn: str = Field(
            description='The Amazon Resource Name (ARN) that uniquely identifies the cluster'
        ),
        policy: dict = Field(description='The JSON policy to attach to the cluster'),
    ):
        """
        Puts a resource policy on an MSK cluster.

        Args:
            cluster_arn (str): The Amazon Resource Name (ARN) that uniquely identifies the cluster
            policy (dict): The JSON policy to attach to the cluster
                Example: {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "arn:aws:iam::123456789012:role/ExampleRole"},
                            "Action": [
                                "kafka:GetBootstrapBrokers",
                                "kafka:DescribeCluster"
                            ],
                            "Resource": "arn:aws:kafka:us-east-1:123456789012:cluster/example-cluster/*"
                        }
                    ]
                }
            region (str): AWS region

        Returns:
            dict: Result of the operation

        Note:
            This operation can ONLY be performed on resources tagged with "MCP Generated".
            Ensure the resource has this tag before attempting to update it.
        """
        # Create a boto3 client
        client = boto3.client(
            'kafka',
            region_name=region,
            config=Config(user_agent_extra=f'awslabs/mcp/aws-msk-mcp-server/{__version__}'),
        )

        # Check if the resource has the "MCP Generated" tag
        if not check_mcp_generated_tag(cluster_arn, client):
            raise ValueError(
                f"Resource {cluster_arn} does not have the 'MCP Generated' tag. "
                "This operation can only be performed on resources tagged with 'MCP Generated'."
            )

        return put_cluster_policy(cluster_arn, policy, client)

    @mcp.tool(name='update_broker_count', description='Updates broker count in an MSK cluster.')
    def update_broker_count_tool(
        region: str = Field(description='AWS region'),
        cluster_arn: str = Field(
            description='The Amazon Resource Name (ARN) that uniquely identifies the cluster'
        ),
        current_version: str = Field(
            description='The version of the cluster that you want to update'
        ),
        target_number_of_broker_nodes: int = Field(
            description='The number of broker nodes that you want the cluster to have'
        ),
    ):
        """
        Updates the number of brokers in an MSK cluster.

        Args:
            cluster_arn (str): The Amazon Resource Name (ARN) that uniquely identifies the cluster
            current_version (str): The version of the cluster that you want to update
            target_number_of_broker_nodes (int): The number of broker nodes that you want the cluster to have
                Note: Must be a multiple of the number of Availability Zones in the current cluster
            region (str): AWS region

        Returns:
            dict: Result of the update operation containing ClusterArn and ClusterOperationArn

        Note:
            This operation can ONLY be performed on resources tagged with "MCP Generated".
            Ensure the resource has this tag before attempting to update it.
        """
        # Create a boto3 client
        client = boto3.client(
            'kafka',
            region_name=region,
            config=Config(user_agent_extra=f'awslabs/mcp/aws-msk-mcp-server/{__version__}'),
        )

        # Check if the resource has the "MCP Generated" tag
        if not check_mcp_generated_tag(cluster_arn, client):
            raise ValueError(
                f"Resource {cluster_arn} does not have the 'MCP Generated' tag. "
                "This operation can only be performed on resources tagged with 'MCP Generated'."
            )

        return update_broker_count(
            cluster_arn, current_version, target_number_of_broker_nodes, client
        )

    @mcp.tool(
        name='associate_scram_secret', description='Associates SCRAM secrets with an MSK cluster.'
    )
    def associate_scram_secret_tool(
        region: str = Field(description='AWS region'),
        cluster_arn: str = Field(description='The ARN of the cluster'),
        secret_arns: list = Field(description='List of secret ARNs to associate'),
    ):
        """
        Associates SCRAM secrets with an MSK cluster.

        Args:
            cluster_arn (str): The ARN of the cluster
            secret_arns (list): List of secret ARNs to associate
            region (str): AWS region

        Returns:
            dict: Result of the operation

        Note:
            This operation can ONLY be performed on resources tagged with "MCP Generated".
            Ensure the resource has this tag before attempting to update it.
        """
        # Create a boto3 client
        client = boto3.client(
            'kafka',
            region_name=region,
            config=Config(user_agent_extra=f'awslabs/mcp/aws-msk-mcp-server/{__version__}'),
        )

        # Check if the resource has the "MCP Generated" tag
        if not check_mcp_generated_tag(cluster_arn, client):
            raise ValueError(
                f"Resource {cluster_arn} does not have the 'MCP Generated' tag. "
                "This operation can only be performed on resources tagged with 'MCP Generated'."
            )

        return batch_associate_scram_secret(cluster_arn, secret_arns, client)

    @mcp.tool(
        name='disassociate_scram_secret',
        description='Disassociates SCRAM secrets from an MSK cluster.',
    )
    def disassociate_scram_secret_tool(
        region: str = Field(description='AWS region'),
        cluster_arn: str = Field(description='The ARN of the cluster'),
        secret_arns: list = Field(description='List of secret ARNs to disassociate'),
    ):
        """
        Disassociates SCRAM secrets from an MSK cluster.

        Args:
            cluster_arn (str): The ARN of the cluster
            secret_arns (list): List of secret ARNs to disassociate
            region (str): AWS region

        Returns:
            dict: Result of the operation

        Note:
            This operation can ONLY be performed on resources tagged with "MCP Generated".
            Ensure the resource has this tag before attempting to update it.
        """
        # Create a boto3 client
        client = boto3.client(
            'kafka',
            region_name=region,
            config=Config(user_agent_extra=f'awslabs/mcp/aws-msk-mcp-server/{__version__}'),
        )

        # Check if the resource has the "MCP Generated" tag
        if not check_mcp_generated_tag(cluster_arn, client):
            raise ValueError(
                f"Resource {cluster_arn} does not have the 'MCP Generated' tag. "
                "This operation can only be performed on resources tagged with 'MCP Generated'."
            )

        return batch_disassociate_scram_secret(cluster_arn, secret_arns, client)

    @mcp.tool(name='reboot_broker', description='Reboots brokers in an MSK cluster.')
    def reboot_broker_tool(
        region: str = Field(description='AWS region'),
        cluster_arn: str = Field(description='The ARN of the cluster'),
        broker_ids: list = Field(description='List of broker IDs to reboot'),
    ):
        """
        Reboots brokers in an MSK cluster.

        Args:
            cluster_arn (str): The ARN of the cluster
            broker_ids (list): List of broker IDs to reboot
            region (str): AWS region

        Returns:
            dict: Result of the operation
        """
        # Create a boto3 client
        client = boto3.client(
            'kafka',
            region_name=region,
            config=Config(user_agent_extra=f'awslabs/mcp/aws-msk-mcp-server/{__version__}'),
        )
        return reboot_broker(cluster_arn, broker_ids, client)
