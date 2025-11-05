import json
import boto3
import os
from datetime import datetime 

# Get environment variables
TARGET_INSTANCE_ID = os.environ.get('EC2_INSTANCE_ID')
SES_FROM_EMAIL = os.environ.get('SES_FROM_EMAIL')
SES_TO_EMAIL = os.environ.get('SES_TO_EMAIL')

# --- Clients ---
s3_client = boto3.client('s3')
ec2_client = boto3.client('ec2')
ses_client = boto3.client('ses')

# --- Constants ---
COMMAND_ON = "ec2->on"
COMMAND_OFF = "ec2->off"

def lambda_handler(event, context):
    
    # 1. Get file info from the S3 event
    try:
        s3_record = event['Records'][0]['s3']
        bucket_name = s3_record['bucket']['name']
        file_key = s3_record['object']['key']
        print(f"New file detected: {file_key} in bucket {bucket_name}")
    except Exception as e:
        print(f"Error parsing S3 event: {e}")
        return {'statusCode': 400, 'body': 'Error parsing event'}

    message = ""

    try:
        file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = file_obj['Body'].read().decode('utf-8')
        data = json.loads(file_content)
        
        # Get the command from the JSON
        command = data.get('command')
        
        if command == COMMAND_ON:
            message = start_ec2_instance()
        elif command == COMMAND_OFF:
            message = stop_ec2_instance()
        else:
            s3_client.delete_object(Bucket=bucket_name, Key=file_key)
            message = f"Invalid command '{command}' received. No action taken. file is deleted"

        # 3. Rename the processed file
        rename_processed_file(bucket_name, file_key)

    except json.JSONDecodeError as e:
        print(f"Invalid JSON format: {e}")
        message = f"File '{file_key}' was not valid JSON. No action taken."
        # Clean up the invalid file
        s3_client.delete_object(Bucket=bucket_name, Key=file_key)
    except Exception as e:
        print(f"Error processing file: {e}")
        message = f"Error processing file: {e}"

    # 4. Send email notification
    try:
        send_confirmation_email(message)
    except Exception as e:
        print(f"Error sending email: {e}")

    return {'statusCode': 200, 'body': json.dumps(message)}


def start_ec2_instance():
    """Starts the target EC2 instance."""
    print(f"Received ON command for instance: {TARGET_INSTANCE_ID}")
    try:
        ec2_client.start_instances(InstanceIds=[TARGET_INSTANCE_ID])
        return f"Command 'ec2->on' received. Starting instance: {TARGET_INSTANCE_ID}"
    except Exception as e:
        print(f"Error starting instance: {e}")
        return f"Error starting instance {TARGET_INSTANCE_ID}: {e}"

def stop_ec2_instance():
    """Stops the target EC2 instance."""
    print(f"Received OFF command for instance: {TARGET_INSTANCE_ID}")
    try:
        ec2_client.stop_instances(InstanceIds=[TARGET_INSTANCE_ID])
        return f"Command 'ec2->off' received. Stopping instance: {TARGET_INSTANCE_ID}"
    except Exception as e:
        print(f"Error stopping instance: {e}")
        return f"Error stopping instance {TARGET_INSTANCE_ID}: {e}"

def rename_processed_file(bucket_name, file_key):
    """Renames the S3 file with a timestamp (Copy + Delete)."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        base_name = os.path.splitext(file_key)[0]
        extension = os.path.splitext(file_key)[1]
        
        new_key = f"{timestamp}-{base_name}{extension}" 
        print(f"Renaming file to: {new_key}")

        copy_source = {'Bucket': bucket_name, 'Key': file_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=bucket_name,
            Key=new_key
        )
        s3_client.delete_object(Bucket=bucket_name, Key=file_key)
    except Exception as e:
        print(f"Error renaming file {file_key}: {e}")

def send_confirmation_email(message_body):
    """Sends an email using Amazon SES."""
    print(f"Sending email to {SES_TO_EMAIL}...")
    ses_client.send_email(
        Source=SES_FROM_EMAIL,
        Destination={
            'ToAddresses': [SES_TO_EMAIL]
        },
        Message={
            'Subject': {
                'Data': 'EC2 Controller Status Update'
            },
            'Body': {
                'Text': {
                    'Data': message_body
                }
            }
        }
    )
    print("Email sent.")