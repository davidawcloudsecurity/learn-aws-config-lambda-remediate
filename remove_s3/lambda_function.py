import boto3
import json
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    bucket_prefix = os.environ.get('BUCKET_PREFIX', '')  # Optional prefix filter
    
    try:
        # Get list of all buckets
        response = s3_client.list_buckets()
        buckets = [b for b in response['Buckets'] if b['Name'].startswith(bucket_prefix)]
        
        # Store results
        bucket_status = []
        
        for bucket in buckets:
            bucket_name = bucket['Name']
            status = {
                'bucket_name': bucket_name,
                'public_access_status': 'Unknown'
            }
            
            try:
                public_access_config = s3_client.get_public_access_block(
                    Bucket=bucket_name
                )
                
                config = public_access_config['PublicAccessBlockConfiguration']
                is_fully_private = (
                    config['BlockPublicAcls'] and
                    config['IgnorePublicAcls'] and
                    config['BlockPublicPolicy'] and
                    config['RestrictPublicBuckets']
                )
                
                status['public_access_status'] = 'Fully Private' if is_fully_private else 'Partially Public'
                status['details'] = {
                    'BlockPublicAcls': config['BlockPublicAcls'],
                    'IgnorePublicAcls': config['IgnorePublicAcls'],
                    'BlockPublicPolicy': config['BlockPublicPolicy'],
                    'RestrictPublicBuckets': config['RestrictPublicBuckets']
                }
                
            except ClientError as e:
                # Check the error code to identify NoSuchPublicAccessBlockConfiguration
                if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
                    status['public_access_status'] = 'No Public Access Block Configured'
                else:
                    status['public_access_status'] = f'Error: {str(e)}'
                
            except Exception as e:
                status['public_access_status'] = f'Error: {str(e)}'
                
            bucket_status.append(status)
            print(f"Processed bucket: {bucket_name} - {status['public_access_status']}")
        
        # Prepare response
        result = {
            'statusCode': 200,
            'body': json.dumps({
                'buckets': bucket_status,
                'total_processed': len(buckets)
            }, indent=2)
        }
        
        return result
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
