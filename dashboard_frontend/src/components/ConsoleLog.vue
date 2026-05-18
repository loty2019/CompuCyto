<template>
  <div
    :class="[
      embedded
        ? 'rounded-lg border border-slate-200 bg-white p-3 shadow-2xl'
        : 'rounded-lg bg-white p-5 shadow-md',
    ]"
  >
    <div class="mb-4 flex items-start justify-between gap-4">
      <div>
        <h2 class="m-0 text-sm font-black uppercase tracking-wide text-gray-900">
          Debug Console
        </h2>
        <p class="mt-1 text-xs text-slate-500">
          API, WebSocket, stage, camera, and browser warnings.
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="filter in logFilters"
          :key="filter.type"
          @click="toggleFilter(filter.type)"
          :title="`Toggle ${filter.label} logs`"
          :class="[
            'rounded border px-2 py-1 text-xs transition-all',
            activeFilters.includes(filter.type)
              ? 'border-blue-600 bg-blue-500 text-white'
              : 'border-gray-300 bg-gray-100 text-gray-600 hover:bg-gray-200',
          ]"
        >
          {{ filter.label }}
        </button>
      </div>
    </div>

    <div
      :class="[
        'mb-4 flex items-center justify-between rounded px-3 py-2 text-xs',
        wsStore.state.isConnected
          ? 'bg-green-50 text-green-800'
          : 'bg-red-50 text-red-800',
      ]"
    >
      <span>WebSocket: {{ wsStore.state.isConnected ? "Connected" : "Disconnected" }}</span>
      <span class="font-mono font-semibold">{{ filteredLogs.length }} logs</span>
    </div>

    <div
      ref="logContainer"
      class="mb-2.5 max-h-[min(58vh,460px)] overflow-y-auto rounded bg-gray-900 p-4 font-mono text-xs text-gray-300"
    >
      <div
        v-for="(log, index) in filteredLogs"
        :key="index"
        class="mb-1 flex gap-2"
      >
        <span class="shrink-0 text-gray-500">[{{ formatTime(log.timestamp) }}]</span>
        <span
          :class="[
            'min-w-0 flex-1 break-words',
            log.type === 'error' && 'font-medium text-red-400',
            log.type === 'success' && 'text-green-400',
            log.type === 'info' && 'text-blue-300',
            log.type === 'warning' && 'text-orange-400',
          ]"
        >
          {{ log.message }}
        </span>
      </div>
      <div
        v-if="filteredLogs.length === 0"
        class="py-8 text-center text-gray-500 italic"
      >
        No logs to display
      </div>
    </div>

    <div class="flex gap-2">
      <button
        @click="store.clearLogs()"
        class="flex-1 cursor-pointer rounded bg-gray-600 py-2 text-xs font-medium text-white transition-colors hover:bg-gray-700"
      >
        Clear Logs
      </button>
      <button
        @click="downloadLogs()"
        class="flex-1 cursor-pointer rounded bg-blue-600 py-2 text-xs font-medium text-white transition-colors hover:bg-blue-700"
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
