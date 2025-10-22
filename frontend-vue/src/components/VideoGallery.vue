<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold text-gray-800">Videos</h2>

      <!-- Filter Toggle -->
      <div class="flex gap-2">
        <button
          @click="videoFilter = 'mine'"
          :class="[
            'px-3 py-1.5 text-sm rounded transition-all',
            videoFilter === 'mine'
              ? 'bg-blue-600 text-white font-medium'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300',
          ]"
        >
          My Videos
        </button>
        <button
          @click="videoFilter = 'all'"
          :class="[
            'px-3 py-1.5 text-sm rounded transition-all',
            videoFilter === 'all'
              ? 'bg-blue-600 text-white font-medium'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300',
          ]"
        >
          All Videos
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
              : 'Enable cleanup mode to delete videos'
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
      <span>Cleanup mode active (Deleting videos is permanent)</span>
    </div>

    <div v-if="loading" class="flex items-center justify-center p-8">
      <div class="text-gray-500">Loading videos...</div>
    </div>

    <div
      v-else
      class="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-3 max-h-96 overflow-y-auto"
    >
      <div
        v-for="video in store.recentVideos"
        :key="video.id"
        class="aspect-video bg-gray-900 rounded flex flex-col items-center justify-center text-sm text-gray-300 cursor-pointer hover:ring-2 hover:ring-blue-500 transition-all relative group"
        :title="`${video.filename}${video.user ? ` - by ${video.user.username}` : ''}`"
        @click="!cleanupMode && playVideo(video)"
      >
        <!-- Video Thumbnail or Placeholder -->
        <video
          v-if="video.thumbnailPath"
          :src="`http://localhost:3000${video.thumbnailPath}`"
          class="w-full h-full object-cover cursor-pointer rounded-md"
          preload="metadata"
        />
        <div
          v-else
          class="flex flex-col items-center justify-center p-2 pointer-events-none"
        >
          <svg
            class="w-12 h-12 text-gray-400 mb-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
          <span class="text-xs text-center break-all px-2">{{
            video.filename
          }}</span>
        </div>

        <!-- Duration Badge -->
        <div
          v-if="video.duration"
          class="absolute top-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-0.5 rounded pointer-events-none"
        >
          {{ formatDuration(video.duration) }}
        </div>

        <!-- File Size Badge -->
        <div
          v-if="video.fileSize"
          class="absolute top-2 left-2 bg-black bg-opacity-75 text-white text-xs px-2 py-0.5 rounded pointer-events-none"
        >
          {{ formatFileSize(video.fileSize) }}
        </div>

        <!-- Delete button (only in cleanup mode) -->
        <div
          v-if="cleanupMode"
          class="absolute inset-0 bg-black bg-opacity-50 group-hover:bg-opacity-70 transition-all flex flex-col items-center justify-center gap-2"
        >
          <!-- Delete button -->
          <button
            @click.stop="deleteVideo(video.id)"
            class="bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded text-xs font-medium transition-all"
          >
            Delete
          </button>
        </div>

        <!-- Username label at bottom (for "All Videos") -->
        <div
          v-if="videoFilter === 'all' && video.user"
          class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-70 text-white text-xs px-2 py-1 truncate pointer-events-none"
        >
          {{ video.user.username }}
        </div>
      </div>
      <div
        v-if="store.recentVideos.length === 0"
        class="col-span-full aspect-video bg-gray-100 rounded flex items-center justify-center text-sm text-gray-500"
      >
        No videos found
      </div>
    </div>

    <!-- Video Player Modal -->
    <div
      v-if="selectedVideo"
      class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
      @click="closeVideo"
    >
      <div
        class="bg-gray-900 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-auto"
        @click.stop
      >
        <div
          class="p-4 border-b border-gray-700 flex justify-between items-center"
        >
          <h3 class="text-white font-medium">{{ selectedVideo.filename }}</h3>
          <div class="flex gap-2 items-center">
            <a
              :href="`http://localhost:8001/videos/${selectedVideo.filename}`"
              :download="selectedVideo.filename"
              class="text-blue-400 hover:text-blue-300 text-sm px-3 py-1 bg-gray-800 rounded hover:bg-gray-700 transition-colors flex items-center gap-1"
              @click.stop
            >
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Download
            </a>
            <button
              @click="closeVideo"
              class="text-gray-400 hover:text-white text-2xl leading-none px-2"
            >
              ×
            </button>
          </div>
        </div>
        <div class="p-4">
          <video
            :src="`http://localhost:8001/videos/${selectedVideo.filename}`"
            controls
            autoplay
            class="w-full rounded"
          />
          <div class="mt-4 text-sm text-gray-400 space-y-1">
            <div v-if="selectedVideo.duration">
              Duration: {{ formatDuration(selectedVideo.duration) }}
            </div>
            <div v-if="selectedVideo.fileSize">
              Size: {{ formatFileSize(selectedVideo.fileSize) }}
            </div>
            <div v-if="selectedVideo.width && selectedVideo.height">
              Resolution: {{ selectedVideo.width }}×{{ selectedVideo.height }}
            </div>
            <div v-if="selectedVideo.capturedAt">
              Recorded: {{ formatDate(selectedVideo.capturedAt) }}
            </div>
            <div v-if="selectedVideo.user">
              By: {{ selectedVideo.user.username }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { videoAPI } from "@/api/client";
import type { Video } from "@/types";

const store = useMicroscopeStore();
const videoFilter = ref<"mine" | "all">("mine");
const loading = ref(false);
const cleanupMode = ref(false);
const selectedVideo = ref<Video | null>(null);

const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
};

