<template>
  <div class="profile-card bg-white p-6 rounded-lg shadow-md">
    <h2 class="text-2xl font-bold text-gray-900 mb-4">User Profile</h2>
    
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700">Email</label>
        <p class="mt-1 text-gray-900">{{ authStore.currentUser?.email }}</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">Username</label>
        <p class="mt-1 text-gray-900">{{ authStore.currentUser?.username }}</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">Role</label>
        <span class="mt-1 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
          {{ authStore.currentUser?.role }}
        </span>
      </div>

      <div v-if="authStore.currentUser?.profile?.fullName">
        <label class="block text-sm font-medium text-gray-700">Full Name</label>
        <p class="mt-1 text-gray-900">{{ authStore.currentUser.profile.fullName }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>
