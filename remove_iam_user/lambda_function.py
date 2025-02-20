import boto3
import json
import os

def lambda_handler(event, context):
    iam_client = boto3.client('iam')
    
    try:
        # Get all IAM users
        response = iam_client.list_users()
        users = response['Users']
        
        user_status = []
        
        for user in users:
            user_name = user['UserName']
            status = {
                'user_name': user_name,
                'has_access_keys': False,
                'has_mfa': False,
                'action': 'No action'
            }
            
            # Check for access keys
            access_keys = iam_client.list_access_keys(UserName=user_name)['AccessKeyMetadata']
            active_access_keys = [key for key in access_keys if key['Status'] == 'Active']
            if active_access_keys:
                status['has_access_keys'] = True
                status['access_key_count'] = len(active_access_keys)
            
            # Check for MFA devices
            mfa_devices = iam_client.list_mfa_devices(UserName=user_name)['MFADevices']
            if mfa_devices:
                status['has_mfa'] = True
                status['mfa_device_count'] = len(mfa_devices)
            
            # Delete user if they have access keys but no MFA
            if status['has_access_keys'] and not status['has_mfa']:
                try:
                    # Remove all access keys first
                    for key in active_access_keys:
                        iam_client.delete_access_key(
                            UserName=user_name,
                            AccessKeyId=key['AccessKeyId']
                        )
                    
                    # Delete the user
                    iam_client.delete_user(UserName=user_name)
                    status['action'] = 'Deleted'
                    print(f"Deleted user: {user_name} (Had access keys, no MFA)")
                except Exception as delete_error:
                    status['action'] = f'Failed to delete: {str(delete_error)}'
            
            user_status.append(status)
            print(f"Processed user: {user_name} - Access Keys: {status['has_access_keys']}, MFA: {status['has_mfa']}, Action: {status['action']}")
        
        result = {
            'statusCode': 200,
            'body': json.dumps({
                'users': user_status,
                'total_processed': len(users)
            }, indent=2)
        }
        
        return result
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
