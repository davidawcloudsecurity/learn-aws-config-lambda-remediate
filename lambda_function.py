import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    errors = []

    try:
        # Describe all security groups
        response = ec2.describe_security_groups()
        
        for sg in response['SecurityGroups']:
            group_id = sg['GroupId']
            
            # Check and remove inbound rules allowing all traffic
            for rule in sg.get('IpPermissions', []):
                if rule.get('IpProtocol') == '-1' or (rule.get('FromPort') == 0 and rule.get('ToPort') == 65535):
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range['CidrIp'] == '0.0.0.0/0':
                            try:
                                ec2.revoke_security_group_ingress(
                                    GroupId=group_id,
                                    IpPermissions=[rule]
                                )
                                print(f"Removed open inbound rule from Security Group: {group_id}")
                            except Exception as e:
                                errors.append(f"Failed to remove inbound rule from {group_id}: {str(e)}")
            
            # Check and remove outbound rules allowing all traffic
            for rule in sg.get('IpPermissionsEgress', []):
                if rule.get('IpProtocol') == '-1' or (rule.get('FromPort') == 0 and rule.get('ToPort') == 65535):
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range['CidrIp'] == '0.0.0.0/0':
                            try:
                                ec2.revoke_security_group_egress(
                                    GroupId=group_id,
                                    IpPermissions=[rule]
                                )
                                print(f"Removed open outbound rule from Security Group: {group_id}")
                            except Exception as e:
                                errors.append(f"Failed to remove outbound rule from {group_id}: {str(e)}")
        
        # If no errors occurred, return success message
        if not errors:
            return {
                'statusCode': 200,
                'body': 'Security Group check and remediation completed successfully'
            }
        # If errors occurred, return the list of errors
        else:
            return {
                'statusCode': 500,
                'body': f"Errors occurred: {errors}"
            }
    
    except Exception as e:
        # Catch any unexpected errors and return them
        return {
            'statusCode': 500,
            'body': f"An unexpected error occurred: {str(e)}"
        }
