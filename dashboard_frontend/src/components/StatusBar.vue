<template>
  <div
    class="flex flex-wrap items-center gap-1.5 rounded-xl px-2 py-1.5"
  >
    <StatusPill label="Camera" :connected="isConnected(store.systemStatus.camera)" />
    <StatusPill label="Database" :connected="isConnected(store.systemStatus.database)" />
    <StatusPill label="Stage" :connected="isConnected(store.systemStatus.raspberryPi)" />
    <StatusPill label="WebSocket" :connected="isWsConnected" />
    <StatusPill
      label="Closet"
      :connected="closetStatus !== 'unknown'"
      :value="closetLabel"
      :alert="closetStatus === 'open'"
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
const closetStatus = ref<"open" | "closed" | "unknown">("unknown");
let closetPollTimer: number | undefined;

const closetLabel = computed(() => {
  if (closetStatus.value === "unknown") {
    return "Unknown";
  }

  return closetStatus.value === "open" ? "Open" : "Closed";
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
              ? "border-red-200 bg-red-50 text-red-700"
              : "border-slate-200 text-slate-600",
          ],
          title: props.value ? `${props.label}: ${props.value}` : props.label,
        },
        [
          h("span", {
            class: [
              "h-2 w-2 rounded-full shadow-sm",
              props.alert
                ? "bg-red-500"
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
  closetPollTimer = window.setInterval(fetchClosetStatus, 1000);
});

onUnmounted(() => {
  if (closetPollTimer !== undefined) {
    window.clearInterval(closetPollTimer);
  }
});

async function fetchClosetStatus() {
  try {
    const response = await piAPI.getClosetState();
    closetStatus.value = response.is_open ? "open" : "closed";
  } catch {
    closetStatus.value = "unknown";
  }
}

function isConnected(status: string): boolean {
  return status === "connected" || status === "running";
}
</script>
