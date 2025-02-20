import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
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
                            print(f"Failed to remove inbound rule from {group_id}: {str(e)}")
        
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
                            print(f"Failed to remove outbound rule from {group_id}: {str(e)}")
    
    return {
        'statusCode': 200,
        'body': 'Security Group check and remediation completed'
    }
