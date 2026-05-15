import { ref } from "vue";
import { controlAPI } from "@/api/client";
import { useMicroscopeStore } from "@/stores/microscope";

function stageErrorMessage(error: any) {
  return (
    error.response?.data?.message ||
    error.response?.data?.detail ||
    error.message
  );
}

export function useStage() {
  const store = useMicroscopeStore();
  const isMoving = ref(false);

  async function move(x?: number, y?: number, z?: number, relative = false) {
    isMoving.value = true;
    try {
      const result = await controlAPI.moveStage({ x, y, z, relative });
      if (result.limit_sensors) {
        store.updateLimitSensors(result.limit_sensors);
      }

      const pos = result.target_position ?? result.targetPosition;
      if (pos) {
        store.addLog(
          `Moving to X:${pos.x.toFixed(0)} Y:${pos.y.toFixed(0)} Z:${pos.z.toFixed(0)}`,
          "info",
        );
      } else {
        store.addLog("Stage move started", "info");
      }

      return result;
    } catch (error: any) {
      store.addLog(`Move failed: ${stageErrorMessage(error)}`, "error");
      throw error;
    } finally {
      isMoving.value = false;
    }
  }

  async function home() {
    isMoving.value = true;
    try {
      const result = await controlAPI.homeStage();
      if (result.limit_sensors) {
        store.updateLimitSensors(result.limit_sensors);
      }
      await updatePosition();
      store.addLog("Stage homed on optical sensors", "success");
    } catch (error: any) {
      store.addLog(`Home failed: ${stageErrorMessage(error)}`, "error");
      throw error;
    } finally {
      isMoving.value = false;
    }
  }

  async function stop() {
    try {
      const result = await controlAPI.emergencyStop();
      if (result.limit_sensors) {
        store.updateLimitSensors(result.limit_sensors);
      }
      store.addLog("Emergency stop activated!", "warning");
    } catch (error: any) {
      store.addLog(`Stop failed: ${stageErrorMessage(error)}`, "error");
      throw error;
    }
  }

  async function updatePosition() {
    try {
      const position = await controlAPI.getPosition();
      store.updatePosition(position);
    } catch (error: any) {
      console.error("Failed to update position:", error);
    }
  }

  async function updateLimitSensors() {
    try {
      const sensors = await controlAPI.getLimitSensors();
      store.updateLimitSensors(sensors);
    } catch (error: any) {
      console.error("Failed to update home sensors:", error);
    }
  }

  return {
    isMoving,
    move,
    home,
    stop,
    updatePosition,
    updateLimitSensors,
  };
}
