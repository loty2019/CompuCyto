<template>
  <div class="min-h-screen bg-slate-100">
    <header
      v-if="authStore.isAuthenticated"
      class="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur"
    >
      <div
        class="mx-auto flex max-w-screen-2xl flex-col gap-2 px-3 py-2 lg:flex-row lg:items-center lg:justify-between"
      >
        <div class="flex items-center justify-between gap-4">
          <div class="flex min-w-0 items-center gap-3">
            <img
              :src="linkLogo"
              alt="Link Biosystems logo"
              class="brand-logo-tile h-12 w-12 sm:h-14 sm:w-14"
            />
            <div class="min-w-0">
              <h1 class="text-2xl font-black tracking-tight text-slate-950">
                CytoCore
              </h1>
              <div
                class="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400"
              >
                LinkBiosystems
              </div>
            </div>
          </div>
          <span class="hidden text-sm text-slate-500 sm:inline">
            Hi, <strong>{{ authStore.currentUser?.username }}</strong>
          </span>
        </div>

        <div
          class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between lg:gap-4"
        >
          <StatusBar />
          <div class="hidden h-7 w-px bg-slate-300 sm:block"></div>
          <AppliancePowerMenu />
          <button
            @click="handleLogout"
            class="lab-button lab-button-secondary"
          >
            Switch Profile
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
import AppliancePowerMenu from "@/components/AppliancePowerMenu.vue";
import linkLogo from "@/assets/link-biosystems-logo.png";

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
