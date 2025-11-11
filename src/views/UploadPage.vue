<script setup>
import { ref } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { getPresignedUploadUrl, uploadFileToS3 } from '../services/api';
import JSONEditor from '../components/JSONEditor.vue';

const selectedFile = ref(null);
const fileInput = ref(null);
const isUploading = ref(false);
const statusMessage = ref('');
const statusDetails = ref('');
const statusType = ref(''); // 'success', 'error', 'info'
const uploadLog = ref([]);

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    // Validate file type
    if (!file.name.endsWith('.json')) {
      statusMessage.value = 'Invalid file type';
      statusDetails.value = 'Please select a JSON file (.json)';
      statusType.value = 'error';
      addLog('error', 'Invalid file type - only JSON files are accepted');
      return;
    }
    
    selectedFile.value = file;
    addLog('info', `File selected: ${file.name}`);
    statusMessage.value = '';
    statusDetails.value = '';
  }
};

const clearFile = () => {
  selectedFile.value = null;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
  statusMessage.value = '';
  statusDetails.value = '';
};

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

const addLog = (type, message) => {
  const now = new Date();
  const timestamp = now.toLocaleTimeString();
  uploadLog.value.push({ timestamp, type, message });
};

const uploadFile = async () => {
  if (!selectedFile.value) return;

  isUploading.value = true;
  statusMessage.value = '';
  statusDetails.value = '';

  try {
    // Step 1: Get presigned upload URL from backend
    addLog('info', 'Requesting upload URL from backend...');
    statusMessage.value = 'Requesting upload URL...';
    statusType.value = 'info';

    const uploadUrl = await getPresignedUploadUrl(
      selectedFile.value.name,
    );

    addLog('info', 'Upload URL received successfully');

    // Step 2: Upload file to S3 using presigned URL
    addLog('info', 'Uploading file to S3...');
    statusMessage.value = 'Uploading file to S3...';
    statusDetails.value = `Uploading ${selectedFile.value.name}`;

    await uploadFileToS3(uploadUrl, selectedFile.value);

    // Success!
    addLog('info', 'File uploaded successfully!');
    statusMessage.value = 'Success!';
    statusDetails.value = `${selectedFile.value.name} has been uploaded successfully.`;
    statusType.value = 'success';

    // Clear file after successful upload
    setTimeout(() => {
      clearFile();
    }, 3000);

  } catch (error) {
    addLog('error', error.message);
    statusMessage.value = 'Error uploading file';
    statusDetails.value = error.message;
    statusType.value = 'error';
  } finally {
    isUploading.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen bg-notion-bg-secondary py-12 px-4 sm:px-6 lg:px-8 animate-fade-in">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-8 animate-slide-up">
        <h1 class="text-4xl font-bold text-notion-text mb-2">
          <font-awesome-icon :icon="['fas', 'server']" class="mr-3 text-notion-accent" />
          EC2 Control Portal Albert
        </h1>
        <p class="text-notion-text-secondary text-sm">Upload your JSON configuration file or use the editor</p>
      </div>

      <!-- Two Column Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <!-- Left Column: File Upload -->
        <div class="notion-card p-8 animate-scale-in">
          <div class="mb-4">
            <h3 class="text-lg font-semibold text-notion-text mb-1 flex items-center">
              <font-awesome-icon :icon="['fas', 'file-alt']" class="mr-2 text-notion-accent" />
              Upload File
            </h3>
            <p class="text-sm text-notion-text-secondary">Select a JSON file from your computer</p>
          </div>
          
          <!-- File Input Section -->
          <!-- File Input Section -->
          <div class="mb-6">
            <div class="relative">
              <input
                type="file"
                ref="fileInput"
                @change="handleFileSelect"
                accept=".json"
                class="hidden"
                id="file-upload"
              />
              <label
                for="file-upload"
                class="flex items-center justify-center w-full px-6 py-12 border-2 border-dashed border-notion-border rounded-lg cursor-pointer hover:border-notion-accent hover:bg-notion-bg-secondary transition-all duration-200"
              >
                <div class="text-center">
                  <font-awesome-icon
                    :icon="['fas', 'cloud-upload-alt']"
                    class="text-4xl text-notion-text-secondary mb-3"
                  />
                  <p class="text-sm text-notion-text-secondary">
                    <span class="font-medium text-notion-accent">Click to upload</span>
                  </p>
                  <p class="text-xs text-notion-text-secondary mt-1">
                    JSON files only
                  </p>
                </div>
              </label>
            </div>
          
            <!-- Selected File Display -->
            <div v-if="selectedFile" class="mt-4 p-4 bg-notion-bg-secondary rounded-lg flex items-center justify-between animate-slide-up">
              <div class="flex items-center">
                <font-awesome-icon :icon="['fas', 'file']" class="text-notion-accent mr-3" />
                <div>
                  <p class="text-sm font-medium text-notion-text">{{ selectedFile.name }}</p>
                  <p class="text-xs text-notion-text-secondary">{{ formatFileSize(selectedFile.size) }}</p>
                </div>
              </div>
              <button
                @click="clearFile"
                class="text-notion-text-secondary hover:text-notion-text transition-colors"
              >
                <font-awesome-icon :icon="['fas', 'times']" />
              </button>
            </div>
          </div>

          <!-- Upload Button -->
          <button
            @click="uploadFile"
            :disabled="!selectedFile || isUploading"
            class="notion-button w-full py-2.5 text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <font-awesome-icon
              v-if="isUploading"
              :icon="['fas', 'spinner']"
              class="mr-2 animate-spin"
            />
            <font-awesome-icon
              v-else
              :icon="['fas', 'upload']"
              class="mr-2"
            />
            {{ isUploading ? 'Uploading...' : 'Upload File' }}
          </button>

          <!-- Status Messages -->
          <div v-if="statusMessage" class="mt-4 animate-slide-up">
            <div
              :class="[
                'p-3 rounded-lg border text-sm',
                statusType === 'success' ? 'bg-green-50 border-green-200 text-green-800' :
                statusType === 'error' ? 'bg-red-50 border-red-200 text-red-800' :
                'bg-blue-50 border-blue-200 text-blue-800'
              ]"
            >
              <div class="flex items-start">
                <font-awesome-icon
                  :icon="['fas', statusType === 'success' ? 'check-circle' : statusType === 'error' ? 'exclamation-circle' : 'info-circle']"
                  class="mt-0.5 mr-2 flex-shrink-0"
                />
                <div class="flex-1">
                  <p class="font-medium">{{ statusMessage }}</p>
                  <p v-if="statusDetails" class="text-xs mt-1 opacity-75">{{ statusDetails }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Upload Log -->
          <div v-if="uploadLog.length > 0" class="mt-4">
            <div class="max-h-32 overflow-y-auto p-3 bg-notion-bg-secondary rounded-lg border border-notion-border">
              <div v-for="(log, index) in uploadLog" :key="index" class="text-xs mb-1">
                <span class="text-notion-text-secondary">{{ log.timestamp }}</span>
                <span class="ml-2" :class="log.type === 'error' ? 'text-red-600' : 'text-notion-text'">
                  {{ log.message }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: JSON Editor -->
        <JSONEditor />
        
      </div>

      <!-- Navigation Links -->
      <div class="mt-6 text-center">
        <router-link
          to="/status"
          class="inline-flex items-center text-notion-accent hover:text-notion-accent-hover transition-colors text-sm font-medium"
        >
          View EC2 Instance Status
          <font-awesome-icon :icon="['fas', 'arrow-right']" class="ml-2" />
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Additional component-specific styles if needed */
</style>
