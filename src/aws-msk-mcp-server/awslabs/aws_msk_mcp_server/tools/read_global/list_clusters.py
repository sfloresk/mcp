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

"""Function to list all MSK clusters.

Maps to AWS CLI command: aws kafka list-clusters-v2.
"""


def list_clusters(
    client, cluster_name_filter=None, cluster_type_filter=None, max_results=10, next_token=None
):
    """Returns a list of all the MSK clusters in this account.

    Args:
        client (boto3.client): Boto3 client for Kafka. Must be provided by get_global_info.
        cluster_name_filter (str): Filter clusters by name prefix
        cluster_type_filter (str): Filter clusters by type (PROVISIONED or SERVERLESS)
        max_results (int): Maximum number of clusters to return
        next_token (str): Token for pagination

    Returns:
        dict: List of MSK clusters
    """
    if client is None:
        raise ValueError(
            'Client must be provided. This function should only be called from get_global_info.'
        )

    # Example implementation
    params = {'MaxResults': max_results}

    if cluster_name_filter:
        params['ClusterNameFilter'] = cluster_name_filter

    if cluster_type_filter:
        params['ClusterTypeFilter'] = cluster_type_filter

    if next_token:
        params['NextToken'] = next_token

    response = client.list_clusters_v2(**params)

    return response
