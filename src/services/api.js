// API configuration and endpoints from environment variables
const API_CONFIG = {
  UPLOAD_URL: import.meta.env.VITE_API_UPLOAD_URL,
  STATUS_URL: import.meta.env.VITE_API_STATUS_URL,
};


/**
 * Request presigned S3 upload URL from backend
 * @param {string} fileName - Name of the file to upload
 * @returns {Promise<string>} Presigned upload URL
 */
export async function getPresignedUploadUrl(filename) {
  const response = await fetch(API_CONFIG.UPLOAD_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      filename, // This part is correct!
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to get upload URL: ${response.statusText}`);
  }

  const data = await response.json();
  
  // FIX 1: Changed 'data.uploadUrl' to 'data.uploadURL'
  // This matches the JSON key { "uploadURL": "..." } from your Python Lambda.
  if (!data.uploadURL) {
    throw new Error('No upload URL received from server');
  }

  // FIX 1 (cont.): Return the correct variable
  return data.uploadURL;
}

/**
 * Upload file to S3 using presigned URL
 * @param {string} uploadUrl - Presigned S3 URL
 * @param {File} file - File to upload
 * @returns {Promise<void>}
 */
export async function uploadFileToS3(uploadUrl, file) {
  try {
    const response = await fetch(uploadUrl, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      // Log the S3 error response for easier debugging
      const errorText = await response.text();
      console.error("S3 Upload Error:", errorText);
      throw new Error(`Failed to upload file: ${response.statusText}`);
    }
  } catch (error) {
    // Better error message for CORS issues
    if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
      throw new Error('S3 CORS error: Your S3 bucket needs CORS configuration. See CORS_FIX.md for instructions.');
    }
    throw error;
  }
}

/**
 * Fetch EC2 instance status from backend
 * @returns {Promise<Array>} Array of EC2 instances
 */
export async function fetchEC2Status() {
  const response = await fetch(API_CONFIG.STATUS_URL, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch status: ${response.statusText}`);
  }

  const data = await response.json();
  console.log("EC2 Status Data:", data);
  
  // Handle both single instance object and array of instances
  // If the response is a single object (not an array), wrap it in an array
  if (data && !Array.isArray(data)) {
    return [data];
  }
  
  return data || [];
}

/**
 * Mock EC2 data for demonstration purposes
 * @returns {Array} Array of mock EC2 instances
 */
export function getMockEC2Data() {
  return [
    {
      instanceId: 'i-1234567890abcdef0',
      name: 'Production Web Server',
      state: 'running',
      instanceType: 't2.micro',
      publicIp: '54.123.45.67',
      privateIp: '172.31.0.1',
      availabilityZone: 'us-east-1a',
      launchTime: '2024-01-15T10:30:00Z',
    },
    {
      instanceId: 'i-0987654321fedcba0',
      name: 'Database Server',
      state: 'stopped',
      instanceType: 't3.medium',
      publicIp: null,
      privateIp: '172.31.0.2',
      availabilityZone: 'us-east-1b',
      launchTime: '2024-01-10T08:15:00Z',
    },
  ];
}