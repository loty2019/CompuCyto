<template>
  <div class="lab-panel">
    <div class="lab-panel-header">
      <div class="flex items-center gap-3">
        <h2 class="lab-title">Videos</h2>
        <span class="lab-count">{{ visibleVideos.length }}</span>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <div class="lab-segment-group">
          <button
            @click="videoFilter = 'mine'"
            :class="['lab-segment', videoFilter === 'mine' ? 'lab-segment-active' : '']"
          >
            Mine
          </button>
          <button
            @click="videoFilter = 'all'"
            :class="['lab-segment', videoFilter === 'all' ? 'lab-segment-active' : '']"
          >
            All
          </button>
        </div>
        <button
          @click="likedOnly = !likedOnly"
          :class="[
            'lab-liked-filter',
            likedOnly ? 'is-active' : '',
          ]"
          :aria-label="likedOnly ? 'Show all videos' : 'Show liked videos'"
          :aria-pressed="likedOnly"
        >
          <span class="lab-liked-heart" aria-hidden="true">&#9829;</span>
          <span class="lab-liked-count" aria-hidden="true">
            {{ favoriteCount }}
          </span>
          <span class="sr-only">
            {{ likedOnly ? "Show all videos" : "Show liked videos" }}
          </span>
        </button>
        <button
          @click="toggleSelectionMode"
          :class="[
            'lab-button',
            'lab-button-primary',
          ]"
          :title="selectionMode ? 'Exit selection mode' : 'Select videos to download or delete'"
        >
          {{ selectionMode ? "Exit Select" : "Select" }}
        </button>
      </div>
    </div>

    <div
      v-if="selectionMode"
      class="lab-alert lab-alert-info mb-3 flex flex-wrap items-center justify-between gap-2"
    >
      <span>
        {{ selectedVideoCount }} video{{ selectedVideoCount === 1 ? "" : "s" }} selected.
      </span>
      <div class="flex flex-wrap items-center gap-2">
        <button
          @click="toggleSelectAllVideos"
          class="lab-button lab-button-secondary min-h-[30px]"
          :disabled="visibleVideos.length === 0"
        >
          {{ allVisibleVideosSelected ? "Clear All" : "Select All" }}
        </button>
        <button
          @click="downloadSelectedVideos"
          class="lab-button lab-button-secondary min-h-[30px]"
          :disabled="selectedVideoCount === 0"
        >
          Download
        </button>
        <button
          @click="deleteSelectedVideos"
          class="lab-button lab-button-danger min-h-[30px]"
          :disabled="selectedVideoCount === 0"
        >
          Delete
        </button>
      </div>
    </div>

    <div v-if="loading" class="lab-panel-inset flex items-center justify-center p-8">
      <div class="text-sm font-semibold text-slate-500">Loading videos...</div>
    </div>

    <div
      v-else
      class="lab-media-grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-3"
    >
      <div
        v-for="video in visibleVideos"
        :key="video.id"
        class="lab-media-tile group aspect-video cursor-pointer bg-slate-950"
        :class="isVideoSelected(video.id) ? 'ring-2 ring-slate-900 ring-offset-2' : ''"
        @click="selectionMode ? toggleVideoSelection(video.id) : playVideo(video)"
      >
        <video
          v-if="video.filename"
          :src="getVideoUrl(video.filename)"
          class="block h-full w-full object-cover"
          preload="metadata"
        />
        <div
          v-else
          class="flex h-full flex-col items-center justify-center p-3 text-center text-xs text-slate-400"
        >
          <span class="break-all">{{ video.filename }}</span>
        </div>

        <div v-if="video.duration" class="lab-media-badge left-2 top-2">
          {{ formatDuration(video.duration) }}
        </div>

        <div v-if="video.fileSize" class="lab-media-badge left-2 bottom-2">
          {{ formatFileSize(video.fileSize) }}
        </div>

        <div
          v-if="isFavorite(video.id)"
          class="lab-media-heart-badge"
          aria-label="Liked video"
        >
          <span aria-hidden="true">&#9829;</span>
        </div>

        <div
          v-if="selectionMode"
          :class="[
            'absolute inset-0 z-20 bg-slate-950/20 transition-colors',
            isVideoSelected(video.id) ? 'bg-slate-950/45' : '',
          ]"
        >
          <span
            :class="[
              'absolute right-2 top-2 flex h-6 w-6 items-center justify-center rounded-md border-2 border-white bg-white/85 shadow-sm',
              isVideoSelected(video.id) ? 'bg-slate-900' : '',
            ]"
            aria-hidden="true"
          >
            <span
              v-if="isVideoSelected(video.id)"
              class="h-2.5 w-2.5 rounded-sm bg-white"
            ></span>
          </span>
          <span class="sr-only">
            {{ isVideoSelected(video.id) ? "Selected" : "Not selected" }}
          </span>
        </div>

        <div
          v-if="!selectionMode && videoFilter === 'all' && video.user"
          class="absolute bottom-0 left-0 right-0 truncate bg-slate-950/75 px-2 py-1 text-xs text-white"
        >
          {{ video.user.username }}
        </div>
      </div>
      <div
        v-if="visibleVideos.length === 0"
        class="col-span-full rounded-md border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-sm text-slate-500"
      >
        {{ likedOnly ? "No liked videos found" : "No videos found" }}
      </div>
    </div>

    <div
      v-if="selectedVideo"
      class="lab-modal-backdrop"
      @click="closeVideo"
    >
      <div class="lab-gallery-modal" @click.stop>
        <div class="lab-gallery-header">
          <div class="min-w-0">
            <h3 class="truncate text-sm font-black text-white">
              {{ selectedVideo.filename }}
            </h3>
            <p class="truncate text-xs font-semibold text-slate-400">
              {{ modalVideoPosition }}
            </p>
          </div>
          <div class="flex shrink-0 items-center gap-2">
            <button
              @click="toggleFavorite(selectedVideo)"
              :class="[
                'lab-favorite-button static shrink-0',
                isFavorite(selectedVideo.id)
                  ? 'is-favorite'
                  : '',
              ]"
              :aria-label="isFavorite(selectedVideo.id) ? 'Remove video from liked' : 'Like video'"
              :aria-pressed="isFavorite(selectedVideo.id)"
            >
              <span aria-hidden="true">&#9829;</span>
            </button>
            <a
              :href="getVideoUrl(selectedVideo.filename)"
              :download="selectedVideo.filename"
              class="lab-gallery-action-button"
              @click.stop
            >
              Download
            </a>
            <button
              @click="deleteSelectedVideo"
              class="lab-gallery-danger-button"
            >
              Delete
            </button>
            <button
              @click="closeVideo"
              class="lab-gallery-action-button"
            >
              Close
            </button>
          </div>
        </div>

        <div class="lab-gallery-body">
          <button
            class="lab-gallery-nav-button left-3"
            @click="showPreviousVideo"
            :disabled="!previousVideo"
            aria-label="Previous video"
          >
            <span class="lab-gallery-chevron is-left" aria-hidden="true"></span>
          </button>

          <div v-if="previousVideo" class="lab-gallery-side-preview left-4">
            <video
              :src="getVideoUrl(previousVideo.filename)"
              muted
              preload="metadata"
            />
          </div>

          <div class="lab-gallery-stage" @wheel.prevent="handleVideoWheel">
            <video
              :src="getVideoUrl(selectedVideo.filename)"
              controls
              autoplay
              class="lab-gallery-media"
            />
          </div>

          <div v-if="nextVideo" class="lab-gallery-side-preview right-4">
            <video
              :src="getVideoUrl(nextVideo.filename)"
              muted
              preload="metadata"
            />
          </div>

          <button
            class="lab-gallery-nav-button right-3"
            @click="showNextVideo"
            :disabled="!nextVideo"
            aria-label="Next video"
          >
            <span class="lab-gallery-chevron is-right" aria-hidden="true"></span>
          </button>
        </div>

        <div class="lab-gallery-details">
          <div class="grid gap-2 text-sm text-slate-300 sm:grid-cols-2">
            <div v-if="selectedVideo.duration">
              Duration: {{ formatDuration(selectedVideo.duration) }}
            </div>
            <div v-if="selectedVideo.fileSize">
              Size: {{ formatFileSize(selectedVideo.fileSize) }}
            </div>
            <div v-if="selectedVideo.width && selectedVideo.height">
              Resolution: {{ selectedVideo.width }} x {{ selectedVideo.height }}
            </div>
            <div v-if="selectedVideo.capturedAt">
              Recorded: {{ formatDate(selectedVideo.capturedAt) }}
            </div>
            <div
              v-if="
                selectedVideo.xPosition !== null ||
                selectedVideo.yPosition !== null ||
                selectedVideo.zPosition !== null
              "
            >
              Position: X={{ formatNumber(selectedVideo.xPosition) }}, Y={{
                formatNumber(selectedVideo.yPosition)
              }}, Z={{ formatNumber(selectedVideo.zPosition) }}
            </div>
            <div v-if="selectedVideo.exposureTime">
              Exposure: {{ formatNumber(selectedVideo.exposureTime) }}ms
            </div>
            <div v-if="selectedVideo.gain">
              Gain: {{ formatNumber(selectedVideo.gain) }}
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
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useMicroscopeStore } from "@/stores/microscope";
import { videoAPI, getVideoUrl } from "@/api/client";
import { useLocalFavorites } from "@/composables/useLocalFavorites";
import type { Video } from "@/types";

