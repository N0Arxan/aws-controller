# AWS EC2 Controller

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Lambda Functions](#lambda-functions)
- [AWS Services Configuration](#aws-services-configuration)
- [Development Setup](#development-setup)
- [Build & Deployment](#build--deployment)
- [Environment Variables](#environment-variables)

## Overview

Static web application hosted on S3 for controlling AWS EC2 instances via JSON command files. Supports two upload methods: file upload and inline JSON editor. Commands include `ec2->on` and `ec2->off`.

**Stack:** Vue 3 + Vite, Tailwind CSS v3, Font Awesome, AWS Lambda (Python 3.x), S3, API Gateway, SES

## Project Structure

```
aws-controller/
├── src/
│   ├── components/
│   │   └── JSONEditor.vue       # Inline JSON editor component
│   ├── services/
│   │   └── api.js               # Centralized API calls
│   ├── views/
│   │   ├── UploadPage.vue       # Main page (file upload + editor)
│   │   └── StatusPage.vue       # EC2 status dashboard
│   ├── router/
│   │   └── index.js             # Routes: /, /status
│   ├── App.vue
│   ├── main.js                  # Font Awesome config
│   └── style.css                # Tailwind directives
├── lambda/
│   ├── generate-upload-url/     # Lambda: S3 presigned URL
│   ├── get-ec2-status/          # Lambda: EC2 instance info
│   └── process-s3-file/         # Lambda: S3 trigger processor
├── public/
├── .env                         # API URLs (DO NOT COMMIT)
├── .env.example                 # Template
├── tailwind.config.js           # Notion theme colors
├── postcss.config.js
├── vite.config.js
└── package.json
```

## Lambda Functions

All functions run on **Python 3.x** runtime. Each requires specific IAM permissions.

### 1. `generate-upload-url`

**Trigger:** API Gateway (POST)  
**Purpose:** Generate presigned S3 upload URLs  
**IAM Permissions:**
```json
{
  "Effect": "Allow",
  "Action": ["s3:PutObject"],
  "Resource": "arn:aws:s3:::[your-bucket-name]/*"
}
```

**Request:**
```json
{
  "fileName": "command.json",
}
```

**Response:**
```json
{
  "uploadUrl": "https://s3.amazonaws.com/...",
  "s3Key": "command.json"
}
```

**⚠️ CORS Required:** Must return `Access-Control-Allow-Origin: *` header

---

### 2. `get-ec2-status`

**Trigger:** API Gateway (GET)  
**Purpose:** Retrieve EC2 instance information  
**IAM Permissions:**
```json
{
  "Effect": "Allow",
  "Action": [
    "ec2:DescribeInstances",
    "ec2:DescribeTags"
  ],
  "Resource": "*"
}
```

**Response:**
```json
{
  "instanceId": "i-xxxxx",
  "name": "EC2-Instance-Name",
  "state": "running",
  "instanceType": "t2.micro",
  "publicIp": "54.x.x.x",
  "privateIp": "172.x.x.x",
  "availabilityZone": "us-east-1a",
  "launchTime": "2024-01-15T10:30:00Z"
}
```

**⚠️ CORS Required:** Must return `Access-Control-Allow-Origin: *` header

---

### 3. `process-s3-file`

**Trigger:** S3 Event (ObjectCreated)  
**Purpose:** Process uploaded JSON files, execute EC2 commands, send confirmation emails  
**IAM Permissions:**
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "ec2:StartInstances",
    "ec2:StopInstances",
    "ec2:DescribeInstances",
    "ses:SendEmail"
  ],
  "Resource": [
    "arn:aws:s3:::arn:aws:s3:::[your-bucket-name]/*",
    "arn:aws:ec2:*:*:instance/*",
    "*"
  ]
}
```

**Supported Commands:**
- `{"command": "ec2->on"}` - Start EC2 instances
- `{"command": "ec2->off"}` - Stop EC2 instances

**No CORS required** (S3 trigger, not API Gateway)

## AWS Services Configuration

### S3 Bucket: `ec2-controller-n0arxan`

**Bucket Policy:** Public read access for static website hosting  
**Static Website Hosting:** Enabled (index: `index.html`)  
**CORS Configuration:**
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```

**⚠️ Upload via AWS Console:** S3 → Bucket → Permissions → CORS configuration → Edit → Paste JSON

---

### SES (Simple Email Service)

**Configuration:**
- **Region:** Must match Lambda region
- **Verified Identities:** 2 personal email addresses
- **Sender Email:** Configured in `process-s3-file` Lambda
- **Recipient Email:** Configured in `process-s3-file` Lambda

**⚠️ Production:** Move SES out of sandbox mode to send to unverified addresses

---

### API Gateway

**Endpoints:**
1. `POST /generate-upload-url` → `generate-upload-url` Lambda
2. `GET /get-ec2-status` → `get-ec2-status` Lambda

**⚠️ Enable CORS:**
- API Gateway → Resources → Actions → Enable CORS
- Deploy API after changes

## Development Setup

```bash
# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your API Gateway URLs

# Start dev server
npm run dev
```

**Environment Variables (`.env`):**
```env
VITE_API_UPLOAD_URL=https://xxxxx.execute-api.amazonaws.com/prod/generate-upload-url
VITE_API_STATUS_URL=https://xxxxx.execute-api.amazonaws.com/prod/get-ec2-status
```

**Note:** Vite requires `VITE_` prefix for client-side access

## Build & Deployment

```bash
# Build production bundle
npm run build

# Output: dist/
```

### Deploy to S3

```bash
# Upload build to S3
aws s3 sync dist/ s3://ec2-controller-n0arxan --delete

# Set index.html as default document
aws s3 website s3://ec2-controller-n0arxan --index-document index.html

# Make bucket public (if not already configured)
aws s3api put-bucket-policy --bucket ec2-controller-n0arxan --policy file://bucket-policy.json
```

**Bucket Policy (`bucket-policy.json`):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::[your-bucket-name]/*"
    }
  ]
}
```

**⚠️ CORS Setup:**
1. Build → Deploy to S3
2. AWS Console → S3 → `your bucket` → Permissions → CORS → Add configuration (see above)
3. Test upload functionality

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_UPLOAD_URL` | API Gateway endpoint for presigned URLs | `https://xxx.execute-api.amazonaws.com/prod/generate-upload-url` |
| `VITE_API_STATUS_URL` | API Gateway endpoint for EC2 status | `https://xxx.execute-api.amazonaws.com/prod/get-ec2-status` |

**Access in code:**
```javascript
import.meta.env.VITE_API_UPLOAD_URL
```

## CI/CD - Auto Deployment

GitHub Actions workflow (`.github/workflows/deploy.yaml`) automatically deploys to S3 on every push to `main` branch.

**Workflow steps:**
1. Checkout code
2. Install dependencies (`npm ci`)
3. Build production bundle (`npm run build`)
4. Sync `dist/` to S3 bucket

**Required GitHub Secrets:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

**S3 Bucket:** `my-ec2-controller-web`  
**Region:** `eu-north-1`

---

**License:** MIT

