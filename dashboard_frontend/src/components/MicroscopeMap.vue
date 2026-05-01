<template>
  <div
    :class="[
      'map-panel rounded-xl border border-slate-200/80 bg-white shadow-md',
      compact ? 'p-2' : 'p-5',
    ]"
  >
    <div class="mb-1.5 flex items-center justify-between gap-2">
      <div>
        <h2 :class="['font-bold text-slate-900', compact ? 'text-sm' : 'text-lg']">
          Map
        </h2>
      </div>
      <div
        v-if="!compact"
        class="rounded-full bg-slate-950 px-2 py-0.5 font-mono text-[10px] font-bold text-white"
      >
        X {{ currentX.toFixed(1) }} / Y {{ currentY.toFixed(1) }}
      </div>
    </div>

    <div class="map-container">
      <svg
        class="microscope-map"
        viewBox="0 0 400 300"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="#dbeafe"
              stroke-width="1"
            />
          </pattern>

          <linearGradient id="stageGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#f0f9ff;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#e0f2fe;stop-opacity:1" />
          </linearGradient>

          <linearGradient id="microscopeGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#60a5fa;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:1" />
          </linearGradient>

          <filter id="shadow">
            <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.3" />
          </filter>

          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <rect width="400" height="300" fill="#f8fafc" />
        <rect width="400" height="300" fill="url(#grid)" />

        <rect
          x="20"
          y="20"
          width="360"
          height="260"
          fill="url(#stageGradient)"
          stroke="#3b82f6"
          stroke-width="2"
          rx="8"
          filter="url(#shadow)"
        />

        <circle cx="25" cy="25" r="3" fill="#3b82f6" opacity="0.5" />
        <circle cx="375" cy="25" r="3" fill="#3b82f6" opacity="0.5" />
        <circle cx="25" cy="275" r="3" fill="#3b82f6" opacity="0.5" />
        <circle cx="375" cy="275" r="3" fill="#3b82f6" opacity="0.5" />

        <g filter="url(#glow)">
          <circle
            cx="200"
            cy="150"
            r="6"
            fill="none"
            stroke="#f59e0b"
            stroke-width="2"
            opacity="0.6"
          />
          <line
            x1="200"
            y1="135"
            x2="200"
            y2="165"
            stroke="#f59e0b"
            stroke-width="2"
            stroke-dasharray="4,4"
          />
          <line
            x1="185"
            y1="150"
            x2="215"
            y2="150"
            stroke="#f59e0b"
            stroke-width="2"
            stroke-dasharray="4,4"
          />
        </g>
        <text
          x="200"
          y="180"
          font-size="11"
          fill="#78716c"
          text-anchor="middle"
          font-weight="600"
        >
          Home
        </text>

        <g font-size="13" fill="#1e40af" font-weight="bold">
          <text x="365" y="155" text-anchor="end">+X</text>
          <text x="35" y="155">-X</text>
          <text x="200" y="40" text-anchor="middle">+Y</text>
          <text x="200" y="270" text-anchor="middle">-Y</text>
        </g>

        <g :transform="`translate(${markerX}, ${markerY})`">
          <rect
            x="-15"
            y="-18"
            width="30"
            height="40"
            fill="#000000"
            opacity="0.15"
            rx="3"
            transform="translate(1, 2)"
          />

          <rect
            x="-15"
            y="-20"
            width="30"
            height="40"
            fill="url(#microscopeGradient)"
            stroke="#1e40af"
            stroke-width="2.5"
            rx="3"
            filter="url(#shadow)"
          />

          <circle cx="0" cy="-8" r="6" fill="#1e3a8a" opacity="0.4" />
          <circle cx="0" cy="-8" r="3" fill="#3b82f6" opacity="0.6" />
          <circle
            cx="0"
            cy="0"
            r="4"
            fill="#fbbf24"
            stroke="#f59e0b"
            stroke-width="2"
            filter="url(#glow)"
          />

          <g v-if="isMoving">
            <circle
              cx="0"
              cy="0"
              r="8"
              fill="none"
              stroke="#3b82f6"
              stroke-width="3"
              opacity="0.6"
            >
              <animate
                attributeName="r"
                from="8"
                to="25"
                dur="1.2s"
                repeatCount="indefinite"
              />
              <animate
                attributeName="opacity"
                from="0.6"
                to="0"
                dur="1.2s"
                repeatCount="indefinite"
              />
            </circle>
            <circle
              cx="0"
              cy="0"
              r="8"
              fill="none"
              stroke="#60a5fa"
              stroke-width="2"
              opacity="0.4"
            >
              <animate
                attributeName="r"
                from="8"
                to="25"
                dur="1.2s"
                begin="0.3s"
                repeatCount="indefinite"
              />
              <animate
                attributeName="opacity"
                from="0.4"
                to="0"
                dur="1.2s"
                begin="0.3s"
                repeatCount="indefinite"
              />
            </circle>
          </g>
        </g>
      </svg>
    </div>

    <div v-if="!compact" :class="compact ? 'mt-2' : 'mt-4'">
      <div
        class="flex items-center gap-3 rounded-lg border border-gray-200 bg-gradient-to-br from-white to-gray-50 p-2.5 shadow-sm transition-all duration-200 hover:border-blue-300 hover:shadow-md"
      >
        <div
          class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-100 to-blue-200 text-sm font-black text-blue-700"
        >
          {{ isMoving ? "MOVE" : "OK" }}
        </div>
        <div class="flex-1">
          <div class="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500">
            Status
          </div>
          <div
            :class="[
              'text-sm font-bold leading-tight',
              isMoving ? 'animate-pulse text-blue-600' : 'text-green-600',
            ]"
          >
            {{ isMoving ? "Moving" : "Idle" }}
          </div>
        </div>
      </div>
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
const maxY = 8000;

const currentX = computed(() => store.position.x);
const currentY = computed(() => store.position.y);
const isMoving = computed(() => store.position.is_moving);

const mapWidth = 360;
const mapHeight = 260;
const mapCenterX = 200;
const mapCenterY = 150;

const markerX = computed(() => {
  const scaledX = (currentX.value / maxX) * (mapWidth / 2);
  return mapCenterX + scaledX;
});

const markerY = computed(() => {
  const scaledY = (currentY.value / maxY) * (mapHeight / 2);
  return mapCenterY - scaledY;
});
</script>

<style scoped>
.map-panel {
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.1), transparent 34%),
    linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.map-container {
  @apply overflow-hidden rounded-xl border border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50 shadow-md;
}

.microscope-map {
  @apply block h-auto w-full;
}
</style>
