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

"""Test fixtures for the cost-analysis-mcp-server."""

import pytest
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_context():
    """Create a mock MCP context."""
    context = AsyncMock()
    context.info = AsyncMock()
    context.error = AsyncMock()
    context.warning = AsyncMock()
    return context


@pytest.fixture
def sample_athena_query_return() -> Dict[str, Any]:
    """Sample athena CUR return"""
    return {
        
    }


@pytest.fixture
def sample_trusted_advisor_return() -> Dict[str, Any]:
    """Sample pricing data from AWS Price List API."""
    return {
        
    }

@pytest.fixture
def mock_boto3() -> MagicMock:
    """Mock boto3 for testing AWS API calls."""
    mock = MagicMock()

    # Mock pricing client
    ta_client = MagicMock()
    ta_client.list_recommendations.return_value = {
            "recommendationSummaries": [
                {
                "arn": "arn:aws:trustedadvisor::576219157147:recommendation/ef3ab5f1-7d4b-c123-a50f-c1a7def02a12",
                "awsServices": [
                    "ec2"
                ],
                "checkArn": "arn:aws:trustedadvisor:::check/c1z7kmr02n",
                "id": "ef3ab5f1-7d4b-c123-a50f-c1a7def02a12",
                "lastUpdatedAt": "2025-06-25 19:02:06.491000+00:00",
                "name": "Amazon EBS cost optimization recommendations for volumes",
                "pillarSpecificAggregates": {
                    "costOptimizing": {
                    "estimatedMonthlySavings": 0.0,
                    "estimatedPercentMonthlySavings": 0.0
                    }
                },
                "pillars": [
                    "cost_optimizing"
                ],
                "resourcesAggregates": {
                    "errorCount": 0,
                    "okCount": 0,
                    "warningCount": 12
                },
                "source": "ta_check",
                "status": "warning",
                "type": "standard"
                }
            ]
        }
    ta_client.list_recommendation_resources.return_value = {
        
    }
    # Mock session
    session = MagicMock()
    session.client.return_value = ta_client
    mock.Session.return_value = session

    return mock
