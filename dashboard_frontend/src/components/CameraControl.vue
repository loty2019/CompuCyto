<template>
  <div class="camera-panel flex h-full flex-col rounded-lg border border-slate-200/80 bg-white p-2.5 shadow-md">
    <div class="mb-2 flex flex-wrap items-center justify-between gap-2">
      <div class="flex items-center gap-2">
        <h2 class="text-sm font-black uppercase tracking-wide text-slate-950">
          CAMERA
        </h2>
        <span
          class="rounded-full border border-slate-300 bg-slate-50 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-slate-600"
        >
          Live
        </span>
      </div>
      <div class="flex items-center gap-2">
          <span
            v-if="feedUrl && !feedError && lightWarning"
            class="flex items-center gap-1 rounded border border-amber-300 bg-amber-50 px-2 py-1 text-xs font-semibold text-amber-700"
            title="The microscope light is currently off"
          >
            ⚠️ Light is OFF
          </span>
        </div>
        <button
          v-if="feedUrl && !feedError"
          @click="stopFeed"
          class="rounded-md border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-bold text-red-700 shadow-sm transition-all hover:bg-red-100 hover:shadow"
        >
          Stop Feed
        </button>
      </div>
    <!-- Live Camera Feed Section -->
    <div class="mt-2 min-h-0 flex-1">
      <div class="grid h-full items-start gap-2 xl:grid-cols-[minmax(0,1fr)_260px]">
        <div
          class="relative flex items-center justify-center overflow-hidden rounded-md border border-slate-300 bg-slate-100 shadow-inner"
          style="aspect-ratio: 4/3; min-height: 245px"
        >
        <div
          v-if="isLoadingFeed"
          class="flex h-full w-full flex-col items-center justify-center gap-3 p-8 text-slate-500"
        >
          <div
            class="inline-block h-10 w-10 animate-spin rounded-full border-4 border-slate-400 border-t-transparent"
          ></div>
          <p class="text-sm font-semibold">
            Loading camera feed... (might take some time)
          </p>
        </div>
        <div
          v-else-if="feedError"
          class="flex h-full w-full flex-col items-center justify-center gap-3 p-8 text-red-700"
        >
          <span class="text-6xl mb-2">⚠️</span>
          <p class="max-w-md text-center text-sm font-semibold">
            {{ feedError }}
          </p>
          <button
            @click="reconnectFeed"
            class="rounded-md border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-bold text-white shadow-sm transition-colors hover:bg-slate-700"
          >
            Reconnect
          </button>
        </div>
        <div
          v-else-if="!feedUrl"
          class="flex h-full w-full flex-col items-center justify-center gap-3 p-8 text-slate-500"
        >
          <p class="text-sm font-semibold">Camera feed not started</p>
          <button
            @click="startFeed"
            :disabled="isClosetOpen"
            class="rounded-md border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-slate-700 hover:shadow-md"
            :class="isClosetOpen ? 'cursor-not-allowed opacity-60 hover:translate-y-0 hover:bg-slate-900' : ''"
          >
            Start Feed
          </button>
        </div>
        <img
          v-else
          :src="feedUrl"
          alt="Live camera feed"
          class="w-full h-full object-cover block"
          :style="cameraFeedStyle"
          @error="handleFeedError"
          @load="handleFeedLoad"
        />
        </div>
        <div class="space-y-2 rounded-lg border border-slate-200 bg-slate-50 p-1.5">
          <IlluminationControl />

          <div class="rounded-lg border border-slate-200 bg-white p-2 shadow-sm">
            <div class="mb-2 flex items-center justify-between gap-2">
              <span class="text-[11px] font-black uppercase text-slate-700">Environment</span>
              <span
                :class="[
                  'flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold',
                  environment.healthy
                    ? 'border-teal-200 bg-teal-50 text-teal-700'
                    : 'border-slate-200 bg-slate-50 text-slate-500',
                ]"
              >
                <span
                  :class="[
                    'h-1.5 w-1.5 rounded-full',
                    environment.healthy ? 'bg-teal-500' : 'bg-slate-400',
                  ]"
                ></span>
                {{ environment.healthy ? "Online" : "Unknown" }}
              </span>
            </div>
            <div class="grid grid-cols-2 gap-1.5">
              <div class="rounded border border-slate-200 bg-white p-2 shadow-sm">
                <div class="text-[10px] font-bold uppercase text-slate-500">Temp</div>
                <div class="mt-1 text-sm font-black text-slate-900">{{ temperatureLabel }}</div>
              </div>
              <div class="rounded border border-slate-200 bg-white p-2 shadow-sm">
                <div class="text-[10px] font-bold uppercase text-slate-500">Humidity</div>
                <div class="mt-1 text-sm font-black text-slate-900">{{ humidityLabel }}</div>
              </div>
            </div>
          </div>

          <div class="rounded-lg border border-slate-200 bg-white p-2 shadow-sm">
            <div class="mb-2 flex items-center justify-between">
              <span class="text-[11px] font-black uppercase text-slate-700">Camera Controls</span>
              <span class="rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-[10px] font-bold text-slate-600">Controls</span>
            </div>
            <div class="space-y-1.5">
              <div class="rounded border border-slate-200 bg-white p-2 shadow-sm">
                <label class="flex cursor-pointer items-center">
                  <input
                    type="checkbox"
                    v-model="autoExposure"
                    @change="toggleAutoExposure"
                    :disabled="!autoExposureSupported"
                    class="h-4 w-4 rounded border-gray-300 bg-gray-100 text-slate-800 focus:ring-2 focus:ring-slate-500 disabled:cursor-not-allowed disabled:opacity-50"
                  />
                  <span class="ml-2 text-xs font-semibold text-gray-700">
                    Auto-Exposure
                  </span>
                  <span
                    v-if="!autoExposureSupported"
                    class="ml-2 text-xs text-red-600"
                  >
                    Not Supported
                  </span>
                </label>
              </div>

              <div
                v-if="gammaSupported"
                class="rounded border border-slate-200 bg-white p-2 shadow-sm"
              >
                <div class="flex justify-between items-center mb-1">
                  <label class="text-xs font-semibold text-gray-700">Gamma</label>
                  <span
                    class="text-xs font-mono text-gray-900 bg-gray-100 px-2 py-0.5 rounded"
                    >{{ gamma.toFixed(2) }}</span
                  >
                </div>
                <input
                  type="range"
                  :value="gammaToSlider(gamma)"
                  :min="0"
                  :max="100"
                  step="1"
                  @input="onGammaSliderChange"
                  class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                />
                <div class="flex justify-between text-xs text-gray-500 mt-0.5">
                  <span>{{ gammaMin.toFixed(1) }}</span>
                  <span>{{ gammaMax.toFixed(1) }}</span>
                </div>
              </div>

              <div
                v-if="!autoExposure"
                class="rounded border border-slate-200 bg-white p-2 shadow-sm"
              >
                <div class="flex justify-between items-center mb-1">
                  <label class="text-xs font-semibold text-gray-700">
                    Exposure
                  </label>
                  <span
                    class="text-xs font-mono text-gray-900 bg-gray-100 px-2 py-0.5 rounded"
                    >{{ exposure.toFixed(1) }} ms</span
                  >
                </div>
                <input
                  type="range"
                  :value="exposureToSlider(exposure)"
                  :min="0"
                  :max="100"
                  step="1"
                  :disabled="autoExposure"
                  @input="onExposureSliderChange"
                  class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:cursor-not-allowed disabled:opacity-50 slider"
                />
                <div class="flex justify-between text-xs text-gray-500 mt-0.5">
                  <span>{{ exposureMin.toFixed(3) }} ms</span>
                  <span>{{ exposureMax.toFixed(1) }} ms</span>
                </div>
              </div>

              <div
                v-if="!autoExposure"
                class="rounded border border-slate-200 bg-white p-2 shadow-sm"
              >
                <div class="flex justify-between items-center mb-1">
                  <label class="text-xs font-semibold text-gray-700">Gain</label>
                  <span
                    class="text-xs font-mono text-gray-900 bg-gray-100 px-2 py-0.5 rounded"
                    >{{ gain.toFixed(2) }}x</span
                  >
                </div>
                <input
                  type="range"
                  v-model.number="gain"
                  :min="gainMin"
                  :max="gainMax"
                  step="0.01"
                  :disabled="autoExposure"
                  @input="onGainChange"
                  class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:cursor-not-allowed disabled:opacity-50 slider"
                />
                <div class="flex justify-between text-xs text-gray-500 mt-0.5">
                  <span>{{ gainMin.toFixed(1) }}x</span>
                  <span>{{ gainMax.toFixed(1) }}x</span>
                </div>
              </div>

              <div class="zoom-control rounded border border-slate-200 bg-white p-2 shadow-sm">
                <div class="mb-1.5 flex items-center justify-between gap-2">
                  <div>
                    <label class="text-xs font-black uppercase text-slate-700">Zoom</label>
                  </div>
                  <span class="font-mono text-[11px] font-black text-slate-700">
                    {{ zTravelPercent }}%
                  </span>
                </div>

                <div class="grid grid-cols-[34px_minmax(0,1fr)_34px] items-center gap-2">
                  <button
                    @pointerdown.prevent="moveFocus(-1)"
                    :disabled="focusDisabled"
                    class="zoom-arrow-button"
                    :class="focusDisabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'"
                    title="Zoom down (-)"
                  >
                    -
                  </button>
                  <div
                    class="zoom-slider-track"
                    :title="`${zRemainingPercent}% to max`"
                  >
                    <div
                      class="zoom-slider-fill"
                      :style="{ width: `${zTravelPercent}%` }"
                    ></div>
                  </div>
                  <button
                    @pointerdown.prevent="moveFocus(1)"
                    :disabled="focusDisabled"
                    class="zoom-arrow-button"
                    :class="focusDisabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'"
                    title="Zoom up (+)"
                  >
                    +
                  </button>
                </div>

                <div class="mt-1.5 grid grid-cols-4 gap-1">
                  <button
                    v-for="option in zStepOptions"
                    :key="option.id"
                    @click="zMultiplier = option.multiplier"
                    class="zoom-increment-button"
                    :class="zMultiplier === option.multiplier ? 'zoom-increment-button-active' : ''"
                    type="button"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Live Feed Info -->
      <div
        v-if="feedUrl && !feedError"
        class="hidden"
      >
        Live feed • Exposure: {{ exposure.toFixed(1) }}ms • Gain:
        {{ gain.toFixed(2) }}x
        <span v-if="gammaSupported"> • Gamma: {{ gamma.toFixed(2) }}</span>
      </div>
    </div>

    <div
      v-if="isClosetOpen"
      class="mt-2 rounded-lg border border-red-300 bg-red-50 px-3 py-2 text-xs font-black uppercase tracking-wide text-red-700"
    >
      Lid open - capture and recording locked
    </div>

    <div class="mt-2 grid gap-2 xl:grid-cols-[minmax(0,1fr)_260px]">
      <div class="grid gap-2 sm:grid-cols-2">
      <!-- Capture Image Button -->
      <button
        @click="capture"
        :disabled="cameraActionDisabled"
        class="action-button action-button-capture"
        :title="isClosetOpen ? 'Close the lid before capture' : 'Capture image'"
      >
        <span
          v-if="camera.isCapturing.value"
          class="flex items-center justify-center gap-2"
        >
          <div
            class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
          ></div>
          Capturing...
        </span>
        <span v-else class="flex items-center justify-center gap-2">
          <span class="action-button-icon action-button-icon-camera"></span>
          Capture Image
        </span>
      </button>

      <!-- Record Video Button -->
      <button
        @click="toggleRecording"
        :disabled="cameraActionDisabled"
        :title="isClosetOpen ? 'Close the lid before recording' : 'Record video'"
        :class="[
          'action-button',
          isRecording
            ? 'action-button-recording'
            : 'action-button-record',
        ]"
      >
        <span v-if="isRecording" class="flex items-center justify-center gap-2">
          <span class="action-button-icon action-button-icon-stop"></span>
          Stop Recording ({{ recordingTime.toFixed(0) }}s)
        </span>
        <span v-else class="flex items-center justify-center gap-2">
          <span class="action-button-icon action-button-icon-record"></span>
          Record Video
        </span>
      </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.camera-panel {
  background:
    radial-gradient(circle at top left, rgba(148, 163, 184, 0.16), transparent 32%),
    linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.action-button {
  @apply flex min-h-[40px] w-full cursor-pointer items-center justify-center rounded-md px-3 py-2 text-sm font-black shadow-sm transition-all disabled:cursor-not-allowed disabled:opacity-60;
}

.action-button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.action-button:active:not(:disabled) {
  transform: translateY(0);
}

.action-button-capture {
  @apply border border-slate-700 bg-slate-800 text-white shadow-slate-300/50 hover:bg-slate-700 hover:shadow-md;
}

.action-button-record {
  @apply border border-slate-700 bg-slate-800 text-white shadow-slate-300/50 hover:bg-slate-700 hover:shadow-md;
}

.action-button-recording {
  @apply border border-red-400 bg-red-600 text-white shadow-red-200/70 hover:bg-red-700 hover:shadow-md;
}

.zoom-arrow-button {
  @apply flex h-8 w-8 items-center justify-center rounded-md border border-slate-700 bg-slate-800 text-base font-black leading-none text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-slate-700 hover:shadow-md active:translate-y-0;
}

.zoom-slider-track {
  @apply relative h-3 overflow-hidden rounded-full border border-slate-300 bg-slate-100 shadow-inner;
}

.zoom-slider-fill {
  @apply absolute bottom-0 left-0 top-0 bg-slate-800 transition-all;
}

.zoom-increment-button {
  @apply h-7 rounded border border-slate-300 bg-white px-1 text-[9px] font-bold text-slate-600 transition-colors hover:border-slate-500 hover:text-slate-900;
}

.zoom-increment-button-active {
  @apply border-slate-800 bg-slate-800 text-white hover:border-slate-800 hover:text-white;
}

.action-button-icon {
  @apply relative inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-md;
  background: rgba(255, 255, 255, 0.18);
}

.action-button-icon-camera::before {
  content: "";
  width: 11px;
  height: 8px;
  border: 2px solid currentColor;
  border-radius: 3px;
}

.action-button-icon-camera::after {
  content: "";
  position: absolute;
  width: 4px;
  height: 4px;
  border-radius: 9999px;
  border: 1px solid currentColor;
}

.action-button-icon-record::before {
  content: "";
  width: 9px;
  height: 9px;
  border-radius: 9999px;
  background: currentColor;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.22);
}

