<template>
  <div class="mx-auto max-w-screen-2xl px-2 pb-3 pt-2 sm:px-3">
    <!-- Main Control Panel: prioritize camera preview with a compact control rail -->
    <div class="mb-3 grid grid-cols-1 gap-2 xl:grid-cols-[minmax(0,1fr)_300px] 2xl:grid-cols-[minmax(0,1fr)_320px]">
      <div id="camera" class="min-w-0">
        <CameraControl />
      </div>

      <aside class="flex min-w-0 flex-col gap-2 xl:sticky xl:top-20 xl:self-start">
        <IlluminationControl />
        <div id="stage"><StageControl /></div>
        <div id="map"><MicroscopeMap compact /></div>
      </aside>
    </div>

    <section class="mb-5 grid grid-cols-1 gap-2 xl:grid-cols-2">
      <div id="gallery" class="min-w-0"><ImageGallery /></div>
      <div id="video-gallery" class="min-w-0"><VideoGallery /></div>
    </section>
    <div id="jobs" class="mb-5"><JobManager /></div>
    <div id="console" class="mb-5"><ConsoleLog /></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { controlAPI } from "@/api/client";
import { useWebSocket } from "@/composables/useWebSocket";
import CameraControl from "@/components/CameraControl.vue";
import IlluminationControl from "@/components/IlluminationControl.vue";
import MicroscopeMap from "@/components/MicroscopeMap.vue";
import StageControl from "@/components/StageControl.vue";
import JobManager from "@/components/JobManager.vue";
import ImageGallery from "@/components/ImageGallery.vue";
import VideoGallery from "@/components/VideoGallery.vue";
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
