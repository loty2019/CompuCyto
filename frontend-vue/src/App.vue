<template>
  <div class="min-h-screen bg-gray-100">
    <header v-if="authStore.isAuthenticated" class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-6">
            <div>
              <h1 class="text-5xl font-bold text-gray-900">🔬 CytoCore</h1>
              <span class="text-sm text-gray-500">LinkBiosystems</span>
            </div>
            <span class="text-base text-gray-600">
              Welcome, <strong>{{ authStore.currentUser?.username }}</strong>
            </span>
          </div>
          
          <nav class="flex items-center gap-2 border-l border-gray-300 pl-6">
            <button @click="scrollToSection('camera')" class="px-3 py-1.5 text-sm font-medium rounded-lg transition-all bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 hover:border-blue-300 hover:shadow-sm hover:-translate-y-0.5 active:bg-blue-200 active:translate-y-0">
              📷 Camera
            </button>
            <button @click="scrollToSection('stage')" class="px-3 py-1.5 text-sm font-medium rounded-lg transition-all bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 hover:border-blue-300 hover:shadow-sm hover:-translate-y-0.5 active:bg-blue-200 active:translate-y-0">
              🎯 Stage
            </button>
            <button @click="scrollToSection('map')" class="px-3 py-1.5 text-sm font-medium rounded-lg transition-all bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 hover:border-blue-300 hover:shadow-sm hover:-translate-y-0.5 active:bg-blue-200 active:translate-y-0">
              🗺️ Map
            </button>
            <button @click="scrollToSection('jobs')" class="px-3 py-1.5 text-sm font-medium rounded-lg transition-all bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 hover:border-blue-300 hover:shadow-sm hover:-translate-y-0.5 active:bg-blue-200 active:translate-y-0">
              💼 Jobs
            </button>
            <button @click="scrollToSection('gallery')" class="px-3 py-1.5 text-sm font-medium rounded-lg transition-all bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 hover:border-blue-300 hover:shadow-sm hover:-translate-y-0.5 active:bg-blue-200 active:translate-y-0">
              🖼️ Gallery
            </button>
            <button @click="scrollToSection('console')" class="px-3 py-1.5 text-sm font-medium rounded-lg transition-all bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 hover:border-blue-300 hover:shadow-sm hover:-translate-y-0.5 active:bg-blue-200 active:translate-y-0">
              📝 Console
            </button>
          </nav>
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

onMounted(() => {
  authStore.initializeAuth()
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const scrollToSection = (sectionId: string) => {
  const element = document.getElementById(sectionId)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}
</script>