.action-button-icon-stop::before {
  content: "";
  width: 9px;
  height: 9px;
  border-radius: 2px;
  background: currentColor;
  animation: recording-stop-pulse 1s ease-in-out infinite;
}

@keyframes recording-stop-pulse {
  0%,
  100% {
    opacity: 0.7;
  }
  50% {
    opacity: 1;
  }
}

/* Custom slider styling */
.slider::-webkit-slider-thumb {
  appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #1f2937;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.15s ease-in-out;
}

.slider::-webkit-slider-thumb:hover {
  background: #0f172a;
  transform: scale(1.1);
}

.slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #1f2937;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.15s ease-in-out;
}

.slider::-moz-range-thumb:hover {
  background: #0f172a;
  transform: scale(1.1);
}

.slider:disabled::-webkit-slider-thumb {
  background: #9ca3af;
  cursor: not-allowed;
}

.slider:disabled::-moz-range-thumb {
  background: #9ca3af;
  cursor: not-allowed;
}
</style>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { useCamera } from "@/composables/useCamera";
import { useStage } from "@/composables/useStage";
import { getActiveProfileHeaders, piAPI } from "@/api/client";
import IlluminationControl from "@/components/IlluminationControl.vue";
import {
  CAMERA_FEED_ROTATION_DEGREES,
  STAGE_AXIS_MAX,
} from "@/config/stage";

