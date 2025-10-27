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
#
"""
Infrastructure Management API Module

This module provides functions to manage infrastructure aspects of MSK clusters.
"""

from botocore.config import Config
from awslabs.aws_msk_mcp_server import __version__
from .common_functions import check_mcp_generated_tag, get_cluster_name

__all__ = ['check_mcp_generated_tag', 'get_cluster_name']
