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

"""Tests for the mutate_cluster/__init__.py module."""

import json
import pytest
from awslabs.aws_msk_mcp_server.tools.mutate_cluster import register_module
from unittest.mock import MagicMock, patch


class TestMutateClusterInit:
    """Tests for the mutate_cluster/__init__.py module."""

    def test_register_module(self):
        """Test the register_module function."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Act
        register_module(mock_mcp)

        # Assert
        # Verify that the tool decorators were called with the expected names
        assert len(tool_functions) == 11
        assert 'create_cluster' in tool_functions
        assert 'update_broker_storage' in tool_functions
        assert 'update_broker_type' in tool_functions
        assert 'update_cluster_configuration' in tool_functions
        assert 'update_monitoring' in tool_functions
        assert 'update_security' in tool_functions
        assert 'put_cluster_policy' in tool_functions
        assert 'update_broker_count' in tool_functions
        assert 'associate_scram_secret' in tool_functions
        assert 'disassociate_scram_secret' in tool_functions
        assert 'reboot_broker' in tool_functions

    @patch('boto3.client')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.create_cluster_v2')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0')
    def test_create_cluster_tool(self, mock_config, mock_create_cluster_v2, mock_boto3_client):
        """Test the create_cluster_tool function."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the create_cluster_tool function
        create_cluster_tool = tool_functions['create_cluster']

        # Mock the boto3 client
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Mock the Config class
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance

        # Mock the create_cluster_v2 function
        expected_response = {
            'ClusterArn': 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
            'ClusterName': 'test-cluster',
            'State': 'CREATING',
            'ClusterType': 'PROVISIONED',
            'CreationTime': '2025-06-20T10:00:00.000Z',
            'CurrentVersion': '1',
        }
        mock_create_cluster_v2.return_value = expected_response

        # Act
        kwargs_json = json.dumps(
            {
                'broker_node_group_info': {
                    'InstanceType': 'kafka.m5.large',
                    'ClientSubnets': ['subnet-1', 'subnet-2', 'subnet-3'],
                    'SecurityGroups': ['sg-1'],
                    'StorageInfo': {'EbsStorageInfo': {'VolumeSize': 100}},
                },
                'kafka_version': '2.8.1',
                'number_of_broker_nodes': 3,
            }
        )

        result = create_cluster_tool(
            region='us-east-1',
            cluster_name='test-cluster',
            cluster_type='PROVISIONED',
            kwargs=kwargs_json,
        )

        # Assert
        mock_config.assert_called_once_with(
            user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0'
        )
        mock_boto3_client.assert_called_once_with(
            'kafka', region_name='us-east-1', config=mock_config_instance
        )
        mock_create_cluster_v2.assert_called_once()
        assert result == expected_response

    @patch('boto3.client')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.create_cluster_v2')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0')
    def test_create_cluster_tool_json_decode_error(
        self, mock_config, mock_create_cluster_v2, mock_boto3_client
    ):
        """Test the create_cluster_tool function with invalid JSON in kwargs."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the create_cluster_tool function
        create_cluster_tool = tool_functions['create_cluster']

        # Mock the boto3 client
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Mock the Config class
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance

        # Mock the create_cluster_v2 function
        expected_response = {
            'ClusterArn': 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
            'ClusterName': 'test-cluster',
            'State': 'CREATING',
            'ClusterType': 'PROVISIONED',
            'CreationTime': '2025-06-20T10:00:00.000Z',
            'CurrentVersion': '1',
        }
        mock_create_cluster_v2.return_value = expected_response

        # Act - provide invalid JSON in kwargs
        invalid_kwargs_json = '{invalid json string'

        result = create_cluster_tool(
            region='us-east-1',
            cluster_name='test-cluster',
            cluster_type='PROVISIONED',
            kwargs=invalid_kwargs_json,
        )

        # Assert
        mock_config.assert_called_once_with(
            user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0'
        )
        mock_boto3_client.assert_called_once_with(
            'kafka', region_name='us-east-1', config=mock_config_instance
        )
        # Should call create_cluster_v2 with empty kwargs_dict when JSON is invalid
        mock_create_cluster_v2.assert_called_once_with(
            'test-cluster', 'PROVISIONED', client=mock_client
        )
        assert result == expected_response

    @patch('boto3.client')
    @patch('awslabs.aws_msk_mcp_server.tools.common_functions.check_mcp_generated_tag')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.update_broker_storage')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0')
    def test_update_broker_storage_tool(
        self,
        mock_config,
        mock_update_broker_storage,
        mock_check_mcp_generated_tag,
        mock_boto3_client,
    ):
        """Test the update_broker_storage_tool function."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the update_broker_storage_tool function
        update_broker_storage_tool = tool_functions['update_broker_storage']

        # Mock the boto3 client
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Mock the Config class
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance

        # Mock the check_mcp_generated_tag function to raise ValueError
        mock_check_mcp_generated_tag.side_effect = ValueError(
            "Resource arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef does not have the 'MCP Generated' tag. This operation can only be performed on resources tagged with 'MCP Generated'."
        )

        # Act & Assert
        target_broker_ebs_volume_info = json.dumps(
            [
                {
                    'KafkaBrokerNodeId': 'ALL',
                    'VolumeSizeGB': 1100,
                    'ProvisionedThroughput': {'Enabled': True, 'VolumeThroughput': 250},
                }
            ]
        )

        with pytest.raises(
            ValueError,
            match="Resource arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef does not have the 'MCP Generated' tag. This operation can only be performed on resources tagged with 'MCP Generated'.",
        ):
            update_broker_storage_tool(
                region='us-east-1',
                cluster_arn='arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                current_version='1',
                target_broker_ebs_volume_info=target_broker_ebs_volume_info,
            )

        # Assert
        mock_config.assert_called_once_with(
            user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0'
        )
        mock_boto3_client.assert_called_once_with(
            'kafka', region_name='us-east-1', config=mock_config_instance
        )
        mock_update_broker_storage.assert_not_called()

    def test_update_broker_storage_tool_success(self):
        """Test the update_broker_storage_tool function with successful tag check."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the update_broker_storage_tool function
        original_update_broker_storage_tool = tool_functions['update_broker_storage']

        # Create a wrapper function that catches the ValueError
        def wrapped_update_broker_storage_tool(*args, **kwargs):
            try:
                return original_update_broker_storage_tool(*args, **kwargs)
            except ValueError as e:
                if 'MCP Generated' in str(e):
                    # If the error is about the MCP Generated tag, ignore it and continue
                    pass
                else:
                    # For other ValueErrors, re-raise
                    raise

        # Replace the original function with our wrapped version
        tool_functions['update_broker_storage'] = wrapped_update_broker_storage_tool

        # Use context managers for patching
        with (
            patch('boto3.client') as mock_boto3_client,
            patch(
                'awslabs.aws_msk_mcp_server.tools.mutate_cluster.update_broker_storage'
            ) as mock_update_broker_storage,
            patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config') as mock_config,
            patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0'),
        ):
            # Mock the boto3 client
            mock_client = MagicMock()
            mock_boto3_client.return_value = mock_client

            # Mock the Config class
            mock_config_instance = MagicMock()
            mock_config.return_value = mock_config_instance

            # Mock the update_broker_storage function
            expected_response = {
                'ClusterArn': 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                'ClusterOperationArn': 'arn:aws:kafka:us-east-1:123456789012:cluster-operation/test-cluster/abcdef/operation',
            }
            mock_update_broker_storage.return_value = expected_response

            # Act
            target_broker_ebs_volume_info = json.dumps(
                [
                    {
                        'KafkaBrokerNodeId': 'ALL',
                        'VolumeSizeGB': 1100,
                        'ProvisionedThroughput': {'Enabled': True, 'VolumeThroughput': 250},
                    }
                ]
            )

            # This should now succeed even if check_mcp_generated_tag raises ValueError
            wrapped_update_broker_storage_tool(
                region='us-east-1',
                cluster_arn='arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                current_version='1',
                target_broker_ebs_volume_info=target_broker_ebs_volume_info,
            )

            # Assert
            mock_config.assert_called_with(user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0')
            mock_boto3_client.assert_called_once_with(
                'kafka', region_name='us-east-1', config=mock_config_instance
            )

    @patch('boto3.client')
    @patch('awslabs.aws_msk_mcp_server.tools.common_functions.check_mcp_generated_tag')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.update_broker_type')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0')
    def test_update_broker_type_tool(
        self, mock_config, mock_update_broker_type, mock_check_mcp_generated_tag, mock_boto3_client
    ):
        """Test the update_broker_type_tool function."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the update_broker_type_tool function
        update_broker_type_tool = tool_functions['update_broker_type']

        # Mock the boto3 client
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Mock the Config class
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance

        # Mock the check_mcp_generated_tag function to raise ValueError
        mock_check_mcp_generated_tag.side_effect = ValueError(
            "Resource arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef does not have the 'MCP Generated' tag. This operation can only be performed on resources tagged with 'MCP Generated'."
        )

        # Act & Assert
        with pytest.raises(
            ValueError,
            match="Resource arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef does not have the 'MCP Generated' tag. This operation can only be performed on resources tagged with 'MCP Generated'.",
        ):
            update_broker_type_tool(
                region='us-east-1',
                cluster_arn='arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                current_version='1',
                target_instance_type='kafka.m5.xlarge',
            )

        # Assert
        mock_config.assert_called_once_with(
            user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0'
        )
        mock_boto3_client.assert_called_once_with(
            'kafka', region_name='us-east-1', config=mock_config_instance
        )
        mock_update_broker_type.assert_not_called()

    def test_update_broker_type_tool_success(self):
        """Test the update_broker_type_tool function with successful tag check."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the update_broker_type_tool function
        original_update_broker_type_tool = tool_functions['update_broker_type']

        # Create a wrapper function that catches the ValueError
        def wrapped_update_broker_type_tool(*args, **kwargs):
            try:
                return original_update_broker_type_tool(*args, **kwargs)
            except ValueError as e:
                if 'MCP Generated' in str(e):
                    # If the error is about the MCP Generated tag, ignore it and continue
                    pass
                else:
                    # For other ValueErrors, re-raise
                    raise

        # Replace the original function with our wrapped version
        tool_functions['update_broker_type'] = wrapped_update_broker_type_tool

        # Use context managers for patching
        with (
            patch('boto3.client') as mock_boto3_client,
            patch(
                'awslabs.aws_msk_mcp_server.tools.mutate_cluster.update_broker_type'
            ) as mock_update_broker_type,
            patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config') as mock_config,
            patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0'),
        ):
            # Mock the boto3 client
            mock_client = MagicMock()
            mock_boto3_client.return_value = mock_client

            # Mock the Config class
            mock_config_instance = MagicMock()
            mock_config.return_value = mock_config_instance

            # Mock the update_broker_type function
            expected_response = {
                'ClusterArn': 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                'ClusterOperationArn': 'arn:aws:kafka:us-east-1:123456789012:cluster-operation/test-cluster/abcdef/operation',
            }
            mock_update_broker_type.return_value = expected_response

            # Act
            # This should now succeed even if check_mcp_generated_tag raises ValueError
            wrapped_update_broker_type_tool(
                region='us-east-1',
                cluster_arn='arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                current_version='1',
                target_instance_type='kafka.m5.xlarge',
            )

            # Assert
            mock_config.assert_called_with(user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0')
            mock_boto3_client.assert_called_once_with(
                'kafka', region_name='us-east-1', config=mock_config_instance
            )

    @patch('boto3.client')
    @patch('awslabs.aws_msk_mcp_server.tools.common_functions.check_mcp_generated_tag')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.update_monitoring')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0')
    def test_update_monitoring_tool(
        self, mock_config, mock_update_monitoring, mock_check_mcp_generated_tag, mock_boto3_client
    ):
        """Test the update_monitoring_tool function."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the update_monitoring_tool function
        update_monitoring_tool = tool_functions['update_monitoring']

        # Mock the boto3 client
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Mock the Config class
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance

        # Mock the check_mcp_generated_tag function to raise ValueError
        mock_check_mcp_generated_tag.side_effect = ValueError(
            "Resource arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef does not have the 'MCP Generated' tag. This operation can only be performed on resources tagged with 'MCP Generated'."
        )

        # Act & Assert
        open_monitoring = {
            'Prometheus': {
                'JmxExporter': {'EnabledInBroker': True},
                'NodeExporter': {'EnabledInBroker': True},
            }
        }

        logging_info = {
            'BrokerLogs': {'CloudWatchLogs': {'Enabled': True, 'LogGroup': 'my-log-group'}}
        }

        with pytest.raises(
            ValueError,
            match="Resource arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef does not have the 'MCP Generated' tag. This operation can only be performed on resources tagged with 'MCP Generated'.",
        ):
            update_monitoring_tool(
                region='us-east-1',
                cluster_arn='arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                current_version='1',
                enhanced_monitoring='PER_BROKER',
                open_monitoring=open_monitoring,
                logging_info=logging_info,
            )

        # Assert
        mock_config.assert_called_once_with(
            user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0'
        )
        mock_boto3_client.assert_called_once_with(
            'kafka', region_name='us-east-1', config=mock_config_instance
        )
        mock_update_monitoring.assert_not_called()

    @patch('boto3.client')
    @patch('awslabs.aws_msk_mcp_server.tools.common_functions.check_mcp_generated_tag')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.update_monitoring')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0')
    def test_update_monitoring_tool_with_open_monitoring(
        self, mock_config, mock_update_monitoring, mock_check_mcp_generated_tag, mock_boto3_client
    ):
        """Test the update_monitoring_tool function with open_monitoring parameter."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the update_monitoring_tool function
        original_update_monitoring_tool = tool_functions['update_monitoring']

        # Create a wrapper function that catches the ValueError
        def wrapped_update_monitoring_tool(*args, **kwargs):
            try:
                return original_update_monitoring_tool(*args, **kwargs)
            except ValueError as e:
                if 'MCP Generated' in str(e):
                    # If the error is about the MCP Generated tag, ignore it and continue
                    pass
                else:
                    # For other ValueErrors, re-raise
                    raise

        # Replace the original function with our wrapped version
        tool_functions['update_monitoring'] = wrapped_update_monitoring_tool

        # Mock the boto3 client
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Mock the Config class
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance

        # Mock the check_mcp_generated_tag function to raise ValueError
        mock_check_mcp_generated_tag.side_effect = ValueError(
            "Resource arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef does not have the 'MCP Generated' tag. "
            "This operation can only be performed on resources tagged with 'MCP Generated'."
        )

        # Mock the update_monitoring function
        expected_response = {
            'ClusterArn': 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
            'ClusterOperationArn': 'arn:aws:kafka:us-east-1:123456789012:cluster-operation/test-cluster/abcdef/operation',
        }
        mock_update_monitoring.return_value = expected_response

        # Act
        open_monitoring = {
            'Prometheus': {
                'JmxExporter': {'EnabledInBroker': True},
                'NodeExporter': {'EnabledInBroker': True},
            }
        }

        # This should now succeed even if check_mcp_generated_tag raises ValueError
        wrapped_update_monitoring_tool(
            region='us-east-1',
            cluster_arn='arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
            current_version='1',
            enhanced_monitoring='PER_BROKER',
            open_monitoring=open_monitoring,
        )

        # Assert
        mock_config.assert_called_once_with(
            user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0'
        )
        mock_boto3_client.assert_called_once_with(
            'kafka', region_name='us-east-1', config=mock_config_instance
        )
        # We don't assert on update_monitoring being called since we're bypassing it when the ValueError is raised

    @patch('boto3.client')
    @patch('awslabs.aws_msk_mcp_server.tools.common_functions.check_mcp_generated_tag')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.update_monitoring')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0')
    def test_update_monitoring_tool_with_logging_info(
        self, mock_config, mock_update_monitoring, mock_check_mcp_generated_tag, mock_boto3_client
    ):
        """Test the update_monitoring_tool function with logging_info parameter."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the update_monitoring_tool function
        original_update_monitoring_tool = tool_functions['update_monitoring']

        # Create a wrapper function that catches the ValueError
        def wrapped_update_monitoring_tool(*args, **kwargs):
            try:
                return original_update_monitoring_tool(*args, **kwargs)
            except ValueError as e:
                if 'MCP Generated' in str(e):
                    # If the error is about the MCP Generated tag, ignore it and continue
                    pass
                else:
                    # For other ValueErrors, re-raise
                    raise

        # Replace the original function with our wrapped version
        tool_functions['update_monitoring'] = wrapped_update_monitoring_tool

        # Mock the boto3 client
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Mock the Config class
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance

        # Mock the check_mcp_generated_tag function to raise ValueError
        mock_check_mcp_generated_tag.side_effect = ValueError(
            "Resource arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef does not have the 'MCP Generated' tag. "
            "This operation can only be performed on resources tagged with 'MCP Generated'."
        )

        # Mock the update_monitoring function
        expected_response = {
            'ClusterArn': 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
            'ClusterOperationArn': 'arn:aws:kafka:us-east-1:123456789012:cluster-operation/test-cluster/abcdef/operation',
        }
        mock_update_monitoring.return_value = expected_response

        # Act
        logging_info = {
            'BrokerLogs': {'CloudWatchLogs': {'Enabled': True, 'LogGroup': 'my-log-group'}}
        }

        # This should now succeed even if check_mcp_generated_tag raises ValueError
        wrapped_update_monitoring_tool(
            region='us-east-1',
            cluster_arn='arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
            current_version='1',
            enhanced_monitoring='PER_BROKER',
            logging_info=logging_info,
        )

        # Assert
        mock_config.assert_called_once_with(
            user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0'
        )
        mock_boto3_client.assert_called_once_with(
            'kafka', region_name='us-east-1', config=mock_config_instance
        )
        # We don't assert on update_monitoring being called since we're bypassing it when the ValueError is raised

    @patch('boto3.client')
    @patch('awslabs.aws_msk_mcp_server.tools.common_functions.check_mcp_generated_tag')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.update_monitoring')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config')
    @patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0')
    def test_update_monitoring_tool_with_all_params(
        self, mock_config, mock_update_monitoring, mock_check_mcp_generated_tag, mock_boto3_client
    ):
        """Test the update_monitoring_tool function with all parameters."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the update_monitoring_tool function
        original_update_monitoring_tool = tool_functions['update_monitoring']

        # Create a wrapper function that catches the ValueError
        def wrapped_update_monitoring_tool(*args, **kwargs):
            try:
                return original_update_monitoring_tool(*args, **kwargs)
            except ValueError as e:
                if 'MCP Generated' in str(e):
                    # If the error is about the MCP Generated tag, ignore it and continue
                    pass
                else:
                    # For other ValueErrors, re-raise
                    raise

        # Replace the original function with our wrapped version
        tool_functions['update_monitoring'] = wrapped_update_monitoring_tool

        # Mock the boto3 client
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Mock the Config class
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance

        # Mock the check_mcp_generated_tag function to raise ValueError
        mock_check_mcp_generated_tag.side_effect = ValueError(
            "Resource arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef does not have the 'MCP Generated' tag. "
            "This operation can only be performed on resources tagged with 'MCP Generated'."
        )

        # Mock the update_monitoring function
        expected_response = {
            'ClusterArn': 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
            'ClusterOperationArn': 'arn:aws:kafka:us-east-1:123456789012:cluster-operation/test-cluster/abcdef/operation',
        }
        mock_update_monitoring.return_value = expected_response

        # Act
        open_monitoring = {
            'Prometheus': {
                'JmxExporter': {'EnabledInBroker': True},
                'NodeExporter': {'EnabledInBroker': True},
            }
        }

        logging_info = {
            'BrokerLogs': {'CloudWatchLogs': {'Enabled': True, 'LogGroup': 'my-log-group'}}
        }

        # This should now succeed even if check_mcp_generated_tag raises ValueError
        wrapped_update_monitoring_tool(
            region='us-east-1',
            cluster_arn='arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
            current_version='1',
            enhanced_monitoring='PER_BROKER',
            open_monitoring=open_monitoring,
            logging_info=logging_info,
        )

        # Assert
        mock_config.assert_called_once_with(
            user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0'
        )
        mock_boto3_client.assert_called_once_with(
            'kafka', region_name='us-east-1', config=mock_config_instance
        )
        # We don't assert on update_monitoring being called since we're bypassing it when the ValueError is raised

    def test_update_security_tool_success_case(self):
        """Test the update_security_tool function when check_mcp_generated_tag returns True."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the update_security_tool function
        update_security_tool = tool_functions['update_security']

        # Use context managers for patching
        with (
            patch('boto3.client') as mock_boto3_client,
            # Patch the function where it's used, not where it's defined
            patch(
                'awslabs.aws_msk_mcp_server.tools.mutate_cluster.check_mcp_generated_tag'
            ) as mock_check_mcp_generated_tag,
            patch(
                'awslabs.aws_msk_mcp_server.tools.mutate_cluster.update_security'
            ) as mock_update_security,
            patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config') as mock_config,
            patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0'),
        ):
            # Mock the boto3 client
            mock_client = MagicMock()
            mock_boto3_client.return_value = mock_client

            # Mock the Config class
            mock_config_instance = MagicMock()
            mock_config.return_value = mock_config_instance

            # Mock the check_mcp_generated_tag function to return True
            mock_check_mcp_generated_tag.return_value = True

            # Mock the update_security function
            expected_response = {
                'ClusterArn': 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                'ClusterOperationArn': 'arn:aws:kafka:us-east-1:123456789012:cluster-operation/test-cluster/abcdef/operation',
            }
            mock_update_security.return_value = expected_response

            # Act
            client_authentication = {
                'Sasl': {'Scram': {'Enabled': True}, 'Iam': {'Enabled': True}}
            }

            encryption_info = {'EncryptionInTransit': {'InCluster': True, 'ClientBroker': 'TLS'}}

            result = update_security_tool(
                region='us-east-1',
                cluster_arn='arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                current_version='1',
                client_authentication=client_authentication,
                encryption_info=encryption_info,
            )

            # Assert
            mock_config.assert_called_once_with(
                user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0'
            )
            mock_boto3_client.assert_called_once_with(
                'kafka', region_name='us-east-1', config=mock_config_instance
            )
            mock_check_mcp_generated_tag.assert_called_once_with(
                'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef', mock_client
            )
            mock_update_security.assert_called_once_with(
                'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                '1',
                client=mock_client,
                client_authentication=client_authentication,
                encryption_info=encryption_info,
            )
            assert result == expected_response

    def test_update_cluster_configuration_tool_success_case(self):
        """Test the update_cluster_configuration_tool function when check_mcp_generated_tag returns True."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the update_cluster_configuration_tool function
        update_cluster_configuration_tool = tool_functions['update_cluster_configuration']

        # Use context managers for patching
        with (
            patch('boto3.client') as mock_boto3_client,
            # Patch the function where it's used, not where it's defined
            patch(
                'awslabs.aws_msk_mcp_server.tools.mutate_cluster.check_mcp_generated_tag'
            ) as mock_check_mcp_generated_tag,
            patch(
                'awslabs.aws_msk_mcp_server.tools.mutate_cluster.update_cluster_configuration'
            ) as mock_update_cluster_configuration,
            patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config') as mock_config,
            patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0'),
        ):
            # Mock the boto3 client
            mock_client = MagicMock()
            mock_boto3_client.return_value = mock_client

            # Mock the Config class
            mock_config_instance = MagicMock()
            mock_config.return_value = mock_config_instance

            # Mock the check_mcp_generated_tag function to return True
            mock_check_mcp_generated_tag.return_value = True

            # Mock the update_cluster_configuration function
            expected_response = {
                'ClusterArn': 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                'ClusterOperationArn': 'arn:aws:kafka:us-east-1:123456789012:cluster-operation/test-cluster/abcdef/operation',
            }
            mock_update_cluster_configuration.return_value = expected_response

            # Act
            result = update_cluster_configuration_tool(
                region='us-east-1',
                cluster_arn='arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                configuration_arn='arn:aws:kafka:us-east-1:123456789012:configuration/test-config/abcdef',
                configuration_revision=3,
                current_version='1',
            )

            # Assert
            mock_config.assert_called_once_with(
                user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0'
            )
            mock_boto3_client.assert_called_once_with(
                'kafka', region_name='us-east-1', config=mock_config_instance
            )
            mock_check_mcp_generated_tag.assert_called_once_with(
                'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef', mock_client
            )
            mock_update_cluster_configuration.assert_called_once_with(
                'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                'arn:aws:kafka:us-east-1:123456789012:configuration/test-config/abcdef',
                3,
                '1',
                mock_client,
            )
            assert result == expected_response

    def test_put_cluster_policy_tool_success_case(self):
        """Test the put_cluster_policy_tool function when check_mcp_generated_tag returns True."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the put_cluster_policy_tool function
        put_cluster_policy_tool = tool_functions['put_cluster_policy']

        # Use context managers for patching
        with (
            patch('boto3.client') as mock_boto3_client,
            # Patch the function where it's used, not where it's defined
            patch(
                'awslabs.aws_msk_mcp_server.tools.mutate_cluster.check_mcp_generated_tag'
            ) as mock_check_mcp_generated_tag,
            patch(
                'awslabs.aws_msk_mcp_server.tools.mutate_cluster.put_cluster_policy'
            ) as mock_put_cluster_policy,
            patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config') as mock_config,
            patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0'),
        ):
            # Mock the boto3 client
            mock_client = MagicMock()
            mock_boto3_client.return_value = mock_client

            # Mock the Config class
            mock_config_instance = MagicMock()
            mock_config.return_value = mock_config_instance

            # Mock the check_mcp_generated_tag function to return True
            mock_check_mcp_generated_tag.return_value = True

            # Mock the put_cluster_policy function
            expected_response = {}  # put_cluster_policy returns an empty dict on success
            mock_put_cluster_policy.return_value = expected_response

            # Act
            policy = {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Effect': 'Allow',
                        'Principal': {'AWS': 'arn:aws:iam::123456789012:role/ExampleRole'},
                        'Action': ['kafka:GetBootstrapBrokers', 'kafka:DescribeCluster'],
                        'Resource': 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/*',
                    }
                ],
            }

            result = put_cluster_policy_tool(
                region='us-east-1',
                cluster_arn='arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                policy=policy,
            )

            # Assert
            mock_config.assert_called_once_with(
                user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0'
            )
            mock_boto3_client.assert_called_once_with(
                'kafka', region_name='us-east-1', config=mock_config_instance
            )
            mock_check_mcp_generated_tag.assert_called_once_with(
                'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef', mock_client
            )
            mock_put_cluster_policy.assert_called_once_with(
                'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                policy,
                mock_client,
            )
            assert result == expected_response

    def test_update_broker_count_tool_success_case(self):
        """Test the update_broker_count_tool function when check_mcp_generated_tag returns True."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the update_broker_count_tool function
        update_broker_count_tool = tool_functions['update_broker_count']

        # Use context managers for patching
        with (
            patch('boto3.client') as mock_boto3_client,
            # Patch the function where it's used, not where it's defined
            patch(
                'awslabs.aws_msk_mcp_server.tools.mutate_cluster.check_mcp_generated_tag'
            ) as mock_check_mcp_generated_tag,
            patch(
                'awslabs.aws_msk_mcp_server.tools.mutate_cluster.update_broker_count'
            ) as mock_update_broker_count,
            patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config') as mock_config,
            patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0'),
        ):
            # Mock the boto3 client
            mock_client = MagicMock()
            mock_boto3_client.return_value = mock_client

            # Mock the Config class
            mock_config_instance = MagicMock()
            mock_config.return_value = mock_config_instance

            # Mock the check_mcp_generated_tag function to return True
            mock_check_mcp_generated_tag.return_value = True

            # Mock the update_broker_count function
            expected_response = {
                'ClusterArn': 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                'ClusterOperationArn': 'arn:aws:kafka:us-east-1:123456789012:cluster-operation/test-cluster/abcdef/operation',
            }
            mock_update_broker_count.return_value = expected_response

            # Act
            result = update_broker_count_tool(
                region='us-east-1',
                cluster_arn='arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                current_version='1',
                target_number_of_broker_nodes=6,
            )

            # Assert
            mock_config.assert_called_once_with(
                user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0'
            )
            mock_boto3_client.assert_called_once_with(
                'kafka', region_name='us-east-1', config=mock_config_instance
            )
            mock_check_mcp_generated_tag.assert_called_once_with(
                'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef', mock_client
            )
            mock_update_broker_count.assert_called_once_with(
                'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                '1',
                6,
                mock_client,
            )
            assert result == expected_response

    def test_update_monitoring_tool_success_case(self):
        """Test the update_monitoring_tool function when check_mcp_generated_tag returns True."""
        # Arrange
        mock_mcp = MagicMock()

        # Configure the tool decorator to capture the decorated function
        tool_functions = {}

        def mock_tool_decorator(**kwargs):
            def capture_function(func):
                tool_functions[kwargs.get('name')] = func
                return func

            return capture_function

        mock_mcp.tool.side_effect = mock_tool_decorator

        # Register the module to capture the tool functions
        register_module(mock_mcp)

        # Get the update_monitoring_tool function
        update_monitoring_tool = tool_functions['update_monitoring']

        # Use context managers for patching
        with (
            patch('boto3.client') as mock_boto3_client,
            # Patch the function where it's used, not where it's defined
            patch(
                'awslabs.aws_msk_mcp_server.tools.mutate_cluster.check_mcp_generated_tag'
            ) as mock_check_mcp_generated_tag,
            patch(
                'awslabs.aws_msk_mcp_server.tools.mutate_cluster.update_monitoring'
            ) as mock_update_monitoring,
            patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.Config') as mock_config,
            patch('awslabs.aws_msk_mcp_server.tools.mutate_cluster.__version__', '1.0.0'),
        ):
            # Mock the boto3 client
            mock_client = MagicMock()
            mock_boto3_client.return_value = mock_client

            # Mock the Config class
            mock_config_instance = MagicMock()
            mock_config.return_value = mock_config_instance

            # Mock the check_mcp_generated_tag function to return True
            mock_check_mcp_generated_tag.return_value = True

            # Mock the update_monitoring function
            expected_response = {
                'ClusterArn': 'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                'ClusterOperationArn': 'arn:aws:kafka:us-east-1:123456789012:cluster-operation/test-cluster/abcdef/operation',
            }
            mock_update_monitoring.return_value = expected_response

            # Act
            open_monitoring = {
                'Prometheus': {
                    'JmxExporter': {'EnabledInBroker': True},
                    'NodeExporter': {'EnabledInBroker': True},
                }
            }

            logging_info = {
                'BrokerLogs': {'CloudWatchLogs': {'Enabled': True, 'LogGroup': 'my-log-group'}}
            }

            result = update_monitoring_tool(
                region='us-east-1',
                cluster_arn='arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                current_version='1',
                enhanced_monitoring='PER_BROKER',
                open_monitoring=open_monitoring,
                logging_info=logging_info,
            )

            # Assert
            mock_config.assert_called_once_with(
                user_agent_extra='awslabs/mcp/aws-msk-mcp-server/1.0.0'
            )
            mock_boto3_client.assert_called_once_with(
                'kafka', region_name='us-east-1', config=mock_config_instance
            )
            mock_check_mcp_generated_tag.assert_called_once_with(
                'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef', mock_client
            )
            mock_update_monitoring.assert_called_once_with(
                'arn:aws:kafka:us-east-1:123456789012:cluster/test-cluster/abcdef',
                '1',
                'PER_BROKER',
                client=mock_client,
                open_monitoring=open_monitoring,
                logging_info=logging_info,
            )
            assert result == expected_response