const store = useMicroscopeStore();
const videoFilter = ref<"mine" | "all">("mine");
const likedOnly = ref(false);
const loading = ref(false);
const selectionMode = ref(false);
const selectedVideoIds = ref<Set<number>>(new Set());
const selectedVideo = ref<Video | null>(null);
const wheelNavigationAt = ref(0);
const {
  favoriteCount,
  favoriteItems,
  isFavorite,
  toggleFavorite,
} = useLocalFavorites<Video>("compucyto:video-favorites");

const likedVideos = computed(() =>
  favoriteItems.value
    .map((favoriteVideo) => {
      return store.videos.find((video) => video.id === favoriteVideo.id) ?? favoriteVideo;
    })
    .filter((video) => Boolean(video.filename)),
);

const visibleVideos = computed(() => {
  const videos = store.videos.slice(0, 60);

  if (!likedOnly.value) {
    return videos;
  }

  return likedVideos.value;
});

const selectedVideos = computed(() =>
  visibleVideos.value.filter((video) => selectedVideoIds.value.has(video.id)),
);

const selectedVideoCount = computed(() => selectedVideoIds.value.size);

const allVisibleVideosSelected = computed(
  () =>
    visibleVideos.value.length > 0 &&
    visibleVideos.value.every((video) => selectedVideoIds.value.has(video.id)),
);

