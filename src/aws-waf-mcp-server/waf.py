import boto3
from mcp.server.fastmcp import FastMCP
import os
# Initialize FastMCP server
mcp = FastMCP("aws_waf")

session = boto3.Session(profile_name=os.getenv('AWS_PROFILE'), region_name=os.getenv('AWS_DEAFULT_REGION'))

# clients
wafv2_client = session.client('wafv2')
elbv2_client = session.client('elbv2')

@mcp.tool()
async def create_waf_acl(name,json_rules_acl):
    """
    Creates a WAFv2 Web ACL (Web Application Firewall Access Control List) with specified rules.
    When creating rules, follow these steps: 
    Follow this steps
    1. Group rules into group rules as much as possible
    2. Follow this order in priority
    * Blocked lists
    * Allowed lists
    * Amazon IP reputation lists
    * Amazon Anonymous IP list
    * AWS baseline managed rule groups
    Then use
    - Core rule set
    - Known bad inputs rule group
    Then use AWS use case specific rule groups
    - For example Linux OS rule group
    Then use Rate based rules
    Then use Intelligent bot threath mitigation rulegroups
    - Bot control rule set
    - Account takeover prevention
    - Account creation Fraud prevention
    - Use scope down statements

    Args:
        name (str): The name of the Web ACL to be created. This name must be unique within the scope
                   and will be used to generate the CloudWatch metric name.
        json_rules_acl (list): A list of rule objects that define the security rules for the Web ACL.
                              Each rule should contain statements for matching web requests and actions
                              to take when requests match.

    Returns:
        dict: AWS response containing the created Web ACL details including:
              - WebACL: Contains the configuration of the created ACL
              - Summary: Contains the WebACL ID, Name, and ARN

    Raises:
        Exception: If there's an error during Web ACL creation, including:
                  - WAFLimitsExceededException: If you exceed the maximum number of Web ACLs
                  - WAFInvalidParameterException: If any parameter is malformed
                  - WAFDuplicateItemException: If the ACL name already exists
                  - Other AWS WAF-related exceptions

    Example:
        rules = [
            {
                'Name': 'RateLimit',
                'Priority': 1,
                'Statement': {
                    'RateBasedStatement': {
                        'Limit': 2000,
                        'AggregateKeyType': 'IP'
                    }
                },
                'Action': {
                    'Block': {}
                },
                'VisibilityConfig': {
                    'SampledRequestsEnabled': True,
                    'CloudWatchMetricsEnabled': True,
                    'MetricName': 'RateLimitRule'
                }
            }
        ]
        
        response = await create_waf_acl('MyWebACL', rules)
    """
    # Create WAFv2 client
    try:
        # Create Web ACL
        response = wafv2_client.create_web_acl(
            Name=name,
            Scope='REGIONAL',  # Use 'CLOUDFRONT' for CloudFront distributions
            Description='Created by MCP',
            DefaultAction={
                'Allow': {}  # Default action to allow requests
            },
            Rules=json_rules_acl,
            VisibilityConfig={
                'SampledRequestsEnabled': False,
                'CloudWatchMetricsEnabled': True,
                'MetricName': f'{name}Metric'
            }
        )
        
        return f"Web ACL created. ARN is {response['Summary']['ARN']}"
        
    except Exception as e:
        return f"Error creating Web ACL: {str(e)}"
        

@mcp.tool()
async def associate_web_acl_to_alb(web_acl_arn, alb_arn):
    """
    Associates an AWS WAF web ACL with an Application Load Balancer.

    This function creates a connection between a WAF web ACL and an ALB, enabling
    the web ACL to filter traffic going to the specified load balancer.

    Args:
        web_acl_arn (str): The Amazon Resource Name (ARN) of the WAF web ACL.
            Format: arn:aws:wafv2:region:account-id:regional/webacl/name/id
        alb_arn (str): The ARN of the Application Load Balancer.
            Format: arn:aws:elasticloadbalancing:region:account-id:loadbalancer/app/name/id

    Returns:
        dict: The response from the AWS WAF service containing details of the association.
              An empty response indicates a successful association.

    Raises:
        WAFInvalidParameterException: If either ARN is malformed or invalid
        WAFNonexistentItemException: If either the web ACL or ALB doesn't exist
        WAFInternalErrorException: If AWS WAF experiences an internal error
        WAFLimitsExceededException: If you've reached the maximum number of web ACL associations
        Exception: Any other unexpected errors during the association process

    Example:
        web_acl_arn = "arn:aws:wafv2:us-west-2:123456789012:regional/webacl/mywebacl/abcd1234"
        alb_arn = "arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/app/my-alb/1234567890"
        
        try:
            response = await associate_web_acl_to_alb(web_acl_arn, alb_arn)
            print("Web ACL successfully associated with ALB")
        except Exception as e:
            print(f"Failed to associate Web ACL: {str(e)}")

    Note:
        - Only one web ACL can be associated with an ALB at a time
        - The web ACL and ALB must be in the same region
        - This operation requires appropriate IAM permissions for WAF and ELB services
    """
    try:
        response = wafv2_client.associate_web_acl(
            WebACLArn=web_acl_arn,
            ResourceArn=alb_arn
        )
        return response
    except Exception as e:
        print(f"Error associating Web ACL: {str(e)}")
        raise

@mcp.tool()
async def get_application_load_balancer_arn_by_name(alb_name):
    """
    Retrieves the Amazon Resource Name (ARN) of an Application Load Balancer by its name.

    Args:
        alb_name (str): The name of the Application Load Balancer to look up.
            Must be the exact name as it appears in AWS.

    Returns:
        str: The ARN of the Application Load Balancer in the format:
            arn:aws:elasticloadbalancing:region:account-id:loadbalancer/app/name/id

    Raises:
        Exception: If no ALB is found with the specified name
        LoadBalancerNotFoundException: If the load balancer name doesn't exist
        Exception: For other AWS API errors or unexpected issues

    Example:
        try:
            alb_arn = await get_application_load_balancer_arn_by_name('my-load-balancer')
            print(f"Found ALB ARN: {alb_arn}")
        except Exception as e:
            print(f"Failed to get ALB ARN: {str(e)}")

    Note:
        - The function assumes the ALB exists in the current AWS region
        - The AWS credentials must have elasticloadbalancing:DescribeLoadBalancers permission
        - Only returns the first matching ALB if multiple exist with the same name
    """

    # Create ELBv2 client
    try:
        # Describe load balancers with the specified name
        response = elbv2_client.describe_load_balancers(
            Names=[alb_name]
        )
        
        # Get the ARN from the first (and should be only) load balancer
        if response['LoadBalancers']:
            return response['LoadBalancers'][0]['LoadBalancerArn']
        else:
            raise Exception(f"No ALB found with name: {alb_name}")
            
    except elbv2_client.exceptions.LoadBalancerNotFoundException:
        raise Exception(f"Load balancer not found: {alb_name}")
    except Exception as e:
        print(f"Error getting ALB ARN: {str(e)}")
        raise

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')