const formatFileSize = (bytes: number | null): string => {
  if (!bytes) return "Unknown";
  const mb = bytes / (1024 * 1024);
  if (mb >= 1) {
    return `${mb.toFixed(1)} MB`;
  }
  return `${(bytes / 1024).toFixed(1)} KB`;
};

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString();
};

const playVideo = (video: Video) => {
  selectedVideo.value = video;
};

const closeVideo = () => {
  selectedVideo.value = null;
};

const deleteVideo = async (videoId: number) => {
  if (!confirm("Are you sure you want to delete this video?")) {
    return;
  }

  try {
    store.addLog(`Deleting video ${videoId}...`, "info");
    await videoAPI.deleteVideo(videoId);
    store.addLog(`Video ${videoId} deleted successfully`, "success");
    // Reload videos
    await loadVideos();
  } catch (error: any) {
    console.error("❌ Failed to delete video:", error);
    store.addLog(`Failed to delete video: ${error.message}`, "error");
  }
};

const loadVideos = async () => {
  loading.value = true;
  try {
    console.log("🔍 [FRONTEND] Loading videos with filter:", videoFilter.value);
    store.addLog(
      `Loading ${videoFilter.value === "mine" ? "your" : "all"} videos from database...`,
      "info"
    );
    const result = await videoAPI.listVideos({
      limit: 20,
      page: 1,
      filter: videoFilter.value,
    });
    console.log("🎬 [FRONTEND] Received videos:", {
      filter: videoFilter.value,
      count: result.videos.length,
      total: result.total,
      videos: result.videos.map((vid) => ({
        id: vid.id,
        filename: vid.filename,
        username: vid.user?.username,
      })),
    });
    store.setVideos(result.videos);
    store.addLog(
      `Loaded ${result.videos.length} videos (${result.total} total)`,
      "success"
    );
  } catch (error: any) {
    console.error("❌ [FRONTEND] Failed to load videos:", error);
    store.addLog(`Failed to load videos: ${error.message}`, "error");
  } finally {
    loading.value = false;
  }
};

// Listen for video recording events
const handleVideoRecorded = (event: Event) => {
  const customEvent = event as CustomEvent;
  const { videoId, filename } = customEvent.detail;
  console.log("🎯 Video recorded event received:", { videoId, filename });
  store.addLog("🎬 New video recorded, refreshing gallery...", "info");
  // Reload videos after recording
  loadVideos();
};

onMounted(() => {
  loadVideos();
  // Add event listener for video recordings
  window.addEventListener("video-recorded", handleVideoRecorded);
});

onUnmounted(() => {
  // Clean up event listener
  window.removeEventListener("video-recorded", handleVideoRecorded);
});

// Reload videos when filter changes
watch(videoFilter, () => {
  loadVideos();
});
</script>