const navigationVideos = computed(() => {
  if (
    selectedVideo.value &&
    !visibleVideos.value.some((video) => video.id === selectedVideo.value?.id)
  ) {
    return [selectedVideo.value, ...visibleVideos.value];
  }

  return visibleVideos.value;
});

const selectedVideoIndex = computed(() => {
  if (!selectedVideo.value) {
    return -1;
  }

  return navigationVideos.value.findIndex(
    (video) => video.id === selectedVideo.value?.id,
  );
});

const getAdjacentVideo = (offset: number): Video | null => {
  const videos = navigationVideos.value;

  if (!selectedVideo.value || videos.length < 2 || selectedVideoIndex.value < 0) {
    return null;
  }

  const nextIndex = selectedVideoIndex.value + offset;

  if (nextIndex < 0 || nextIndex >= videos.length) {
    return null;
  }

  return videos[nextIndex];
};

const previousVideo = computed(() => getAdjacentVideo(-1));
const nextVideo = computed(() => getAdjacentVideo(1));
const modalVideoPosition = computed(() => {
  if (selectedVideoIndex.value < 0) {
    return "";
  }

  return `${selectedVideoIndex.value + 1} of ${navigationVideos.value.length}`;
});

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

const formatNumber = (value: number | null | undefined): string => {
  if (value === null || value === undefined) {
    return "N/A";
  }

  return new Intl.NumberFormat(undefined, {
    maximumFractionDigits: 2,
  }).format(value);
};

const playVideo = (video: Video) => {
  selectedVideo.value = video;
};

const closeVideo = () => {
  selectedVideo.value = null;
};

const toggleSelectionMode = () => {
  selectionMode.value = !selectionMode.value;

  if (!selectionMode.value) {
    selectedVideoIds.value = new Set();
  }
};

const isVideoSelected = (videoId: number): boolean => {
  return selectedVideoIds.value.has(videoId);
};

const toggleVideoSelection = (videoId: number) => {
  const nextSelectedIds = new Set(selectedVideoIds.value);

  if (nextSelectedIds.has(videoId)) {
    nextSelectedIds.delete(videoId);
  } else {
    nextSelectedIds.add(videoId);
  }

  selectedVideoIds.value = nextSelectedIds;
};

const toggleSelectAllVideos = () => {
  if (allVisibleVideosSelected.value) {
    selectedVideoIds.value = new Set();
    return;
  }

  selectedVideoIds.value = new Set(visibleVideos.value.map((video) => video.id));
};

const showPreviousVideo = () => {
  if (previousVideo.value) {
    selectedVideo.value = previousVideo.value;
  }
};

const showNextVideo = () => {
  if (nextVideo.value) {
    selectedVideo.value = nextVideo.value;
  }
};

