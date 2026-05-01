<template>
  <div
    class="flex flex-wrap items-center gap-1.5 rounded-xl px-2 py-1.5"
  >
    <StatusPill label="Camera" :connected="isConnected(store.systemStatus.camera)" />
    <StatusPill label="Database" :connected="isConnected(store.systemStatus.database)" />
    <StatusPill label="Stage" :connected="isConnected(store.systemStatus.raspberryPi)" />
    <StatusPill label="WebSocket" :connected="isWsConnected" />

    <div
      :class="[
        'rounded-full px-2 py-0.5 text-[10px] font-black uppercase tracking-wide',
        store.isSystemHealthy
          ? 'border border-slate-200 bg-white text-slate-700'
          : 'border border-amber-200 bg-amber-50 text-amber-700',
      ]"
    >
      {{ store.isSystemHealthy ? "System Healthy" : "System Degraded" }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { useWebSocketStore } from "@/stores/websocket";
import { storeToRefs } from "pinia";

const store = useMicroscopeStore();
const wsStore = useWebSocketStore();
const { state: wsState } = storeToRefs(wsStore);

const isWsConnected = computed(() => wsState.value.isConnected);

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
  },
  setup(props) {
    return () =>
      h(
        "div",
        {
          class:
            "flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-2 py-0.5 text-[11px] font-bold text-slate-600 shadow-sm",
          title: props.label,
        },
        [
          h("span", {
            class: [
              "h-2 w-2 rounded-full shadow-sm",
              props.connected ? "bg-teal-500" : "bg-red-500",
            ],
          }),
          h("span", props.label),
        ],
      );
  },
});

function isConnected(status: string): boolean {
  return status === "connected" || status === "running";
}
</script>
