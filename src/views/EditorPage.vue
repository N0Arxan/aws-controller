<script setup>
import { ref } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { getPresignedUploadUrl, uploadFileToS3 } from '../services/api';

const jsonContent = ref('{\n    "command": ""\n}');
const isUploading = ref(false);
const statusMessage = ref('');
const statusDetails = ref('');
const statusType = ref(''); // 'success', 'error', 'info'
const uploadLog = ref([]);
const jsonError = ref('');

const validateJSON = () => {
  try {
    JSON.parse(jsonContent.value);
    jsonError.value = '';
    return true;
  } catch (error) {
    jsonError.value = error.message;
    return false;
  }
};

const formatJSON = () => {
  try {
    const parsed = JSON.parse(jsonContent.value);
    jsonContent.value = JSON.stringify(parsed, null, 4);
    jsonError.value = '';
    addLog('info', 'JSON formatted successfully');
  } catch (error) {
    jsonError.value = error.message;
    addLog('error', 'Invalid JSON format');
  }
};

const clearEditor = () => {
  jsonContent.value = '{\n    "command": ""\n}';
  jsonError.value = '';
  statusMessage.value = '';
  statusDetails.value = '';
  uploadLog.value = [];
};

const addLog = (type, message) => {
  const now = new Date();
  const timestamp = now.toLocaleTimeString();
  uploadLog.value.push({ timestamp, type, message });
};

const uploadJSON = async () => {
  // Validate JSON first
  if (!validateJSON()) {
    statusMessage.value = 'Invalid JSON';
    statusDetails.value = 'Please fix the JSON syntax errors before uploading';
    statusType.value = 'error';
    addLog('error', 'JSON validation failed');
    return;
  }

  isUploading.value = true;
  statusMessage.value = '';
  statusDetails.value = '';

  try {
    // Create a blob from JSON content
    const jsonBlob = new Blob([jsonContent.value], { type: 'application/json' });
    const fileName = `command-${Date.now()}.json`;
    const file = new File([jsonBlob], fileName, { type: 'application/json' });

    // Step 1: Get presigned upload URL from backend
    addLog('info', 'Requesting upload URL from backend...');
    statusMessage.value = 'Requesting upload URL...';
    statusType.value = 'info';

    const uploadUrl = await getPresignedUploadUrl(fileName);

    addLog('info', 'Upload URL received successfully');

    // Step 2: Upload file to S3 using presigned URL
    addLog('info', 'Uploading JSON to S3...');
    statusMessage.value = 'Uploading JSON to S3...';
    statusDetails.value = `Uploading ${fileName}`;

    await uploadFileToS3(uploadUrl, file);

    // Success!
    addLog('info', 'JSON uploaded successfully!');
    statusMessage.value = 'Success!';
    statusDetails.value = `${fileName} has been uploaded successfully.`;
    statusType.value = 'success';

    // Optional: Clear editor after successful upload
    setTimeout(() => {
      statusMessage.value = '';
      statusDetails.value = '';
    }, 3000);

  } catch (error) {
    addLog('error', error.message);
    statusMessage.value = 'Error uploading JSON';
    statusDetails.value = error.message;
    statusType.value = 'error';
  } finally {
    isUploading.value = false;
  }
};

// Auto-validate on content change
const onContentChange = () => {
  if (jsonContent.value.trim()) {
    validateJSON();
  }
};
</script>

