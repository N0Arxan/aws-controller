<script setup>
import { ref, watch, onMounted } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { getPresignedUploadUrl, uploadFileToS3 } from '../services/api';

const jsonContent = ref('{\n    "command": ""\n}');
const isUploading = ref(false);
const statusMessage = ref('');
const statusDetails = ref('');
const statusType = ref('');
const uploadLog = ref([]);
const jsonError = ref('');
const editorRef = ref(null);

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

const addLog = (type, message) => {
  const now = new Date();
  const timestamp = now.toLocaleTimeString();
  uploadLog.value.push({ timestamp, type, message });
};

const uploadJSON = async () => {
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
    const jsonBlob = new Blob([jsonContent.value], { type: 'application/json' });
    const fileName = `command-${Date.now()}.json`;
    const file = new File([jsonBlob], fileName, { type: 'application/json' });

    addLog('info', 'Requesting upload URL from backend...');
    statusMessage.value = 'Requesting upload URL...';
    statusType.value = 'info';

    const uploadUrl = await getPresignedUploadUrl(fileName);
    addLog('info', 'Upload URL received successfully');

    addLog('info', 'Uploading JSON to S3...');
    statusMessage.value = 'Uploading JSON to S3...';
    statusDetails.value = `Uploading ${fileName}`;

    await uploadFileToS3(uploadUrl, file);

    addLog('info', 'JSON uploaded successfully!');
    statusMessage.value = 'Success!';
    statusDetails.value = `${fileName} has been uploaded successfully.`;
    statusType.value = 'success';

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
watch(jsonContent, () => {
  if (jsonContent.value.trim()) {
    validateJSON();
  }
});

// Render highlighted JSON in contenteditable div
const renderHighlightedJSON = () => {
  if (!editorRef.value) return;
  
  // Only update if not focused (to avoid caret jump during typing)
  if (document.activeElement !== editorRef.value) {
    editorRef.value.innerHTML = highlightJSON(jsonContent.value);
  }
};

// Sync contenteditable changes to jsonContent
const onEditorInput = () => {
  if (!editorRef.value) return;
  // Get plain text (not HTML)
  jsonContent.value = editorRef.value.innerText;
};

// On blur, re-render with syntax highlighting
const onEditorBlur = () => {
  renderHighlightedJSON();
};

// Handle Tab key to insert spaces
const insertTab = (e) => {
  e.preventDefault();
  const sel = window.getSelection();
  if (!sel.rangeCount) return;
  
  const range = sel.getRangeAt(0);
  const tabNode = document.createTextNode('    '); // 4 spaces
  range.deleteContents();
  range.insertNode(tabNode);
  range.setStartAfter(tabNode);
  range.setEndAfter(tabNode);
  sel.removeAllRanges();
  sel.addRange(range);
  
  onEditorInput();
};

// Initial render on mount
onMounted(() => {
  renderHighlightedJSON();
});

// Syntax highlighting helper
const highlightJSON = (json) => {
  if (!json) return '';
  
  return json
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, (match) => {
      let cls = 'text-notion-text';
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = 'text-blue-600 font-semibold'; // keys
        } else {
          cls = 'text-green-600'; // string values
        }
      } else if (/true|false/.test(match)) {
        cls = 'text-purple-600 font-semibold'; // booleans
      } else if (/null/.test(match)) {
        cls = 'text-red-500 font-medium'; // null
      } else {
        cls = 'text-orange-600'; // numbers
      }
      return `<span class="${cls}">${match}</span>`;
    })
    .replace(/([{}[\],])/g, '<span class="text-notion-text-secondary font-bold">$1</span>'); // brackets and punctuation
};
</script>

<template>
  <div class="notion-card p-6 animate-scale-in">
    <div class="mb-4">
      <h3 class="text-lg font-semibold text-notion-text mb-1 flex items-center">
        <font-awesome-icon :icon="['fas', 'code']" class="mr-2 text-notion-accent" />
        JSON Editor
      </h3>
      <p class="text-sm text-notion-text-secondary">Write your command directly</p>
    </div>

    <!-- JSON Editor with syntax highlighting -->
    <div class="relative">
      <div
        ref="editorRef"
        class="json-editor w-full h-64 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-notion-accent/20 focus:border-notion-accent transition-all duration-200 font-mono text-sm leading-relaxed overflow-auto"
        :class="jsonError ? 'border-red-300 bg-red-50/30' : 'border-notion-border bg-white'"
        contenteditable="true"
        spellcheck="false"
        @input="onEditorInput"
        @blur="onEditorBlur"
        @keydown.tab.prevent="insertTab"
        aria-label="JSON Editor"
      ></div>
    </div>

    <!-- JSON Error Display -->
    <div v-if="jsonError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg animate-slide-up">
      <div class="flex items-start">
        <font-awesome-icon
          :icon="['fas', 'exclamation-circle']"
          class="text-red-600 mt-0.5 mr-2 flex-shrink-0"
        />
        <div class="flex-1">
          <p class="text-sm font-medium text-red-800">Syntax Error</p>
          <p class="text-xs text-red-600 mt-1 font-mono">{{ jsonError }}</p>
        </div>
      </div>
    </div>

    <!-- Valid JSON Indicator -->
    <div v-else-if="jsonContent.trim()" class="mt-3 p-2 bg-green-50 border border-green-200 rounded-lg animate-slide-up">
      <div class="flex items-center">
        <font-awesome-icon
          :icon="['fas', 'check-circle']"
          class="text-green-600 mr-2 text-sm"
        />
        <p class="text-xs text-green-800">Valid JSON</p>
      </div>
    </div>

    <!-- Upload Button -->
    <button
      @click="uploadJSON"
      :disabled="isUploading || !!jsonError || !jsonContent.trim()"
      class="notion-button w-full py-2.5 text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mt-4"
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

    <!-- Upload Log (Compact) -->
    <div v-if="uploadLog.length > 0" class="mt-4">
      <div class="max-h-24 overflow-y-auto p-3 bg-notion-bg-secondary rounded-lg border border-notion-border">
        <div v-for="(log, index) in uploadLog" :key="index" class="text-xs mb-1">
          <span class="text-notion-text-secondary">{{ log.timestamp }}</span>
          <span class="ml-2" :class="log.type === 'error' ? 'text-red-600' : 'text-notion-text'">
            {{ log.message }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* JSON Editor contenteditable styling */
.json-editor {
  white-space: pre;
  tab-size: 4;
  -moz-tab-size: 4;
}

.json-editor:empty:before {
  content: '{\A    "command": ""\A}';
  color: #9ca3af;
  white-space: pre;
}

/* Custom scrollbar */
.json-editor::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.json-editor::-webkit-scrollbar-track {
  background: #f7f6f3;
  border-radius: 3px;
}

.json-editor::-webkit-scrollbar-thumb {
  background: #e9e9e7;
  border-radius: 3px;
}

.json-editor::-webkit-scrollbar-thumb:hover {
  background: #d1d1cf;
}
</style>