const store = useMicroscopeStore();
const camera = useCamera();
const stage = useStage();

// Camera settings with limits
const exposure = ref(100);
const exposureMin = ref(0.001);
const exposureMax = ref(200); // Reduced from 1000 for better control
const gain = ref(1.0);
const gainMin = ref(1.0);
const gainMax = ref(4.0); // Reduced from 16.0 for better control
const gamma = ref(1.0);
const gammaMin = ref(0.5);
const gammaMax = ref(4.0);
const gammaSupported = ref(true); // Will be updated from camera
const autoExposure = ref(false);
const autoExposureSupported = ref(true); // Will be updated from camera
const baseZStep = 100;
const zStepOptions = [
  { id: "finer", label: "Finer", multiplier: 1 },
  { id: "fine", label: "Fine", multiplier: 2 },
  { id: "medium", label: "Medium", multiplier: 5 },
  { id: "bigger", label: "Bigger", multiplier: 10 },
] as const;
const zMultiplier = ref(2);
const zMaxPosition = STAGE_AXIS_MAX.z;

// Debounce timer for live updates
let updateTimer: ReturnType<typeof setTimeout> | null = null;

const feedUrl = ref("");
const isLoadingFeed = ref(false);
const feedError = ref("");
let websocket: WebSocket | null = null;
let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
const isConnecting = ref(false);
let environmentPollTimer: ReturnType<typeof setInterval> | null = null;

