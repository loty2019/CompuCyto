<template>
  <div
    :class="[
      embedded
        ? 'lab-panel border-slate-300 shadow-lg'
        : 'lab-panel',
    ]"
  >
    <div class="lab-panel-header mb-3 items-start">
      <div>
        <h2 class="lab-title">
          Debug Console
        </h2>
        <p class="mt-1 text-xs text-slate-500">
          API, WebSocket, stage, camera, and browser warnings.
        </p>
      </div>
      <div class="lab-segment-group flex-wrap gap-1 border-0 bg-transparent p-0">
        <button
          v-for="filter in logFilters"
          :key="filter.type"
          @click="toggleFilter(filter.type)"
          :title="`Toggle ${filter.label} logs`"
          :class="[
            'lab-segment border border-slate-300 bg-white',
            activeFilters.includes(filter.type)
              ? 'lab-segment-active'
              : '',
          ]"
        >
          {{ filter.label }}
        </button>
      </div>
    </div>

    <div
      :class="[
        'mb-3 flex items-center justify-between rounded-md border px-3 py-2 text-xs font-semibold',
        wsStore.state.isConnected
          ? 'border-teal-200 bg-teal-50 text-teal-800'
          : 'border-red-200 bg-red-50 text-red-800',
      ]"
    >
      <span>WebSocket: {{ wsStore.state.isConnected ? "Connected" : "Disconnected" }}</span>
      <span class="font-mono font-semibold">{{ filteredLogs.length }} logs</span>
    </div>

    <div
      ref="logContainer"
      class="mb-2.5 max-h-[min(58vh,460px)] overflow-y-auto rounded-md border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-slate-300"
    >
      <div
        v-for="(log, index) in filteredLogs"
        :key="index"
        class="mb-1 flex gap-2"
      >
        <span class="shrink-0 text-slate-500">[{{ formatTime(log.timestamp) }}]</span>
        <span
          :class="[
            'min-w-0 flex-1 break-words',
            log.type === 'error' && 'font-medium text-red-400',
            log.type === 'success' && 'text-teal-300',
            log.type === 'info' && 'text-slate-300',
            log.type === 'warning' && 'text-amber-300',
          ]"
        >
          {{ log.message }}
        </span>
      </div>
      <div
        v-if="filteredLogs.length === 0"
        class="py-8 text-center italic text-slate-500"
      >
        No logs to display
      </div>
    </div>

    <div class="flex gap-2">
      <button
        @click="store.clearLogs()"
        class="lab-button lab-button-secondary flex-1"
      >
        Clear Logs
      </button>
      <button
        @click="downloadLogs()"
        class="lab-button lab-button-primary flex-1"
      >
        Download Logs
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { useWebSocketStore } from "@/stores/websocket";
import type { LogEntry } from "@/types";

defineProps<{
  embedded?: boolean;
}>();

const store = useMicroscopeStore();
const wsStore = useWebSocketStore();
const logContainer = ref<HTMLElement | null>(null);

const logFilters: Array<{ type: LogEntry["type"]; label: string }> = [
  { type: "info", label: "Info" },
  { type: "success", label: "Success" },
  { type: "error", label: "Error" },
  { type: "warning", label: "Warning" },
];

const activeFilters = ref<LogEntry["type"][]>([
  "info",
  "success",
  "error",
  "warning",
]);

const filteredLogs = computed(() => {
  return store.logs.filter((log) => activeFilters.value.includes(log.type));
});

function toggleFilter(type: LogEntry["type"]) {
  const index = activeFilters.value.indexOf(type);
  if (index > -1) {
    activeFilters.value.splice(index, 1);
  } else {
    activeFilters.value.push(type);
  }
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString();
}

function downloadLogs() {
  const logText = store.logs
    .map(
      (log) =>
        `[${log.timestamp.toISOString()}] [${log.type.toUpperCase()}] ${log.message}`,
    )
    .join("\n");

  const blob = new Blob([logText], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `console-logs-${new Date().toISOString()}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}

watch(
  () => store.logs.length,
  async () => {
    await nextTick();
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight;
    }
  },
);
</script>
