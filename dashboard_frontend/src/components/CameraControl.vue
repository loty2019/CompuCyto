<template>
  <div class="camera-panel rounded-xl border border-slate-200/80 bg-white p-2.5 shadow-md">
    <div class="mb-2 flex flex-wrap items-center justify-between gap-2">
      <div class="flex items-baseline gap-2">
        <h2 class="text-lg font-black text-slate-950">Camera</h2>
        <span class="text-xs font-bold uppercase text-slate-500">Live Preview</span>
      </div>
      <div class="flex items-center gap-2">
          <span
            v-if="feedUrl && !feedError && lightWarning"
            class="text-xs font-semibold text-yellow-600 bg-yellow-50 px-2 py-1 rounded border border-yellow-300 flex items-center gap-1"
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
    <div class="mt-2">
      <div class="grid items-start gap-2 xl:grid-cols-[minmax(0,1fr)_260px]">
        <div
          class="relative flex items-center justify-center overflow-hidden rounded-xl border border-slate-700 bg-slate-950 shadow-lg shadow-slate-300/40 ring-4 ring-slate-900"
          style="aspect-ratio: 4/3; min-height: 245px"
        >
        <div
          v-if="isLoadingFeed"
          class="flex flex-col items-center justify-center gap-4 text-blue-300 w-full h-full p-8"
        >
          <div
            class="inline-block w-16 h-16 border-4 border-blue-400 border-t-transparent rounded-full animate-spin"
          ></div>
          <p class="text-lg font-semibold">
            Loading camera feed... (might take some time)
          </p>
        </div>
        <div
          v-else-if="feedError"
          class="flex flex-col items-center justify-center gap-4 text-red-300 w-full h-full p-8"
        >
          <span class="text-6xl mb-2">⚠️</span>
          <p class="text-base font-semibold text-center max-w-md">
            {{ feedError }}
          </p>
          <button
            @click="reconnectFeed"
            class="rounded-lg bg-blue-500 px-6 py-3 text-base font-bold text-white shadow-lg transition-colors hover:bg-blue-600"
          >
            Reconnect
          </button>
        </div>
        <div
          v-else-if="!feedUrl"
          class="flex flex-col items-center justify-center gap-4 text-slate-400 w-full h-full p-8"
        >
          <p class="text-lg font-semibold">Camera feed not started</p>
          <button
            @click="startFeed"
            class="rounded-lg bg-blue-500 px-6 py-3 text-base font-bold text-white shadow-lg transition-colors hover:bg-blue-600"
          >
            Start Feed
          </button>
        </div>
        <img
          v-else
          :src="feedUrl"
          alt="Live camera feed"
          class="w-full h-full object-cover block"
          @error="handleFeedError"
          @load="handleFeedLoad"
        />
        </div>
        <div class="space-y-2 rounded-xl border border-slate-200 bg-slate-50 p-2 shadow-inner">
          <div class="rounded-xl border border-white/80 bg-white/85 p-2 shadow-sm">
            <div class="mb-2 flex items-center justify-between">
              <span class="text-[11px] font-black uppercase text-slate-700">Camera Tuning</span>
              <span class="rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-[10px] font-bold text-slate-600">Controls</span>
            </div>
            <div class="space-y-1.5">
              <div class="rounded-lg border border-slate-200 bg-white p-2 shadow-sm">
                <label class="flex cursor-pointer items-center">
                  <input
                    type="checkbox"
                    v-model="autoExposure"
                    @change="toggleAutoExposure"
                    :disabled="!autoExposureSupported"
                    class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 disabled:cursor-not-allowed disabled:opacity-50"
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
                class="rounded-lg border border-slate-200 bg-white p-2 shadow-sm"
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

              <div class="rounded-lg border border-slate-200 bg-white p-2 shadow-sm">
                <div class="flex justify-between items-center mb-1">
                  <label class="text-xs font-semibold text-gray-700">
                    Exposure
                    <span v-if="autoExposure" class="text-xs text-blue-600 ml-1">
                      Auto
                    </span>
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

              <div class="rounded-lg border border-slate-200 bg-white p-2 shadow-sm">
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
                  @input="onGainChange"
                  class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                />
                <div class="flex justify-between text-xs text-gray-500 mt-0.5">
                  <span>{{ gainMin.toFixed(1) }}x</span>
                  <span>{{ gainMax.toFixed(1) }}x</span>
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

    <div class="mt-2 grid gap-2 sm:grid-cols-2">
      <!-- Capture Image Button -->
      <button
        @click="capture"
        :disabled="camera.isCapturing.value"
        class="action-button action-button-capture"
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
        :disabled="camera.isCapturing.value"
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
</template>

<style scoped>
.camera-panel {
  background:
    radial-gradient(circle at top left, rgba(148, 163, 184, 0.16), transparent 32%),
    linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.action-button {
  @apply flex min-h-[44px] w-full cursor-pointer items-center justify-center rounded-lg px-3 py-2 text-sm font-black shadow-md transition-all disabled:cursor-not-allowed disabled:opacity-60;
}

.action-button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.action-button:active:not(:disabled) {
  transform: translateY(0);
}

.action-button-capture {
  @apply border border-slate-700 bg-slate-800 text-white shadow-slate-300/60 hover:bg-slate-700 hover:shadow-lg;
}

.action-button-record {
  @apply border border-blue-700 bg-blue-700 text-white shadow-blue-300/50 hover:bg-blue-800 hover:shadow-lg;
}

.action-button-recording {
  @apply border border-red-400 bg-red-600 text-white shadow-red-200/70 hover:bg-red-700 hover:shadow-lg;
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
  background: #3b82f6;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.15s ease-in-out;
}

.slider::-webkit-slider-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
}

.slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.15s ease-in-out;
}

.slider::-moz-range-thumb:hover {
  background: #2563eb;
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
import { piAPI } from "@/api/client";

const store = useMicroscopeStore();
const camera = useCamera();

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

// Debounce timer for live updates
let updateTimer: ReturnType<typeof setTimeout> | null = null;

const feedUrl = ref("");
const isLoadingFeed = ref(false);
const feedError = ref("");
let websocket: WebSocket | null = null;
let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
const isConnecting = ref(false);

// Video recording state
const isRecording = ref(false);
const recordingTime = ref(0);
let recordingInterval: ReturnType<typeof setInterval> | null = null;
let recordingStartTime: Date | null = null;

// Computed warning based on store's light status and feed status
const lightWarning = computed(() => {
  return feedUrl.value !== "" && !feedError.value && !store.lightStatus.isOn;
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

  // Auto-start the feed
  //startFeed();
});

onUnmounted(() => {
  stopFeed();
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
  }
  if (updateTimer) {
    clearTimeout(updateTimer);
  }
});

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

async function capture() {
  await camera.captureImage({
    exposure: exposure.value,
    gain: gain.value,
    gamma: gamma.value,
  });
}

async function startFeed() {
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
  if (isRecording.value) {
    await stopRecording();
  } else {
    await startRecording();
  }
}

async function startRecording() {
  try {
    store.addLog("Starting video recording...", "info");

    const token = localStorage.getItem("access_token");
    const response = await fetch("/api/v1/camera/video/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
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

    const token = localStorage.getItem("access_token");
    const response = await fetch("/api/v1/camera/video/stop", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
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
