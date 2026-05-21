<template>
  <div class="stage-panel lab-panel-dense overflow-hidden">
    <div class="lab-panel-header mb-1.5">
      <h2 class="lab-title">
        Stage
      </h2>
      
    </div>

    <div
      v-if="isClosetOpen"
      class="lab-alert lab-alert-danger mb-1.5 px-2 py-1 text-[10px] uppercase tracking-wide"
    >
      Lid open - stage locked
    </div>

    <div
      v-if="!stageReady"
      class="lab-alert lab-alert-warning mb-1.5 px-2 py-1 text-[10px] uppercase tracking-wide"
    >
      Home required before movement
    </div>
    <div class="mb-1.5 grid grid-cols-3 gap-1">
      <div
        v-for="axis in homeAxes"
        :key="axis"
        class="home-chip"
        :class="homeChipClass(axis)"
      >
        <span>{{ axis.toUpperCase() }}</span>
        <span>{{ homeChipLabel(axis) }}</span>
      </div>
    </div>

    <div class="mb-2 mt-3 grid grid-cols-2 gap-1.5 border-t border-slate-200 pt-3 pb-1.5">
      <div class="position-chip">
        <span class="position-axis">X</span>
        <span class="position-reading">
          <span class="position-value">{{ store.position.x.toFixed(1) }}</span>
          <span class="position-limit">/ {{ STAGE_AXIS_MAX.x.toFixed(1) }}</span>
        </span>
      </div>
      <div class="position-chip">
        <span class="position-axis">Y</span>
        <span class="position-reading">
          <span class="position-value">{{ store.position.y.toFixed(1) }}</span>
          <span class="position-limit">/ {{ STAGE_AXIS_MAX.y.toFixed(1) }}</span>
        </span>
      </div>
    </div>

    <div class="mt-2 border-t border-slate-200 pt-3">
      <div class="mb-3">
        <div class="multiplier-grid">
          <button
            v-for="profile in jogProfiles"
            :key="profile.id"
            @click="selectedJogProfileId = profile.id"
            class="multiplier-button"
            :class="
              selectedJogProfileId === profile.id
                ? 'multiplier-button-active'
                : ''
            "
            type="button"
          >
            {{ profile.label }}
          </button>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-1.5">
        <div></div>
        <button
          @pointerdown.prevent="pressMoveButton('arrowup', 'y', 1)"
          :aria-disabled="!!movementBlockedReason('y', 1)"
          class="stage-button stage-button-primary"
          :class="
            movementBlockedReason('y', 1)
              ? 'cursor-not-allowed opacity-60'
              : 'cursor-pointer'
          "
          :style="getButtonStyle('arrowup')"
          title="Move up"
        >
          <span class="stage-button-symbol">&uarr;</span>
        </button>
        <div></div>

        <button
          @pointerdown.prevent="pressMoveButton('arrowleft', 'x', 1)"
          :aria-disabled="!!movementBlockedReason('x', 1)"
          class="stage-button stage-button-primary"
          :class="
            movementBlockedReason('x', 1)
              ? 'cursor-not-allowed opacity-60'
              : 'cursor-pointer'
          "
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
          :disabled="homeDisabled"
          class="stage-button stage-button-secondary"
          :class="[
            !stageReady ? 'stage-button-home-required' : '',
            homeDisabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer',
          ]"
          :style="getButtonStyle('home')"
        >
          <span>{{ homingInProgress ? "Homing" : "Home" }}</span>
        </button>
        <button
          @pointerdown.prevent="pressMoveButton('arrowright', 'x', -1)"
          :aria-disabled="!!movementBlockedReason('x', -1)"
          class="stage-button stage-button-primary"
          :class="
            movementBlockedReason('x', -1)
              ? 'cursor-not-allowed opacity-60'
              : 'cursor-pointer'
          "
          :style="getButtonStyle('arrowright')"
          title="Move right"
        >
          <span class="stage-button-symbol">&rarr;</span>
        </button>

        <div></div>
        <button
          @pointerdown.prevent="pressMoveButton('arrowdown', 'y', -1)"
          :aria-disabled="!!movementBlockedReason('y', -1)"
          class="stage-button stage-button-primary outline-none"
          :class="
            movementBlockedReason('y', -1)
              ? 'cursor-not-allowed opacity-60'
              : 'cursor-pointer'
          "
          :style="getButtonStyle('arrowdown')"
          title="Move down"
        >
          <span class="stage-button-symbol">&darr;</span>
        </button>
        <div></div>
      </div>
    </div>

    <div class="mt-3 border-t border-slate-200 pt-3">
      <button
        @click="stopStage"
        class="stage-button w-full cursor-pointer bg-red-600 text-white hover:bg-red-700"
        :style="getButtonStyle('stop')"
        title="Emergency Stop"
      >
        STOP
      </button>
    </div>

    <div
      v-if="showStopResetPopup"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="stop-reset-title"
    >
      <div class="w-full max-w-sm rounded-lg border border-amber-200 bg-white p-4 shadow-xl">
        <div class="mb-3 flex items-start justify-between gap-3">
          <div>
            <h3
              id="stop-reset-title"
              class="text-sm font-black uppercase tracking-wide text-slate-900"
            >
              Stage stopped
            </h3>
            <p class="mt-1 text-xs leading-5 text-slate-600">
              The PSU is off. Reset the stage before moving again.
            </p>
          </div>
          <button
            type="button"
            class="rounded px-2 py-1 text-sm font-bold text-slate-500 hover:bg-slate-100 hover:text-slate-900"
            aria-label="Close reset instructions"
            @click="showStopResetPopup = false"
          >
            x
          </button>
        </div>

        <ol class="space-y-2 text-xs leading-5 text-slate-700">
          <li>1. Clear the stage area and close the lid if it is open.</li>
          <li>2. Press Home to turn the PSU back on and re-home X, Y, and Z.</li>
          <li>3. Wait until all home chips show Homed before jogging.</li>
        </ol>

        <div class="mt-4 flex justify-end gap-2">
          <button
            type="button"
            class="stage-button stage-button-secondary min-w-20"
            @click="showStopResetPopup = false"
          >
            OK
          </button>
          <button
            type="button"
            class="stage-button min-w-20 bg-slate-900 text-white hover:bg-slate-700"
            :disabled="homeDisabled"
            :class="homeDisabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'"
            @click="homeFromStopPopup"
          >
            Home
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { useStage } from "@/composables/useStage";
import { STAGE_AXIS_MAX } from "@/config/stage";

