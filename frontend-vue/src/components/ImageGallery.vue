<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold text-gray-800">Images</h2>
      
      <!-- Filter Toggle -->
      <div class="flex gap-2">
        <button 
          @click="photoFilter = 'mine'"
          :class="[
            'px-3 py-1.5 text-sm rounded transition-all',
            photoFilter === 'mine' 
              ? 'bg-blue-600 text-white font-medium' 
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          ]"
        >
          My Photos
        </button>
        <button 
          @click="photoFilter = 'all'"
          :class="[
            'px-3 py-1.5 text-sm rounded transition-all',
            photoFilter === 'all' 
              ? 'bg-blue-600 text-white font-medium' 
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          ]"
        >
          All Photos
        </button>
      </div>
    </div>

    <div class="grid grid-cols-[repeat(auto-fill,minmax(120px,1fr))] gap-2.5 max-h-96 overflow-y-auto">
      <div
        v-for="image in store.recentImages"
        :key="image.id"
        class="aspect-square bg-gray-200 rounded flex flex-col items-center justify-center text-sm text-gray-600 cursor-pointer hover:bg-gray-300 transition-colors relative"
        :title="`${image.filename}${image.user ? ` - by ${image.user.username}` : ''}`"
      >
        <span>{{ image.id }}</span>
        <div v-if="photoFilter === 'all' && image.user" class="absolute bottom-1 left-1 right-1 bg-black bg-opacity-60 text-white text-xs px-1 py-0.5 rounded truncate">
          {{ image.user.username }}
        </div>
      </div>
      <div v-if="store.images.length === 0" class="aspect-square bg-gray-200 rounded flex items-center justify-center text-sm text-gray-600">
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
