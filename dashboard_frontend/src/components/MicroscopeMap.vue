<template>
  <section
    :class="[
      'map-panel rounded-lg border border-slate-200/80 bg-white shadow-md',
      compact ? 'p-1.5' : 'p-3',
    ]"
  >
    <div class="mb-1.5 flex items-center justify-between gap-2">
      <h2 class="text-sm font-black uppercase tracking-wide text-slate-950">
        MAP
      </h2>

      <button
        type="button"
        class="map-action"
        :class="pickMode ? 'map-action-active' : ''"
        :aria-disabled="pickModeDisabled"
        @click="togglePickMode"
      >
        {{ pickMode ? "Cancel" : "Pick destination" }}
      </button>
    </div>

    <div
      v-if="pickMode"
      class="destination-strip"
    >
      <span>Destination</span>
      <strong>X {{ destinationLabel("x") }}</strong>
      <strong>Y {{ destinationLabel("y") }}</strong>
    </div>

    <svg
      ref="svgRef"
      class="microscope-map"
      :class="pickMode ? 'microscope-map-pick' : ''"
      viewBox="0 0 300 300"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Stage map"
      @click="handleMapClick"
      @pointermove="handleMapPointerMove"
      @pointerleave="hoverTarget = null"
    >
        <defs>
          <linearGradient id="stagePlate" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" />
            <stop offset="62%" stop-color="#f1f5f9" />
            <stop offset="100%" stop-color="#e2e8f0" />
          </linearGradient>
          <pattern id="stageGrid" width="18" height="18" patternUnits="userSpaceOnUse">
            <path
              d="M 18 0 L 0 0 0 18"
              fill="none"
              stroke="#d8dee8"
              stroke-width="0.7"
            />
          </pattern>
          <pattern id="stageMajorGrid" width="90" height="90" patternUnits="userSpaceOnUse">
            <path
              d="M 90 0 L 0 0 0 90"
              fill="none"
              stroke="#aab4c4"
              stroke-width="1"
            />
          </pattern>
          <clipPath id="stageClip">
            <rect
              :x="stageLeft"
              :y="stageTop"
              :width="stageWidth"
              :height="stageHeight"
              rx="7"
            />
          </clipPath>
        </defs>

        <g>
          <rect
            :x="stageLeft"
            :y="stageTop"
            :width="stageWidth"
            :height="stageHeight"
            rx="4"
            fill="url(#stagePlate)"
            stroke="#334155"
            stroke-width="1.5"
          />
          <path
            :d="`M ${stageLeft + 2} ${stageBottom - 3} H ${stageRight - 2} M ${stageRight - 3} ${stageTop + 2} V ${stageBottom - 2}`"
            stroke="#0f172a"
            stroke-width="1"
            opacity="0.14"
            fill="none"
          />
        </g>

        <g clip-path="url(#stageClip)">
          <rect
            :x="stageLeft"
            :y="stageTop"
            :width="stageWidth"
            :height="stageHeight"
            fill="url(#stageGrid)"
            opacity="0.85"
          />
          <rect
            :x="stageLeft"
            :y="stageTop"
            :width="stageWidth"
            :height="stageHeight"
            fill="url(#stageMajorGrid)"
            opacity="0.55"
          />
          <line
            :x1="stageLeft"
            :y1="stageTop"
            :x2="stageRight"
            :y2="stageTop"
            stroke="#0f172a"
            stroke-width="2"
            opacity="0.26"
          />
          <line
            :x1="stageRight"
            :y1="stageTop"
            :x2="stageRight"
            :y2="stageBottom"
            stroke="#0f172a"
            stroke-width="2"
            opacity="0.26"
          />
        </g>

        <rect
          :x="stageLeft"
          :y="stageTop"
          :width="stageWidth"
          :height="stageHeight"
          fill="transparent"
          :class="pickMode ? 'stage-pick-zone' : ''"
        />

        <g class="map-labels">
          <text
            :x="stageRight + 6"
            :y="stageBottom - 3"
            text-anchor="start"
            fill="#475569"
          >
            X max
          </text>
          <text
            :x="stageLeft - 8"
            :y="stageTop + 2"
            text-anchor="end"
            fill="#475569"
            :transform="`rotate(-90 ${stageLeft - 8} ${stageTop + 2})`"
          >
            Y max
          </text>
          <text
            :x="stageLeft - 7"
            :y="stageBottom + 6"
            text-anchor="end"
            fill="#64748b"
          >
            0
          </text>
        </g>

        <g v-if="pickMode && hoverTarget" :transform="`translate(${hoverMarkerX}, ${hoverMarkerY})`">
          <line
            :x1="stageLeft - hoverMarkerX"
            y1="0"
            :x2="stageRight - hoverMarkerX"
            y2="0"
            stroke="#0f172a"
            stroke-width="1.2"
            opacity="0.58"
          />
          <line
            x1="0"
            :y1="stageTop - hoverMarkerY"
            x2="0"
            :y2="stageBottom - hoverMarkerY"
            stroke="#0f172a"
            stroke-width="1.2"
            opacity="0.58"
          />
        </g>

        <g
          class="stage-marker"
          :class="isMoving ? 'stage-marker-moving' : ''"
          :transform="`translate(${markerX}, ${markerY})`"
        >
          <line
            :x1="stageLeft - markerX"
            y1="0"
            :x2="stageRight - markerX"
            y2="0"
            stroke="#334155"
            stroke-width="1"
            stroke-dasharray="3 4"
            opacity="0.32"
          />
          <line
            x1="0"
            :y1="stageTop - markerY"
            x2="0"
            :y2="stageBottom - markerY"
            stroke="#334155"
            stroke-width="1"
            stroke-dasharray="3 4"
            opacity="0.32"
          />
          <rect
            class="stage-marker-ping"
            x="-9"
            y="-9"
            width="18"
            height="18"
            rx="2"
            fill="none"
            stroke="#2563eb"
            stroke-width="1.4"
          />
          <rect
            class="stage-marker-core"
            x="-7"
            y="-7"
            width="14"
            height="14"
            rx="2"
            fill="#0f172a"
          />
          <path
            class="stage-marker-crosshair"
            d="M -13 0 H -8 M 8 0 H 13 M 0 -13 V -8 M 0 8 V 13"
            stroke="#0f172a"
            stroke-width="1.4"
            stroke-linecap="round"
          />
          <circle
            v-if="isMoving"
            class="stage-marker-ring"
            r="15"
            fill="none"
            stroke="#2563eb"
            stroke-width="1.8"
            opacity="0.55"
          />
        </g>

        <g v-if="lastPickedTarget" :transform="`translate(${targetMarkerX}, ${targetMarkerY})`">
          <rect x="-9" y="-9" width="18" height="18" fill="none" stroke="#2563eb" stroke-width="1.8" stroke-dasharray="3 3" />
          <circle r="2.5" fill="#2563eb" />
        </g>

        <g>
          <text
            :x="mapWidth / 2"
            :y="stageBottom + 12.5"
            text-anchor="middle"
            fill="#475569"
            font-size="8"
            font-weight="900"
          >
            LID SIDE / FRONT
          </text>
        </g>
    </svg>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { useStage } from "@/composables/useStage";
