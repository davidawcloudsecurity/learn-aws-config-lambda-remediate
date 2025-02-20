import boto3
import json

def lambda_handler(event, context):
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    try:
        # Get list of all buckets
        response = s3_client.list_buckets()
        buckets = response['Buckets']
        
        # Store results
        deleted_buckets = []
        skipped_buckets = []
        
        for bucket in buckets:
            bucket_name = bucket['Name']
            
            # Check public access block configuration
            try:
                public_access_config = s3_client.get_public_access_block(
                    Bucket=bucket_name
                )
                
                # Get the configuration settings
                config = public_access_config['PublicAccessBlockConfiguration']
                
                # Check if all public access is blocked
                is_fully_private = (
                    config['BlockPublicAcls'] and
                    config['IgnorePublicAcls'] and
                    config['BlockPublicPolicy'] and
                    config['RestrictPublicBuckets']
                )
                
                if is_fully_private:
                    # Delete the bucket if public access is fully blocked
                    s3_client.delete_bucket(Bucket=bucket_name)
                    deleted_buckets.append(bucket_name)
                    print(f"Deleted bucket: {bucket_name}")
                else:
                    skipped_buckets.append({
                        'bucket': bucket_name,
                        'reason': 'Public access not fully blocked'
                    })
                    print(f"Skipped bucket: {bucket_name} - Public access not fully blocked")
                    
            except s3_client.exceptions.NoSuchPublicAccessBlockConfiguration:
                # Skip buckets with no public access block configuration
                skipped_buckets.append({
                    'bucket': bucket_name,
                    'reason': 'No public access block configuration'
                })
                print(f"Skipped bucket: {bucket_name} - No public access block configuration")
                
            except Exception as e:
                skipped_buckets.append({
                    'bucket': bucket_name,
                    'reason': str(e)
                })
                print(f"Error processing {bucket_name}: {str(e)}")
        
        # Prepare response
        result = {
            'statusCode': 200,
            'body': json.dumps({
                'deleted_buckets': deleted_buckets,
                'skipped_buckets': skipped_buckets,
                'total_processed': len(buckets)
            })
        }
        
        return result
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
