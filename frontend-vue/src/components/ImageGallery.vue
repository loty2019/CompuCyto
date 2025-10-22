<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
      <h2 class="text-xl font-bold text-gray-800">
        Images
      </h2>
      <span class="text-sm text-gray-600 px-1 border border-gray-300">
         {{ store.recentImages.length }}
      </span>
      </div>
      <!-- Filter Toggle -->
      <div class="flex gap-2">
        <button
          @click="photoFilter = 'mine'"
          :class="[
            'px-3 py-1.5 text-sm rounded transition-all',
            photoFilter === 'mine'
              ? 'bg-blue-600 text-white font-medium'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300',
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
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300',
          ]"
        >
          All Photos
        </button>
        <div class="border-l border-gray-300 mx-1"></div>
        <button
          @click="cleanupMode = !cleanupMode"
          :class="[
            'px-3 py-1.5 text-sm rounded transition-all',
            cleanupMode
              ? 'bg-red-600 text-white font-medium'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300',
          ]"
          :title="
            cleanupMode
              ? 'Exit cleanup mode'
              : 'Enable cleanup mode to delete images'
          "
        >
          {{ cleanupMode ? "Exit Cleanup" : "🧹 Cleanup" }}
        </button>
      </div>
    </div>

    <!-- Cleanup Mode Warning -->
    <div
      v-if="cleanupMode"
      class="mb-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700 flex items-center gap-2"
    >
      <span class="text-lg">⚠️</span>
      <span>Cleanup mode active (Deleting images is permanent)</span>
    </div>

    <div v-if="loading" class="flex items-center justify-center p-8">
      <div class="text-gray-500">Loading images...</div>
    </div>

    <div
      v-else
      class="grid grid-cols-[repeat(auto-fill,minmax(120px,1fr))] gap-2.5 max-h-96 overflow-y-auto"
    >
      <div
        v-for="image in store.recentImages"
        :key="image.id"
        class="aspect-square bg-gray-200 rounded flex flex-col items-center justify-center text-sm text-gray-600 cursor-pointer hover:bg-gray-300 transition-colors relative"
        :title="`${image.filename}${image.user ? ` - by ${image.user.username}` : ''}`"
      >
        <!-- Actual Image -->
        <img
          :src="`http://localhost:8001/captures/${image.filename}`"
          :alt="image.filename"
          class="w-full h-full object-cover cursor-pointer rounded-md"
          @error="handleImageError($event)"
        />

        <!-- delete button (only in cleanup mode) -->
        <div
          v-if="cleanupMode"
          class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-70 transition-all flex flex-col items-center justify-center gap-2"
        >
          <!-- Username -->
          <div
            v-if="image.user"
            class="opacity-0 group-hover:opacity-100 text-white text-sm font-medium transition-opacity"
          >
            {{ image.user.username }}
          </div>

          <!-- Delete button -->
          <button
            @click="deleteImage(image.id)"
            class="opacity-1 group-hover:opacity-100 bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded text-xs font-medium transition-all"
          >
            Delete
          </button>
        </div>

        <!-- Info overlay when NOT in cleanup mode -->
        <div
          v-else
          class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-60 transition-all flex items-center justify-center"
        >
          <div
            v-if="image.user"
            class="opacity-0 group-hover:opacity-100 text-white text-sm font-medium transition-opacity"
          >
            {{ image.user.username }}
          </div>
        </div>

        <!-- Username label at bottom (for "All Photos") -->
        <div
          v-if="photoFilter === 'all' && image.user"
          class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-70 text-white text-xs px-2 py-1 truncate"
        >
          {{ image.user.username }}
        </div>
      </div>
      <div
        v-if="store.recentImages.length === 0"
        class="col-span-full aspect-square bg-gray-100 rounded flex items-center justify-center text-sm text-gray-500"
      >
        No images found
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { imageAPI } from "@/api/client";

const store = useMicroscopeStore();
const photoFilter = ref<"mine" | "all">("mine");
const loading = ref(false);
const cleanupMode = ref(false);

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  console.error("❌ Failed to load image:", img.src);
  // Show a placeholder or the filename if image fails to load
  img.style.display = "none";
  const parent = img.parentElement;
  if (parent) {
    parent.classList.add(
      "flex",
      "items-center",
      "justify-center",
      "flex-col",
      "text-center",
      "p-2"
    );
    const filename = img.alt;
    parent.innerHTML += `<span class="text-xs text-gray-500 break-all">${filename}</span>`;
  }
};

const deleteImage = async (imageId: number) => {
  if (!confirm("Are you sure you want to delete this image?")) {
    return;
  }

  try {
    store.addLog(`Deleting image ${imageId}...`, "info");
    await imageAPI.deleteImage(imageId);
    store.addLog(`Image ${imageId} deleted successfully`, "success");
    // Reload images
    await loadImages();
  } catch (error: any) {
    console.error("❌ Failed to delete image:", error);
    store.addLog(`Failed to delete image: ${error.message}`, "error");
  }
};

const loadImages = async () => {
  loading.value = true;
  try {
    console.log("🔍 [FRONTEND] Loading images with filter:", photoFilter.value);
    store.addLog(
      `Loading ${photoFilter.value === "mine" ? "your" : "all"} images from database...`,
      "info"
    );
    const result = await imageAPI.listImages({
      limit: 20,
      page: 1,
      filter: photoFilter.value,
    });
    console.log("📸 [FRONTEND] Received images:", {
      filter: photoFilter.value,
      count: result.images.length,
      total: result.total,
      images: result.images.map((img) => ({
        id: img.id,
        filename: img.filename,
        username: img.user?.username,
      })),
    });
    store.setImages(result.images);
    store.addLog(
      `Loaded ${result.images.length} images (${result.total} total)`,
      "success"
    );
  } catch (error: any) {
    console.error("❌ [FRONTEND] Failed to load images:", error);
    store.addLog(`Failed to load images: ${error.message}`, "error");
  } finally {
    loading.value = false;
  }
};

// Listen for image capture events
const handleImageCaptured = (event: Event) => {
  const customEvent = event as CustomEvent;
  const { imageId, filename } = customEvent.detail;
  console.log("🎯 Image captured event received:", { imageId, filename });
  store.addLog("📸 New image captured, refreshing gallery...", "info");
  // Reload images after capture
  loadImages();
};

onMounted(() => {
  loadImages();
  // Add event listener for image captures
  window.addEventListener("image-captured", handleImageCaptured);
});

onUnmounted(() => {
  // Clean up event listener
  window.removeEventListener("image-captured", handleImageCaptured);
});

// Reload images when filter changes
watch(photoFilter, () => {
  loadImages();
});
</script>