<template>
  <div class="min-h-screen bg-notion-bg-secondary py-12 px-4 sm:px-6 lg:px-8 animate-fade-in">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-8 animate-slide-up">
        <h1 class="text-4xl font-bold text-notion-text mb-2">
          <font-awesome-icon :icon="['fas', 'code']" class="mr-3 text-notion-accent" />
          JSON Command Editor
        </h1>
        <p class="text-notion-text-secondary text-sm">Create and upload your JSON commands directly</p>
      </div>

      <!-- Main Card -->
      <div class="notion-card p-8 animate-scale-in">
        <!-- Toolbar -->
        <div class="flex items-center justify-between mb-4">
          <label class="text-sm font-medium text-notion-text">
            <font-awesome-icon :icon="['fas', 'edit']" class="mr-2" />
            Edit JSON
          </label>
          <div class="flex gap-2">
            <button
              @click="formatJSON"
              class="px-3 py-1.5 text-sm border border-notion-border rounded-md hover:bg-notion-bg-secondary transition-colors text-notion-text flex items-center"
              title="Format JSON"
            >
              <font-awesome-icon :icon="['fas', 'magic']" class="mr-2" />
              Format
            </button>
            <button
              @click="clearEditor"
              class="px-3 py-1.5 text-sm border border-notion-border rounded-md hover:bg-notion-bg-secondary transition-colors text-notion-text flex items-center"
              title="Clear Editor"
            >
              <font-awesome-icon :icon="['fas', 'eraser']" class="mr-2" />
              Clear
            </button>
          </div>
        </div>

        <!-- JSON Editor -->
        <div class="relative">
          <textarea
            v-model="jsonContent"
            @input="onContentChange"
            class="w-full h-96 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-notion-accent/20 focus:border-notion-accent transition-all duration-200 resize-none bg-white font-mono text-sm"
            :class="jsonError ? 'border-red-300' : 'border-notion-border'"
            placeholder='{\n    "command": "your-command-here"\n}'
            spellcheck="false"
          ></textarea>
          
          <!-- Line Numbers Effect (Optional styling) -->
          <div class="absolute top-3 left-2 text-notion-text-secondary text-xs font-mono select-none pointer-events-none opacity-30 leading-5">
            <div v-for="n in 20" :key="n">{{ n }}</div>
          </div>
        </div>

        <!-- JSON Error Display -->
        <div v-if="jsonError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg animate-slide-up">
          <div class="flex items-start">
            <font-awesome-icon
              :icon="['fas', 'exclamation-circle']"
              class="text-red-600 mt-0.5 mr-2"
            />
            <div class="flex-1">
              <p class="text-sm font-medium text-red-800">JSON Syntax Error</p>
              <p class="text-xs text-red-600 mt-1 font-mono">{{ jsonError }}</p>
            </div>
          </div>
        </div>

        <!-- Valid JSON Indicator -->
        <div v-else-if="jsonContent.trim()" class="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg animate-slide-up">
          <div class="flex items-center">
            <font-awesome-icon
              :icon="['fas', 'check-circle']"
              class="text-green-600 mr-2"
            />
            <p class="text-sm text-green-800">Valid JSON</p>
          </div>
        </div>

        <!-- Upload Button -->
        <button
          @click="uploadJSON"
          :disabled="isUploading || !!jsonError || !jsonContent.trim()"
          class="notion-button w-full py-3 text-base disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mt-6"
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
          {{ isUploading ? 'Uploading...' : 'Upload JSON' }}
        </button>

        <!-- Status Messages -->
        <div v-if="statusMessage" class="mt-6 animate-slide-up">
          <div
            :class="[
              'p-4 rounded-lg border',
              statusType === 'success' ? 'bg-green-50 border-green-200 text-green-800' :
              statusType === 'error' ? 'bg-red-50 border-red-200 text-red-800' :
              'bg-blue-50 border-blue-200 text-blue-800'
            ]"
          >
            <div class="flex items-start">
              <font-awesome-icon
                :icon="['fas', statusType === 'success' ? 'check-circle' : statusType === 'error' ? 'exclamation-circle' : 'info-circle']"
                class="mt-0.5 mr-3"
              />
              <div class="flex-1">
                <p class="text-sm font-medium">{{ statusMessage }}</p>
                <p v-if="statusDetails" class="text-xs mt-1 opacity-75">{{ statusDetails }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Upload Log -->
        <div v-if="uploadLog.length > 0" class="mt-6">
          <h3 class="text-sm font-medium text-notion-text mb-3">
            <font-awesome-icon :icon="['fas', 'list']" class="mr-2" />
            Upload Log
          </h3>
          <div class="notion-textarea h-32 overflow-y-auto">
            <div v-for="(log, index) in uploadLog" :key="index" class="text-xs mb-1">
              <span class="text-notion-text-secondary">{{ log.timestamp }}</span>
              <span class="ml-2" :class="log.type === 'error' ? 'text-red-600' : 'text-notion-text'">
                {{ log.message }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Links -->
      <div class="mt-6 flex justify-between items-center">
        <router-link
          to="/"
          class="inline-flex items-center text-notion-accent hover:text-notion-accent-hover transition-colors text-sm font-medium"
        >
          <font-awesome-icon :icon="['fas', 'arrow-left']" class="mr-2" />
          Upload File
        </router-link>
        
        <router-link
          to="/status"
          class="inline-flex items-center text-notion-accent hover:text-notion-accent-hover transition-colors text-sm font-medium"
        >
          View EC2 Status
          <font-awesome-icon :icon="['fas', 'arrow-right']" class="ml-2" />
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom scrollbar for textarea */
textarea::-webkit-scrollbar {
  width: 8px;
}

textarea::-webkit-scrollbar-track {
  background: #f7f6f3;
  border-radius: 4px;
}

textarea::-webkit-scrollbar-thumb {
  background: #e9e9e7;
  border-radius: 4px;
}

textarea::-webkit-scrollbar-thumb:hover {
  background: #d1d1cf;
}
</style>