import { STAGE_AXIS_MAX } from "@/config/stage";

defineProps<{
  compact?: boolean;
}>();

const store = useMicroscopeStore();
const stage = useStage();
const svgRef = ref<SVGSVGElement | null>(null);
const pickMode = ref(false);
const lastPickedTarget = ref<{ x: number; y: number } | null>(null);
const hoverTarget = ref<{ x: number; y: number } | null>(null);

const maxX = STAGE_AXIS_MAX.x;
const maxY = STAGE_AXIS_MAX.y;
const targetSnapSteps = 25;
const targetArrivalTolerance = 35;

const mapWidth = 300;
const stageTop = 8;
const stageHeight = 270;
const stageWidth = stageHeight * (maxX / maxY);
const stageLeft = (mapWidth - stageWidth) / 2;
const stageRight = stageLeft + stageWidth;
const stageBottom = stageTop + stageHeight;

const currentX = computed(() => store.position.x);
const currentY = computed(() => store.position.y);
const isMoving = computed(() => store.position.is_moving);
const isClosetOpen = computed(() => store.closetStatus === "open");
const stageReady = computed(
  () =>
    !!store.limitSensors?.x.homed &&
    !!store.limitSensors?.y.homed &&
    !!store.limitSensors?.z.homed,
);
const pickModeDisabled = computed(
  () => isMoving.value || stage.isMoving.value || isClosetOpen.value || !stageReady.value,
);

