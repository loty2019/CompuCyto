<template>
  <div class="card">
    <h2>📷 Camera Control</h2>

    <div class="control-group">
      <label>Exposure (ms)</label>
      <input
        type="number"
        v-model.number="exposure"
        min="1"
        max="1000"
        @change="updateSettings"
      />
    </div>

    <div class="control-group">
      <label>Gain</label>
      <input
        type="number"
        v-model.number="gain"
        min="0.1"
        max="10"
        step="0.1"
        @change="updateSettings"
      />
    </div>

    <!-- Live Camera Feed Section -->
    <div class="live-feed-section">
      <h3>📹 Live Feed</h3>
      <div class="feed-container">
        <div v-if="isLoadingFeed" class="feed-placeholder loading">
          <div class="spinner"></div>
          <p>Loading camera feed...</p>
        </div>
        <div v-else-if="feedError" class="feed-placeholder error">
          <span class="error-icon">⚠️</span>
          <p>{{ feedError }}</p>
          <button @click="reconnectFeed" class="btn btn-sm">Reconnect</button>
        </div>
        <div v-else-if="!feedUrl" class="feed-placeholder">
          <span class="camera-icon">📷</span>
          <p>Camera feed not available</p>
          <button @click="startFeed" class="btn btn-sm">Start Feed</button>
        </div>
        <img 
          v-else
          :src="feedUrl" 
          alt="Live camera feed"
          class="live-feed-image"
          @error="handleFeedError"
          @load="handleFeedLoad"
        />
      </div>
    </div>

    <button
      @click="capture"
      :disabled="camera.isCapturing.value"
      class="btn btn-success w-full"
    >
      {{ camera.isCapturing.value ? 'Capturing...' : '📸 Capture Image' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useMicroscopeStore } from '@/stores/microscope'
import { useCamera } from '@/composables/useCamera'

const store = useMicroscopeStore()
const camera = useCamera()

const exposure = ref(100)
const gain = ref(1.0)

// Live feed state
const feedUrl = ref('')
const isLoadingFeed = ref(false)
const feedError = ref('')
let feedInterval: number | null = null

onMounted(async () => {
  await camera.loadSettings()
  exposure.value = store.cameraSettings.exposure
  gain.value = store.cameraSettings.gain
  
  // Optionally auto-start the feed
  // startFeed()
})

onUnmounted(() => {
  stopFeed()
})

async function updateSettings() {
  await camera.updateSettings({
    exposure: exposure.value,
    gain: gain.value
  })
}

async function capture() {
  await camera.captureImage({
    exposure: exposure.value,
    gain: gain.value
  })
}

function startFeed() {
  isLoadingFeed.value = true
  feedError.value = ''
  
  // Set up live feed URL (adjust this endpoint based on your backend)
  // This could be a WebSocket stream, MJPEG stream, or refreshing image
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000'
  
  // Option 1: MJPEG stream (if your backend supports it)
  feedUrl.value = `${baseUrl}/api/v1/camera/stream`
  
  // Option 2: Refresh image periodically (fallback)
  // feedInterval = window.setInterval(() => {
  //   feedUrl.value = `${baseUrl}/api/v1/camera/preview?t=${Date.now()}`
  // }, 100) // Update every 100ms for ~10fps
  
  isLoadingFeed.value = false
}

function stopFeed() {
  if (feedInterval) {
    clearInterval(feedInterval)
    feedInterval = null
  }
  feedUrl.value = ''
}

function reconnectFeed() {
  stopFeed()
  setTimeout(startFeed, 500)
}

function handleFeedError() {
  feedError.value = 'Failed to load camera feed'
  isLoadingFeed.value = false
}

function handleFeedLoad() {
  feedError.value = ''
  isLoadingFeed.value = false
}
</script>

<style scoped>
.live-feed-section {
  @apply my-4 pb-4 border-b border-gray-200;
}

.live-feed-section h3 {
  @apply text-base font-semibold text-gray-700 mb-3;
}

.feed-container {
  @apply bg-gray-900 rounded-lg overflow-hidden;
  aspect-ratio: 16 / 9;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
}

.feed-placeholder {
  @apply flex flex-col items-center justify-center gap-3 text-gray-400;
  width: 100%;
  height: 100%;
}

.feed-placeholder.loading {
  @apply text-blue-400;
}

.feed-placeholder.error {
  @apply text-red-400;
}

.feed-placeholder p {
  @apply text-sm font-medium;
}

.camera-icon,
.error-icon {
  @apply text-4xl mb-2;
}

.spinner {
  @apply inline-block w-8 h-8 border-4 border-blue-400 border-t-transparent rounded-full;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.live-feed-image {
  @apply w-full h-full object-cover;
  display: block;
}

.btn-sm {
  @apply px-3 py-1 text-sm;
}
</style>
