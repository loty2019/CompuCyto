<template>
  <div class="bg-white p-5 rounded-lg shadow-md">
    <h2 class="text-xl font-bold mb-4 text-gray-900">Camera Control</h2>

    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-1"
        >Exposure (ms)</label
      >
      <input
        type="number"
        v-model.number="exposure"
        min="1"
        max="1000"
        @change="updateSettings"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>

    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-1">Gain</label>
      <input
        type="number"
        v-model.number="gain"
        min="0.1"
        max="10"
        step="0.1"
        @change="updateSettings"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>

    <!-- Live Camera Feed Section -->
    <div class="my-4 pb-4 border-b border-gray-200">
      <h3 class="text-base font-semibold text-gray-700 mb-3 pb-2 border-b-2">
        Live Feed
      </h3>
      <div
        class="bg-gray-900 rounded-lg overflow-hidden relative flex items-center justify-center shadow-lg"
        style="aspect-ratio: 16/9"
      >
        <div
          v-if="isLoadingFeed"
          class="flex flex-col items-center justify-center gap-3 text-blue-400 w-full h-full"
        >
          <div
            class="inline-block w-8 h-8 border-4 border-blue-400 border-t-transparent rounded-full animate-spin"
          ></div>
          <p class="text-sm font-medium">Loading camera feed...</p>
        </div>
        <div
          v-else-if="feedError"
          class="flex flex-col items-center justify-center gap-3 text-red-400 w-full h-full"
        >
          <span class="text-4xl mb-2">⚠️</span>
          <p class="text-sm font-medium">{{ feedError }}</p>
          <button
            @click="reconnectFeed"
            class="bg-blue-500 text-white px-3 py-1 text-sm rounded hover:bg-blue-700 transition-colors"
          >
            Reconnect
          </button>
        </div>
        <div
          v-else-if="!feedUrl"
          class="flex flex-col items-center justify-center gap-3 text-gray-400 w-full h-full"
        >
          <!-- <span class="text-4xl mb-2">📷</span> -->
          <p class="text-sm font-medium">Camera feed not available</p>
          <button
            @click="startFeed"
            class="bg-blue-500 text-white px-3 py-1 text-sm rounded hover:bg-blue-700 transition-colors"
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
    </div>

    <button
      @click="capture"
      :disabled="camera.isCapturing.value"
      class="w-full bg-blue-500 text-white px-5 py-2.5 rounded cursor-pointer text-sm font-medium transition-colors hover:bg-blue-600 disabled:opacity-60 disabled:cursor-not-allowed"
    >
      {{ camera.isCapturing.value ? "Capturing..." : "Capture Image" }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { useCamera } from "@/composables/useCamera";

const store = useMicroscopeStore();
const camera = useCamera();

const exposure = ref(100);
const gain = ref(1.0);

const feedUrl = ref("");
const isLoadingFeed = ref(false);
const feedError = ref("");
let websocket: WebSocket | null = null;
let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
const isConnecting = ref(false);

onMounted(async () => {
  await camera.loadSettings();
  exposure.value = store.cameraSettings.exposure;
  gain.value = store.cameraSettings.gain;

  // Auto-start the feed
  //startFeed();
});

onUnmounted(() => {
  stopFeed();
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
  }
});

async function updateSettings() {
  await camera.updateSettings({
    exposure: exposure.value,
    gain: gain.value,
  });
}

async function capture() {
  await camera.captureImage({
    exposure: exposure.value,
    gain: gain.value,
  });
}

function startFeed() {
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
      console.log("WebSocket connected");
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
  console.log("Stopping feed...");

  // Clear reconnection timeout
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
    reconnectTimeout = null;
  }

  // Close WebSocket
  if (websocket) {
    websocket.onclose = null; // Prevent auto-reconnect
    websocket.close();
    websocket = null;
  }

  feedUrl.value = "";
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
</script>
