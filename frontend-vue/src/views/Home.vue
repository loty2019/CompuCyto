<template>
  <div class="max-w-screen-xl mx-auto px-5 pb-5 pt-2">
    <header class="bg-white p-5 rounded-lg mb-2 shadow-md">
      <StatusBar />
    </header>

    <!-- Main Control Panel: Camera (left) + Stage & Map (right column) -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-2 mb-5">
      <!-- Camera Control - Takes up 2/3 on large screens -->
      <div id="camera" class="lg:col-span-2">
        <CameraControl />
      </div>

      <!-- Right Column - Stage + Map stacked vertically -->
      <div class="flex flex-col gap-2">
        <div id="stage"><StageControl /></div>
        <div id="map"><MicroscopeMap /></div>
      </div>
    </div>

    <div id="gallery" class="mb-5"><ImageGallery /></div>
    <div id="jobs" class="mb-5"><JobManager /></div>
    <div id="console" class="mb-5"><ConsoleLog /></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { controlAPI } from "@/api/client";
import { useWebSocket } from "@/composables/useWebSocket";
import StatusBar from "@/components/StatusBar.vue";
import CameraControl from "@/components/CameraControl.vue";
import StageControl from "@/components/StageControl.vue";
import MicroscopeMap from "@/components/MicroscopeMap.vue";
import JobManager from "@/components/JobManager.vue";
import ImageGallery from "@/components/ImageGallery.vue";
import ConsoleLog from "@/components/ConsoleLog.vue";

const store = useMicroscopeStore();

// Initialize WebSocket
useWebSocket();

onMounted(async () => {
  // Load initial status from health endpoint
  try {
    const health = await controlAPI.getHealth();
    // Map health check to system status
    store.updateSystemStatus({
      camera: health.checks.pythonCamera ? "connected" : "disconnected",
      stage: "connected", // TODO: Add separate stage health check if needed
      database: health.checks.database ? "connected" : "disconnected",
      raspberryPi: health.checks.raspberryPi ? "connected" : "disconnected",
      queue: "stopped", // TODO: Add queue status when available
    });
    store.addLog(`System health check: ${health.status}`, "success");
  } catch (error: any) {
    store.addLog(`Failed to load system status: ${error.message}`, "error");
    // Set all to disconnected on error
    store.updateSystemStatus({
      camera: "disconnected",
      stage: "disconnected",
      database: "disconnected",
      raspberryPi: "disconnected",
      queue: "stopped",
    });
  }

  // Poll health status every 10 seconds
  setInterval(async () => {
    try {
      const health = await controlAPI.getHealth();
      store.updateSystemStatus({
        camera: health.checks.pythonCamera ? "connected" : "disconnected",
        stage: "connected", // TODO: Add separate stage health check if needed
        database: health.checks.database ? "connected" : "disconnected",
        raspberryPi: health.checks.raspberryPi ? "connected" : "disconnected",
        queue: "stopped",
      });
    } catch (error) {
      // Silently fail on polling errors to avoid log spam
    }
  }, 10000);
});
</script>

<style scoped>
#camera,
#stage,
#map,
#jobs,
#gallery,
#console {
  @apply scroll-mt-24;
}
</style>