const environment = ref<{
  temperature_c: number | null;
  humidity: number | null;
  healthy: boolean;
}>({
  temperature_c: null,
  humidity: null,
  healthy: false,
});

// Video recording state
const isRecording = ref(false);
const recordingTime = ref(0);
let recordingInterval: ReturnType<typeof setInterval> | null = null;
let recordingStartTime: Date | null = null;

// Computed warning based on store's light status and feed status
const lightWarning = computed(() => {
  return feedUrl.value !== "" && !feedError.value && !store.lightStatus.isOn;
});
const isClosetOpen = computed(() => store.closetStatus === "open");
const cameraActionDisabled = computed(
  () => camera.isCapturing.value || isClosetOpen.value,
);
const zIsHomed = computed(() => !!store.limitSensors?.z.homed);
const focusDisabled = computed(
  () => stage.isMoving.value || isClosetOpen.value || !zIsHomed.value,
);
const clampedZPosition = computed(() =>
  Math.min(Math.max(store.position.z, 0), zMaxPosition),
);
const zTravelPercent = computed(() =>
  Math.round((clampedZPosition.value / zMaxPosition) * 100),
);
const zRemainingPercent = computed(() => Math.max(100 - zTravelPercent.value, 0));
const cameraFeedStyle = computed(() => ({
  transform: `rotate(${CAMERA_FEED_ROTATION_DEGREES}deg)`,
}));
const temperatureLabel = computed(() => {
  if (environment.value.temperature_c === null) {
    return "Unknown";
  }

  return `${environment.value.temperature_c.toFixed(1)} C`;
});
const humidityLabel = computed(() => {
  if (environment.value.humidity === null) {
    return "Unknown";
  }

  return `${environment.value.humidity.toFixed(1)}%`;
});

