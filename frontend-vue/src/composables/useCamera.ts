import { ref } from "vue";
import { controlAPI } from "@/api/client";
import { useMicroscopeStore } from "@/stores/microscope";
import type { CaptureRequest } from "@/types";

export function useCamera() {
  const store = useMicroscopeStore();
  const isCapturing = ref(false);

  async function captureImage(params?: CaptureRequest) {
    isCapturing.value = true;
    try {
      const result = await controlAPI.captureImage({
        exposure: params?.exposure ?? store.cameraSettings.exposure,
        gain: params?.gain ?? store.cameraSettings.gain,
        gamma: params?.gamma ?? store.cameraSettings.gamma,
      });

      // Check for warnings in response
      if (result.warning) {
        store.addLog(`⚠️ Warning: ${result.warning}`, "warning");
      }

      // Check if database save failed
      if (result.success && !result.databaseSaved) {
        store.addLog("❌ Image captured but NOT saved to database!", "error");
        store.addLog(`Image file: ${result.filename}`, "info");
      } else if (result.success && result.databaseSaved) {
        store.addLog(
          `✅ Image captured and saved (DB ID: ${result.imageId})`,
          "success"
        );

        // Trigger image gallery reload after a short delay (to allow file to be written)
        setTimeout(() => {
          window.dispatchEvent(
            new CustomEvent("image-captured", {
              detail: { imageId: result.imageId, filename: result.filename },
            })
          );
        }, 500);
      }

      store.addLog(`📸 Image: ${result.filename}`, "info");
      return result;
    } catch (error: any) {
      store.addLog(`Capture failed: ${error.message}`, "error");
      throw error;
    } finally {
      isCapturing.value = false;
    }
  }

  async function updateSettings(settings: {
    exposure?: number;
    gain?: number;
    gamma?: number;
    autoExposure?: boolean;
  }) {
    try {
      await controlAPI.updateCameraSettings(settings);
      store.updateCameraSettings(settings);
      store.addLog("Camera settings updated", "success");
    } catch (error: any) {
      store.addLog(`Failed to update settings: ${error.message}`, "error");
      throw error;
    }
  }

  async function loadSettings() {
    try {
      const settings = await controlAPI.getCameraSettings();
      store.updateCameraSettings(settings);
    } catch (error: any) {
      store.addLog(`Failed to load settings: ${error.message}`, "error");
    }
  }

  return {
    isCapturing,
    captureImage,
    updateSettings,
    loadSettings,
  };
}