const store = useMicroscopeStore();
const stage = useStage();

const jogProfiles = [
  { id: "finer", label: "Finer", steps: 25 },
  { id: "fine", label: "Fine", steps: 100 },
  { id: "medium", label: "Medium", steps: 500 },
  { id: "bigger", label: "Bigger", steps: 2000 },
] as const;
const selectedJogProfileId = ref<(typeof jogProfiles)[number]["id"]>("medium");
const activeJogProfile = computed(
  () =>
    jogProfiles.find((profile) => profile.id === selectedJogProfileId.value) ??
    jogProfiles[2],
);
const pressedKeys = ref<Set<string>>(new Set());
const clickedButtons = ref<Set<string>>(new Set());
const homingInProgress = ref(false);
const showStopResetPopup = ref(false);
const isClosetOpen = computed(() => store.closetStatus === "open");
const stageReady = computed(
  () =>
    !!store.limitSensors?.x.homed &&
    !!store.limitSensors?.y.homed &&
    !!store.limitSensors?.z.homed,
);
const homeDisabled = computed(
  () =>
    homingInProgress.value ||
    stage.isMoving.value ||
    store.position.is_moving ||
    isClosetOpen.value,
);
const xyMovementDisabled = computed(() => homeDisabled.value || !stageReady.value);
const homeAxes = ["x", "y", "z"] as const;

let intervalId: number | null = null;

onMounted(() => {
  intervalId = window.setInterval(stage.updatePosition, 2000);
  stage.updatePosition();
  stage.updateLimitSensors();

  window.addEventListener("keydown", handleKeyDown);
  window.addEventListener("keyup", handleKeyUp);
});

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);

  window.removeEventListener("keydown", handleKeyDown);
  window.removeEventListener("keyup", handleKeyUp);
});

async function move(x: number, y: number) {
  if (isClosetOpen.value) {
    store.addLog("Stage movement blocked: lid is open", "warning");
    return;
  }

  if (!stageReady.value) {
    store.addLog("Home stage before movement", "warning");
    return;
  }

  await stage.move(x, y, undefined, true);
  setTimeout(stage.updatePosition, 500);
}

async function homeStage() {
  if (isClosetOpen.value) {
    store.addLog("Stage home blocked: lid is open", "warning");
    return;
  }

  homingInProgress.value = true;
  try {
    store.addLog("Homing stage X, Y, then Z; parking Z near focus...", "info");
    await stage.home();
    await stage.updatePosition();
    await stage.updateLimitSensors();
    store.addLog("Homing successful: X/Y are at 0 and Z is near focus", "success");
  } finally {
    homingInProgress.value = false;
  }
}

