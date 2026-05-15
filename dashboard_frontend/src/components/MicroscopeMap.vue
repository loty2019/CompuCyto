<template>
  <div
    :class="[
      'map-panel rounded-xl border border-slate-200/80 bg-white shadow-md',
      compact ? 'p-2' : 'p-5',
    ]"
  >
    <div class="mb-1.5 flex items-center justify-between gap-2">
      <h2 :class="['font-bold text-slate-900', compact ? 'text-sm' : 'text-lg']">
        Map
      </h2>
      <div
        v-if="!compact"
        class="rounded-full bg-slate-950 px-2 py-0.5 font-mono text-[10px] font-bold text-white"
      >
        X {{ currentX.toFixed(0) }} / Y {{ currentY.toFixed(0) }}
      </div>
    </div>

    <div class="map-container">
      <svg
        class="microscope-map"
        viewBox="0 0 260 360"
        xmlns="http://www.w3.org/2000/svg"
        aria-label="Stage map"
      >
        <rect width="260" height="360" fill="#f8fafc" />

        <rect
          :x="stageLeft"
          :y="stageTop"
          :width="stageWidth"
          :height="stageHeight"
          fill="#ffffff"
          stroke="#334155"
          stroke-width="2"
          rx="4"
        />

        <line
          :x1="stageLeft"
          :y1="stageBottom"
          :x2="stageRight"
          :y2="stageBottom"
          stroke="#0f172a"
          stroke-width="3"
        />
        <line
          :x1="stageLeft"
          :y1="stageTop"
          :x2="stageLeft"
          :y2="stageBottom"
          stroke="#64748b"
          stroke-width="2"
        />

        <g font-size="11" fill="#475569" font-weight="800">
          <text :x="stageLeft" :y="stageBottom + 18" text-anchor="middle">X 0</text>
          <text :x="stageRight" :y="stageBottom + 18" text-anchor="middle">+X</text>
          <text :x="stageLeft - 22" :y="stageTop + stageHeight / 2" text-anchor="middle">Y</text>
          <text :x="stageLeft - 8" :y="stageTop + 4" text-anchor="end">+Y</text>
          <text :x="stageLeft - 8" :y="stageBottom" text-anchor="end">0</text>
        </g>

        <g :transform="`translate(${markerX}, ${markerY})`">
          <circle
            r="8"
            fill="#2563eb"
            stroke="#ffffff"
            stroke-width="3"
          />
          <circle
            v-if="isMoving"
            r="15"
            fill="none"
            stroke="#2563eb"
            stroke-width="2"
            opacity="0.45"
          />
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";

defineProps<{
  compact?: boolean;
}>();

const store = useMicroscopeStore();

const maxX = 10000;
const maxY = 10000;

const stageLeft = 60;
const stageTop = 20;
const stageWidth = 150;
const stageHeight = 300;
const stageRight = stageLeft + stageWidth;
const stageBottom = stageTop + stageHeight;

const currentX = computed(() => store.position.x);
const currentY = computed(() => store.position.y);
const isMoving = computed(() => store.position.is_moving);

const markerX = computed(() => {
  const normalizedX = Math.min(Math.max(currentX.value / maxX, 0), 1);
  return stageLeft + normalizedX * stageWidth;
});

const markerY = computed(() => {
  const normalizedY = Math.min(Math.max(currentY.value / maxY, 0), 1);
  return stageBottom - normalizedY * stageHeight;
});
</script>

<style scoped>
.map-panel {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.map-container {
  @apply overflow-hidden rounded-lg border border-slate-200 bg-slate-50 shadow-inner;
}

.microscope-map {
  @apply block h-auto w-full;
}
</style>
