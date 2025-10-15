<template>
  <div id="app">
    <!-- Header with logout button (only shown when authenticated) -->
    <header v-if="authStore.isAuthenticated" class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <div class="flex items-center gap-6">
          <div class="flex items-center">
        <div class="flex flex-col">
            <h1 class="text-5xl font-bold text-gray-900">🔬 CytoCore</h1>
          <span class="text-sm pl-48 text-gray-500">LinkBiosystems</span>
        </div>
        <span class="ml-6 pt-2 text-m text-gray-600">
          Welcome, <strong>{{ authStore.currentUser?.username }}</strong>
        </span>
          </div>
          
          <!-- Quick Navigation Buttons -->
          <div class="flex items-center gap-2 border-gray-300 pl-6 ml-4">
        <button @click="scrollToSection('camera')" class="nav-btn">📷 Camera</button>
        <button @click="scrollToSection('stage')" class="nav-btn">🎯 Stage</button>
        <button @click="scrollToSection('map')" class="nav-btn">🗺️ Map</button>
        <button @click="scrollToSection('jobs')" class="nav-btn">💼 Jobs</button>
        <button @click="scrollToSection('gallery')" class="nav-btn">🖼️ Gallery</button>
        <button @click="scrollToSection('console')" class="nav-btn">📝 Console</button>
          </div>
        </div>
        
        <button
          @click="handleLogout"
          class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors"
        >
          Logout
        </button>
      </div>
    </header>

    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Initialize auth from localStorage on app mount
onMounted(() => {
  authStore.initializeAuth()
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// Scroll to section smoothly
const scrollToSection = (sectionId: string) => {
  const element = document.getElementById(sectionId)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  background: #f5f5f5;
}

.nav-btn {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.5rem;
  transition: all 0.2s;
  background-color: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
  cursor: pointer;
}

.nav-btn:hover {
  background-color: #dbeafe;
  border-color: #93c5fd;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  transform: translateY(-1px);
}

.nav-btn:active {
  background-color: #bfdbfe;
  transform: translateY(0);
}
</style>
