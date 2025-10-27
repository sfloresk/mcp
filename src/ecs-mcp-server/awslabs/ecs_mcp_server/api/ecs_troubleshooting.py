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
ECS troubleshooting tool that aggregates all troubleshooting functionality.

This module provides a single entry point for all ECS troubleshooting operations
that were previously available as separate tools.
"""

import inspect
import logging
from typing import Any, Dict, Literal, Optional

from awslabs.ecs_mcp_server.api.troubleshooting_tools.detect_image_pull_failures import (
    detect_image_pull_failures,
)
from awslabs.ecs_mcp_server.api.troubleshooting_tools.fetch_cloudformation_status import (
    fetch_cloudformation_status,
)
from awslabs.ecs_mcp_server.api.troubleshooting_tools.fetch_network_configuration import (
    fetch_network_configuration,
)
from awslabs.ecs_mcp_server.api.troubleshooting_tools.fetch_service_events import (
    fetch_service_events,
)
from awslabs.ecs_mcp_server.api.troubleshooting_tools.fetch_task_failures import (
    fetch_task_failures,
)
from awslabs.ecs_mcp_server.api.troubleshooting_tools.fetch_task_logs import (
    fetch_task_logs,
)
from awslabs.ecs_mcp_server.api.troubleshooting_tools.get_ecs_troubleshooting_guidance import (
    get_ecs_troubleshooting_guidance,
)

logger = logging.getLogger(__name__)

# Type definitions
TroubleshootingAction = Literal[
    "get_ecs_troubleshooting_guidance",
    "fetch_cloudformation_status",
    "fetch_service_events",
    "fetch_task_failures",
    "fetch_task_logs",
    "detect_image_pull_failures",
    "fetch_network_configuration",
]

# Combined actions configuration with inline parameter transformers and documentation
ACTIONS = {
    "get_ecs_troubleshooting_guidance": {
        "func": get_ecs_troubleshooting_guidance,
        "required_params": ["ecs_cluster_name"],
        "optional_params": ["ecs_service_name", "symptoms_description"],
        "transformer": lambda params: {
            "cluster_name": params["ecs_cluster_name"],
            "service_name": params.get("ecs_service_name"),
            "symptoms_description": params.get("symptoms_description"),
        },
        "description": "Initial assessment and data collection",
        "param_descriptions": {
            "ecs_cluster_name": "The name of the ECS Cluster to troubleshoot",
            "ecs_service_name": "The name of the ECS Service to troubleshoot (optional)",
            "symptoms_description": "Description of symptoms experienced by the uhser",
        },
        "example": (
            'action="get_ecs_troubleshooting_guidance", '
            'parameters={"ecs_cluster_name": "my-cluster", "ecs_service_name": "my-service", '
            '"symptoms_description": "ALB returning 503 errors"}'
        ),
    },
    "fetch_cloudformation_status": {
        "func": fetch_cloudformation_status,
        "required_params": ["cfn_stack_name"],
        "optional_params": [],
        "transformer": lambda params: {"stack_id": params.get("cfn_stack_name")},
        "description": "Infrastructure-level diagnostics for CloudFormation Stacks",
        "param_descriptions": {"cfn_stack_name": "The CloudFormation Stack identifier to analyze"},
        "example": (
            'action="fetch_cloudformation_status", parameters={"cfn_stack_name": "my-app-stack"}'
        ),
    },
    "fetch_service_events": {
        "func": fetch_service_events,
        "required_params": ["ecs_cluster_name", "ecs_service_name"],
        "optional_params": ["time_window", "start_time", "end_time"],
        "transformer": lambda params: {
            "cluster_name": params["ecs_cluster_name"],
            "service_name": params["ecs_service_name"],
            "time_window": params.get("time_window", 3600),
            "start_time": params.get("start_time"),
            "end_time": params.get("end_time"),
        },
        "description": "Service-level diagnostics for ECS Services",
        "param_descriptions": {
            "ecs_cluster_name": "The name of the ECS Cluster",
            "ecs_service_name": "The name of the ECS Service to analyze",
            "time_window": "Time window in seconds to look back for events (default: 3600)",
            "start_time": (
                "Explicit start time for the analysis window "
                "(UTC, takes precedence over time_window if provided)"
            ),
            "end_time": (
                "Explicit end time for the analysis window "
                "(UTC, defaults to current time if not provided)"
            ),
        },
        "example": (
            'action="fetch_service_events", '
            'parameters={"ecs_cluster_name": "my-cluster", "ecs_service_name": "my-service", '
            '"time_window": 7200}'
        ),
    },
    "fetch_task_failures": {
        "func": fetch_task_failures,
        "required_params": ["ecs_cluster_name"],
        "optional_params": ["time_window", "start_time", "end_time"],
        "transformer": lambda params: {
            "cluster_name": params["ecs_cluster_name"],
            "time_window": params.get("time_window", 3600),
            "start_time": params.get("start_time"),
            "end_time": params.get("end_time"),
        },
        "description": "Task-level diagnostics for ECS Task failures",
        "param_descriptions": {
            "ecs_cluster_name": "The name of the ECS Cluster",
            "time_window": "Time window in seconds to look back for failures (default: 3600)",
            "start_time": (
                "Explicit start time for the analysis window "
                "(UTC, takes precedence over time_window if provided)"
            ),
            "end_time": (
                "Explicit end time for the analysis window "
                "(UTC, defaults to current time if not provided)"
            ),
        },
        "example": (
            'action="fetch_task_failures", '
            'parameters={"ecs_cluster_name": "my-cluster", "time_window": 3600}'
        ),
    },
    "fetch_task_logs": {
        "func": fetch_task_logs,
        "required_params": ["ecs_cluster_name"],
        "optional_params": [
            "ecs_task_id",
            "time_window",
            "filter_pattern",
            "start_time",
            "end_time",
        ],
        "transformer": lambda params: {
            "cluster_name": params["ecs_cluster_name"],
            "task_id": params.get("ecs_task_id"),
            "time_window": params.get("time_window", 3600),
            "filter_pattern": params.get("filter_pattern"),
            "start_time": params.get("start_time"),
            "end_time": params.get("end_time"),
        },
        "description": "Application-level diagnostics through CloudWatch Logs",
        "param_descriptions": {
            "ecs_cluster_name": "The name of the ECS Cluster",
            "ecs_task_id": "Specific ECS Task ID to retrieve logs for",
            "time_window": "Time window in seconds to look back for logs (default: 3600)",
            "filter_pattern": "CloudWatch Logs filter pattern",
            "start_time": (
                "Explicit start time for the analysis window "
                "(UTC, takes precedence over time_window if provided)"
            ),
            "end_time": (
                "Explicit end time for the analysis window "
                "(UTC, defaults to current time if not provided)"
            ),
        },
        "example": (
            'action="fetch_task_logs", '
            'parameters={"ecs_cluster_name": "my-cluster", "filter_pattern": "ERROR", '
            '"time_window": 1800}'
        ),
    },
    "detect_image_pull_failures": {
        "func": detect_image_pull_failures,
        "required_params": [],  # No single required param, but need at least one combo
        "optional_params": [
            "ecs_cluster_name",
            "ecs_service_name",
            "cfn_stack_name",
            "family_prefix",
            "ecs_task_id",
        ],
        "transformer": lambda params: {
            "cluster_name": params.get("ecs_cluster_name"),
            "service_name": params.get("ecs_service_name"),
            "stack_name": params.get("cfn_stack_name"),
            "family_prefix": params.get("family_prefix"),
            "task_id": params.get("ecs_task_id"),
        },
        "description": "Specialized tool for detecting container image pull failures",
        "param_descriptions": {
            "ecs_cluster_name": (
                "Name of the ECS Cluster (required if ecs_service_name/ecs_task_id provided)"
            ),
            "ecs_service_name": "Name of the ECS Service (requires ecs_cluster_name)",
            "cfn_stack_name": "Name of the CloudFormation Stack to find related Task Definitions",
            "family_prefix": "Prefix to filter Task Definition families (e.g., 'my-app')",
            "ecs_task_id": (
                "ID of an ECS Task to get its Task Definition (requires ecs_cluster_name)"
            ),
        },
        "example": (
            'action="detect_image_pull_failures", '
            'parameters={"ecs_cluster_name": "my-cluster", "ecs_service_name": "my-service"}'
        ),
    },
    "fetch_network_configuration": {
        "func": fetch_network_configuration,
        "required_params": ["ecs_cluster_name"],
        "optional_params": ["vpc_id"],
        "transformer": lambda params: {
            "cluster_name": params["ecs_cluster_name"],
            "vpc_id": params.get("vpc_id"),
        },
        "description": "Network-level diagnostics for ECS deployments",
        "param_descriptions": {
            "ecs_cluster_name": "Name of the ECS Cluster to analyze",
            "vpc_id": "Specific VPC ID to analyze (optional)",
        },
        "example": (
            'action="fetch_network_configuration", '
            'parameters={"ecs_cluster_name": "my-cluster", '
            '"vpc_id": "vpc-12345678"}'
        ),
    },
}


def generate_troubleshooting_docs():
    """Generate documentation for the troubleshooting tools based on the ACTIONS dictionary."""

    # Generate the main body of the documentation
    actions_docs = []
    quick_usage_examples = []

    for action_name, action_data in ACTIONS.items():
        # Build the action documentation
        action_doc = f"### {len(actions_docs) + 1}. {action_name}\n"
        action_doc += f"{action_data['description']}\n"

        # Required parameters
        action_doc += "- Required: " + ", ".join(action_data["required_params"]) + "\n"

        # Optional parameters if any
        if action_data.get("optional_params"):
            optional_params_with_desc = []
            for param in action_data.get("optional_params", []):
                desc = action_data["param_descriptions"].get(param, "")
                optional_params_with_desc.append(f"{param} ({desc})")
            if optional_params_with_desc:
                action_doc += "- Optional: " + ", ".join(optional_params_with_desc) + "\n"

        # Example usage
        action_doc += f"- Example: {action_data['example']}\n"

        actions_docs.append(action_doc)

        # Build a quick usage example
        example = f"# {action_data['description']}\n"
        example += f'action: "{action_name}"\n'

        # Extract parameters from the example string
        import re

        params_match = re.search(r"parameters=\{(.*?)\}", action_data["example"])
        if params_match:
            params_str = params_match.group(1)
            example += f"parameters: {{{params_str}}}\n"
        else:
            example += "parameters: {}\n"

        quick_usage_examples.append(example)

    # Combine all documentation sections
    doc_header = """
