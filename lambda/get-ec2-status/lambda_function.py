import json
import boto3
import os
import datetime

# Get the instance ID from environment variables
TARGET_INSTANCE_ID = os.environ.get('EC2_INSTANCE_ID')

ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    
    try:
        response = ec2_client.describe_instances(InstanceIds=[TARGET_INSTANCE_ID])
        
        if not response['Reservations'] or not response['Reservations'][0]['Instances']:
            raise Exception("Instance not found")
        
        instance = response['Reservations'][0]['Instances'][0]
        
        instance_name = "N/A"
        if 'Tags' in instance:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break
        
        state = instance['State']['Name']
        public_ip = instance.get('PublicIpAddress', None)
        private_ip = instance.get('PrivateIpAddress', None)
        instance_type = instance['InstanceType']
        availability_zone = instance['Placement']['AvailabilityZone']
        launch_time = instance['LaunchTime'].isoformat()
        
        instance_data = {
            "instanceId": instance['InstanceId'],
            "name": instance_name,
            "state": state,
            "instanceType": instance_type,
            "publicIp": public_ip,
            "privateIp": private_ip,
            "availabilityZone": availability_zone,
            "launchTime": launch_time
        }
        

        return instance_data
        
    except Exception as e:
        print(f"Error: {e}")
        # With non-proxy, you must raise an error to signal a 500
        raise Exception(f"Error processing request: {str(e)}")