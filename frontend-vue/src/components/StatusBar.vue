<template>
  <div class="status-bar">
    <div class="status-item">
      <div :class="['status-indicator', getStatusClass(store.systemStatus.camera)]"></div>
      <span>Camera</span>
    </div>
    <div class="status-item">
      <div :class="['status-indicator', getStatusClass(store.systemStatus.stage)]"></div>
      <span>Stage</span>
    </div>
    <div class="status-item">
      <div :class="['status-indicator', getStatusClass(store.systemStatus.database)]"></div>
      <span>Database</span>
    </div>
    <div class="status-item">
      <div :class="['status-indicator', getStatusClass(store.systemStatus.raspberryPi)]"></div>
      <span>Raspberry Pi</span>
    </div>
    <div class="status-item">
      <div :class="['status-indicator', wsStore.state.isConnected ? 'connected' : 'disconnected']"></div>
      <span>WebSocket</span>
    </div>
    <div v-if="store.isSystemHealthy" class="health-indicator healthy">
      ✓ System Healthy
    </div>
    <div v-else class="health-indicator unhealthy">
      ⚠ System Degraded
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMicroscopeStore } from '@/stores/microscope'
import { useWebSocketStore } from '@/stores/websocket'

const store = useMicroscopeStore()
const wsStore = useWebSocketStore()

function getStatusClass(status: string): string {
  switch (status) {
    case 'connected':
    case 'running':
      return 'connected'
    case 'disconnected':
    case 'stopped':
      return 'disconnected'
    default:
      return 'unknown'
  }
}
</script>

<style scoped>
.status-bar {
  @apply flex gap-5 items-center;
}

.status-item {
  @apply flex items-center gap-2 text-sm;
}

.status-indicator {
  @apply w-3 h-3 rounded-full bg-gray-400 transition-colors;
}

.status-indicator.connected,
.status-indicator.running {
  @apply bg-green-500;
}

.status-indicator.disconnected {
  @apply bg-red-500;
}

.status-indicator.stopped {
  @apply bg-orange-500;
}

.status-indicator.unknown {
  @apply bg-gray-400;
}

.health-indicator {
  @apply ml-4 px-3 py-1 rounded-full text-sm font-semibold;
}

.health-indicator.healthy {
  @apply bg-green-100 text-green-700;
}

.health-indicator.unhealthy {
  @apply bg-orange-100 text-orange-700;
}
</style>
