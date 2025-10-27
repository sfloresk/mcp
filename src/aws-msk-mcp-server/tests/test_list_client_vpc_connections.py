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

"""Tests for the list_client_vpc_connections module."""

import pytest
from awslabs.aws_msk_mcp_server.tools.read_cluster.list_client_vpc_connections import (
    list_client_vpc_connections,
)
from botocore.exceptions import ClientError
from unittest.mock import MagicMock


class TestListClientVpcConnections:
    """Tests for the list_client_vpc_connections module."""

    def test_list_client_vpc_connections_basic(self):
        """Test the list_client_vpc_connections function with basic parameters."""
        # Arrange
        mock_client = MagicMock()
        expected_response = {
            'VpcConnectionInfoList': [
                {
                    'VpcConnectionArn': 'arn:aws:kafka:us-east-1:123456789012:vpc-connection/test-connection/abcdef',
                    'VpcId': 'vpc-12345',
                    'SubnetIds': ['subnet-1', 'subnet-2', 'subnet-3'],
                    'SecurityGroups': ['sg-1'],
                    'CreationTime': '2025-06-20T10:00:00.000Z',
                    'VpcConnectionState': 'ACTIVE',
                }
            ]
        }
        mock_client.list_client_vpc_connections.return_value = expected_response

        # Act
        cluster_arn = 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef'
        result = list_client_vpc_connections(cluster_arn, mock_client)

        # Assert
        mock_client.list_client_vpc_connections.assert_called_once_with(
            ClusterArn=cluster_arn, MaxResults=10
        )
        assert result == expected_response
        assert 'VpcConnectionInfoList' in result
        assert len(result['VpcConnectionInfoList']) == 1
        assert result['VpcConnectionInfoList'][0]['VpcId'] == 'vpc-12345'
        assert result['VpcConnectionInfoList'][0]['VpcConnectionState'] == 'ACTIVE'

    def test_list_client_vpc_connections_with_pagination(self):
        """Test the list_client_vpc_connections function with pagination parameters."""
        # Arrange
        mock_client = MagicMock()
        expected_response = {
            'VpcConnectionInfoList': [
                {
                    'VpcConnectionArn': 'arn:aws:kafka:us-east-1:123456789012:vpc-connection/test-connection/abcdef',
                    'VpcId': 'vpc-12345',
                    'SubnetIds': ['subnet-1', 'subnet-2', 'subnet-3'],
                    'SecurityGroups': ['sg-1'],
                    'CreationTime': '2025-06-20T10:00:00.000Z',
                    'VpcConnectionState': 'ACTIVE',
                }
            ],
            'NextToken': 'next-token-value',
        }
        mock_client.list_client_vpc_connections.return_value = expected_response

        # Act
        cluster_arn = 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef'
        max_results = 5
        next_token = 'token'
        result = list_client_vpc_connections(cluster_arn, mock_client, max_results, next_token)

        # Assert
        mock_client.list_client_vpc_connections.assert_called_once_with(
            ClusterArn=cluster_arn, MaxResults=max_results, NextToken=next_token
        )
        assert result == expected_response
        assert 'VpcConnectionInfoList' in result
        assert 'NextToken' in result
        assert result['NextToken'] == 'next-token-value'

    def test_list_client_vpc_connections_empty_response(self):
        """Test the list_client_vpc_connections function with an empty response."""
        # Arrange
        mock_client = MagicMock()
        expected_response = {'VpcConnectionInfoList': []}
        mock_client.list_client_vpc_connections.return_value = expected_response

        # Act
        cluster_arn = 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef'
        result = list_client_vpc_connections(cluster_arn, mock_client)

        # Assert
        mock_client.list_client_vpc_connections.assert_called_once_with(
            ClusterArn=cluster_arn, MaxResults=10
        )
        assert result == expected_response
        assert 'VpcConnectionInfoList' in result
        assert len(result['VpcConnectionInfoList']) == 0

    def test_list_client_vpc_connections_error(self):
        """Test the list_client_vpc_connections function when the API call fails."""
        # Arrange
        mock_client = MagicMock()
        mock_client.list_client_vpc_connections.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Cluster not found'}},
            'ListClientVpcConnections',
        )

        # Act & Assert
        cluster_arn = 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef'
        with pytest.raises(ClientError) as excinfo:
            list_client_vpc_connections(cluster_arn, mock_client)

        # Verify the error
        assert 'ResourceNotFoundException' in str(excinfo.value)
        assert 'Cluster not found' in str(excinfo.value)
        mock_client.list_client_vpc_connections.assert_called_once_with(
            ClusterArn=cluster_arn, MaxResults=10
        )

    def test_list_client_vpc_connections_missing_client(self):
        """Test the list_client_vpc_connections function with a missing client."""
        # Act & Assert
        cluster_arn = 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef'
        with pytest.raises(ValueError) as excinfo:
            list_client_vpc_connections(cluster_arn, None)

        # Verify the error
        assert 'Client must be provided' in str(excinfo.value)
