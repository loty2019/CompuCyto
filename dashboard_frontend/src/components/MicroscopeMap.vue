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
        viewBox="0 0 300 360"
        xmlns="http://www.w3.org/2000/svg"
        aria-label="Stage map"
      >
        <defs>
          <linearGradient id="stageSurface" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" />
            <stop offset="100%" stop-color="#eef6ff" />
          </linearGradient>
          <pattern id="stageGrid" width="24" height="24" patternUnits="userSpaceOnUse">
            <path
              d="M 24 0 L 0 0 0 24"
              fill="none"
              stroke="#dbeafe"
              stroke-width="1"
            />
          </pattern>
          <filter id="markerShadow">
            <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.28" />
          </filter>
        </defs>

        <rect width="300" height="360" fill="#f8fafc" />

        <rect
          x="10"
          y="10"
          width="280"
          height="340"
          fill="#f1f5f9"
          stroke="#e2e8f0"
          stroke-width="1"
          rx="10"
        />

        <rect
          :x="stageLeft"
          :y="stageTop"
          :width="stageWidth"
          :height="stageHeight"
          fill="url(#stageSurface)"
          stroke="#1e293b"
          stroke-width="2"
          rx="6"
        />
        <rect
          :x="stageLeft"
          :y="stageTop"
          :width="stageWidth"
          :height="stageHeight"
          fill="url(#stageGrid)"
          opacity="0.7"
          rx="6"
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
        <line
          :x1="stageLeft"
          :y1="stageBottom"
          :x2="stageRight"
          :y2="stageBottom"
          stroke="#2563eb"
          stroke-width="2"
          opacity="0.8"
        />
        <line
          :x1="stageLeft"
          :y1="stageTop"
          :x2="stageLeft"
          :y2="stageBottom"
          stroke="#0f766e"
          stroke-width="2"
          opacity="0.8"
        />

        <g font-size="10" fill="#475569" font-weight="800">
          <text :x="stageLeft" :y="stageBottom + 18" text-anchor="middle">X 0</text>
          <text :x="stageRight" :y="stageBottom + 18" text-anchor="middle">X max</text>
          <text :x="stageLeft - 18" :y="stageTop + stageHeight / 2" text-anchor="middle">Y</text>
          <text :x="stageLeft - 8" :y="stageTop + 4" text-anchor="end">Y max</text>
          <text :x="stageLeft - 8" :y="stageBottom" text-anchor="end">0</text>
        </g>

        <g font-size="9" fill="#64748b" font-weight="700">
          <text :x="markerX" :y="stageBottom + 32" text-anchor="middle">
            X {{ currentX.toFixed(0) }}
          </text>
          <text :x="stageRight + 8" :y="markerY + 3">
            Y {{ currentY.toFixed(0) }}
          </text>
        </g>

        <g :transform="`translate(${markerX}, ${markerY})`">
          <line
            :x1="stageLeft - markerX"
            y1="0"
            :x2="stageRight - markerX"
            y2="0"
            stroke="#2563eb"
            stroke-width="1.5"
            stroke-dasharray="4 4"
            opacity="0.65"
          />
          <line
            x1="0"
            :y1="stageTop - markerY"
            x2="0"
            :y2="stageBottom - markerY"
            stroke="#0f766e"
            stroke-width="1.5"
            stroke-dasharray="4 4"
            opacity="0.65"
          />
          <circle
            r="9"
            fill="#2563eb"
            stroke="#ffffff"
            stroke-width="3"
            filter="url(#markerShadow)"
          />
          <circle r="3" fill="#f8fafc" />
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
import { STAGE_AXIS_MAX } from "@/config/stage";

defineProps<{
  compact?: boolean;
}>();

const store = useMicroscopeStore();

const maxX = STAGE_AXIS_MAX.x;
const maxY = STAGE_AXIS_MAX.y;

const stageLeft = 54;
const stageTop = 24;
const stageWidth = 184;
const stageHeight = 280;
const stageRight = stageLeft + stageWidth;
const stageBottom = stageTop + stageHeight;

const currentX = computed(() => store.position.x);
const currentY = computed(() => store.position.y);
const isMoving = computed(() => store.position.is_moving);

const markerX = computed(() => {
  const normalizedX = Math.min(Math.max(currentX.value / maxX, 0), 1);
  return stageRight - normalizedX * stageWidth;
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
