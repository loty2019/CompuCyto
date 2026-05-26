<template>
  <div ref="menuRoot" class="relative">
    <button
      type="button"
      class="flex h-8 w-8 items-center justify-center rounded-md border border-slate-300 bg-white text-base font-bold leading-none text-slate-700 shadow-sm transition hover:border-slate-400 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-teal-500/40"
      title="Appliance power controls"
      aria-label="Appliance power controls"
      :aria-expanded="isOpen"
      @click="isOpen = !isOpen"
    >
      ⏻
    </button>

    <div
      v-if="isOpen"
      class="absolute right-0 top-full z-50 mt-2 w-56 rounded-md border border-slate-200 bg-white p-2 text-xs shadow-lg"
    >
      <div
        v-if="message"
        class="mb-2 rounded border border-slate-200 bg-slate-50 px-2 py-1 text-slate-600"
      >
        {{ message }}
      </div>

      <template v-if="pendingAction === 'shutdown'">
        <div class="mb-2 font-semibold text-red-700">Shut down system?</div>
        <div class="flex gap-2">
          <button
            type="button"
            class="lab-button flex-1 bg-red-600 text-white hover:bg-red-700"
            :disabled="isBusy"
            @click="runShutdown"
          >
            Confirm
          </button>
          <button
            type="button"
            class="lab-button lab-button-secondary flex-1"
            :disabled="isBusy"
            @click="pendingAction = null"
          >
            Cancel
          </button>
        </div>
      </template>

      <template v-else-if="pendingAction">
        <div class="mb-2 font-semibold text-slate-800">
          Restart {{ pendingAction === "restart-pi" ? "Pi" : "this PC" }}?
        </div>
        <div class="flex gap-2">
          <button
            type="button"
            class="lab-button flex-1 bg-amber-500 text-white hover:bg-amber-600"
            :disabled="isBusy"
            @click="runRestart"
          >
            Confirm
          </button>
          <button
            type="button"
            class="lab-button lab-button-secondary flex-1"
            :disabled="isBusy"
            @click="pendingAction = null"
          >
            Cancel
          </button>
        </div>
      </template>

      <template v-else>
        <button
          type="button"
          class="mb-1 flex w-full items-center gap-2 rounded border border-red-200 bg-red-50 px-2 py-1.5 font-semibold text-red-700 hover:bg-red-100"
          :disabled="isBusy"
          @click="pendingAction = 'shutdown'"
        >
          <span class="flex h-5 w-5 items-center justify-center rounded bg-red-100 text-sm">⏻</span>
          <span>Shut down</span>
        </button>
        <div class="grid grid-cols-2 gap-1">
          <button
            type="button"
            class="rounded border border-slate-200 px-2 py-1.5 font-semibold text-slate-700 hover:bg-slate-50"
            :disabled="isBusy"
            @click="pendingAction = 'restart-pi'"
          >
            Restart Pi
          </button>
          <button
            type="button"
            class="rounded border border-slate-200 px-2 py-1.5 font-semibold text-slate-700 hover:bg-slate-50"
            :disabled="isBusy"
            @click="pendingAction = 'restart-windows'"
          >
            Restart PC
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { controlAPI } from "@/api/client";

type PendingAction = "shutdown" | "restart-pi" | "restart-windows" | null;

const isOpen = ref(false);
const isBusy = ref(false);
const pendingAction = ref<PendingAction>(null);
const message = ref("");
const menuRoot = ref<HTMLElement | null>(null);

onMounted(() => {
  document.addEventListener("pointerdown", handleOutsideClick);
});

onUnmounted(() => {
  document.removeEventListener("pointerdown", handleOutsideClick);
});

async function runShutdown() {
  await runAction("Shutting down Pi, then Windows...", () =>
    controlAPI.shutdownAppliance(),
  );
}

async function runRestart() {
  const action = pendingAction.value;
  if (action === "restart-pi") {
    await runAction("Restarting Pi...", () => controlAPI.restartPi());
  } else if (action === "restart-windows") {
    await runAction("Restarting Windows...", () => controlAPI.restartWindows());
  }
}

async function runAction(
  busyMessage: string,
  action: () => Promise<{ success: boolean; message: string }>,
) {
  isBusy.value = true;
  message.value = busyMessage;

  try {
    const result = await action();
    message.value = result.message;
    pendingAction.value = null;
  } catch (error: any) {
    message.value =
      error?.response?.data?.message || error?.message || "Power action failed.";
  } finally {
    isBusy.value = false;
  }
}

function handleOutsideClick(event: PointerEvent) {
  if (!menuRoot.value?.contains(event.target as Node)) {
    isOpen.value = false;
    pendingAction.value = null;
  }
}
</script>
