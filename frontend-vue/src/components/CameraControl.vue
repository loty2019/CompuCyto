<template>
  <div class="bg-white p-4 rounded-xl shadow-lg">
    <h2 class="text-xl font-bold mb-4 text-gray-900">Camera Controls</h2>

    <!-- Two Column Layout for Controls -->
    <div class="grid grid-cols-2 gap-4 mb-4">
      <!-- Left Column -->
      <div class="space-y-4">
        <!-- Auto-Exposure Controls -->
        <div class="p-3 bg-gray-50 rounded-lg border border-gray-200">
          <div class="flex flex-col gap-2">
            <label class="flex items-center cursor-pointer">
              <input
                type="checkbox"
                v-model="autoExposure"
                @change="toggleAutoExposure"
                :disabled="!autoExposureSupported"
                class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
              <span class="ml-2 text-sm font-semibold text-gray-700"
                >Auto-Exposure</span
              >
              <span
                v-if="!autoExposureSupported"
                class="ml-2 text-xs text-red-600"
                >(Not Supported)</span
              >
            </label>
            <button
              @click="performAutoExposureOnce"
              :disabled="autoExposure || !autoExposureSupported"
              class="w-full px-3 py-1 text-xs font-medium text-white bg-blue-500 rounded hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Auto Once
            </button>
          </div>
        </div>

        <!-- Exposure Slider -->
        <div>
          <div class="flex justify-between items-center mb-1">
            <label class="text-sm font-semibold text-gray-700">
              Exposure
              <span v-if="autoExposure" class="text-xs text-blue-600 ml-1"
                >(Auto)</span
              >
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
      </div>

      <!-- Right Column -->
      <div class="space-y-4">
        <!-- Gain Slider -->
        <div>
          <div class="flex justify-between items-center mb-1">
            <label class="text-sm font-semibold text-gray-700">Gain</label>
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

        <!-- Gamma Slider -->
        <div v-if="gammaSupported">
          <div class="flex justify-between items-center mb-1">
            <label class="text-sm font-semibold text-gray-700">Gamma</label>
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
      </div>
    </div>

    <!-- Live Camera Feed Section -->
    <div class="mt-4 pb-4 pt-2 border-t-2">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <h3 class="text-base font-bold text-gray-800 text-xl">
            Live Preview
          </h3>
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
          class="bg-red-500 text-white px-3 py-1.5 text-s rounded hover:bg-red-600 transition-colors font-medium shadow-sm"
        >
          Stop Feed
        </button>
      </div>
      <div
        class="bg-gray-900 rounded-xl overflow-hidden relative flex items-center justify-center shadow-2xl border-4 border-gray-300"
        style="aspect-ratio: 4/3; min-height: 400px"
      >
        <div
          v-if="isLoadingFeed"
          class="flex flex-col items-center justify-center gap-4 text-blue-400 w-full h-full p-8"
        >
          <div
            class="inline-block w-16 h-16 border-4 border-blue-400 border-t-transparent rounded-full animate-spin"
          ></div>
          <p class="text-lg font-semibold">Loading camera feed...</p>
        </div>
        <div
          v-else-if="feedError"
          class="flex flex-col items-center justify-center gap-4 text-red-400 w-full h-full p-8"
        >
          <span class="text-6xl mb-2">⚠️</span>
          <p class="text-base font-semibold text-center max-w-md">
            {{ feedError }}
          </p>
          <button
            @click="reconnectFeed"
            class="bg-blue-500 text-white px-6 py-3 text-base rounded-lg hover:bg-blue-700 transition-colors shadow-lg font-medium"
          >
            Reconnect
          </button>
        </div>
        <div
          v-else-if="!feedUrl"
          class="flex flex-col items-center justify-center gap-4 text-gray-400 w-full h-full p-8"
        >
          <p class="text-lg font-semibold">Camera feed not started</p>
          <button
            @click="startFeed"
            class="bg-blue-500 text-white px-6 py-3 text-base rounded-lg hover:bg-blue-700 transition-colors shadow-lg font-medium"
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

      <!-- Live Feed Info -->
      <div
        v-if="feedUrl && !feedError"
        class="mt-2 text-xs text-gray-500 text-center"
      >
        Live feed • Exposure: {{ exposure.toFixed(1) }}ms • Gain:
        {{ gain.toFixed(2) }}x
        <span v-if="gammaSupported"> • Gamma: {{ gamma.toFixed(2) }}</span>
      </div>
    </div> 
    
    <div class="flex gap-6">
      <!-- Capture Image Button -->
      <button
        @click="capture"
        :disabled="camera.isCapturing.value"
        class="w-full bg-blue-600 text-white px-4 py-3 rounded-lg cursor-pointer text-base font-bold transition-all hover:bg-blue-700 hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed shadow-md transform hover:scale-[1.01] active:scale-[0.99]"
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
          Capture Image
        </span>
      </button>

      <!-- Record Video Button -->
      <button
        @click="toggleRecording"
        :disabled="camera.isCapturing.value"
        :class="[
          'w-full px-4 py-3 rounded-lg cursor-pointer text-base font-bold transition-all hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed shadow-md transform hover:scale-[1.01] active:scale-[0.99]',
          isRecording
            ? 'bg-red-600 text-white hover:bg-red-700'
            : 'bg-green-600 text-white hover:bg-green-700',
        ]"
      >
        <span v-if="isRecording" class="flex items-center justify-center gap-2">
          <div
            class="inline-block w-3 h-3 bg-white rounded-sm animate-pulse"
          ></div>
          Stop Recording ({{ recordingTime.toFixed(0) }}s)
        </span>
        <span v-else class="flex items-center justify-center gap-2">
          Record Video
        </span>
      </button>
    </div>
  </div>
