import boto3
import json
import os
from botocore.exceptions import ClientError

def set_public_access_block(s3_client, bucket_name):
    """Set all public access block settings to True (block public access)"""
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    bucket_prefix = os.environ.get('BUCKET_PREFIX', '')  # Default to "breakrule"
    
    try:
        response = s3_client.list_buckets()
        buckets = [b for b in response['Buckets'] if b['Name'].startswith(bucket_prefix)]
        
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
                
                if is_fully_private:
                    status['public_access_status'] = 'Fully Private'
                    status['action'] = 'No change needed'
                else:
                    status['public_access_status'] = 'Partially Public'
                    # Turn off public access for Partially Public buckets
                    try:
                        set_public_access_block(s3_client, bucket_name)
                        status['action'] = 'Public access blocked'
                        print(f"Blocked public access for bucket: {bucket_name} (Partially Public)")
                    except Exception as update_error:
                        status['action'] = f'Failed to block public access: {str(update_error)}'
                
                status['details'] = {
                    'BlockPublicAcls': config['BlockPublicAcls'],
                    'IgnorePublicAcls': config['IgnorePublicAcls'],
                    'BlockPublicPolicy': config['BlockPublicPolicy'],
                    'RestrictPublicBuckets': config['RestrictPublicBuckets']
                }
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
                    status['public_access_status'] = 'Fully Public'
                    # Turn off public access for Fully Public buckets
                    try:
                        set_public_access_block(s3_client, bucket_name)
                        status['action'] = 'Public access blocked'
                        print(f"Blocked public access for bucket: {bucket_name} (Fully Public)")
                    except Exception as update_error:
                        status['action'] = f'Failed to block public access: {str(update_error)}'
                else:
                    status['public_access_status'] = f'Error: {str(e)}'
                
            except Exception as e:
                status['public_access_status'] = f'Error: {str(e)}'
                
            bucket_status.append(status)
            print(f"Processed bucket: {bucket_name} - {status['public_access_status']}")
        
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
            'body': json.dumps({'error': str(e)})
        }
