import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    
    # Get list of all buckets
    try:
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
    except ClientError as e:
        print(f"Error listing buckets: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to list buckets')
        }
    
    # Check each bucket's policy
    for bucket in buckets:
        try:
            policy = s3_client.get_bucket_policy(Bucket=bucket)
            policy_json = json.loads(policy['Policy'])
            has_secure_transport_deny = check_secure_transport(policy_json)
            
            if has_secure_transport_deny:
                print(f"Bucket {bucket}: Secure transport enforced.")
            else:
                print(f"Bucket {bucket}: WARNING - No secure transport enforcement found!")
                
        except ClientError as e:
            # If no policy exists, it won't enforce secure transport
            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                print(f"Bucket {bucket}: WARNING - No policy exists!")
            else:
                print(f"Bucket {bucket}: Error retrieving policy - {e}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Bucket scan completed')
    }

def check_secure_transport(policy_json):
    """
    Check if the policy has a Deny statement for non-secure transport.
    Returns True if found, False otherwise.
    """
    statements = policy_json.get('Statement', [])
    if isinstance(statements, dict):  # Handle single-statement policies
        statements = [statements]
        
    for statement in statements:
        if (statement.get('Effect') == 'Deny' and
            'Condition' in statement and
            'Bool' in statement['Condition'] and
            statement['Condition']['Bool'].get('aws:SecureTransport') == 'false'):
            # Verify it applies to s3:* actions and the bucket resource
            actions = statement.get('Action', [])
            if isinstance(actions, str):
                actions = [actions]
            if 's3:*' in actions or any(a.startswith('s3:') for a in actions):
                return True
    return False
