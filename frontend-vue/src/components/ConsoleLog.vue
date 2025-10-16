<template>
  <div class="bg-white p-5 rounded-lg shadow-md">
    <div class="flex justify-between items-start mb-4 gap-4">
      <h2 class="text-xl font-bold m-0 text-gray-900">📋 Console</h2>
      <div class="flex gap-2 flex-wrap">
        <button 
          v-for="filter in logFilters" 
          :key="filter.type"
          @click="toggleFilter(filter.type)"
          :title="`Toggle ${filter.label} logs`"
          :class="[
            'px-2 py-1 text-xs rounded border transition-all',
            activeFilters.includes(filter.type) 
              ? 'bg-blue-500 text-white border-blue-600' 
              : 'border-gray-300 bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
        >
          {{ filter.emoji }} {{ filter.label }}
        </button>
      </div>
    </div>

    <div 
      :class="[
        'px-3 py-2 rounded text-xs mb-4 flex justify-between items-center',
        wsStore.state.isConnected 
          ? 'bg-green-50 text-green-800' 
          : 'bg-red-50 text-red-800'
      ]"
    >
      <span>WebSocket: {{ wsStore.state.isConnected ? 'Connected' : 'Disconnected' }}</span>
      <span class="font-mono font-semibold">{{ filteredLogs.length }} logs</span>
    </div>

    <div class="bg-gray-900 text-gray-300 p-4 rounded font-mono text-xs max-h-[400px] overflow-y-auto mb-2.5" ref="logContainer">
      <div
        v-for="(log, index) in filteredLogs"
        :key="index"
        class="mb-1 flex gap-2"
      >
        <span class="text-gray-500 shrink-0">[{{ formatTime(log.timestamp) }}]</span>
        <span 
          :class="[
            'flex-1',
            log.type === 'error' && 'text-red-400 font-medium',
            log.type === 'success' && 'text-green-400',
            log.type === 'info' && 'text-blue-300',
            log.type === 'warning' && 'text-orange-400'
          ]"
        >
          {{ log.message }}
        </span>
      </div>
      <div v-if="filteredLogs.length === 0" class="text-gray-500 text-center py-8 italic">
        No logs to display
      </div>
    </div>

    <div class="flex gap-2">
      <button 
        @click="store.clearLogs()" 
        class="flex-1 py-2 text-xs bg-gray-600 text-white rounded cursor-pointer font-medium transition-colors hover:bg-gray-700"
      >
        Clear Logs
      </button>
      <button 
        @click="downloadLogs()" 
        class="flex-1 py-2 text-xs bg-blue-600 text-white rounded cursor-pointer font-medium transition-colors hover:bg-blue-700"
      >
        Download Logs
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useMicroscopeStore } from '@/stores/microscope'
import { useWebSocketStore } from '@/stores/websocket'

const store = useMicroscopeStore()
const wsStore = useWebSocketStore()
const logContainer = ref<HTMLElement | null>(null)

const logFilters = [
  { type: 'info', label: 'Info', emoji: 'ℹ️' },
  { type: 'success', label: 'Success', emoji: '✅' },
  { type: 'error', label: 'Error', emoji: '❌' },
  { type: 'warning', label: 'Warning', emoji: '⚠️' }
]

const activeFilters = ref(['info', 'success', 'error', 'warning'])

const filteredLogs = computed(() => {
  return store.logs.filter(log => activeFilters.value.includes(log.type))
})

function toggleFilter(type: string) {
  const index = activeFilters.value.indexOf(type)
  if (index > -1) {
    activeFilters.value.splice(index, 1)
  } else {
    activeFilters.value.push(type)
  }
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString()
}

function downloadLogs() {
  const logText = store.logs.map(log => 
    `[${log.timestamp.toISOString()}] [${log.type.toUpperCase()}] ${log.message}`
  ).join('\n')
  
  const blob = new Blob([logText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `console-logs-${new Date().toISOString()}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

watch(() => store.logs.length, async () => {
  await nextTick()
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
})
</script>