// Watch for light status changes and log them
watch(
  () => store.lightStatus.isOn,
  (isOn, wasOn) => {
    // Only log if feed is active and light status changed
    if (feedUrl.value && wasOn !== undefined && !isOn && wasOn) {
      store.addLog("⚠️ Camera light turned OFF", "warning");
    }
  },
);

onMounted(async () => {
  await loadCameraSettings();
  await fetchEnvironment();
  await stage.updatePosition();
  await stage.updateLimitSensors();
  environmentPollTimer = setInterval(fetchEnvironment, 5000);
  window.addEventListener("keydown", handleZoomKeyDown);

  // Auto-start the feed
  //startFeed();
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleZoomKeyDown);
  stopFeed();
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
  }
  if (updateTimer) {
    clearTimeout(updateTimer);
  }
  if (environmentPollTimer) {
    clearInterval(environmentPollTimer);
  }
});

async function fetchEnvironment() {
  try {
    const response = await piAPI.getEnvironment();
    environment.value = {
      temperature_c: response.temperature_c,
      humidity: response.humidity,
      healthy: response.healthy,
    };
  } catch {
    environment.value = {
      temperature_c: null,
      humidity: null,
      healthy: false,
    };
  }
}

async function loadCameraSettings() {
  try {
    await camera.loadSettings();
    const settings = store.cameraSettings;

    // Update exposure
    exposure.value = settings.exposure || 100;
    exposureMin.value = settings.exposureMin || 0.001;
    // Cap the max at 200ms for better slider control, even if camera supports more
    exposureMax.value = Math.min(settings.exposureMax || 200, 200);

    // Update gain
    gain.value = settings.gain || 1.0;
    gainMin.value = settings.gainMin || 1.0;
    // Cap the max at 4.0x for better slider control, even if camera supports more
    gainMax.value = Math.min(settings.gainMax || 4.0, 4.0);

    // Update gamma
    gamma.value = settings.gamma || 1.0;
    gammaMin.value = settings.gammaMin || 0.5;
    gammaMax.value = settings.gammaMax || 4.0;
    gammaSupported.value = settings.gammaSupported !== false; // Default to true if not specified

    // Update auto-exposure
    autoExposure.value = settings.autoExposure || false;
    autoExposureSupported.value = settings.autoExposureSupported !== false; // Default to true if not specified

    console.log("Camera settings loaded:", {
      exposure: exposure.value,
      exposureRange: `${exposureMin.value} - ${exposureMax.value}`,
      gain: gain.value,
      gainRange: `${gainMin.value} - ${gainMax.value}`,
      gamma: gamma.value,
      gammaRange: `${gammaMin.value} - ${gammaMax.value}`,
      gammaSupported: gammaSupported.value,
      autoExposure: autoExposure.value,
      autoExposureSupported: autoExposureSupported.value,
    });

    // Warn if auto-exposure not supported
    if (!autoExposureSupported.value) {
      store.addLog("⚠️ Auto-exposure not supported by this camera", "warning");
    }

    // Warn if gamma not supported
    if (!gammaSupported.value) {
      store.addLog("⚠️ Gamma not supported by this camera", "warning");
    }
  } catch (error) {
    console.error("Failed to load camera settings:", error);
  }
}

