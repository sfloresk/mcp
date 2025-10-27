"""
Test script for the image pull failure detection functionality.

This script tests the new functionality for detecting image pull failures
in ECS deployments. It can be used to verify that the enhanced troubleshooting
tools correctly identify and diagnose image pull issues.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import boto3
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from awslabs.ecs_mcp_server.api.troubleshooting_tools.detect_image_pull_failures import (
    detect_image_pull_failures,
)
from awslabs.ecs_mcp_server.api.troubleshooting_tools.get_ecs_troubleshooting_guidance import (
    validate_container_images,
)


class TestImagePullFailureDetection(unittest.TestCase):
    """Test the image pull failure detection functionality."""

    @pytest.mark.anyio
    @patch(
        "awslabs.ecs_mcp_server.api.troubleshooting_tools.get_ecs_troubleshooting_guidance.boto3.client"
    )
    async def test_validate_container_images(self, mock_boto3_client):
        """Test validating container images."""
        # Mock the ECR client
        mock_ecr = MagicMock()

        # Configure the mock to fail for the test repo
        def mock_describe_repositories(repositoryNames):
            if repositoryNames[0] == "non-existent-image":
                error = {"Error": {"Code": "RepositoryNotFoundException"}}
                raise boto3.client("ecr").exceptions.RepositoryNotFoundException(
                    error, "DescribeRepositories"
                )
            return {"repositories": [{"repositoryName": repositoryNames[0]}]}

        mock_ecr.describe_repositories.side_effect = mock_describe_repositories

        # Configure mock boto3 client to return our mock
        mock_boto3_client.return_value = mock_ecr

        # Create test task definitions
        task_defs = [
            {
                "taskDefinitionArn": (
                    "arn:aws:ecs:us-west-2:123456789012:task-definition/failing-task-def-prbqv:1"
                ),
                "family": "failing-task-def-prbqv",
                "containerDefinitions": [
                    {"name": "web", "image": "non-existent-repo/non-existent-image:latest"}
                ],
            }
        ]

        # Call the function
        result = await validate_container_images(task_defs)

        # Verify the result
        assert len(result) == 1
        assert result[0]["image"] == "non-existent-repo/non-existent-image:latest"
        assert result[0]["exists"] == "unknown"  # External images have unknown status
        assert result[0]["repository_type"] == "external"

    @pytest.mark.anyio
    @patch(
        "awslabs.ecs_mcp_server.api.troubleshooting_tools.detect_image_pull_failures.get_task_definitions"
    )
    @patch(
        "awslabs.ecs_mcp_server.api.troubleshooting_tools.detect_image_pull_failures.validate_container_images"
    )
    async def test_detect_image_pull_failures(self, mock_validate_images, mock_find_task_defs):
        """Test the detect_image_pull_failures function."""
        # Mock the task definitions
        mock_find_task_defs.return_value = [
            {
                "taskDefinitionArn": (
                    "arn:aws:ecs:us-west-2:123456789012:task-definition/failing-task-def-prbqv:1"
                ),
                "family": "failing-task-def-prbqv",
                "containerDefinitions": [
                    {"name": "web", "image": "non-existent-repo/non-existent-image:latest"}
                ],
            }
        ]

        # Mock the image check results
        mock_validate_images.return_value = [
            {
                "image": "non-existent-repo/non-existent-image:latest",
                "task_definition": (
                    "arn:aws:ecs:us-west-2:123456789012:task-definition/failing-task-def-prbqv:1"
                ),
                "container_name": "web",
                "exists": "unknown",
                "error": "Repository not found in ECR",
                "repository_type": "external",
            }
        ]

        # Call the function
        result = await detect_image_pull_failures("test-failure-prbqv")

        # Verify the result
        assert "success" in result["status"]
        assert len(result["image_issues"]) > 0
        assert "container image" in result["assessment"]
        assert len(result["recommendations"]) > 0

        # Make sure it contains a specific recommendation
        found_recommendation = False
        for recommendation in result["recommendations"]:
            if "non-existent-repo/non-existent-image" in recommendation and (
                "accessible" in recommendation.lower() or "verify" in recommendation.lower()
            ):
                found_recommendation = True
                break
        assert found_recommendation, "Should recommend verifying the external image accessibility"

    @pytest.mark.anyio
    async def test_detect_image_pull_failures_parameter_validation(self):
        """Test parameter validation in detect_image_pull_failures."""
        # Expected error message from parameter validation
        expected_error_msg = (
            "At least one of: ecs_cluster_name+ecs_service_name, ecs_cluster_name+ecs_task_id, "
            "cfn_stack_name, or family_prefix must be provided"
        )

        # Call with no parameters - should trigger validation error
        result = await detect_image_pull_failures()

        # Verify the result shows parameter validation error
        assert result["status"] == "error"
        assert result["error"] == expected_error_msg

        # Specific assertion for the exact error message
        assert result["error"] == expected_error_msg, (
            f"Expected exact error message, got: {result['error']}"
        )

        # Call with incomplete parameters - should also trigger validation error
        result = await detect_image_pull_failures(cluster_name="test-cluster")

        # Verify the result shows parameter validation error
        assert result["status"] == "error"
        assert result["error"] == expected_error_msg

        # Test other incomplete parameter combinations
        result = await detect_image_pull_failures(service_name="test-service")
        assert result["status"] == "error"
        assert result["error"] == expected_error_msg

        result = await detect_image_pull_failures(task_id="test-task-id")
        assert result["status"] == "error"
        assert result["error"] == expected_error_msg


@pytest.mark.anyio
async def test_detect_image_pull_failures_parameter_validation_standalone():
    """Standalone test for parameter validation in detect_image_pull_failures."""
    # Expected error message from parameter validation
    expected_error_msg = (
        "At least one of: ecs_cluster_name+ecs_service_name, ecs_cluster_name+ecs_task_id, "
        "cfn_stack_name, or family_prefix must be provided"
    )

    # Call with no parameters - should trigger validation error
    result = await detect_image_pull_failures()

    # Verify the result shows parameter validation error
    assert result["status"] == "error"
    assert result["error"] == expected_error_msg

    # Specific assertion for the exact error message
    assert result["error"] == expected_error_msg

    # Call with incomplete parameters - should also trigger validation error
    result = await detect_image_pull_failures(cluster_name="test-cluster")
    assert result["status"] == "error"
    assert result["error"] == expected_error_msg

    # Test other incomplete parameter combinations
    result = await detect_image_pull_failures(service_name="test-service")
    assert result["status"] == "error"
    assert result["error"] == expected_error_msg

    result = await detect_image_pull_failures(task_id="test-task-id")
    assert result["status"] == "error"
    assert result["error"] == expected_error_msg


if __name__ == "__main__":
    unittest.main()
