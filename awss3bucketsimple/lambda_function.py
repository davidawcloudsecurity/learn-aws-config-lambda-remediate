import boto3
import json

def evaluate_compliance(configuration_item):
    s3 = boto3.client('s3')
    bucket_name = configuration_item['resourceName']
    
    try:
        response = s3.get_public_access_block(Bucket=bucket_name)
        settings = response['PublicAccessBlockConfiguration']
        if all([
            settings.get('BlockPublicAcls', False),
            settings.get('IgnorePublicAcls', False),
            settings.get('BlockPublicPolicy', False),
            settings.get('RestrictPublicBuckets', False)
        ]):
            return 'COMPLIANT'
        else:
            return 'NON_COMPLIANT'
    except s3.exceptions.NoSuchPublicAccessBlockConfiguration:
        return 'NON_COMPLIANT'
    except Exception as e:
        print(f"Error evaluating {bucket_name}: {str(e)}")
        return 'NON_COMPLIANT'

def lambda_handler(event, context):
    invoking_event = json.loads(event['invokingEvent'])
    config_item = invoking_event.get('configurationItem', {})
    
    if config_item['resourceType'] != 'AWS::S3::Bucket':
        return {
            'resultToken': event['resultToken']
        }
    
    compliance = evaluate_compliance(config_item)
    
    evaluation = {
        'ComplianceResourceType': 'AWS::S3::Bucket',
        'ComplianceResourceId': config_item['resourceName'],
        'ComplianceType': compliance,
        'OrderingTimestamp': config_item['configurationItemCaptureTime']
    }
    
    config = boto3.client('config')
    response = config.put_evaluations(
        Evaluations=[evaluation],
        ResultToken=event['resultToken']
    )
    return response