// Logarithmic scale conversion for exposure slider
// This makes the slider less sensitive at lower values
function exposureToSlider(exposureValue: number): number {
  // Convert exposure value to logarithmic slider position (0-100)
  const logMin = Math.log(Math.max(exposureMin.value, 0.001)); // Avoid log(0)
  const logMax = Math.log(exposureMax.value);
  const logValue = Math.log(Math.max(exposureValue, 0.001));
  return ((logValue - logMin) / (logMax - logMin)) * 100;
}

function sliderToExposure(sliderValue: number): number {
  // Convert slider position (0-100) to exposure value using logarithmic scale
  const logMin = Math.log(Math.max(exposureMin.value, 0.001));
  const logMax = Math.log(exposureMax.value);
  const logValue = logMin + (sliderValue / 100) * (logMax - logMin);
  return Math.exp(logValue);
}

function onExposureSliderChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const sliderValue = parseFloat(target.value);
  exposure.value = sliderToExposure(sliderValue);

  // Debounce the update to avoid flooding the API
  if (updateTimer) {
    clearTimeout(updateTimer);
  }

  updateTimer = setTimeout(async () => {
    await updateSettingsToCamera({ exposure: exposure.value });
  }, 150); // 150ms debounce
}

function onGainChange() {
  if (autoExposure.value) {
    return;
  }

  // Debounce the update to avoid flooding the API
  if (updateTimer) {
    clearTimeout(updateTimer);
  }

  updateTimer = setTimeout(async () => {
    await updateSettingsToCamera({ gain: gain.value });
  }, 150); // 150ms debounce
}

// Logarithmic scale conversion for gamma slider
// This makes the slider less sensitive at lower values
function gammaToSlider(gammaValue: number): number {
  // Convert gamma value to logarithmic slider position (0-100)
  const logMin = Math.log(gammaMin.value);
  const logMax = Math.log(gammaMax.value);
  const logValue = Math.log(gammaValue);
  return ((logValue - logMin) / (logMax - logMin)) * 100;
}

function sliderToGamma(sliderValue: number): number {
  // Convert slider position (0-100) to gamma value using logarithmic scale
  const logMin = Math.log(gammaMin.value);
  const logMax = Math.log(gammaMax.value);
  const logValue = logMin + (sliderValue / 100) * (logMax - logMin);
  return Math.exp(logValue);
}

function onGammaSliderChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const sliderValue = parseFloat(target.value);
  gamma.value = sliderToGamma(sliderValue);

  // Debounce the update to avoid flooding the API
  if (updateTimer) {
    clearTimeout(updateTimer);
  }

  updateTimer = setTimeout(async () => {
    await updateSettingsToCamera({ gamma: gamma.value });
  }, 150); // 150ms debounce
}

async function toggleAutoExposure() {
  await updateSettingsToCamera({ autoExposure: autoExposure.value });

  // Reload settings to get updated exposure value if auto-exposure was enabled
  if (autoExposure.value) {
    setTimeout(loadCameraSettings, 500);
  }
}

