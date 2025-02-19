import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    response = ec2.describe_security_groups()

    for sg in response['SecurityGroups']:
        for rule in sg.get('IpPermissionsEgress', []):
            if 'IpRanges' in rule:
                for ip_range in rule['IpRanges']:
                    if ip_range['CidrIp'] == '0.0.0.0/0':
                        try:
                            ec2.revoke_security_group_egress(
                                GroupId=sg['GroupId'],
                                IpProtocol=rule['IpProtocol'],
                                FromPort=rule.get('FromPort'),
                                ToPort=rule.get('ToPort'),
                                CidrIp='0.0.0.0/0'
                            )
                            print(f"Removed open outbound rule from Security Group: {sg['GroupId']}")
                        except Exception as e:
                            print(f"Failed to remove rule from {sg['GroupId']}: {str(e)}")

    return {
        'statusCode': 200,
        'body': 'Security Group check and remediation completed'
    }