</template>

<style scoped>
/* Custom slider styling */
.slider::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
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
  width: 20px;
  height: 20px;
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
import apiClient from "@/api/client";

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
  }
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

async function performAutoExposureOnce() {
  try {
    store.addLog("Performing one-time auto-exposure...", "info");

    const API_BASE_URL =
      import.meta.env.VITE_API_BASE_URL || "http://localhost:3000";
    const response = await fetch(
      `${API_BASE_URL}/api/v1/camera/settings/auto-exposure/once`.replace(
        ":3000",
        ":8001"
      ),
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    const result = await response.json();

    if (result.success) {
      exposure.value = result.exposure;
      store.addLog(
        `Auto-exposure completed: ${result.exposure.toFixed(1)}ms`,
        "success"
      );
      await loadCameraSettings(); // Reload all settings
    } else {
      store.addLog("Auto-exposure failed", "error");
    }
  } catch (error: any) {
    store.addLog(`Auto-exposure error: ${error.message}`, "error");
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
    const response = await apiClient.get("/api/v1/microscope/light/status");
    store.updateLightStatus(response.data.isOn, response.data.brightness);

    if (!response.data.isOn) {
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
          console.log("Camera stream ready:", message);
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

    const API_BASE_URL =
      import.meta.env.VITE_API_BASE_URL || "http://localhost:3000";
    const response = await fetch(
      `${API_BASE_URL}/video/record/start?duration=30&playback_frame_rate=25&decimation=1`.replace(
        ":3000",
        ":8001"
      ),
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

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
        `Recording started: ${result.filename} (${result.duration}s max)`,
        "success"
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

    const API_BASE_URL =
      import.meta.env.VITE_API_BASE_URL || "http://localhost:3000";
    const response = await fetch(
      `${API_BASE_URL}/video/record/stop`.replace(":3000", ":8001"),
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    const result = await response.json();

    if (result.success) {
      isRecording.value = false;
      recordingTime.value = 0;
      recordingStartTime = null;

      store.addLog(
        `Video saved: ${result.filename} (${result.duration.toFixed(1)}s, ${(result.fileSize / 1024 / 1024).toFixed(2)}MB)`,
        "success"
      );
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