async function updateSettingsToCamera(settings: {
  exposure?: number;
  gain?: number;
  gamma?: number;
  autoExposure?: boolean;
}) {
  try {
    await camera.updateSettings(settings);

    // Update store
    if (settings.exposure !== undefined) {
      store.updateCameraSettings({ exposure: settings.exposure });
    }
    if (settings.gain !== undefined) {
      store.updateCameraSettings({ gain: settings.gain });
    }
    if (settings.gamma !== undefined) {
      store.updateCameraSettings({ gamma: settings.gamma });
    }

    // Don't show log for every slider change to avoid spam
    // store.addLog("Camera settings updated", "success");
  } catch (error: any) {
    store.addLog(`Failed to update settings: ${error.message}`, "error");
    throw error;
  }
}

async function moveFocus(direction: 1 | -1) {
  if (isClosetOpen.value) {
    store.addLog("Zoom movement blocked: lid is open", "warning");
    return;
  }

  if (!zIsHomed.value) {
    store.addLog("Home stage before zoom movement", "warning");
    return;
  }

  const steps = Math.max(1, Math.round(baseZStep * zMultiplier.value));
  await stage.move(0, 0, steps * direction, true);
  setTimeout(stage.updatePosition, 500);
}

function handleZoomKeyDown(event: KeyboardEvent) {
  const target = event.target as HTMLElement;
  if (
    target.tagName === "INPUT" ||
    target.tagName === "TEXTAREA" ||
    target.isContentEditable
  ) {
    return;
  }

  if (event.repeat) {
    return;
  }

  if (event.key === "-" || event.key === "_") {
    event.preventDefault();
    if (!focusDisabled.value) {
      moveFocus(-1);
    }
  }

  if (event.key === "+" || event.key === "=") {
    event.preventDefault();
    if (!focusDisabled.value) {
      moveFocus(1);
    }
  }
}

async function capture() {
  if (isClosetOpen.value) {
    store.addLog("Capture blocked: lid is open", "warning");
    return;
  }

  await camera.captureImage({
    exposure: exposure.value,
    gain: gain.value,
    gamma: gamma.value,
  });
}

async function startFeed() {
  if (isClosetOpen.value) {
    store.addLog("Camera feed blocked: lid is open", "warning");
    return;
  }

  if (websocket && websocket.readyState === WebSocket.OPEN) {
    console.log("WebSocket already connected");
    return;
  }

  if (isConnecting.value) {
    console.log("Already connecting...");
    return;
  }

  isLoadingFeed.value = true;
  isConnecting.value = true;
  feedError.value = "";
  feedUrl.value = ""; // Clear old image

  // Check light status once when starting feed (update store)
  try {
    const response = await piAPI.getLedLampState();
    store.updateLightStatus(response.is_on);

    if (!response.is_on) {
      store.addLog("⚠️ Camera light is OFF", "warning");
    }
  } catch (error) {
    console.error("Failed to check light status:", error);
  }

  // Connect to WebSocket stream
  const wsBaseUrl = (
    import.meta.env.VITE_API_BASE_URL || "http://localhost:3000"
  )
    .replace("http://", "ws://")
    .replace("https://", "wss://");

  const wsUrl = `${wsBaseUrl}/ws/camera/stream`.replace(":3000", ":8001");

  console.log("Connecting to WebSocket:", wsUrl);

  try {
    websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log("✅ WebSocket connected");
      // Stop loading immediately when connection opens
      isLoadingFeed.value = false;
      isConnecting.value = false;
      feedError.value = "";

      // Clear any pending reconnection
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
        reconnectTimeout = null;
      }
    };

    websocket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);

        if (message.type === "frame" && message.data) {
          // Update the feed with base64 encoded JPEG
          feedUrl.value = `data:image/jpeg;base64,${message.data}`;
        } else if (message.type === "connected") {
          console.log("🔌 Camera stream connected:", message);
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    websocket.onerror = (error) => {
      console.error("WebSocket error:", error);
      feedError.value =
        "Connection error - check if Python camera service is running";
      isLoadingFeed.value = false;
      isConnecting.value = false;
    };

    websocket.onclose = (event) => {
      console.log("WebSocket closed:", event.code, event.reason);
      isConnecting.value = false;

      if (!feedError.value) {
        feedError.value = "Connection lost";
      }

      // Auto-reconnect after 3 seconds if not manually stopped
      if (!reconnectTimeout) {
        console.log("Scheduling reconnection in 3 seconds...");
        reconnectTimeout = setTimeout(() => {
          reconnectTimeout = null;
          console.log("Attempting to reconnect...");
          startFeed();
        }, 3000);
      }
    };
  } catch (error) {
    console.error("Failed to create WebSocket:", error);
    feedError.value = "Failed to connect to camera service";
    isLoadingFeed.value = false;
    isConnecting.value = false;
  }
}