const markerX = computed(() => positionToMapX(currentX.value));
const markerY = computed(() => positionToMapY(currentY.value));

const targetMarkerX = computed(() => {
  if (!lastPickedTarget.value) return markerX.value;
  return positionToMapX(lastPickedTarget.value.x);
});
const targetMarkerY = computed(() => {
  if (!lastPickedTarget.value) return markerY.value;
  return positionToMapY(lastPickedTarget.value.y);
});
const hoverMarkerX = computed(() => {
  if (!hoverTarget.value) return markerX.value;
  return positionToMapX(hoverTarget.value.x);
});
const hoverMarkerY = computed(() => {
  if (!hoverTarget.value) return markerY.value;
  return positionToMapY(hoverTarget.value.y);
});

function positionToMapX(position: number) {
  const normalizedX = Math.min(Math.max(position / maxX, 0), 1);
  return stageRight - normalizedX * stageWidth;
}

function positionToMapY(position: number) {
  const normalizedY = Math.min(Math.max(position / maxY, 0), 1);
  return stageBottom - normalizedY * stageHeight;
}

function togglePickMode() {
  if (pickModeDisabled.value) {
    logPickModeBlocked();
    return;
  }

  pickMode.value = !pickMode.value;
  hoverTarget.value = null;
}

function logPickModeBlocked() {
  if (isClosetOpen.value) {
    store.addLog("Map move blocked: lid is open", "warning");
    return;
  }

  if (!stageReady.value) {
    store.addLog("Home stage before using map move", "warning");
    return;
  }

  if (isMoving.value || stage.isMoving.value) {
    store.addLog("Map move blocked while stage is moving", "warning");
  }
}

async function handleMapClick(event: MouseEvent) {
  if (!pickMode.value) return;

  if (pickModeDisabled.value) {
    logPickModeBlocked();
    return;
  }

  const point = getSvgPoint(event);
  if (!point) return;

  const target = pointToStageTarget(point);
  if (!target) {
    store.addLog("Map move blocked: choose a point inside the stage area", "warning");
    return;
  }

  lastPickedTarget.value = target;
  pickMode.value = false;
  hoverTarget.value = null;

  store.addLog(`Map move target: X ${target.x}, Y ${target.y}`, "info");
  await stage.move(target.x, target.y, undefined, false);
  void clearTargetWhenArrived(target);
}

function handleMapPointerMove(event: PointerEvent) {
  if (!pickMode.value) return;

  const point = getSvgPoint(event);
  hoverTarget.value = point ? pointToStageTarget(point) : null;
}

function pointToStageTarget(point: DOMPoint) {
  const insideStage =
    point.x >= stageLeft &&
    point.x <= stageRight &&
    point.y >= stageTop &&
    point.y <= stageBottom;

  if (!insideStage) {
    return null;
  }

  return {
    x: snapToSteps(((stageRight - point.x) / stageWidth) * maxX, maxX),
    y: snapToSteps(((stageBottom - point.y) / stageHeight) * maxY, maxY),
  };
}

