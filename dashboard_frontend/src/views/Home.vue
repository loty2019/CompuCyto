<template>
  <div class="mx-auto max-w-screen-2xl px-2 pb-4 pt-2 sm:px-3">
    <!-- Main Control Panel: prioritize camera preview with a compact control rail -->
    <div class="main-control-grid mb-3 grid grid-cols-1 items-stretch gap-3">
      <CameraControl />

      <aside
        class="stage-map-column flex min-w-0 flex-col gap-3 xl:sticky xl:top-20 xl:self-start"
      >
        <div id="stage"><StageControl /></div>
        <div id="map"><MicroscopeMap compact /></div>
      </aside>
    </div>

    <section class="mb-3 grid grid-cols-1 gap-3 xl:grid-cols-2">
      <div id="gallery" class="min-w-0"><ImageGallery /></div>
      <div id="video-gallery" class="min-w-0"><VideoGallery /></div>
    </section>
    <div id="jobs" class="mb-4"><JobManager /></div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { controlAPI } from "@/api/client";
import { useWebSocket } from "@/composables/useWebSocket";
import CameraControl from "@/components/CameraControl.vue";
import MicroscopeMap from "@/components/MicroscopeMap.vue";
import StageControl from "@/components/StageControl.vue";
import JobManager from "@/components/JobManager.vue";
import ImageGallery from "@/components/ImageGallery.vue";
import VideoGallery from "@/components/VideoGallery.vue";

const store = useMicroscopeStore();

let healthPollInterval: ReturnType<typeof setInterval> | null = null;

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
  healthPollInterval = setInterval(async () => {
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

onBeforeUnmount(() => {
  if (healthPollInterval) {
    clearInterval(healthPollInterval);
  }
});
</script>

<style scoped>
#camera,
#stage,
#map,
#jobs,
#gallery {
  @apply scroll-mt-24;
}

@media (min-width: 1280px) {
  .main-control-grid {
    grid-template-columns: minmax(0, 1fr) 300px 320px;
  }
}
</style>
