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
"""Function to delete a VPC connection for an MSK cluster.

Maps to AWS CLI command: aws kafka delete-vpc-connection.
"""

from ..common_functions import check_mcp_generated_tag


def delete_vpc_connection(vpc_connection_arn, client):
    """Deletes a VPC connection for an MSK cluster.

    Args:
        vpc_connection_arn (str): The Amazon Resource Name (ARN) of the VPC connection
        client (boto3.client): Boto3 client for Kafka. Must be provided by the tool function.

    Returns:
        dict: Information about the deleted VPC connection
    """
    if client is None:
        raise ValueError(
            'Client must be provided. This function should only be called from a tool function.'
        )

    if not check_mcp_generated_tag(vpc_connection_arn, client):
        raise ValueError(
            f"Resource {vpc_connection_arn} does not have the 'MCP Generated' tag. "
            "This operation can only be performed on resources tagged with 'MCP Generated'."
        )

    response = client.delete_vpc_connection(VpcConnectionArn=vpc_connection_arn)

    return response
