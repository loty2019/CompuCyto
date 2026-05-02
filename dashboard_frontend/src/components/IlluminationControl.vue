<template>
  <div class="illumination-panel flex h-full flex-col rounded-lg border border-slate-200/80 bg-white p-2 shadow-md">
    <div class="mb-1.5 flex items-center justify-between">
      <h2 class="text-sm font-black uppercase tracking-wide text-slate-950">Light</h2>
      <span class="text-[10px] font-bold uppercase tracking-wide text-slate-400">L / F</span>
    </div>

    <div
      v-if="lightError || flrLightError"
      class="mb-2 rounded-lg border border-red-200 bg-red-50 p-2 text-xs font-medium text-red-700"
    >
      <span v-if="lightError" class="block">Main Light: {{ lightError }}</span>
      <span v-if="flrLightError" class="block">FLR Light: {{ flrLightError }}</span>
    </div>

    <div class="grid grid-cols-2 gap-1.5">
      <button
        @click="toggleLight"
        :disabled="isToggling || lightLoading"
        :class="[
          'light-card',
          isLightOn
            ? 'border-amber-300 bg-amber-50 text-slate-800 shadow-amber-200/50'
            : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50',
          isToggling || lightLoading ? 'cursor-not-allowed opacity-70' : 'cursor-pointer',
        ]"
      >
        <span
          class="light-card-dot"
          :class="isLightOn ? 'light-card-dot-on light-card-dot-main bg-amber-400' : 'bg-slate-300'"
        ></span>
        <span class="flex-1 text-left">
          <span class="block text-xs font-black">Main</span>
          <span class="text-[11px] font-semibold opacity-70">{{ isLightOn ? "On" : "Off" }}</span>
        </span>
      </button>

      <button
        @click="toggleFlrLight"
        :disabled="isFlrToggling || flrLightLoading"
        :class="[
          'light-card',
          isFlrLightOn
            ? 'border-indigo-300 bg-indigo-50 text-slate-800 shadow-indigo-200/50'
            : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50',
          isFlrToggling || flrLightLoading ? 'cursor-not-allowed opacity-70' : 'cursor-pointer',
        ]"
      >
        <span
          class="light-card-dot"
          :class="isFlrLightOn ? 'light-card-dot-on light-card-dot-flr bg-indigo-500' : 'bg-slate-300'"
        ></span>
        <span class="flex-1 text-left">
          <span class="block text-xs font-black">FLR</span>
          <span class="text-[11px] font-semibold opacity-70">{{ isFlrLightOn ? "On" : "Off" }}</span>
        </span>
      </button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { piAPI } from "@/api/client";

const store = useMicroscopeStore();

const isLightOn = ref(false);
const lightLoading = ref(true);
const isToggling = ref(false);
const lightError = ref("");

const isFlrLightOn = ref(false);
const flrLightLoading = ref(true);
const isFlrToggling = ref(false);
const flrLightError = ref("");

onMounted(() => {
  fetchLightStatus();
  fetchFlrLightStatus();
  window.addEventListener("keydown", handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeyDown);
});

async function fetchLightStatus() {
  try {
    lightLoading.value = true;
    lightError.value = "";
    const response = await piAPI.getLedLampState();
    isLightOn.value = response.is_on;
    store.updateLightStatus(response.is_on);
  } catch (err: any) {
    console.error("Failed to fetch light status:", err);
    lightError.value = "Failed to connect";
  } finally {
    lightLoading.value = false;
  }
}

async function toggleLight() {
  try {
    isToggling.value = true;
    lightError.value = "";
    const response = await piAPI.toggleLedLamp();
    isLightOn.value = response.is_on;
    store.updateLightStatus(response.is_on);
  } catch (err: any) {
    console.error("Failed to toggle light:", err);
    lightError.value = "Failed to toggle";
    await fetchLightStatus();
  } finally {
    isToggling.value = false;
  }
}

async function fetchFlrLightStatus() {
  try {
    flrLightLoading.value = true;
    flrLightError.value = "";
    const response = await piAPI.getLedFlrState();
    isFlrLightOn.value = response.is_on;
  } catch (err: any) {
    console.error("Failed to fetch FLR light status:", err);
    flrLightError.value = "Failed to connect";
  } finally {
    flrLightLoading.value = false;
  }
}

async function toggleFlrLight() {
  try {
    isFlrToggling.value = true;
    flrLightError.value = "";
    const response = await piAPI.toggleLedFlr();
    isFlrLightOn.value = response.is_on;
  } catch (err: any) {
    console.error("Failed to toggle FLR light:", err);
    flrLightError.value = "Failed to toggle FLR";
    await fetchFlrLightStatus();
  } finally {
    isFlrToggling.value = false;
  }
}

function handleKeyDown(event: KeyboardEvent) {
  const target = event.target as HTMLElement;
  if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") {
    return;
  }

  const key = event.key.toLowerCase();
  if (key === "l" && !isToggling.value && !lightLoading.value) {
    toggleLight();
  }
  if (key === "f" && !isFlrToggling.value && !flrLightLoading.value) {
    toggleFlrLight();
  }
}
</script>

<style scoped>
.illumination-panel {
  background:
    radial-gradient(circle at top right, rgba(148, 163, 184, 0.18), transparent 34%),
    linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.light-card {
  @apply flex min-h-[42px] items-center gap-2 rounded-md border px-2 py-1.5 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md active:translate-y-0;
}

.light-card-dot {
  @apply h-2 w-2 rounded-full shadow-inner;
}

.light-card-dot-on {
  animation: light-dot-pulse 1.15s ease-in-out infinite;
}

.light-card-dot-main {
  box-shadow: 0 0 10px rgba(245, 158, 11, 0.85);
}

.light-card-dot-flr {
  box-shadow: 0 0 10px rgba(99, 102, 241, 0.85);
}

@keyframes light-dot-pulse {
  0%,
  100% {
    opacity: 0.72;
    transform: scale(0.9);
  }
  50% {
    opacity: 1;
    transform: scale(1.35);
  }
}
</style>
