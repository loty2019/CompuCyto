<template>
  <div
    class="stage-panel overflow-hidden rounded-lg border border-slate-200/80 bg-white p-2 shadow-md"
  >
    <div class="mb-1.5 flex items-center justify-between gap-2">
      <h2 class="text-sm font-black uppercase tracking-wide text-slate-950">
        Stage
      </h2>
      <span
        class="rounded-full border border-slate-300 bg-slate-50 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-slate-600"
      >
        Relative
      </span>
    </div>

    <div
      v-if="isClosetOpen"
      class="mb-1.5 rounded-md border border-red-300 bg-red-50 px-2 py-1 text-[10px] font-black uppercase tracking-wide text-red-700"
    >
      Lid open - stage locked
    </div>

    <div
      v-if="!stageReady"
      class="mb-1.5 rounded-md border border-amber-300 bg-amber-50 px-2 py-1 text-[10px] font-black uppercase tracking-wide text-amber-700"
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

    <div
      class="mb-1.5 grid grid-cols-2 gap-1 rounded-md border border-slate-200 bg-slate-50 p-1 shadow-inner"
    >
      <div class="position-chip">
        <span class="position-axis">X</span>
        <span class="position-value">{{ store.position.x.toFixed(1) }}</span>
      </div>
      <div class="position-chip">
        <span class="position-axis">Y</span>
        <span class="position-value">{{ store.position.y.toFixed(1) }}</span>
      </div>
    </div>

    <div class="rounded-lg border border-slate-200 bg-slate-50 p-1.5">
      <div class="mb-1.5">
        <div class="mb-1 flex items-center justify-between gap-2">
          <span class="section-label">Jog</span>
          <span class="text-[10px] font-bold text-slate-500"
            >{{ activeJogProfile.steps }} steps</span
          >
        </div>
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
          @click="
            handleButtonClick('arrowup');
            moveAxis('y', 1);
          "
          :disabled="movementButtonDisabled('y', 1)"
          class="stage-button stage-button-primary"
          :class="
            movementButtonDisabled('y', 1)
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
          @click="
            handleButtonClick('arrowleft');
            moveAxis('x', 1);
          "
          :disabled="movementButtonDisabled('x', 1)"
          class="stage-button stage-button-primary"
          :class="
            movementButtonDisabled('x', 1)
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
          class="stage-button stage-button-home"
          :class="
            homeDisabled
              ? 'cursor-not-allowed opacity-60'
              : 'cursor-pointer'
          "
          :style="getButtonStyle('home')"
        >
          <span>{{ homingInProgress ? "Homing" : "Home" }}</span>
        </button>
        <button
          @click="
            handleButtonClick('arrowright');
            moveAxis('x', -1);
          "
          :disabled="movementButtonDisabled('x', -1)"
          class="stage-button stage-button-primary"
          :class="
            movementButtonDisabled('x', -1)
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
          @click="
            handleButtonClick('arrowdown');
            moveAxis('y', -1);
          "
          :disabled="movementButtonDisabled('y', -1)"
          class="stage-button stage-button-primary outline-none"
          :class="
            movementButtonDisabled('y', -1)
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

const jogProfiles = [
  { id: "fine", label: "Fine", steps: 25 },
  { id: "small", label: "Small", steps: 100 },
  { id: "medium", label: "Med", steps: 500 },
  { id: "large", label: "Large", steps: 2000 },
  { id: "travel", label: "Travel", steps: 5000 },
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
    store.addLog("Homing stage X, Y, then Z...", "info");
    await stage.home();
    await stage.updatePosition();
    await stage.updateLimitSensors();
    store.addLog("Homing successful: X, Y, and Z are at 0", "success");
  } finally {
    homingInProgress.value = false;
  }
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
  if (movementButtonDisabled(axis, direction)) {
    return;
  }

  const steps = activeJogProfile.value.steps * direction;
  if (axis === "x") {
    move(steps, 0);
  } else {
    move(0, steps);
  }
}

function movementButtonDisabled(axis: "x" | "y", direction: 1 | -1) {
  if (xyMovementDisabled.value) {
    return true;
  }

  const currentPosition = axis === "x" ? store.position.x : store.position.y;
  const requestedSteps = activeJogProfile.value.steps * direction;
  return currentPosition + requestedSteps < 0;
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
  background:
    radial-gradient(
      circle at top left,
      rgba(148, 163, 184, 0.16),
      transparent 34%
    ),
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
  @apply flex min-h-[34px] items-center justify-center gap-1 rounded-md px-1.5 py-1 text-[11px] font-bold shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md active:translate-y-0;
}

.stage-button-primary {
  @apply border border-slate-700 bg-slate-800 text-white shadow-slate-300/50 hover:bg-slate-700;
}

.stage-button-home {
  @apply border border-blue-700 bg-blue-700 text-white shadow-blue-300/40 hover:bg-blue-800;
}

.stage-button-secondary {
  @apply border border-slate-300 bg-white text-slate-700 shadow-slate-200/60 hover:border-slate-500 hover:text-slate-950;
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
