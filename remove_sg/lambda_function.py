import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    errors = []

    try:
        # Describe all security groups
        response = ec2.describe_security_groups()
        
        for sg in response['SecurityGroups']:
            group_id = sg['GroupId']
            
            # Check and remove inbound rules allowing all traffic from 0.0.0.0/0
            for rule in sg.get('IpPermissions', []):
                # Check if the rule allows all protocols (-1) and all ports (0-65535)
                is_all_traffic = (rule.get('IpProtocol') == '-1' or 
                                (rule.get('FromPort') == 0 and rule.get('ToPort') == 65535))
                
                # Check if the rule includes 0.0.0.0/0 in its IP ranges
                has_open_cidr = any(ip_range['CidrIp'] == '0.0.0.0/0' for ip_range in rule.get('IpRanges', []))
                
                if is_all_traffic and has_open_cidr:
                    # Extract rule details for logging
                    rule_id = rule.get('SecurityGroupRuleId', 'No Rule ID available')
                    ip_protocol = rule.get('IpProtocol', 'All')
                    port_range = f"{rule.get('FromPort', '0')}-{rule.get('ToPort', '65535')}" if 'FromPort' in rule and 'ToPort' in rule else 'All'
                    source = [ip_range['CidrIp'] for ip_range in rule.get('IpRanges', []) if ip_range['CidrIp'] == '0.0.0.0/0'][0]
                    traffic_type = 'All traffic'  # This is inferred since we already checked for all protocols/ports

                    # Print identified rule details
                    print(f"Identified rule for removal:")
                    print(f"  Security Group ID: {group_id}")
                    print(f"  Security Group Rule ID: {rule_id}")
                    print(f"  Traffic Type: {traffic_type}")
                    print(f"  Protocol: {ip_protocol}")
                    print(f"  Port Range: {port_range}")
                    print(f"  Source: {source}")

                    try:
                        ec2.revoke_security_group_ingress(
                            GroupId=group_id,
                            IpPermissions=[rule]
                        )
                        print(f"Removed open inbound rule from Security Group: {group_id}")
                    except Exception as e:
                        errors.append(f"Failed to remove inbound rule from {group_id}: {str(e)}")
            
            # Check and remove outbound rules allowing all traffic from 0.0.0.0/0
            for rule in sg.get('IpPermissionsEgress', []):
                # Check if the rule allows all protocols (-1) and all ports (0-65535)
                is_all_traffic = (rule.get('IpProtocol') == '-1' or 
                                (rule.get('FromPort') == 0 and rule.get('ToPort') == 65535))
                
                # Check if the rule includes 0.0.0.0/0 in its IP ranges
                has_open_cidr = any(ip_range['CidrIp'] == '0.0.0.0/0' for ip_range in rule.get('IpRanges', []))
                
                if is_all_traffic and has_open_cidr:
                    # Extract rule details for logging
                    rule_id = rule.get('SecurityGroupRuleId', 'No Rule ID available')
                    ip_protocol = rule.get('IpProtocol', 'All')
                    port_range = f"{rule.get('FromPort', '0')}-{rule.get('ToPort', '65535')}" if 'FromPort' in rule and 'ToPort' in rule else 'All'
                    source = [ip_range['CidrIp'] for ip_range in rule.get('IpRanges', []) if ip_range['CidrIp'] == '0.0.0.0/0'][0]
                    traffic_type = 'All traffic'  # This is inferred since we already checked for all protocols/ports

                    # Print identified rule details
                    print(f"Identified rule for removal:")
                    print(f"  Security Group ID: {group_id}")
                    print(f"  Security Group Rule ID: {rule_id}")
                    print(f"  Traffic Type: {traffic_type}")
                    print(f"  Protocol: {ip_protocol}")
                    print(f"  Port Range: {port_range}")
                    print(f"  Source: {source}")

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
