<template>
  <div class="card">
    <div class="console-header">
      <h2>📋 Console</h2>
      <div class="console-controls">
        <button 
          v-for="filter in logFilters" 
          :key="filter.type"
          @click="toggleFilter(filter.type)"
          :class="['filter-btn', { active: activeFilters.includes(filter.type) }]"
          :title="`Toggle ${filter.label} logs`"
        >
          {{ filter.emoji }} {{ filter.label }}
        </button>
      </div>
    </div>

    <div class="websocket-status" :class="{ connected: wsStore.state.isConnected }">
      WebSocket: {{ wsStore.state.isConnected ? 'Connected' : 'Disconnected' }}
      <span class="log-count">{{ filteredLogs.length }} logs</span>
    </div>

    <div class="log-container" ref="logContainer">
      <div
        v-for="(log, index) in filteredLogs"
        :key="index"
        :class="['log-entry', log.type]"
      >
        <span class="log-time">[{{ formatTime(log.timestamp) }}]</span>
        <span class="log-message">{{ log.message }}</span>
      </div>
      <div v-if="filteredLogs.length === 0" class="no-logs">
        No logs to display
      </div>
    </div>

    <div class="console-footer">
      <button @click="store.clearLogs()" class="btn clear-btn">Clear Logs</button>
      <button @click="downloadLogs()" class="btn download-btn">Download Logs</button>
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

// Auto-scroll to bottom when new logs arrive
watch(() => store.logs.length, async () => {
  await nextTick()
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
})
</script>

<style scoped>
.console-header {
  @apply flex justify-between items-start mb-4 gap-4;
}

.console-header h2 {
  @apply m-0;
}

.console-controls {
  @apply flex gap-2 flex-wrap;
}

.filter-btn {
  @apply px-2 py-1 text-xs rounded border border-gray-300 bg-gray-100 text-gray-600 transition-all;
}

.filter-btn:hover {
  @apply bg-gray-200;
}

.filter-btn.active {
  @apply bg-blue-500 text-white border-blue-600;
}

.websocket-status {
  @apply px-3 py-2 rounded text-xs bg-red-50 text-red-800 mb-4 flex justify-between items-center;
}

.websocket-status.connected {
  @apply bg-green-50 text-green-800;
}

.log-count {
  @apply font-mono font-semibold;
}

.log-container {
  @apply bg-gray-900 text-gray-300 p-4 rounded font-mono text-xs max-h-[400px] overflow-y-auto mb-2.5;
}

.log-entry {
  @apply mb-1 flex gap-2;
}

.log-time {
  @apply text-gray-500 shrink-0;
}

.log-message {
  @apply flex-1;
}

.log-entry.error .log-message {
  @apply text-red-400 font-medium;
}

.log-entry.success .log-message {
  @apply text-green-400;
}

.log-entry.info .log-message {
  @apply text-blue-300;
}

.log-entry.warning .log-message {
  @apply text-orange-400;
}

.no-logs {
  @apply text-gray-500 text-center py-8 italic;
}

.console-footer {
  @apply flex gap-2;
}

.clear-btn {
  @apply flex-1 py-2 text-xs bg-gray-600;
}

.clear-btn:hover {
  @apply bg-gray-700;
}

.download-btn {
  @apply flex-1 py-2 text-xs bg-blue-600;
}

.download-btn:hover {
  @apply bg-blue-700;
}
</style>
