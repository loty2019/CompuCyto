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
        @click="handleButtonClick('arrowup'); move(0, 100, 0)" 
        :disabled="stage.isMoving.value" 
        class="bg-blue-500 text-white p-4 rounded text-sm font-medium hover:bg-blue-700"
        :class="stage.isMoving.value ? 'cursor-not-allowed' : 'cursor-pointer'"
        :style="getButtonStyle('arrowup')"
      >
        ↑ Y+
      </button>
      <div></div>

      <button 
        @click="handleButtonClick('arrowleft'); move(-100, 0, 0)" 
        :disabled="stage.isMoving.value" 
        class="bg-blue-500 text-white p-4 rounded text-sm font-medium hover:bg-blue-700"
        :class="stage.isMoving.value ? 'cursor-not-allowed' : 'cursor-pointer'"
        :style="getButtonStyle('arrowleft')"
      >
        ← X-
      </button>
      <button 
        @click="handleButtonClick('home'); stage.home()" 
        :disabled="stage.isMoving.value" 
        class="bg-orange-400 text-white p-4 rounded text-sm font-medium hover:bg-orange-600"
        :class="stage.isMoving.value ? 'cursor-not-allowed' : 'cursor-pointer'"
        :style="getButtonStyle('home')"
      >
        ⌂ Home
      </button>
      <button 
        @click="handleButtonClick('arrowright'); move(100, 0, 0)" 
        :disabled="stage.isMoving.value" 
        class="bg-blue-500 text-white p-4 rounded text-sm font-medium hover:bg-blue-700"
        :class="stage.isMoving.value ? 'cursor-not-allowed' : 'cursor-pointer'"
        :style="getButtonStyle('arrowright')"
      >
        X+ →
      </button>

      <div></div>
      <button 
        @click="handleButtonClick('arrowdown'); move(0, -100, 0)" 
        :disabled="stage.isMoving.value" 
        class="bg-blue-500 text-white p-4 rounded text-sm font-medium hover:bg-blue-700"
        :class="stage.isMoving.value ? 'cursor-not-allowed' : 'cursor-pointer'"
        :style="getButtonStyle('arrowdown')"
      >
        ↓ Y-
      </button>
      
      <!-- Light Toggle Button -->
      <button 
        @click="handleButtonClick('l'); toggleLight()"
        :disabled="isToggling || lightLoading"
        :title="isLightOn ? 'Light ON - Click to turn OFF (Press L)' : 'Light OFF - Click to turn ON (Press L)'"
        :class="[
          'p-4 rounded text-xs leading-tight font-medium',
          isLightOn 
            ? 'bg-yellow-500 text-white hover:bg-yellow-600 hover:shadow-lg shadow-lg shadow-yellow-500/60 '
            : 'bg-blue-300 text-white hover:bg-blue-700',
          (isToggling || lightLoading) ? 'cursor-not-allowed' : 'cursor-pointer'
        ]"
        :style="getButtonStyle('l')"
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
      <h3 class="text-base font-semibold text-gray-700 mb-3">Focus</h3>
      <div class="flex gap-2">
        <button 
          @click="handleZClick('up')" 
          :disabled="stage.isMoving.value" 
          class="flex-1 bg-blue-500 text-white px-5 py-2.5 rounded text-sm font-medium hover:bg-blue-700"
          :class="stage.isMoving.value ? 'cursor-not-allowed' : 'cursor-pointer'"
          :style="getButtonStyle('zup')"
        >
          Z+ ↑
        </button>
        <button 
          @click="handleZClick('down')" 
          :disabled="stage.isMoving.value" 
          class="flex-1 bg-blue-500 text-white px-5 py-2.5 rounded text-sm font-medium hover:bg-blue-700"
          :class="stage.isMoving.value ? 'cursor-not-allowed' : 'cursor-pointer'"
          :style="getButtonStyle('zdown')"
        >
          Z- ↓
        </button>
        <button 
          @click="stage.stop()" 
          class="flex-1 bg-red-700 text-white px-5 py-2.5 rounded cursor-pointer text-sm font-medium hover:bg-red-800"
          :style="getButtonStyle('stop')"
          title="Emergency Stop"
        >
          STOP
        </button>
      </div>
    </div>

    <!-- Keyboard Shortcuts Info -->
    <div class="mt-4 p-3 bg-blue-50 rounded text-xs text-gray-600">
      <!-- <div class="font-semibold mb-1">⌨ Keyboard Shortcuts:</div> -->
      <div class="grid grid-cols-2 gap-1">
        <span>Arrow Keys: Move Stage (XY)</span>
        <span>L: Toggle Light</span>
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

// Visual feedback for key presses
const pressedKeys = ref<Set<string>>(new Set())

// Visual feedback for button clicks
const clickedButtons = ref<Set<string>>(new Set())

let intervalId: number | null = null

onMounted(() => {
  intervalId = window.setInterval(stage.updatePosition, 2000)
  stage.updatePosition()
  fetchLightStatus()
  
  // Add keyboard event listeners
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('keyup', handleKeyUp)
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
  
  // Remove keyboard event listeners
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('keyup', handleKeyUp)
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

function handleKeyDown(event: KeyboardEvent) {
  // Prevent handling if user is typing in an input field
  const target = event.target as HTMLElement
  if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
    return
  }

  const key = event.key.toLowerCase()
  
  // Prevent default browser behavior for arrow keys
  if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright'].includes(key)) {
    event.preventDefault()
  }

  // Ignore if key is already pressed (prevent key repeat)
  if (pressedKeys.value.has(key)) {
    return
  }

  pressedKeys.value.add(key)

  // Handle light toggle (L key)
  if (key === 'l') {
    if (!isToggling.value && !lightLoading.value) {
      toggleLight()
    }
    return
  }

  // Handle movement keys (Arrow keys)
  if (stage.isMoving.value) {
    return
  }

  switch (key) {
    case 'arrowup':
      move(0, 100, 0)
      break
    case 'arrowdown':
      move(0, -100, 0)
      break
    case 'arrowleft':
      move(-100, 0, 0)
      break
    case 'arrowright':
      move(100, 0, 0)
      break
  }
}

function handleKeyUp(event: KeyboardEvent) {
  const key = event.key.toLowerCase()
  pressedKeys.value.delete(key)
}

function isKeyPressed(key: string): boolean {
  return pressedKeys.value.has(key)
}

function handleButtonClick(buttonId: string) {
  clickedButtons.value.add(buttonId)
  setTimeout(() => {
    clickedButtons.value.delete(buttonId)
  }, 150) // Visual feedback for 150ms
}

function handleZClick(direction: 'up' | 'down') {
  const buttonId = direction === 'up' ? 'zup' : 'zdown'
  handleButtonClick(buttonId)
  if (direction === 'up') {
    move(0, 0, 10)
  } else {
    move(0, 0, -10)
  }
}

function getButtonStyle(buttonId: string): string {
  const isClicked = clickedButtons.value.has(buttonId)
  const isPressed = isKeyPressed(buttonId)
  
  if (isClicked || isPressed) {
    // Darker and scaled down
    return 'filter: brightness(0.7); transform: scale(0.95); transition: all 0.05s ease;'
  }
  return 'transition: all 0.05s ease;'
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