function stopFeed() {
  console.log("🛑 Stopping feed...");

  // Clear reconnection timeout
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
    reconnectTimeout = null;
  }

  // Close WebSocket properly
  if (websocket) {
    // Remove all event handlers first to prevent any reconnection logic
    websocket.onclose = null;
    websocket.onerror = null;
    websocket.onmessage = null;
    websocket.onopen = null;

    // Close with a normal closure code
    if (
      websocket.readyState === WebSocket.OPEN ||
      websocket.readyState === WebSocket.CONNECTING
    ) {
      websocket.close(1000, "User stopped feed");
      console.log("✅ WebSocket closed");
    }
    websocket = null;
  }

  feedUrl.value = "";
  feedError.value = "";
  isLoadingFeed.value = false;
  isConnecting.value = false;
}

function reconnectFeed() {
  feedError.value = "";
  stopFeed();
  setTimeout(startFeed, 500);
}

function handleFeedError() {
  feedError.value = "Failed to load camera feed";
  isLoadingFeed.value = false;
}

function handleFeedLoad() {
  feedError.value = "";
  isLoadingFeed.value = false;
}

async function toggleRecording() {
  if (isClosetOpen.value && !isRecording.value) {
    store.addLog("Recording blocked: lid is open", "warning");
    return;
  }

  if (isRecording.value) {
    await stopRecording();
  } else {
    await startRecording();
  }
}

async function startRecording() {
  try {
    store.addLog("Starting video recording...", "info");

    const response = await fetch("/api/v1/camera/video/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getActiveProfileHeaders(),
      },
      body: JSON.stringify({
        duration: 30,
        playbackFrameRate: 25,
        decimation: 1,
      }),
    });

    const result = await response.json();

    if (result.success) {
      isRecording.value = true;
      recordingStartTime = new Date();
      recordingTime.value = 0;

      // Update timer every 100ms
      recordingInterval = setInterval(() => {
        if (recordingStartTime) {
          recordingTime.value =
            (new Date().getTime() - recordingStartTime.getTime()) / 1000;
        }
      }, 100);

      store.addLog(
        `Recording started (click Stop Recording to finish)`,
        "success",
      );
    } else {
      store.addLog("Failed to start recording", "error");
    }
  } catch (error: any) {
    store.addLog(`Recording error: ${error.message}`, "error");
  }
}

async function stopRecording() {
  try {
    // Clear the timer
    if (recordingInterval) {
      clearInterval(recordingInterval);
      recordingInterval = null;
    }

    store.addLog("Stopping video recording...", "info");

    const response = await fetch("/api/v1/camera/video/stop", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getActiveProfileHeaders(),
      },
    });

    const result = await response.json();

    if (result.success) {
      isRecording.value = false;
      recordingTime.value = 0;
      recordingStartTime = null;

      const fileSizeMB = result.file_size
        ? (result.file_size / 1024 / 1024).toFixed(2)
        : "?";
      const durationSec = result.duration?.toFixed(1) || "?";

      store.addLog(
        `✅ Video saved: ${result.filename} (${durationSec}s, ${fileSizeMB}MB)`,
        "success",
      );

      // Dispatch event to notify video gallery to refresh
      if (result.videoId) {
        window.dispatchEvent(
          new CustomEvent("video-recorded", {
            detail: { videoId: result.videoId, filename: result.filename },
          }),
        );
      }
    } else {
      store.addLog("Failed to stop recording", "error");
    }
  } catch (error: any) {
    isRecording.value = false;
    recordingTime.value = 0;
    if (recordingInterval) {
      clearInterval(recordingInterval);
      recordingInterval = null;
    }
    store.addLog(`Recording stop error: ${error.message}`, "error");
  }
}
</script>
