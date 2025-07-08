# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""awslabs MCP Cost optimization mcp server implementation.

This server provides tools for optmization of AWS service across different user tiers.
"""

import argparse
import boto3
import logging
import os
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


ta_client = boto3.client('trustedadvisor')
athena_client = boto3.client('athena')



mcp = FastMCP(
    name='awslabs.cost-optimization-mcp-server',
    instructions="""Use this server for questions on workload optimizations and bills for AWS

    REQUIRED WORKFLOW:
    Analyze costs optimizations of AWS services by following these steps in order:

    1. Query trusted advisor:
       - MUST first invoke get_trusted_advisor_recommendations() to get findingds that can reduce the AWS costs
    
    2. Run athena queries to find out the costs of the resources. Use LIKE conditionals when looking for resource specific costs

    3. Output:
       Return to user:
       - Answer to the question in detailed cost optimizations report in markdown format 
       - Source of the data (Trusted advisor or Athena)

    ACCURACY GUIDELINES:
    - When uncertain about service compatibility or pricing details, EXCLUDE them rather than making assumptions
    - For database compatibility, only include CONFIRMED supported databases
    - Add clear disclaimers about what is NOT included in calculations
    - PROVIDING LESS INFORMATION IS BETTER THAN GIVING WRONG INFORMATION

    IMPORTANT: Steps MUST be executed in this exact order. Each step must be attempted
    before moving to the next. The report is particularly focused on
    how answering the question from the user.""",
    dependencies=['pydantic', 'boto3', 'beautifulsoup4', 'websearch'],
)

profile_name = os.getenv('AWS_PROFILE', 'default')
logger.info(f'Using AWS profile {profile_name}')


@mcp.tool(
    name='get_recommendations',
    description='Get trusted advisor recommendations for performance and cost optimization recommendations',
)
async def get_trusted_advisor_recommendations(ctx: Context) -> Optional[Dict]:
    """Get trusted advisor recommendations for performance and cost optimization recommendations.

    Args:
        ctx: MCP context for logging and state management

    Returns:
        dict: Dictionary containing the check name, resources associated with the check and metadata to calculate potential savings
    """
    try:
       # Get results for each cost optimization check
        results = []
        # Get all available Trusted Advisor checks
        for pillar_to_check in ["cost_optimizing","performance"]:
            for status_to_check in ["warning","error"]:
                ta_paginator_list_recommendations = ta_client.get_paginator('list_recommendations').paginate(pillar=pillar_to_check, status=status_to_check)
                
                for ta_page_list_recommendations in ta_paginator_list_recommendations:
                    for check in ta_page_list_recommendations['recommendationSummaries']:
                        recommendation_arn = check['arn']
                        
                        
                        # Get the check result
                        ta_paginator_resources = ta_client.get_paginator('list_recommendation_resources').paginate(
                            recommendationIdentifier=recommendation_arn,
                            exclusionStatus='included')
                        for ta_page_resources in ta_paginator_resources:
                            resources = []
                            for resource_summary in ta_page_resources["recommendationResourceSummaries"]:
                                resources.append(resource_summary['metadata'])
                        results.append({
                            "check_name": check['name'],
                            "resources":resources,
                            "metadata": check["pillarSpecificAggregates"]
                            })
                        
        logger.info(f'Recommendations: {results}')
        return results
    except Exception as e:
        await ctx.error(f'Failed to get recommendations from trusted advisor: {e}')
        return None
    
@mcp.tool(
    name='execute_cost_query',
    description=f"Retrieve results of queries against cost and usage report. Always use table {os.getenv('AWS_CUR_TABLE_NAME')}",
)
async def execute_athena_cur_query(query: str,ctx: Context) -> Optional[Dict]:
    """Execute an athena query against cost and usage report.

    Args:
        ctx: MCP context for logging and state management

    Returns:
        dict: Dictionary containing the query result
    """
    try:
        logger.info(f"Executing query: {query}")
        # Start the query execution
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': os.getenv('AWS_CUR_DB_NAME')
            },
            ResultConfiguration={
                'OutputLocation': os.getenv('AWS_ATHENA_RESULTS_BUCKET'),
            }
        )
        
        # Get the query execution ID
        query_execution_id = response['QueryExecutionId']
        logger.info(f"Query execution ID: {query_execution_id}")
        
        # Wait for the query to complete
        attemps = 0
        while attemps < 6:
            response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            state = response['QueryExecution']['Status']['State']
            
            if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
                
            logger.info(f"Query is in {state} state, waiting...")
            time.sleep(2)
        
        # Check if query was successful
        if state == 'SUCCEEDED':
            # Get the results
            results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
            return results['ResultSet']
        else:
            error_details = response['QueryExecution']['Status'].get('StateChangeReason', 'No error details available')
            logger.error(f"Query failed with state {state}: {error_details}")
            return {
                'status': 'error',
                'services': [],
                'message': f'Query failed with state {state}',
                'details': {'error': error_details},
            }
    except Exception as e:
        await ctx.error(f'Failed to execute athena query: {e}')
        return None

def main():
    """Run the MCP server with CLI argument support."""
    parser = argparse.ArgumentParser(description='Optimize costs of AWS services')
    parser.add_argument('--sse', action='store_true', help='Use SSE transport')
    parser.add_argument('--port', type=int, default=8888, help='Port to run the server on')

    args = parser.parse_args()

    # Run server with appropriate transport
    if args.sse:
        mcp.settings.port = args.port
        mcp.run(transport='sse')
    else:
        mcp.run()


if __name__ == '__main__':
    main()
