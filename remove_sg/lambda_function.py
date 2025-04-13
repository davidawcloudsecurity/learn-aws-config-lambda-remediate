import boto3

# use vpc-sg-open-only-to-authorized-ports

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    errors = []

    try:
        # Describe all security group rules
        paginator = ec2.get_paginator('describe_security_group_rules')
        for page in paginator.paginate():
            for rule in page['SecurityGroupRules']:
                # Check if the rule allows all traffic (protocol -1 or ports 0-65535)
                is_all_traffic = (rule.get('IpProtocol') == '-1' or 
                                (rule.get('FromPort') == 0 and rule.get('ToPort') == 65535))
                
                # Check if the rule includes 0.0.0.0/0 in its IP ranges
                has_open_cidr = (rule.get('CidrIpv4') == '0.0.0.0/0')
                
                # Check if the rule is inbound or outbound
                is_egress = rule.get('IsEgress', False)
                
                if is_all_traffic and has_open_cidr:
                    # Extract rule details for logging
                    rule_id = rule.get('SecurityGroupRuleId')
                    group_id = rule.get('GroupId')
                    ip_protocol = rule.get('IpProtocol', 'All')
                    port_range = f"{rule.get('FromPort', '0')}-{rule.get('ToPort', '65535')}" if 'FromPort' in rule and 'ToPort' in rule else 'All'
                    source = rule.get('CidrIpv4', '0.0.0.0/0')
                    traffic_type = 'All traffic'  # This is inferred since we already checked for all protocols/ports

                    # Print identified rule details
                    print(f"Identified rule for removal:")
                    print(f"  Security Group ID: {group_id}")
                    print(f"  Security Group Rule ID: {rule_id}")
                    print(f"  Traffic Type: {traffic_type}")
                    print(f"  Protocol: {ip_protocol}")
                    print(f"  Port Range: {port_range}")
                    print(f"  Source: {source}")
                    print(f"  Direction: {'Outbound' if is_egress else 'Inbound'}")

                    try:
                        if is_egress:
                            # Remove outbound rule
                            ec2.revoke_security_group_egress(
                                GroupId=group_id,
                                SecurityGroupRuleIds=[rule_id]
                            )
                            print(f"Removed open outbound rule from Security Group: {group_id}")
                        else:
                            # Remove inbound rule
                            ec2.revoke_security_group_ingress(
                                GroupId=group_id,
                                SecurityGroupRuleIds=[rule_id]
                            )
                            print(f"Removed open inbound rule from Security Group: {group_id}")
                    except Exception as e:
                        errors.append(f"Failed to remove rule {rule_id} from {group_id}: {str(e)}")
        
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
