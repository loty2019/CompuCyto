<template>
  <div class="card">
    <div class="header-section">
      <h2>🖼️ Recent Images</h2>
      
      <!-- Filter Toggle -->
      <div class="filter-toggle">
        <button 
          :class="{ active: photoFilter === 'mine' }"
          @click="photoFilter = 'mine'"
          class="filter-btn"
        >
          My Photos
        </button>
        <button 
          :class="{ active: photoFilter === 'all' }"
          @click="photoFilter = 'all'"
          class="filter-btn"
        >
          All Photos
        </button>
      </div>
    </div>

    <div class="image-gallery">
      <div
        v-for="image in store.recentImages"
        :key="image.id"
        class="image-item"
        :title="`${image.filename}${image.user ? ` - by ${image.user.username}` : ''}`"
      >
        <span>{{ image.id }}</span>
        <div v-if="photoFilter === 'all' && image.user" class="user-badge">
          {{ image.user.username }}
        </div>
      </div>
      <div v-if="store.images.length === 0" class="image-item empty">
        No images
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useMicroscopeStore } from '@/stores/microscope'
import { imageAPI } from '@/api/client'

const store = useMicroscopeStore()
const photoFilter = ref<'mine' | 'all'>('mine')

const loadImages = async () => {
  try {
    const result = await imageAPI.listImages({ 
      limit: 20,
      filter: photoFilter.value 
    })
    store.setImages(result.images)
  } catch (error: any) {
    store.addLog(`Failed to load images: ${error.message}`, 'error')
  }
}

onMounted(() => {
  loadImages()
})

// Reload images when filter changes
watch(photoFilter, () => {
  loadImages()
})
</script>

<style scoped>
.header-section {
  @apply flex items-center justify-between mb-4;
}

.filter-toggle {
  @apply flex gap-2;
}

.filter-btn {
  @apply px-3 py-1.5 text-sm rounded transition-all;
  @apply bg-gray-200 text-gray-700;
}

.filter-btn:hover {
  @apply bg-gray-300;
}

.filter-btn.active {
  @apply bg-blue-600 text-white font-medium;
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  @apply gap-2.5 max-h-96 overflow-y-auto;
}

.image-item {
  @apply aspect-square bg-gray-200 rounded flex flex-col items-center justify-center text-sm text-gray-600 cursor-pointer transition-colors relative;
}

.image-item:hover:not(.empty) {
  @apply bg-gray-300;
}

.image-item.empty {
  @apply cursor-default;
}

.user-badge {
  @apply absolute bottom-1 left-1 right-1 bg-black bg-opacity-60 text-white text-xs px-1 py-0.5 rounded truncate;
}
</style>
