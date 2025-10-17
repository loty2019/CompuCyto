<template>
  <div class="flex gap-5 items-center">
    <div class="flex items-center gap-2 text-sm" title="Backend Python">
      <div class="relative flex items-center justify-center w-3 h-3">
        <div
          :class="[
            'absolute w-3 h-3 rounded-full transition-colors z-10',
            isConnected(store.systemStatus.camera)
              ? 'bg-green-500'
              : 'bg-red-500',
          ]"
        ></div>
        <div
          v-if="isConnected(store.systemStatus.camera)"
          class="absolute w-3 h-3 rounded-full bg-green-500 animate-ping opacity-75"
        ></div>
      </div>
      <span>Camera</span>
    </div>
    <!-- <div class="flex items-center gap-2 text-sm">
      <div class="relative flex items-center justify-center w-3 h-3">
        <div :class="['absolute w-3 h-3 rounded-full transition-colors z-10', isConnected(store.systemStatus.stage) ? 'bg-green-500' : 'bg-red-500']"></div>
        <div v-if="isConnected(store.systemStatus.stage)" class="absolute w-3 h-3 rounded-full bg-green-500 animate-ping opacity-75"></div>
      </div>
      <span>Stage</span>
    </div> -->
    <div class="flex items-center gap-2 text-sm" title="Postgres">
      <div class="relative flex items-center justify-center w-3 h-3">
        <div
          :class="[
            'absolute w-3 h-3 rounded-full transition-colors z-10',
            isConnected(store.systemStatus.database)
              ? 'bg-green-500'
              : 'bg-red-500',
          ]"
        ></div>
        <div
          v-if="isConnected(store.systemStatus.database)"
          class="absolute w-3 h-3 rounded-full bg-green-500 animate-ping opacity-75"
        ></div>
      </div>
      <span>Database</span>
    </div>
    <div class="flex items-center gap-2 text-sm" title="Raspberry Pi 5">
      <div class="relative flex items-center justify-center w-3 h-3">
        <div
          :class="[
            'absolute w-3 h-3 rounded-full transition-colors z-10',
            isConnected(store.systemStatus.raspberryPi)
              ? 'bg-green-500'
              : 'bg-red-500',
          ]"
        ></div>
        <div
          v-if="isConnected(store.systemStatus.raspberryPi)"
          class="absolute w-3 h-3 rounded-full bg-green-500 animate-ping opacity-75"
        ></div>
      </div>
      <span>Stage</span>
    </div>
    <div class="flex items-center gap-2 text-sm">
      <div class="relative flex items-center justify-center w-3 h-3">
        <div
          :class="[
            'absolute w-3 h-3 rounded-full transition-colors z-10',
            isWsConnected ? 'bg-green-500' : 'bg-red-500',
          ]"
        ></div>
        <div
          v-if="isWsConnected"
          class="absolute w-3 h-3 rounded-full bg-green-500 animate-ping opacity-75"
        ></div>
      </div>
      <span>WebSocket</span>
    </div>
    <div
      v-if="store.isSystemHealthy"
      class="ml-4 px-3 py-1 rounded-full text-sm font-semibold bg-green-100 text-green-700"
    >
      ✓ System Healthy
    </div>
    <div
      v-else
      class="ml-4 px-3 py-1 rounded-full text-sm font-semibold bg-orange-100 text-orange-700"
    >
      ⚠ System Degraded
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { useWebSocketStore } from "@/stores/websocket";
import { storeToRefs } from "pinia";

const store = useMicroscopeStore();
const wsStore = useWebSocketStore();
const { state: wsState } = storeToRefs(wsStore);

const isWsConnected = computed(() => wsState.value.isConnected);

function isConnected(status: string): boolean {
  return status === "connected" || status === "running";
}
</script>
