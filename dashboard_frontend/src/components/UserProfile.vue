<template>
  <div class="rounded-lg bg-white p-6 shadow-md">
    <h2 class="mb-4 text-2xl font-bold text-gray-900">Profile</h2>

    <div class="flex items-center gap-4">
      <div class="grid h-16 w-16 place-items-center rounded-full border border-slate-300 bg-slate-50 text-slate-700">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="h-8 w-8"
          aria-hidden="true"
        >
          <path d="M14 3h4v3h-4z" />
          <path d="M9 18h10" />
          <path d="M11 21h6" />
          <path d="M10 18a7 7 0 0 1 7-7" />
          <path d="M13 6l3 3-5 5-3-3z" />
          <path d="M6 14l4 4" />
        </svg>
      </div>
      <div>
        <p class="text-lg font-black text-gray-950">
          {{ authStore.currentUser?.username }}
        </p>
        <p class="text-sm font-semibold uppercase tracking-[0.16em] text-gray-500">
          {{ authStore.currentUser?.role }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>
