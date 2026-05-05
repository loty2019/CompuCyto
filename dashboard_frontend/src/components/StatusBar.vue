<template>
  <div
    class="flex flex-wrap items-center gap-1.5 rounded-xl px-2 py-1.5"
  >
    <StatusPill label="Camera" :connected="isConnected(store.systemStatus.camera)" />
    <StatusPill label="Database" :connected="isConnected(store.systemStatus.database)" />
    <StatusPill label="Stage" :connected="isConnected(store.systemStatus.raspberryPi)" />
    <StatusPill label="WebSocket" :connected="isWsConnected" />
    <StatusPill
      label="Lid"
      :connected="store.closetStatus !== 'unknown'"
      :value="closetLabel"
      :alert="store.closetStatus === 'open'"
    />
    <StatusPill
      label="Temp"
      :connected="environmentConnected"
      :value="temperatureLabel"
    />
    <StatusPill
      label="Humidity"
      :connected="environmentConnected"
      :value="humidityLabel"
    />

    <div
      :class="[
        'rounded-full px-2 py-0.5 text-[10px] font-black uppercase tracking-wide',
        store.isSystemHealthy
          ? 'border border-green-200 bg-green-50 text-slate-700'
          : 'border border-amber-200 bg-amber-50 text-amber-700',
      ]"
    >
      {{ store.isSystemHealthy ? "System Healthy" : "System Degraded" }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onMounted, onUnmounted, ref } from "vue";
import { piAPI } from "@/api/client";
import { useMicroscopeStore } from "@/stores/microscope";
import { useWebSocketStore } from "@/stores/websocket";
import { storeToRefs } from "pinia";

const store = useMicroscopeStore();
const wsStore = useWebSocketStore();
const { state: wsState } = storeToRefs(wsStore);

const isWsConnected = computed(() => wsState.value.isConnected);
let closetPollTimer: number | undefined;
let environmentPollTimer: number | undefined;

const environment = ref<{
  temperature_c: number | null;
  humidity: number | null;
  healthy: boolean;
}>({
  temperature_c: null,
  humidity: null,
  healthy: false,
});

const closetLabel = computed(() => {
  if (store.closetStatus === "unknown") {
    return "Unknown";
  }

  return store.closetStatus === "open" ? "Open" : "Closed";
});

const environmentConnected = computed(() => environment.value.healthy);

const temperatureLabel = computed(() => {
  if (environment.value.temperature_c === null) {
    return "Unknown";
  }

  return `${environment.value.temperature_c.toFixed(1)} C`;
});

const humidityLabel = computed(() => {
  if (environment.value.humidity === null) {
    return "Unknown";
  }

  return `${environment.value.humidity.toFixed(1)}%`;
});

const StatusPill = defineComponent({
  props: {
    label: {
      type: String,
      required: true,
    },
    connected: {
      type: Boolean,
      required: true,
    },
    value: {
      type: String,
      default: "",
    },
    alert: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    return () =>
      h(
        "div",
        {
          class: [
            "flex items-center gap-1.5 rounded-full border bg-white px-2 py-0.5 text-[11px] font-bold shadow-sm",
            props.alert
              ? "closet-alert border-red-400 bg-red-100 text-red-800"
              : "border-slate-200 text-slate-600",
          ],
          title: props.value ? `${props.label}: ${props.value}` : props.label,
        },
        [
          h("span", {
            class: [
              "h-2 w-2 rounded-full shadow-sm",
              props.alert
                ? "closet-alert-dot bg-red-600"
                : props.connected
                  ? "bg-teal-500"
                  : "bg-slate-400",
            ],
          }),
          h("span", props.value ? `${props.label}: ${props.value}` : props.label),
        ],
      );
  },
});

onMounted(() => {
  fetchClosetStatus();
  fetchEnvironment();
  closetPollTimer = window.setInterval(fetchClosetStatus, 1000);
  environmentPollTimer = window.setInterval(fetchEnvironment, 5000);
});

onUnmounted(() => {
  if (closetPollTimer !== undefined) {
    window.clearInterval(closetPollTimer);
  }
  if (environmentPollTimer !== undefined) {
    window.clearInterval(environmentPollTimer);
  }
});

async function fetchClosetStatus() {
  try {
    const response = await piAPI.getClosetState();
    store.updateClosetStatus(response.is_open ? "open" : "closed");
  } catch {
    store.updateClosetStatus("unknown");
  }
}

async function fetchEnvironment() {
  try {
    const response = await piAPI.getEnvironment();
    environment.value = {
      temperature_c: response.temperature_c,
      humidity: response.humidity,
      healthy: response.healthy,
    };
  } catch {
    environment.value = {
      temperature_c: null,
      humidity: null,
      healthy: false,
    };
  }
}

function isConnected(status: string): boolean {
  return status === "connected" || status === "running";
}
</script>

<style scoped>
.closet-alert {
  animation: closet-alert-pulse 0.85s ease-in-out infinite;
}

.closet-alert-dot {
  animation: closet-dot-pulse 0.85s ease-in-out infinite;
}

@keyframes closet-alert-pulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.42);
  }
  50% {
    box-shadow: 0 0 0 5px rgba(220, 38, 38, 0.08);
  }
}

@keyframes closet-dot-pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.75;
  }
  50% {
    transform: scale(1.45);
    opacity: 1;
  }
}
</style>
