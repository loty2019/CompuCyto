<template>
  <div class="stage-panel overflow-hidden rounded-lg border border-slate-200/80 bg-white p-2 shadow-md">
    <div class="mb-1.5 flex items-center justify-between gap-2">
      <h2 class="text-sm font-black uppercase tracking-wide text-slate-950">Stage</h2>
      <span class="rounded-full border border-slate-300 bg-slate-50 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-slate-600">
        Relative
      </span>
    </div>

    <div
      v-if="isClosetOpen"
      class="mb-1.5 rounded-md border border-red-300 bg-red-50 px-2 py-1 text-[10px] font-black uppercase tracking-wide text-red-700"
    >
      Lid open - stage locked
    </div>

    <div class="mb-1.5 grid grid-cols-3 gap-1 rounded-md border border-slate-200 bg-slate-50 p-1 shadow-inner">
      <div class="position-chip">
        <span class="position-axis">X</span>
        <span class="position-value">{{ store.position.x.toFixed(1) }}</span>
      </div>
      <div class="position-chip">
        <span class="position-axis">Y</span>
        <span class="position-value">{{ store.position.y.toFixed(1) }}</span>
      </div>
      <div class="position-chip">
        <span class="position-axis">Z</span>
        <span class="position-value">{{ store.position.z.toFixed(1) }}</span>
      </div>
    </div>

    <div class="rounded-lg border border-slate-200 bg-slate-50 p-1.5">
      <div class="mb-1.5">
        <div class="mb-1 flex items-center justify-between gap-2">
          <span class="section-label">XY Speed</span>
          <span class="text-[10px] font-bold text-slate-500">{{ xyMultiplier }}x</span>
        </div>
        <div class="multiplier-grid">
          <button
            v-for="option in xyMultipliers"
            :key="`xy-${option}`"
            @click="xyMultiplier = option"
            class="multiplier-button"
            :class="xyMultiplier === option ? 'multiplier-button-active' : ''"
            type="button"
          >
            {{ option }}x
          </button>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-1.5">
        <div></div>
        <button
          @click="
            handleButtonClick('arrowup');
            moveAxis('x', 1);
          "
          :disabled="movementDisabled"
          class="stage-button stage-button-primary"
          :class="movementDisabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'"
          :style="getButtonStyle('arrowup')"
          title="Move up"
        >
          <span class="stage-button-symbol">&uarr;</span>
        </button>
        <div></div>

        <button
          @click="
            handleButtonClick('arrowleft');
            moveAxis('y', -1);
          "
          :disabled="movementDisabled"
          class="stage-button stage-button-primary"
          :class="movementDisabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'"
          :style="getButtonStyle('arrowleft')"
          title="Move left"
        >
          <span class="stage-button-symbol">&larr;</span>
        </button>
        <button
          @click="
            handleButtonClick('home');
            homeStage();
          "
          :disabled="movementDisabled"
          class="stage-button stage-button-home"
          :class="movementDisabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'"
          :style="getButtonStyle('home')"
        >
          <span>Home</span>
        </button>
        <button
          @click="
            handleButtonClick('arrowright');
            moveAxis('y', 1);
          "
          :disabled="movementDisabled"
          class="stage-button stage-button-primary"
          :class="movementDisabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'"
          :style="getButtonStyle('arrowright')"
          title="Move right"
        >
          <span class="stage-button-symbol">&rarr;</span>
        </button>

        <div></div>
        <button
          @click="
            handleButtonClick('arrowdown');
            moveAxis('x', -1);
          "
          :disabled="movementDisabled"
          class="stage-button stage-button-primary outline-none"
          :class="movementDisabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'"
          :style="getButtonStyle('arrowdown')"
          title="Move down"
        >
          <span class="stage-button-symbol">&darr;</span>
        </button>
        <div></div>
      </div>
    </div>

    <div class="mt-1.5">
      <button
        @click="stage.stop()"
        class="stage-button w-full cursor-pointer bg-red-600 text-white shadow-md shadow-red-300/40 hover:bg-red-700"
        :style="getButtonStyle('stop')"
        title="Emergency Stop"
      >
        STOP
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { useStage } from "@/composables/useStage";

const store = useMicroscopeStore();
const stage = useStage();