ECS troubleshooting tool with multiple diagnostic actions.

This tool provides access to all ECS troubleshooting operations through a single
interface. Use the 'action' parameter to specify which troubleshooting operation
to perform.

## Available Actions and Parameters:

"""

    doc_examples = """
## Quick Usage Examples:

```
"""

    doc_footer = """```

Parameters:
    action: The troubleshooting action to perform (see available actions above)
    parameters: Action-specific parameters (see parameter specifications above)

Returns:
    Results from the selected troubleshooting action
"""

    # Combine all the documentation parts
    full_doc = (
        doc_header
        + "\n".join(actions_docs)
        + doc_examples
        + "\n".join(quick_usage_examples)
        + doc_footer
    )

    return full_doc


def _validate_action(action: str) -> None:
    """Validate that the action is supported."""
    if action not in ACTIONS:
        valid_actions = ", ".join(ACTIONS.keys())
        raise ValueError(f"Invalid action '{action}'. Valid actions: {valid_actions}")


def _validate_parameters(action: str, parameters: Dict[str, Any]) -> None:
    """Validate required parameters for the given action."""
    required = ACTIONS[action]["required_params"]

    # Special case for detect_image_pull_failures which needs at least one of several combinations
    if action == "detect_image_pull_failures":
        if not any(
            [
                (parameters.get("ecs_cluster_name") and parameters.get("ecs_service_name")),
                (parameters.get("ecs_cluster_name") and parameters.get("ecs_task_id")),
                parameters.get("cfn_stack_name"),
                parameters.get("family_prefix"),
            ]
        ):
            raise ValueError(
                "At least one of: ecs_cluster_name+ecs_service_name, ecs_cluster_name+ecs_task_id, "
                "cfn_stack_name, or family_prefix must be provided for 'detect_image_pull_failures'"
            )
        return

    # Check required parameters
    for param in required:
        if param not in parameters:
            raise ValueError(f"Missing required parameter '{param}' for action '{action}'")


# Pre-generate the documentation once to avoid regenerating it on each call
TROUBLESHOOTING_DOCS = generate_troubleshooting_docs()


async def ecs_troubleshooting_tool(
    action: TroubleshootingAction = "get_ecs_troubleshooting_guidance",
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    ECS troubleshooting tool.

    This tool provides access to all ECS troubleshooting operations through a single
    interface. Use the 'action' parameter to specify which troubleshooting operation
    to perform.

    Args:
        action: The troubleshooting action to perform
        parameters: Action-specific parameters

    Returns:
        Results from the selected troubleshooting action

    Raises:
        ValueError: If action is invalid or required parameters are missing
    """
    # NOTE: The full documentation is available in the TROUBLESHOOTING_DOCS variable
    try:
        if parameters is None:
            parameters = {}

        # Validate action
        _validate_action(action)

        # Check security permissions for sensitive data actions
        sensitive_data_actions = [
            "fetch_task_logs",
            "fetch_service_events",
            "fetch_task_failures",
            "fetch_network_configuration",
        ]
        if action in sensitive_data_actions:
            # Import here to avoid circular imports
            from awslabs.ecs_mcp_server.utils.config import get_config

            # Check if sensitive data access is allowed
            config = get_config()
            if not config.get("allow-sensitive-data", False):
                return {
                    "status": "error",
                    "error": (
                        f"Action {action} is not allowed without ALLOW_SENSITIVE_DATA=true "
                        f"in your environment due to potential exposure of sensitive information."
                    ),
                }

        # Validate parameters
        _validate_parameters(action, parameters)

        # Get action configuration
        action_config = ACTIONS[action]

        # Transform parameters using action-specific transformer
        func_params = action_config["transformer"](parameters)

        # Call the function and await it if it's a coroutine
        result = action_config["func"](**func_params)
        if inspect.iscoroutine(result):
            result = await result

        return result

    except ValueError as e:
        logger.error(f"Parameter validation error: {str(e)}")
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.exception(f"Error in ecs_troubleshooting_tool: {str(e)}")
        return {"status": "error", "error": f"Internal error: {str(e)}"}