function snapToSteps(position: number, axisMax: number) {
  const snapped = Math.round(position / targetSnapSteps) * targetSnapSteps;
  return Math.min(Math.max(snapped, 0), axisMax);
}

function destinationLabel(axis: "x" | "y") {
  if (!hoverTarget.value) {
    return "--";
  }

  return hoverTarget.value[axis].toFixed(0);
}

function getSvgPoint(event: MouseEvent) {
  const svg = svgRef.value;
  const matrix = svg?.getScreenCTM();

  if (!svg || !matrix) {
    return null;
  }

  const point = svg.createSVGPoint();
  point.x = event.clientX;
  point.y = event.clientY;
  return point.matrixTransform(matrix.inverse());
}

async function clearTargetWhenArrived(target: { x: number; y: number }) {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    await wait(350);
    await stage.updatePosition();

    if (
      Math.abs(store.position.x - target.x) <= targetArrivalTolerance &&
      Math.abs(store.position.y - target.y) <= targetArrivalTolerance &&
      !store.position.is_moving
    ) {
      if (
        lastPickedTarget.value?.x === target.x &&
        lastPickedTarget.value?.y === target.y
      ) {
        lastPickedTarget.value = null;
      }
      return;
    }
  }
}

function wait(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}
</script>

<style scoped>
.map-panel {
  background: #ffffff;
}

.microscope-map {
  @apply block h-auto w-full border rounded border-slate-200 bg-transparent;
}

.microscope-map-pick,
.stage-pick-zone {
  @apply cursor-crosshair;
}

.map-action {
  @apply flex min-h-[30px] items-center justify-center rounded-md border border-slate-300 bg-white px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-slate-700 shadow-sm transition-all hover:-translate-y-0.5 hover:border-slate-500 hover:bg-slate-50 hover:text-slate-950 hover:shadow-md active:translate-y-0;
}

.map-action[aria-disabled="true"] {
  @apply cursor-not-allowed opacity-50;
}

.map-action-active {
  @apply border-slate-800 bg-slate-800 text-white shadow-slate-300/50 hover:border-slate-800 hover:bg-slate-700 hover:text-white;
}

.stage-marker {
  pointer-events: none;
}

.stage-marker-core,
.stage-marker-crosshair,
.stage-marker-ring,
.stage-marker-ping {
  transform-box: fill-box;
  transform-origin: center;
}

.stage-marker-moving .stage-marker-core {
  animation: marker-core-breathe 1.15s ease-in-out infinite;
}

.stage-marker-moving .stage-marker-ring {
  animation: marker-ring-breathe 1.15s ease-in-out infinite;
}

.stage-marker-ping {
  animation: marker-square-ping 1.8s ease-out infinite;
  opacity: 0.22;
}

.map-labels {
  pointer-events: none;
  font-size: 7.5px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
  opacity: 0.62;
}

.destination-strip {
  @apply mb-1.5 flex items-center gap-2 rounded border border-slate-300 bg-slate-50 px-2 py-1 font-mono text-xs text-slate-900;
}

.destination-strip span {
  @apply mr-auto font-sans text-[9px] font-black uppercase tracking-wide text-slate-500;
}

.destination-strip strong {
  @apply font-mono text-xs font-semibold;
}

@keyframes marker-core-breathe {
  0%,
  100% {
    opacity: 0.94;
  }
  50% {
    opacity: 1;
  }
}

@keyframes marker-ring-breathe {
  0%,
  100% {
    opacity: 0.32;
  }
  50% {
    opacity: 0.58;
  }
}

@keyframes marker-square-ping {
  0% {
    transform: scale(0.82);
    opacity: 0.22;
  }
  62% {
    opacity: 0.12;
  }
  100% {
    transform: scale(1.9);
    opacity: 0;
  }
}

</style>