const baseXYStep = 100;
const xyMultipliers = [0.1, 0.5, 1, 2, 5, 10];
const xyMultiplier = ref(1);
const pressedKeys = ref<Set<string>>(new Set());
const clickedButtons = ref<Set<string>>(new Set());
const isClosetOpen = computed(() => store.closetStatus === "open");
const movementDisabled = computed(
  () => stage.isMoving.value || isClosetOpen.value,
);

let intervalId: number | null = null;

onMounted(() => {
  intervalId = window.setInterval(stage.updatePosition, 2000);
  stage.updatePosition();

  window.addEventListener("keydown", handleKeyDown);
  window.addEventListener("keyup", handleKeyUp);
});

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);

  window.removeEventListener("keydown", handleKeyDown);
  window.removeEventListener("keyup", handleKeyUp);
});

async function move(x: number, y: number, z: number) {
  if (isClosetOpen.value) {
    store.addLog("Stage movement blocked: lid is open", "warning");
    return;
  }

  await stage.move(x, y, z, true);
  setTimeout(stage.updatePosition, 500);
}

async function homeStage() {
  if (isClosetOpen.value) {
    store.addLog("Stage home blocked: lid is open", "warning");
    return;
  }

  await stage.home();
}

function moveAxis(axis: "x" | "y", direction: 1 | -1) {
  const steps = Math.round(baseXYStep * xyMultiplier.value) * direction;
  if (axis === "x") {
    move(steps, 0, 0);
  } else {
    move(0, steps, 0);
  }
}

function handleKeyDown(event: KeyboardEvent) {
  const target = event.target as HTMLElement;
  if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") {
    return;
  }

  const key = event.key.toLowerCase();

  if (["arrowup", "arrowdown", "arrowleft", "arrowright"].includes(key)) {
    event.preventDefault();
  }

  if (pressedKeys.value.has(key)) {
    return;
  }

  pressedKeys.value.add(key);

  if (movementDisabled.value) {
    return;
  }

  switch (key) {
    case "arrowup":
      moveAxis("x", 1);
      break;
    case "arrowdown":
      moveAxis("x", -1);
      break;
    case "arrowleft":
      moveAxis("y", -1);
      break;
    case "arrowright":
      moveAxis("y", 1);
      break;
  }
}

function handleKeyUp(event: KeyboardEvent) {
  const key = event.key.toLowerCase();
  pressedKeys.value.delete(key);
}

function isKeyPressed(key: string): boolean {
  return pressedKeys.value.has(key);
}

function handleButtonClick(buttonId: string) {
  clickedButtons.value.add(buttonId);
  setTimeout(() => {
    clickedButtons.value.delete(buttonId);
  }, 150);
}

function getButtonStyle(buttonId: string): string {
  const isClicked = clickedButtons.value.has(buttonId);
  const isPressed = isKeyPressed(buttonId);

  if (isClicked || isPressed) {
    return "filter: brightness(0.82); transform: scale(0.96); transition: all 0.05s ease;";
  }
  return "transition: all 0.05s ease;";
}
</script>

<style scoped>
.stage-panel {
  background:
    radial-gradient(circle at top left, rgba(148, 163, 184, 0.16), transparent 34%),
    linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.position-chip {
  @apply flex flex-col rounded border border-slate-200 bg-white px-1.5 py-0.5 shadow-sm;
}

.position-axis {
  @apply text-[9px] font-bold uppercase tracking-wide text-slate-500;
}

.position-value {
  @apply font-mono text-xs font-semibold tracking-tight text-slate-900;
}

.section-label {
  @apply text-[10px] font-bold uppercase tracking-wide text-slate-500;
}

.stage-button {
  @apply flex min-h-[34px] items-center justify-center gap-1 rounded-md px-1.5 py-1 text-[11px] font-bold shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md active:translate-y-0;
}

.stage-button-primary {
  @apply border border-slate-700 bg-slate-800 text-white shadow-slate-300/50 hover:bg-slate-700;
}

.stage-button-home {
  @apply border border-blue-700 bg-blue-700 text-white shadow-blue-300/40 hover:bg-blue-800;
}

.stage-button-symbol {
  @apply text-lg leading-none;
}

.multiplier-button {
  @apply h-7 rounded border border-slate-300 bg-white px-1.5 text-[10px] font-bold text-slate-600 transition-colors hover:border-slate-500 hover:text-slate-900;
}

.multiplier-button-active {
  @apply border-slate-800 bg-slate-800 text-white hover:border-slate-800 hover:text-white;
}

.multiplier-grid {
  @apply grid grid-cols-3 gap-1;
}
</style>
