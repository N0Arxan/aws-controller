import json
import boto3
import os
import uuid

S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

ALLOWED_CONTENT_TYPE = "application/json"

URL_EXPIRATION_SECONDS = 60 

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    
    try:
        body = json.loads(event.get('body', '{}'))
        client_filename = body.get('filename')
        
        if not client_filename:
            raise ValueError("Missing 'filename' in request body")
        
        if not client_filename.endswith('.json'):
            raise ValueError("File must be a .json file")
            
        s3_key = client_filename

    except Exception as e:
        print(f"Error parsing body: {e}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }

    presigned_params = {
        'Bucket': S3_BUCKET_NAME,
        'Key': s3_key,
        'ContentType': ALLOWED_CONTENT_TYPE, 
    }

    try:
        upload_url = s3_client.generate_presigned_url(
            'put_object',
            Params=presigned_params,
            ExpiresIn=URL_EXPIRATION_SECONDS
        )
        
        return {
            "statusCode": 200,

            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({
                "uploadURL": upload_url, 
                "s3Key": s3_key
            })
        }
        
    except Exception as e:
        print(f"Error generating URL: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Could not generate upload URL"})
        }