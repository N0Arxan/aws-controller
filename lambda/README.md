# Lambda Functions

This directory contains all AWS Lambda functions for the EC2 Control Portal backend.

## Structure

```
lambda/
├── generate-upload-url/    # Generates presigned S3 URLs for file upload
├── get-ec2-status/         # Fetches EC2 instance status
└── process-s3-file/        # Processes files uploaded to S3 (optional)
```

## Lambda Functions

### 1. `generate-upload-url`
**Purpose:** Generate presigned S3 upload URLs for the frontend to upload JSON files directly to S3.

**Trigger:** API Gateway (POST)  
**Runtime:** Python 3.x  
**IAM Permissions Required:**
- `s3:PutObject` on your S3 bucket

**API Request:**
```json
{
  "filename": "config.json"
}
```

**API Response:**
```json
{
  "uploadURL": "https://s3.amazonaws.com/bucket/key?presigned-params"
}
```

### 2. `get-ec2-status`
**Purpose:** Retrieve EC2 instance information and status.

**Trigger:** API Gateway (GET)  
**Runtime:** Python 3.x  
**IAM Permissions Required:**
- `ec2:DescribeInstances`
- `ec2:DescribeTags`

**API Response:**
```json
{
  "instanceId": "i-1234567890abcdef0",
  "name": "My EC2 Instance",
  "state": "running",
  "instanceType": "t2.micro",
  "publicIp": "54.123.45.67",
  "privateIp": "172.31.0.1",
  "availabilityZone": "us-east-1a",
  "launchTime": "2024-01-15T10:30:00Z"
}
```

### 3. `process-s3-file` (Optional)
**Purpose:** Process JSON files uploaded to S3 (e.g., execute commands, update configurations).

**Trigger:** S3 Event (ObjectCreated)  
**Runtime:** Python 3.x  
**IAM Permissions Required:**
- `s3:GetObject`
- `ec2:*` (depending on commands)

## Deployment

### Option 1: AWS Console
1. Go to AWS Lambda Console
2. Create a new function for each Lambda
3. Copy the code from the respective directory
4. Configure environment variables
5. Set up IAM roles with required permissions
6. Create API Gateway endpoints (for `generate-upload-url` and `get-ec2-status`)
7. Enable CORS on API Gateway

### Option 2: AWS SAM (Serverless Application Model)
See `template.yaml` in the root directory for SAM deployment configuration.

### Option 3: AWS CLI
```bash
# Package and deploy each function
cd lambda/generate-upload-url
zip -r function.zip .
aws lambda update-function-code \
  --function-name generate-upload-url \
  --zip-file fileb://function.zip
```

## Environment Variables

Each Lambda function may require environment variables:

**generate-upload-url:**
- `S3_BUCKET_NAME` - Name of the S3 bucket for uploads

**get-ec2-status:**
- `EC2_REGION` - AWS region (e.g., `eu-north-1`)
- `INSTANCE_ID` - Specific instance ID to monitor (optional)

**process-s3-file:**
- `S3_BUCKET_NAME` - Name of the S3 bucket
- `EC2_REGION` - AWS region

## CORS Configuration

**IMPORTANT:** All Lambda functions must return CORS headers:

```python
{
    'statusCode': 200,
    'headers': {
        'Access-Control-Allow-Origin': '*',  # or your domain
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Content-Type': 'application/json'
    },
    'body': json.dumps(data)
}
```

See `CORS_FIX.md` in the root directory for detailed CORS setup.

## Testing

Test each function locally or in AWS Console:

```bash
# Test generate-upload-url
aws lambda invoke \
  --function-name generate-upload-url \
  --payload '{"filename": "test.json"}' \
  response.json

# Test get-ec2-status
aws lambda invoke \
  --function-name get-ec2-status \
  response.json
```

## Security Best Practices

1. **Use IAM roles** - Don't hardcode AWS credentials
2. **Least privilege** - Grant only necessary permissions
3. **CORS restrictions** - In production, specify exact domains instead of `*`
4. **API Gateway authentication** - Add API keys or Cognito auth
5. **Environment variables** - Store sensitive data in AWS Secrets Manager
6. **Logging** - Enable CloudWatch logs for debugging

## Common Issues

### CORS Errors
- Ensure CORS headers are in Lambda responses
- Enable CORS in API Gateway
- Deploy API Gateway changes

### Permission Errors
- Check IAM role attached to Lambda
- Verify resource policies (S3 bucket, EC2)
- Check CloudWatch logs for detailed errors

## Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway CORS](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html)
- [S3 Presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html)
