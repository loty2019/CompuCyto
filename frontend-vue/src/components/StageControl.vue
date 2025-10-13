<template>
  <div class="card">
    <h2>🎯 Stage Control</h2>

    <div class="position-display">
      <div>X: <span>{{ store.position.x.toFixed(1) }}</span></div>
      <div>Y: <span>{{ store.position.y.toFixed(1) }}</span></div>
      <div>Z: <span>{{ store.position.z.toFixed(1) }}</span></div>
    </div>

    <div class="stage-control">
      <div></div>
      <button @click="move(0, 100, 0)" :disabled="stage.isMoving.value" class="btn">↑ Y+</button>
      <div></div>

      <button @click="move(-100, 0, 0)" :disabled="stage.isMoving.value" class="btn">← X-</button>
      <button @click="stage.home()" class="center btn" :disabled="stage.isMoving.value">⌂ Home</button>
      <button @click="move(100, 0, 0)" :disabled="stage.isMoving.value" class="btn">X+ →</button>

      <div></div>
      <button @click="move(0, -100, 0)" :disabled="stage.isMoving.value" class="btn">↓ Y-</button>
      
      <!-- Light Toggle Button -->
      <button 
        @click="toggleLight"
        :class="['btn', 'light-btn', { 'light-on': isLightOn }]"
        :disabled="isToggling || lightLoading"
        :title="isLightOn ? 'Light ON - Click to turn OFF' : 'Light OFF - Click to turn ON'"
      >
        <span v-if="isLightOn">💡 ON</span>
        <span v-else>💡 OFF</span>
      </button>
    </div>

    <!-- Brightness slider (shown when light is on) -->
    <div v-if="isLightOn && !lightLoading" class="brightness-section">
      <label for="brightness">💡 Brightness: {{ brightness }}%</label>
      <input 
        id="brightness"
        type="range" 
        min="0" 
        max="100" 
        v-model.number="brightness"
        @change="setBrightness"
        class="brightness-slider"
      />
    </div>

    <div v-if="lightError" class="error-banner">⚠️ {{ lightError }}</div>

    <!-- Focus Section (Z-Axis) -->
    <div class="focus-section">
      <h3>🔍 Focus</h3>
      <div class="button-group">
        <button @click="move(0, 0, 10)" :disabled="stage.isMoving.value" class="btn">Z+ ↑</button>
        <button @click="move(0, 0, -10)" :disabled="stage.isMoving.value" class="btn">Z- ↓</button>
        <button @click="stage.stop()" class="btn btn-danger">⛔ STOP</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useMicroscopeStore } from '@/stores/microscope'
import { useStage } from '@/composables/useStage'
import apiClient from '@/api/client'

const store = useMicroscopeStore()
const stage = useStage()

// Light control state
const isLightOn = ref(false)
const brightness = ref(100)
const lightLoading = ref(true)
const isToggling = ref(false)
const lightError = ref('')

let intervalId: number | null = null

onMounted(() => {
  // Poll position every 2 seconds
  intervalId = window.setInterval(stage.updatePosition, 2000)
  stage.updatePosition()
  
  // Load initial light status
  fetchLightStatus()
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})

async function move(x: number, y: number, z: number) {
  await stage.move(x, y, z, true)
  setTimeout(stage.updatePosition, 500)
}

// Light control functions
async function fetchLightStatus() {
  try {
    lightLoading.value = true
    lightError.value = ''
    
    const response = await apiClient.get('/api/v1/microscope/light/status')
    
    isLightOn.value = response.data.isOn
    brightness.value = response.data.brightness || 100
  } catch (err: any) {
    console.error('Failed to fetch light status:', err)
    lightError.value = 'Failed to connect'
  } finally {
    lightLoading.value = false
  }
}

async function toggleLight() {
  try {
    isToggling.value = true
    lightError.value = ''
    
    const response = await apiClient.post('/api/v1/microscope/light/toggle')
    
    isLightOn.value = response.data.isOn
    brightness.value = response.data.brightness || 100
  } catch (err: any) {
    console.error('Failed to toggle light:', err)
    lightError.value = 'Failed to toggle'
    await fetchLightStatus()
  } finally {
    isToggling.value = false
  }
}

async function setBrightness() {
  try {
    lightError.value = ''
    
    const response = await apiClient.post('/api/v1/microscope/light/set', {
      isOn: true,
      brightness: brightness.value,
    })
    
    isLightOn.value = response.data.isOn
    brightness.value = response.data.brightness
  } catch (err: any) {
    console.error('Failed to set brightness:', err)
    lightError.value = 'Failed to adjust brightness'
    await fetchLightStatus()
  }
}
</script>

<style scoped>
.position-display {
  @apply bg-gray-100 p-4 rounded mb-4 font-mono;
}

.position-display div {
  @apply mb-1;
}

/* Stage Control Styles */
.stage-control {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  @apply gap-2.5 mb-4;
}

.stage-control button {
  @apply p-4;
}

.stage-control .center {
  @apply bg-orange-600;
}

.stage-control .center:hover:not(:disabled) {
  @apply bg-orange-700;
}

/* Light Button in Stage Control Grid */
.light-btn {
  font-size: 0.875rem;
  line-height: 1.2;
  transition: all 0.2s ease;
}

.light-btn.light-on {
  @apply bg-yellow-500;
  box-shadow: 0 0 10px rgba(234, 179, 8, 0.5);
}

.light-btn.light-on:hover:not(:disabled) {
  @apply bg-yellow-600;
  box-shadow: 0 0 15px rgba(234, 179, 8, 0.7);
}

/* Brightness Section */
.brightness-section {
  @apply mb-4 p-3 bg-gray-50 rounded;
}

.brightness-section label {
  @apply block text-sm font-medium text-gray-700 mb-2;
}

.brightness-slider {
  @apply w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer;
}

.brightness-slider::-webkit-slider-thumb {
  @apply appearance-none w-4 h-4 bg-yellow-500 rounded-full cursor-pointer;
  box-shadow: 0 0 5px rgba(234, 179, 8, 0.5);
}

.brightness-slider::-moz-range-thumb {
  @apply w-4 h-4 bg-yellow-500 rounded-full cursor-pointer border-0;
  box-shadow: 0 0 5px rgba(234, 179, 8, 0.5);
}

/* Error Banner */
.error-banner {
  @apply text-xs text-red-600 bg-red-50 p-2 rounded mb-3;
}

/* Focus Section */
.focus-section {
  @apply mt-6 pt-4 border-t-2 border-gray-200;
}

.focus-section h3 {
  @apply text-base font-semibold text-gray-700 mb-3;
}
</style>