const handleVideoWheel = (event: WheelEvent) => {
  const delta =
    Math.abs(event.deltaX) > Math.abs(event.deltaY)
      ? event.deltaX
      : event.deltaY;

  if (Math.abs(delta) < 25 || Date.now() - wheelNavigationAt.value < 350) {
    return;
  }

  wheelNavigationAt.value = Date.now();

  if (delta > 0) {
    showNextVideo();
    return;
  }

  showPreviousVideo();
};

const handleVideoKeydown = (event: KeyboardEvent) => {
  if (!selectedVideo.value) {
    return;
  }

  if (event.key === "Escape") {
    closeVideo();
  } else if (event.key === "ArrowLeft") {
    showPreviousVideo();
  } else if (event.key === "ArrowRight") {
    showNextVideo();
  }
};

const deleteVideo = async (videoId: number): Promise<boolean> => {
  if (!confirm("Are you sure you want to delete this video?")) {
    return false;
  }

  try {
    store.addLog(`Deleting video ${videoId}...`, "info");
    await videoAPI.deleteVideo(videoId);
    store.addLog(`Video ${videoId} deleted successfully`, "success");
    await loadVideos();
    return true;
  } catch (error: any) {
    console.error("Failed to delete video:", error);
    store.addLog(`Failed to delete video: ${error.message}`, "error");
    return false;
  }
};

const deleteSelectedVideos = async () => {
  const videosToDelete = selectedVideos.value;

  if (videosToDelete.length === 0) {
    return;
  }

  if (
    !confirm(
      `Delete ${videosToDelete.length} selected video${
        videosToDelete.length === 1 ? "" : "s"
      }? This cannot be undone.`,
    )
  ) {
    return;
  }

  const failedVideoIds: number[] = [];

  store.addLog(`Deleting ${videosToDelete.length} selected videos...`, "info");

  for (const video of videosToDelete) {
    try {
      await videoAPI.deleteVideo(video.id);
    } catch (error: any) {
      console.error("Failed to delete video:", error);
      failedVideoIds.push(video.id);
    }
  }

  if (failedVideoIds.length > 0) {
    store.addLog(
      `Deleted ${videosToDelete.length - failedVideoIds.length} videos. Failed: ${failedVideoIds.join(", ")}`,
      "warning",
    );
  } else {
    store.addLog(`Deleted ${videosToDelete.length} selected videos`, "success");
  }

  selectedVideoIds.value = new Set();
  await loadVideos();
};

const downloadFile = (href: string, filename: string) => {
  const link = document.createElement("a");
  link.href = href;
  link.download = filename;
  link.rel = "noopener";
  document.body.appendChild(link);
  link.click();
  link.remove();
};

const downloadSelectedVideos = () => {
  const videosToDownload = selectedVideos.value;

  if (videosToDownload.length === 0) {
    return;
  }

  videosToDownload.forEach((video, index) => {
    window.setTimeout(() => {
      downloadFile(getVideoUrl(video.filename), video.filename);
    }, index * 150);
  });

  store.addLog(
    `Started download for ${videosToDownload.length} selected videos`,
    "success",
  );
};

const deleteSelectedVideo = async () => {
  if (!selectedVideo.value) {
    return;
  }

  const deleted = await deleteVideo(selectedVideo.value.id);
  if (deleted) {
    closeVideo();
  }
};

const loadVideos = async () => {
  loading.value = true;
  try {
    console.log("[FRONTEND] Loading videos with filter:", videoFilter.value);
    store.addLog(
      `Loading ${videoFilter.value === "mine" ? "your" : "all"} videos from database...`,
      "info",
    );
    const result = await videoAPI.listVideos({
      limit: 60,
      page: 1,
      filter: videoFilter.value,
    });
    console.log("[FRONTEND] Received videos:", {
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
      "success",
    );
  } catch (error: any) {
    console.error("[FRONTEND] Failed to load videos:", error);
    store.addLog(`Failed to load videos: ${error.message}`, "error");
  } finally {
    loading.value = false;
  }
};

const handleVideoRecorded = () => {
  store.addLog("New video recorded, refreshing gallery...", "info");
  loadVideos();
};

onMounted(() => {
  loadVideos();
  window.addEventListener("video-recorded", handleVideoRecorded);
  window.addEventListener("keydown", handleVideoKeydown);
});

onUnmounted(() => {
  window.removeEventListener("video-recorded", handleVideoRecorded);
  window.removeEventListener("keydown", handleVideoKeydown);
});

watch(videoFilter, () => {
  selectedVideoIds.value = new Set();
  loadVideos();
});

watch(likedOnly, () => {
  selectedVideoIds.value = new Set();
});
</script>
