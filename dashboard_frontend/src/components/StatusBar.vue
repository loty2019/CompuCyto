<template>
  <div class="flex flex-wrap items-center gap-1.5 px-1 py-1">
    <StatusPill
      label="Camera"
      :connected="isConnected(store.systemStatus.camera)"
    />
    <StatusPill
      label="Database"
      :connected="isConnected(store.systemStatus.database)"
    />
    <StatusPill
      label="Stage"
      :connected="isConnected(store.systemStatus.raspberryPi)"
    />
    <StatusPill label="WebSocket" :connected="isWsConnected" />
    <StatusPill
      label="Lid"
      :connected="store.closetStatus !== 'unknown'"
      :value="closetLabel"
      :alert="store.closetStatus === 'open'"
    />
    <div class="relative" ref="debugMenu">
      <button
        type="button"
        @click="isDebugOpen = !isDebugOpen"
        :class="[
          'lab-button min-h-[26px] rounded-full px-2 py-0.5 text-[10px] uppercase tracking-wide',
          store.isSystemHealthy
            ? 'border border-green-200 bg-green-50 text-slate-700'
            : 'border border-amber-200 bg-amber-50 text-amber-700',
        ]"
        :aria-expanded="isDebugOpen"
        aria-label="Open debug logs"
        title="System debug logs"
      >
        <span
          :class="[
            'h-2 w-2 rounded-full',
            store.isSystemHealthy ? 'bg-teal-500' : 'bg-amber-500',
          ]"
        ></span>
        <span>{{ store.isSystemHealthy ? "System Healthy" : "System Degraded" }}</span>
        <span
          v-if="importantLogCount > 0"
          class="rounded-full bg-slate-900 px-1.5 py-px text-[9px] text-white"
        >
          {{ importantLogCount }}
        </span>
      </button>

      <div
        v-if="isDebugOpen"
        class="absolute right-0 top-full z-50 mt-2 w-[min(92vw,760px)]"
      >
        <ConsoleLog embedded />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onMounted, onUnmounted, ref } from "vue";
import { piAPI } from "@/api/client";
import ConsoleLog from "@/components/ConsoleLog.vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { useWebSocketStore } from "@/stores/websocket";
import { storeToRefs } from "pinia";

const store = useMicroscopeStore();
const wsStore = useWebSocketStore();
const { state: wsState } = storeToRefs(wsStore);

const isWsConnected = computed(() => wsState.value.isConnected);
const isDebugOpen = ref(false);
const debugMenu = ref<HTMLElement | null>(null);
let closetPollTimer: number | undefined;

const importantLogCount = computed(
  () => store.logs.filter((log) => log.type === "error").length,
);

const closetLabel = computed(() => {
  if (store.closetStatus === "unknown") {
    return "Unknown";
  }

  return store.closetStatus === "open" ? "Open" : "Closed";
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
            "flex min-h-[26px] items-center gap-1.5 rounded-full border bg-white px-2 py-0.5 text-[11px] font-bold",
            props.alert
              ? "closet-alert border-red-400 bg-red-100 text-red-800"
              : "border-slate-200 text-slate-600",
          ],
          title: props.value ? `${props.label}: ${props.value}` : props.label,
        },
        [
          h("span", {
            class: [
              "h-2 w-2 rounded-full",
              props.alert
                ? "closet-alert-dot bg-red-600"
                : props.connected
                  ? "bg-teal-500"
                  : "bg-slate-400",
            ],
          }),
          h(
            "span",
            props.value ? `${props.label}: ${props.value}` : props.label,
          ),
        ],
      );
  },
});

onMounted(() => {
  fetchClosetStatus();
  closetPollTimer = window.setInterval(fetchClosetStatus, 1000);
  document.addEventListener("pointerdown", handleOutsideClick);
});

onUnmounted(() => {
  if (closetPollTimer !== undefined) {
    window.clearInterval(closetPollTimer);
  }
  document.removeEventListener("pointerdown", handleOutsideClick);
});

async function fetchClosetStatus() {
  try {
    const response = await piAPI.getClosetState();
    store.updateClosetStatus(response.is_open ? "open" : "closed");
  } catch {
    store.updateClosetStatus("unknown");
  }
}

function isConnected(status: string): boolean {
  return status === "connected" || status === "running";
}

function handleOutsideClick(event: PointerEvent) {
  if (!debugMenu.value?.contains(event.target as Node)) {
    isDebugOpen.value = false;
  }
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
