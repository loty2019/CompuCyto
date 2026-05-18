import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "./assets/main.css";
import { useMicroscopeStore } from "./stores/microscope";
import type { LogEntry } from "./types";

const pinia = createPinia();
const app = createApp(App);

app.use(pinia);
app.use(router);

app.mount("#app");

setTimeout(() => {
  const microscopeStore = useMicroscopeStore();
  const originalConsoleWarn = console.warn.bind(console);
  const originalConsoleError = console.error.bind(console);

  window.__logToConsole = (message: string, type: LogEntry["type"]) => {
    microscopeStore.addLog(message, type);
  };

  console.warn = (...args: unknown[]) => {
    originalConsoleWarn(...args);
    microscopeStore.addLog(
      `Browser warning: ${formatConsoleArgs(args)}`,
      "warning",
    );
  };

  console.error = (...args: unknown[]) => {
    originalConsoleError(...args);
    microscopeStore.addLog(
      `Browser error: ${formatConsoleArgs(args)}`,
      "error",
    );
  };

  window.addEventListener("error", (event) => {
    microscopeStore.addLog(`Unhandled error: ${event.message}`, "error");
  });

  window.addEventListener("unhandledrejection", (event) => {
    microscopeStore.addLog(
      `Unhandled promise rejection: ${formatConsoleArgs([event.reason])}`,
      "error",
    );
  });

  microscopeStore.addLog("Application started", "success");
}, 0);

function formatConsoleArgs(args: unknown[]) {
  return args
    .map((arg) => {
      if (arg instanceof Error) {
        return arg.message;
      }

      if (typeof arg === "string") {
        return arg;
      }

      try {
        return JSON.stringify(arg);
      } catch {
        return String(arg);
      }
    })
    .join(" ");
}
