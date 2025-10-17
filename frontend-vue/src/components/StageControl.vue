<template>
  <div class="bg-white p-5 rounded-lg shadow-md">
    <h2 class="text-xl font-bold mb-4 text-gray-900">Stage Control</h2>

    <div class="bg-gray-100 p-4 rounded mb-4 font-mono text-sm">
      <div class="mb-1">X: <span class="font-semibold">{{ store.position.x.toFixed(1) }}</span></div>
      <div class="mb-1">Y: <span class="font-semibold">{{ store.position.y.toFixed(1) }}</span></div>
      <div>Z: <span class="font-semibold">{{ store.position.z.toFixed(1) }}</span></div>
    </div>

    <div class="grid grid-cols-3 gap-2.5 mb-4">
      <div></div>
      <button 
        @click="move(0, 100, 0)" 
        :disabled="stage.isMoving.value" 
        class="bg-blue-500 text-white p-4 rounded cursor-pointer text-sm font-medium transition-colors hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed"
      >
        ↑ Y+
      </button>
      <div></div>

      <button 
        @click="move(-100, 0, 0)" 
        :disabled="stage.isMoving.value" 
        class="bg-blue-500 text-white p-4 rounded cursor-pointer text-sm font-medium transition-colors hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed"
      >
        ← X-
      </button>
      <button 
        @click="stage.home()" 
        :disabled="stage.isMoving.value" 
        class="bg-orange-600 text-white p-4 rounded cursor-pointer text-sm font-medium transition-colors hover:bg-orange-700 disabled:opacity-60 disabled:cursor-not-allowed"
      >
        ⌂ Home
      </button>
      <button 
        @click="move(100, 0, 0)" 
        :disabled="stage.isMoving.value" 
        class="bg-blue-500 text-white p-4 rounded cursor-pointer text-sm font-medium transition-colors hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed"
      >
        X+ →
      </button>

      <div></div>
      <button 
        @click="move(0, -100, 0)" 
        :disabled="stage.isMoving.value" 
        class="bg-blue-500 text-white p-4 rounded cursor-pointer text-sm font-medium transition-colors hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed"
      >
        ↓ Y-
      </button>
      
      <!-- Light Toggle Button -->
      <button 
        @click="toggleLight"
        :disabled="isToggling || lightLoading"
        :title="isLightOn ? 'Light ON - Click to turn OFF' : 'Light OFF - Click to turn ON'"
        :class="[
          'p-4 rounded cursor-pointer text-xs leading-tight font-medium transition-all',
          isLightOn 
            ? 'bg-yellow-500 text-white hover:bg-yellow-600 hover:shadow-lg shadow-lg shadow-yellow-500/60 '
            : 'bg-blue-300 text-white hover:bg-blue-700',
          (isToggling || lightLoading) && 'opacity-60 cursor-not-allowed'
        ]"
      >
        <span v-if="isLightOn">💡 ON</span>
        <span v-else>💡 OFF</span>
      </button>
    </div>

    <div v-if="lightError" class="text-xs text-red-600 bg-red-50 p-2 rounded mb-3">
      ⚠️ {{ lightError }}
    </div>

    <!-- Focus Section (Z-Axis) -->
    <div class="mt-6 pt-4 border-t-2 border-gray-200">
      <h3 class="text-base font-semibold text-gray-700 mb-3">🔍 Focus</h3>
      <div class="flex gap-2">
        <button 
          @click="move(0, 0, 10)" 
          :disabled="stage.isMoving.value" 
          class="flex-1 bg-blue-500 text-white px-5 py-2.5 rounded cursor-pointer text-sm font-medium transition-colors hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          Z+ ↑
        </button>
        <button 
          @click="move(0, 0, -10)" 
          :disabled="stage.isMoving.value" 
          class="flex-1 bg-blue-500 text-white px-5 py-2.5 rounded cursor-pointer text-sm font-medium transition-colors hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          Z- ↓
        </button>
        <button 
          @click="stage.stop()" 
          class="flex-1 bg-red-500 text-white px-5 py-2.5 rounded cursor-pointer text-sm font-medium transition-colors hover:bg-red-700"
        >
          ⛔ STOP
        </button>
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

const isLightOn = ref(false)
const lightLoading = ref(true)
const isToggling = ref(false)
const lightError = ref('')

let intervalId: number | null = null

onMounted(() => {
  intervalId = window.setInterval(stage.updatePosition, 2000)
  stage.updatePosition()
  fetchLightStatus()
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
})

async function move(x: number, y: number, z: number) {
  await stage.move(x, y, z, true)
  setTimeout(stage.updatePosition, 500)
}

async function fetchLightStatus() {
  try {
    lightLoading.value = true
    lightError.value = ''
    const response = await apiClient.get('/api/v1/microscope/light/status')
    isLightOn.value = response.data.isOn
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
  } catch (err: any) {
    console.error('Failed to toggle light:', err)
    lightError.value = 'Failed to toggle'
    await fetchLightStatus()
  } finally {
    isToggling.value = false
  }
}
</script>

<style scoped>
.btn-movement {
  @apply bg-blue-500 text-white p-4 rounded text-sm font-medium transition-colors hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed;
}

.btn-home {
  @apply bg-orange-600 text-white p-4 rounded text-sm font-medium transition-colors hover:bg-orange-700 disabled:opacity-60 disabled:cursor-not-allowed;
}

.btn-stop {
  @apply bg-red-500 text-white px-5 py-2.5 rounded text-sm font-medium transition-colors hover:bg-red-700;
}
</style>
