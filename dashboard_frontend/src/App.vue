<template>
  <div class="min-h-screen bg-slate-200">
    <header
      v-if="authStore.isAuthenticated"
      class="sticky top-0 z-30 border-b border-slate-200/80 bg-white/90 shadow-sm backdrop-blur"
    >
      <div
        class="mx-auto flex max-w-screen-xl flex-col gap-2 px-3 py-2 lg:flex-row lg:items-center lg:justify-between"
      >
        <div class="flex items-center justify-between gap-4">
          <div>
            <h1 class="text-2xl font-black tracking-tight text-slate-950">
              CytoCore
            </h1>
            <div
              class="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400"
            >
              LinkBiosystems
            </div>
          </div>
          <span class="hidden text-sm text-slate-500 sm:inline">
            Welcome, <strong>{{ authStore.currentUser?.username }}</strong>
          </span>
        </div>

        <div
          class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between lg:gap-4"
        >
          <StatusBar />
          <div class="hidden h-7 w-px bg-slate-300 sm:block"></div>
          <button
            @click="handleLogout"
            class="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-xs font-bold text-slate-700 transition-all hover:-translate-y-0.5 hover:border-red-300 hover:bg-red-50 hover:text-red-700 hover:shadow-sm"
          >
            Logout
          </button>
        </div>
      </div>
    </header>

    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import StatusBar from "@/components/StatusBar.vue";

const router = useRouter();
const authStore = useAuthStore();

onMounted(() => {
  authStore.initializeAuth();
});

const handleLogout = () => {
  authStore.logout();
  router.push("/login");
};
</script>
