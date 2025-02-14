# Description: This Lambda function redacts social security numbers (SSNs) from objects in an S3 bucket. It is invoked
# by an S3 event notification when an object is created in the bucket. The function retrieves the object, redacts SSNs
# from the content, and optionally saves the redacted content back to another S3 bucket or key. The function logs the
# original and redacted content for testing purposes. The redact_ssn function uses a regular expression to match SSNs in
# the format xxx-xx-xxxx, and the re.sub function replaces the matched SSNs with '***-**-****'.

import json
import re
import logging
import boto3
from botocore.exceptions import ClientError

# Initialize logging: we're using serverless logging, so this will write to CloudWatch Logs and info level
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize s3 client
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

# Regular expression to match SSN format: xxx-xx-xxxx
SSN_REGEX = r'\b\d{3}-\d{2}-\d{4}\b'

def redact_ssn(data):
    """
    Redacts all social security numbers (SSNs) in the provided data.

    Parameters:
    data (str): The input string containing SSNs.

    Returns:
    str: The input string with SSNs redacted.
    """
    return re.sub(SSN_REGEX, '***-**-****', data)

def lambda_handler(event, context):
    """
    Lambda handler to redact SSNs from objects in an S3 bucket.

    Parameters:
    event (dict): The lambda event data containing bucket and key information.

    Returns:
    dict: A response object with status code and message.
    """
    bucket_name = key = None
    try:
        # Get the bucket and key from the event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        # Log the event, bucket, and key for testing
        try:
            logger.info(f"Event: {json.dumps(event, indent=2)}")
        except TypeError as e:
            logger.error(f"Error serializing event: {e}")

        # Retrieve the object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        file_content = response['Body'].read().decode('utf-8')

        # Redact SSNs from the file content
        redacted_content = redact_ssn(file_content)

        # Log the original and redacted content for testing
        # *** This will go to CloudWatch logs so don't be doing this in production!
        logger.info(f"Original Content: {file_content}")
        logger.info(f"Redacted Content: {redacted_content}")

        # Optionally, save the redacted content back to another S3 bucket or key
        # Uncomment below lines to save in another bucket/key
        # target_bucket = 'my-redacted-s3-bucket'
        # target_key = 'redacted-{key}'
        # s3_client.put_object(Bucket=target_bucket, Key=target_key, Body=redacted_content.encode('utf-8'))

        return {
            'statusCode': 200,
            'body': json.dumps('SSNs redacted successfully')
        }
    except ClientError as e:
        logger.error(f"ClientError: {e.response['Error']['Message']}")
        raise e
    except Exception as e:
        logger.error(f"Error processing object {key} from bucket {bucket_name}. Event: {json.dumps(event, indent=2)}")
        logger.error(e)
        raise e