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

"""Tests for the server module of the cost-analysis-mcp-server."""

import pytest
from awslabs.cost_optimization_mcp_server.server import (
    get_trusted_advisor_recommendations,
    execute_athena_cur_query
)
from unittest.mock import MagicMock, patch


class TestTrustedAdvisor:
    """Tests for the get_trusted_advisor_recommendations function."""

    @pytest.mark.asyncio
    async def test_get_trusted_advisor_recommendations(self, mock_context):
        """Test analyzing a valid CDK project."""
        result = await get_trusted_advisor_recommendations(mock_context)

        assert result is not None
        assert result['status'] == 'success'
        assert 'services' in result

        # Check for expected services
        services = {service['name'] for service in result['services']}
        assert 'lambda' in services
        assert 'dynamodb' in services
        assert 's3' in services
        assert 'iam' in services
