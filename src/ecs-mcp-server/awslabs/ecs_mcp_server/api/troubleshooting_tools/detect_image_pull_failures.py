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
Specialized tool for detecting container image pull failures.

This module provides a function to find related task definitions and check if their
container images exist and are accessible, helping to diagnose image pull failures in ECS.
"""

import logging
from typing import Any, Dict, Optional

from awslabs.ecs_mcp_server.api.troubleshooting_tools.get_ecs_troubleshooting_guidance import (
    validate_container_images as _validate_container_images,
)
from awslabs.ecs_mcp_server.api.troubleshooting_tools.utils import (
    find_task_definitions as _find_task_definitions,
)

logger = logging.getLogger(__name__)


async def detect_image_pull_failures(
    cluster_name: Optional[str] = None,
    service_name: Optional[str] = None,
    stack_name: Optional[str] = None,
    family_prefix: Optional[str] = None,
    task_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Specialized tool for detecting image pull failures.

    This function finds task definitions based on the provided parameters and checks
    if their container images exist and are accessible, helping to diagnose image pull failures.

    At least one of the parameter combinations must be provided: cluster_name+service_name,
    cluster_name+task_id, stack_name, or family_prefix.

    Parameters
    ----------
    cluster_name : str, optional
        Name of the ECS Cluster (required if service_name or task_id is provided)
    service_name : str, optional
        Name of the ECS Service (requires cluster_name)
    stack_name : str, optional
        Name of the CloudFormation Stack to find related Task Definitions
    family_prefix : str, optional
        Prefix to filter Task Definition families (e.g., "my-app")
    task_id : str, optional
        ID of an ECS Task to get its Task Definition (requires cluster_name)

    Returns
    -------
    Dict[str, Any]
        Dictionary with image issues analysis and recommendations
    """
    try:
        response = {
            "status": "success",
            "image_issues": [],
            "assessment": "",
            "recommendations": [],
        }

        # Validate parameters
        if not any(
            [(cluster_name and service_name), (cluster_name and task_id), stack_name, family_prefix]
        ):
            error_msg = (
                "At least one of: ecs_cluster_name+ecs_service_name, ecs_cluster_name+ecs_task_id, "
                "cfn_stack_name, or family_prefix must be provided"
            )
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
            }

        # Find related task definitions
        try:
            task_definitions = await _find_task_definitions(
                cluster_name=cluster_name,
                service_name=service_name,
                stack_name=stack_name,
                family_prefix=family_prefix,
                task_id=task_id,
            )
        except Exception as e:
            logger.exception("Error getting task definitions: %s", str(e))
            return {
                "status": "error",
                "error": str(e),
                "assessment": f"Error checking for image pull failures: {str(e)}",
            }

        if not task_definitions:
            parameter_desc = ""
            if cluster_name and service_name:
                parameter_desc = f"cluster '{cluster_name}' and service '{service_name}'"
            elif cluster_name and task_id:
                parameter_desc = f"cluster '{cluster_name}' and task ID '{task_id}'"
            elif stack_name:
                parameter_desc = f"stack '{stack_name}'"
            elif family_prefix:
                parameter_desc = f"family prefix '{family_prefix}'"

            response["assessment"] = f"No task definitions found for {parameter_desc}"
            response["recommendations"].append("Check if your task definition is named differently")
            return response

        # Check container images
        try:
            image_results = await _validate_container_images(task_definitions)
        except Exception as e:
            logger.exception("Error validating container images: %s", str(e))
            return {
                "status": "error",
                "error": str(e),
                "assessment": f"Error validating container images: {str(e)}",
                "image_issues": [],
            }

        # Analyze results
        failed_images = [result for result in image_results if result["exists"] != "true"]

        if failed_images:
            response["assessment"] = (
                f"Found {len(failed_images)} container image(s) that may be causing pull failures"
            )
            response["image_issues"] = failed_images

            for failed in failed_images:
                task_def_arn = failed.get("task_definition", "")
                task_def_name = task_def_arn.split("/")[-1] if task_def_arn else "unknown"
                container_name = failed.get("container_name", "unknown")

                if failed["repository_type"] == "ecr":
                    response["recommendations"].append(
                        f"ECR image '{failed['image']}' not found in task definition "
                        f"'{task_def_name}', container '{container_name}'. "
                        f"Check if the repository exists and the image has been pushed."
                    )
                elif failed["exists"] == "unknown":
                    response["recommendations"].append(
                        f"External image '{failed['image']}' in task definition "
                        f"'{task_def_name}', container '{container_name}' "
                        f"cannot be verified without pulling. Verify that the image exists, "
                        f"is spelled correctly, and is publicly accessible or has proper "
                        f"credentials configured in your task execution role."
                    )
                else:
                    response["recommendations"].append(
                        f"Image '{failed['image']}' in task definition "
                        f"'{task_def_name}', container '{container_name}' "
                        f"has issues. Check the image reference and ensure it points to a "
                        f"valid repository."
                    )
        else:
            response["assessment"] = "All container images appear to be valid and accessible."

        # Add recommendations based on task_definition analysis
        for task_def in task_definitions:
            task_def_arn = task_def.get("taskDefinitionArn", "")
            task_def_name = task_def_arn.split("/")[-1] if task_def_arn else "unknown"

            # Check if task definition has execution role for ECR image pulling
            execution_role_arn = task_def.get("executionRoleArn")
            if not execution_role_arn and any(
                "ecr" in container.get("image", "")
                for container in task_def.get("containerDefinitions", [])
            ):
                response["recommendations"].append(
                    f"Task definition '{task_def_name}' uses ECR images but does not have "
                    f"an execution role. Add an executionRole with AmazonECR-ReadOnly permissions."
                )

        return response
    except Exception as e:
        logger.exception("Error in detect_image_pull_failures: %s", str(e))
        return {
            "status": "error",
            "error": str(e),
            "assessment": f"Error checking for image pull failures: {str(e)}",
            "image_issues": [],
        }
