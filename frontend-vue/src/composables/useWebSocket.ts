import { ref, onMounted, onUnmounted } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { useWebSocketStore } from "@/stores/websocket";
import type { WSMessage } from "@/types";
import { io, Socket } from "socket.io-client";

export function useWebSocket() {
  const microscopeStore = useMicroscopeStore();
  const wsStore = useWebSocketStore();

  const socket = ref<Socket | null>(null);
  // Connect to NestJS backend on port 3000 with /ws namespace
  const WS_URL = import.meta.env.VITE_WS_URL || "http://localhost:3000";

  function connect() {
    if (socket.value?.connected) {
      return;
    }

    try {
      socket.value = io(WS_URL, {
        path: "/socket.io",
        transports: ["websocket", "polling"],
        reconnection: true,
        reconnectionDelay: 5000,
        reconnectionAttempts: 5,
      });

      socket.value.on("connect", () => {
        wsStore.setConnected(true);
        wsStore.resetReconnectAttempts();
        microscopeStore.addLog("WebSocket connected", "success");
      });

      socket.value.on("message", (message: WSMessage) => {
        handleMessage(message);
      });

      socket.value.on("status", (data: any) => {
        handleMessage({ type: "status", data });
      });

      socket.value.on("disconnect", () => {
        wsStore.setConnected(false);
        microscopeStore.addLog("WebSocket disconnected", "error");
      });

      socket.value.on("connect_error", (error) => {
        console.error("WebSocket connection error:", error);
        wsStore.incrementReconnectAttempts();
        if (!wsStore.canReconnect()) {
          microscopeStore.addLog("WebSocket connection failed", "error");
        }
      });
    } catch (error) {
      console.error("Failed to connect WebSocket:", error);
      microscopeStore.addLog("Failed to connect WebSocket", "error");
    }
  }

  function disconnect() {
    if (socket.value) {
      socket.value.disconnect();
      socket.value = null;
    }
  }

  function send(data: any) {
    if (socket.value?.connected) {
      socket.value.emit("message", data);
    }
  }

  function handleMessage(message: WSMessage) {
    switch (message.type) {
      case "position":
        microscopeStore.updatePosition(message.data);
        break;

      case "job_progress":
        microscopeStore.updateJob(message.data.job_id, {
          progress: message.data.progress,
          total_steps: message.data.total_steps,
          status: message.data.status as any,
        });
        microscopeStore.addLog(
          `Job ${message.data.job_id}: ${message.data.progress}/${message.data.total_steps}`,
          "info"
        );
        break;

      case "image_captured":
        microscopeStore.addLog(
          `Image captured: ${message.data.filename}`,
          "success"
        );
        // Optionally refresh image list
        break;

      case "status":
        microscopeStore.updateSystemStatus({
          camera: message.data.camera,
          stage: message.data.stage,
        });
        break;

      case "error":
        microscopeStore.addLog(
          `${message.data.component}: ${message.data.message}`,
          "error"
        );
        break;

      case "echo":
        // Echo response - can be used for testing
        break;
    }
  }

  onMounted(() => {
    connect();
  });

  onUnmounted(() => {
    disconnect();
  });

  return {
    isConnected: () => wsStore.state.isConnected,
    connect,
    disconnect,
    send,
  };
}