async function stopStage() {
  handleButtonClick("stop");
  await stage.stop();
  await stage.updatePosition();
  await stage.updateLimitSensors();
  showStopResetPopup.value = true;
}

async function homeFromStopPopup() {
  await homeStage();
  showStopResetPopup.value = false;
}

function homeChipLabel(axis: "x" | "y" | "z") {
  if (homingInProgress.value && !store.limitSensors?.[axis]?.homed) {
    return "Wait";
  }

  return store.limitSensors?.[axis]?.homed ? "Homed" : "Needed";
}

function homeChipClass(axis: "x" | "y" | "z") {
  if (store.limitSensors?.[axis]?.homed) {
    return "home-chip-ready";
  }

  if (homingInProgress.value) {
    return "home-chip-busy";
  }

  return "home-chip-needed";
}

function moveAxis(axis: "x" | "y", direction: 1 | -1) {
  const blockedReason = movementBlockedReason(axis, direction);
  if (blockedReason) {
    store.addLog(blockedReason, "warning");
    return;
  }

  const steps = activeJogProfile.value.steps * direction;
  if (axis === "x") {
    move(steps, 0);
  } else {
    move(0, steps);
  }
}

function pressMoveButton(buttonId: string, axis: "x" | "y", direction: 1 | -1) {
  handleButtonClick(buttonId);
  moveAxis(axis, direction);
}

function movementBlockedReason(axis: "x" | "y", direction: 1 | -1) {
  if (xyMovementDisabled.value) {
    if (isClosetOpen.value) return "Stage movement blocked: lid is open";
    if (!stageReady.value) return "Home stage before movement";
    return "Stage movement blocked while homing or moving";
  }

  const currentPosition = axis === "x" ? store.position.x : store.position.y;
  const requestedSteps = activeJogProfile.value.steps * direction;
  const targetPosition = currentPosition + requestedSteps;
  const axisLabel = axis.toUpperCase();
  const axisMax = STAGE_AXIS_MAX[axis];

  if (targetPosition < 0) {
    return `${axisLabel} move blocked: target ${targetPosition.toFixed(0)} is below minimum 0`;
  }

  if (targetPosition > axisMax) {
    return `${axisLabel} move blocked: target ${targetPosition.toFixed(0)} exceeds maximum ${axisMax}`;
  }

  return "";
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

  if (xyMovementDisabled.value) {
    return;
  }

  switch (key) {
    case "arrowup":
      moveAxis("y", 1);
      break;
    case "arrowdown":
      moveAxis("y", -1);
      break;
    case "arrowleft":
      moveAxis("x", 1);
      break;
    case "arrowright":
      moveAxis("x", -1);
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
  background: #ffffff;
}

.position-chip {
  @apply flex flex-col rounded-md border border-slate-200/70 bg-slate-50/80 px-2 py-1 shadow-[inset_0_1px_0_rgba(255,255,255,0.8)];
}

.position-axis {
  @apply text-[9px] font-bold uppercase tracking-wide text-slate-500;
}

.position-reading {
  @apply flex items-baseline gap-1 whitespace-nowrap font-mono;
}

.position-value {
  @apply text-xs font-semibold tracking-tight text-slate-900;
}

.position-limit {
  @apply text-[10px] font-medium tracking-tight text-slate-400;
}

.home-chip {
  @apply flex h-6 items-center justify-between rounded border px-1.5 text-[9px] font-black uppercase tracking-wide;
}

.home-chip-ready {
  @apply border-teal-300 bg-teal-50 text-teal-700;
}

.home-chip-needed {
  @apply border-amber-300 bg-amber-50 text-amber-700;
}

.home-chip-busy {
  @apply border-blue-300 bg-blue-50 text-blue-700;
  animation: home-chip-pulse 0.85s ease-in-out infinite;
}

.stage-button {
  @apply flex min-h-[34px] items-center justify-center gap-1 rounded-md px-1.5 py-1 text-[11px] font-bold transition-all hover:-translate-y-0.5 active:translate-y-0;
}

.stage-button-primary {
  @apply border border-slate-800 bg-slate-900 text-white hover:bg-slate-700;
}

.stage-button-secondary {
  @apply border border-slate-300 bg-white text-slate-700 hover:border-slate-500 hover:bg-slate-50 hover:text-slate-950;
}

.stage-button-home-required {
  @apply border-slate-800 bg-slate-900 text-white hover:border-slate-800 hover:bg-slate-700 hover:text-white;
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
  @apply grid grid-cols-4 gap-1;
}

@keyframes home-chip-pulse {
  0%,
  100% {
    opacity: 0.72;
  }
  50% {
    opacity: 1;
  }
}
</style>
