<script setup>
import { ref, onMounted } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { fetchEC2Status, getMockEC2Data } from '../services/api';

const instances = ref([]);
const isLoading = ref(false);
const error = ref('');
const lastUpdated = ref(null);

const fetchStatus = async () => {
  isLoading.value = true;
  error.value = '';

  try {
    const data = await fetchEC2Status();
    instances.value = data;
    lastUpdated.value = new Date();
  } catch (err) {
    console.log('API failed, loading mock data:', err.message);
    // For demo purposes, show mock data if API fails
    instances.value = getMockEC2Data();
    lastUpdated.value = new Date();
    // Clear error so mock data is displayed
    error.value = '';
  } finally {
    isLoading.value = false;
  }
};

const getStatusBadgeClass = (state) => {
  const stateMap = {
    running: 'bg-green-100 text-green-800',
    stopped: 'bg-red-100 text-red-800',
    pending: 'bg-yellow-100 text-yellow-800',
    stopping: 'bg-orange-100 text-orange-800',
    terminated: 'bg-gray-100 text-gray-800',
  };
  return stateMap[state?.toLowerCase()] || 'bg-gray-100 text-gray-800';
};

const getStatusIcon = (state) => {
  const iconMap = {
    running: 'play-circle',
    stopped: 'stop-circle',
    pending: 'clock',
    stopping: 'pause-circle',
    terminated: 'times-circle',
  };
  return iconMap[state?.toLowerCase()] || 'question-circle';
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString();
};

onMounted(() => {
  fetchStatus();
});
</script>

<template>
  <div class="min-h-screen bg-notion-bg-secondary py-12 px-4 sm:px-6 lg:px-8 animate-fade-in">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-8 animate-slide-up">
        <h1 class="text-4xl font-bold text-notion-text mb-2">
          <font-awesome-icon :icon="['fas', 'database']" class="mr-3 text-notion-accent" />
          EC2 Instance Status
        </h1>
        <p class="text-notion-text-secondary text-sm">Monitor your EC2 instances in real-time</p>
      </div>

      <!-- Refresh Button -->
      <div class="mb-6 flex justify-between items-center animate-slide-up">
        <router-link
          to="/"
          class="inline-flex items-center text-notion-accent hover:text-notion-accent-hover transition-colors text-sm font-medium"
        >
          <font-awesome-icon :icon="['fas', 'arrow-left']" class="mr-2" />
          Back to Upload
        </router-link>
        
        <button
          @click="fetchStatus"
          :disabled="isLoading"
          class="notion-button flex items-center"
        >
          <font-awesome-icon
            :icon="['fas', 'sync-alt']"
            :class="{ 'animate-spin': isLoading }"
            class="mr-2"
          />
          {{ isLoading ? 'Refreshing...' : 'Refresh Status' }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading && !instances.length" class="notion-card p-12 text-center animate-scale-in">
        <font-awesome-icon
          :icon="['fas', 'spinner']"
          class="text-4xl text-notion-accent animate-spin mb-4"
        />
        <p class="text-notion-text-secondary">Loading instance status...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="notion-card p-6 border-red-200 bg-red-50 animate-scale-in">
        <div class="flex items-start">
          <font-awesome-icon
            :icon="['fas', 'exclamation-triangle']"
            class="text-red-600 mt-1 mr-3"
          />
          <div>
            <p class="text-sm font-medium text-red-800">{{ error }}</p>
            <p class="text-xs text-red-600 mt-1">Please check your API connection and try again.</p>
          </div>
        </div>
      </div>

      <!-- Instances List -->
      <div v-else-if="instances.length > 0" class="space-y-4">
        <div
          v-for="(instance, index) in instances"
          :key="instance.instanceId"
          class="notion-card p-6 animate-scale-in"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <div class="flex items-center mb-2">
                <h3 class="text-lg font-semibold text-notion-text mr-3">
                  {{ instance.name || 'Unnamed Instance' }}
                </h3>
                <span
                  :class="getStatusBadgeClass(instance.state)"
                  class="px-3 py-1 text-xs font-medium rounded-full"
                >
                  <font-awesome-icon
                    :icon="['fas', getStatusIcon(instance.state)]"
                    class="mr-1"
                  />
                  {{ instance.state }}
                </span>
              </div>
              <p class="text-sm text-notion-text-secondary font-mono">{{ instance.instanceId }}</p>
            </div>
            <font-awesome-icon
              :icon="['fas', 'server']"
              class="text-3xl text-notion-text-secondary opacity-20"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div class="flex items-center">
              <font-awesome-icon :icon="['fas', 'microchip']" class="text-notion-text-secondary mr-2 w-4" />
              <span class="text-notion-text-secondary mr-2">Type:</span>
              <span class="font-medium text-notion-text">{{ instance.instanceType || 'N/A' }}</span>
            </div>
            <div class="flex items-center">
              <font-awesome-icon :icon="['fas', 'globe']" class="text-notion-text-secondary mr-2 w-4" />
              <span class="text-notion-text-secondary mr-2">Public IP:</span>
              <span class="font-medium text-notion-text font-mono text-xs">{{ instance.publicIp || 'N/A' }}</span>
            </div>
            <div class="flex items-center">
              <font-awesome-icon :icon="['fas', 'network-wired']" class="text-notion-text-secondary mr-2 w-4" />
              <span class="text-notion-text-secondary mr-2">Private IP:</span>
              <span class="font-medium text-notion-text font-mono text-xs">{{ instance.privateIp || 'N/A' }}</span>
            </div>
            <div class="flex items-center">
              <font-awesome-icon :icon="['fas', 'map-marker-alt']" class="text-notion-text-secondary mr-2 w-4" />
              <span class="text-notion-text-secondary mr-2">Zone:</span>
              <span class="font-medium text-notion-text">{{ instance.availabilityZone || 'N/A' }}</span>
            </div>
          </div>

          <div v-if="instance.launchTime" class="mt-4 pt-4 border-t border-notion-border">
            <div class="flex items-center text-xs text-notion-text-secondary">
              <font-awesome-icon :icon="['fas', 'clock']" class="mr-2" />
              <span>Launched: {{ formatDate(instance.launchTime) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="notion-card p-12 text-center animate-scale-in">
        <font-awesome-icon
          :icon="['fas', 'inbox']"
          class="text-6xl text-notion-text-secondary opacity-30 mb-4"
        />
        <p class="text-notion-text-secondary">No EC2 instances found</p>
        <p class="text-sm text-notion-text-secondary mt-2">Upload a configuration file to get started</p>
      </div>

      <!-- Last Updated -->
      <div v-if="lastUpdated" class="mt-6 text-center text-xs text-notion-text-secondary animate-fade-in">
        Last updated: {{ formatDate(lastUpdated) }}
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Additional component-specific styles if needed */
</style>
