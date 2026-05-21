<template>
  <div class="lab-panel">
    <div class="lab-panel-header">
      <div class="flex items-center gap-3">
        <h2 class="lab-title">Images</h2>
        <span class="lab-count">{{ visibleImages.length }}</span>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <div class="lab-segment-group">
          <button
            @click="photoFilter = 'mine'"
            :class="['lab-segment', photoFilter === 'mine' ? 'lab-segment-active' : '']"
          >
            Mine
          </button>
          <button
            @click="photoFilter = 'all'"
            :class="['lab-segment', photoFilter === 'all' ? 'lab-segment-active' : '']"
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
          :aria-label="likedOnly ? 'Show all images' : 'Show liked images'"
          :aria-pressed="likedOnly"
        >
          <span class="lab-liked-heart" aria-hidden="true">&#9829;</span>
          <span class="lab-liked-count" aria-hidden="true">
            {{ favoriteCount }}
          </span>
          <span class="sr-only">
            {{ likedOnly ? "Show all images" : "Show liked images" }}
          </span>
        </button>
        <button
          @click="toggleSelectionMode"
          :class="[
            'lab-button',
            'lab-button-primary',
          ]"
          :title="selectionMode ? 'Exit selection mode' : 'Select images to download or delete'"
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
        {{ selectedImageCount }} image{{ selectedImageCount === 1 ? "" : "s" }} selected.
      </span>
      <div class="flex flex-wrap items-center gap-2">
        <button
          @click="toggleSelectAllImages"
          class="lab-button lab-button-secondary min-h-[30px]"
          :disabled="visibleImages.length === 0"
        >
          {{ allVisibleImagesSelected ? "Clear All" : "Select All" }}
        </button>
        <button
          @click="downloadSelectedImages"
          class="lab-button lab-button-secondary min-h-[30px]"
          :disabled="selectedImageCount === 0"
        >
          Download
        </button>
        <button
          @click="deleteSelectedImages"
          class="lab-button lab-button-danger min-h-[30px]"
          :disabled="selectedImageCount === 0"
        >
          Delete
        </button>
      </div>
    </div>

    <div v-if="loading" class="lab-panel-inset flex items-center justify-center p-8">
      <div class="text-sm font-semibold text-slate-500">Loading images...</div>
    </div>

    <div
      v-else
      class="lab-media-grid grid-cols-[repeat(auto-fill,minmax(120px,1fr))] gap-2.5"
    >
      <div
        v-for="image in visibleImages"
        :key="image.id"
        class="lab-media-tile group aspect-square cursor-pointer"
        :class="isImageSelected(image.id) ? 'ring-2 ring-slate-900 ring-offset-2' : ''"
        @click="selectionMode ? toggleImageSelection(image.id) : viewImage(image)"
      >
        <img
          :src="getImageUrl(image.filename)"
          :alt="image.filename"
          class="block h-full w-full object-cover"
          @error="handleImageError($event)"
        />

        <div
          v-if="isFavorite(image.id)"
          class="lab-media-heart-badge"
          aria-label="Liked image"
        >
          <span aria-hidden="true">&#9829;</span>
        </div>

        <div
          v-if="selectionMode"
          :class="[
            'absolute inset-0 z-20 bg-slate-950/20 transition-colors',
            isImageSelected(image.id) ? 'bg-slate-950/45' : '',
          ]"
        >
          <span
            :class="[
              'absolute left-2 top-2 flex h-6 w-6 items-center justify-center rounded-md border-2 border-white bg-white/85 shadow-sm',
              isImageSelected(image.id) ? 'bg-slate-900' : '',
            ]"
            aria-hidden="true"
          >
            <span
              v-if="isImageSelected(image.id)"
              class="h-2.5 w-2.5 rounded-sm bg-white"
            ></span>
          </span>
          <span class="sr-only">
            {{ isImageSelected(image.id) ? "Selected" : "Not selected" }}
          </span>
        </div>

        <div
          v-if="!selectionMode && photoFilter === 'all' && image.user"
          class="absolute bottom-0 left-0 right-0 truncate bg-slate-950/75 px-2 py-1 text-xs text-white"
        >
          {{ image.user.username }}
        </div>
      </div>
      <div
        v-if="visibleImages.length === 0"
        class="col-span-full rounded-md border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-sm text-slate-500"
      >
        {{ likedOnly ? "No liked images found" : "No images found" }}
      </div>
    </div>

    <div
      v-if="selectedImage"
      class="lab-modal-backdrop"
      @click="closeImage"
    >
      <div class="lab-gallery-modal" @click.stop>
        <div class="lab-gallery-header">
          <div class="min-w-0">
            <h3 class="truncate text-sm font-black text-white">
              {{ selectedImage.filename }}
            </h3>
            <p class="truncate text-xs font-semibold text-slate-400">
              {{ modalImagePosition }}
            </p>
          </div>
          <div class="flex shrink-0 items-center gap-2">
            <button
              @click="toggleFavorite(selectedImage)"
              :class="[
                'lab-favorite-button static shrink-0',
                isFavorite(selectedImage.id)
                  ? 'is-favorite'
                  : '',
              ]"
              :aria-label="isFavorite(selectedImage.id) ? 'Remove image from liked' : 'Like image'"
              :aria-pressed="isFavorite(selectedImage.id)"
            >
              <span aria-hidden="true">&#9829;</span>
            </button>
            <a
              :href="getImageUrl(selectedImage.filename)"
              :download="selectedImage.filename"
              class="lab-gallery-action-button"
              @click.stop
            >
              Download
            </a>
            <button
              @click="deleteSelectedImage"
              class="lab-gallery-danger-button"
            >
              Delete
            </button>
            <button
              @click="closeImage"
              class="lab-gallery-action-button"
            >
              Close
            </button>
          </div>
        </div>

        <div class="lab-gallery-body">
          <button
            class="lab-gallery-nav-button left-3"
            @click="showPreviousImage"
            :disabled="!previousImage"
            aria-label="Previous image"
          >
            <span class="lab-gallery-chevron is-left" aria-hidden="true"></span>
          </button>

          <div v-if="previousImage" class="lab-gallery-side-preview left-4">
            <img
              :src="getImageUrl(previousImage.filename)"
              :alt="previousImage.filename"
            />
          </div>

          <div class="lab-gallery-stage" @wheel.prevent="handleImageWheel">
            <img
              :src="getImageUrl(selectedImage.filename)"
              :alt="selectedImage.filename"
              class="lab-gallery-media"
            />
          </div>

          <div v-if="nextImage" class="lab-gallery-side-preview right-4">
            <img
              :src="getImageUrl(nextImage.filename)"
              :alt="nextImage.filename"
            />
          </div>

          <button
            class="lab-gallery-nav-button right-3"
            @click="showNextImage"
            :disabled="!nextImage"
            aria-label="Next image"
          >
            <span class="lab-gallery-chevron is-right" aria-hidden="true"></span>
          </button>
        </div>

        <div class="lab-gallery-details">
          <div class="grid gap-2 text-sm text-slate-300 sm:grid-cols-2">
            <div v-if="selectedImage.width && selectedImage.height">
              Resolution: {{ selectedImage.width }} x {{ selectedImage.height }}
            </div>
            <div v-if="selectedImage.file_size">
              Size: {{ formatFileSize(selectedImage.file_size) }}
            </div>
            <div v-if="selectedImage.captured_at">
              Captured: {{ formatDate(selectedImage.captured_at) }}
            </div>
            <div
              v-if="
                selectedImage.x_position !== null ||
                selectedImage.y_position !== null ||
                selectedImage.z_position !== null
              "
            >
              Position: X={{ formatNumber(selectedImage.x_position) }}, Y={{
                formatNumber(selectedImage.y_position)
              }}, Z={{ formatNumber(selectedImage.z_position) }}
            </div>
            <div v-if="selectedImage.exposure_time">
              Exposure: {{ formatNumber(selectedImage.exposure_time) }}ms
            </div>
            <div v-if="selectedImage.gain">
              Gain: {{ formatNumber(selectedImage.gain) }}
            </div>
            <div v-if="selectedImage.gamma">
              Gamma: {{ formatNumber(selectedImage.gamma) }}
            </div>
            <div v-if="selectedImage.user">
              By: {{ selectedImage.user.username }}
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
import { imageAPI, getImageUrl, normalizeImage } from "@/api/client";
import { useLocalFavorites } from "@/composables/useLocalFavorites";
import type { Image } from "@/types";

const store = useMicroscopeStore();
const photoFilter = ref<"mine" | "all">("mine");
const likedOnly = ref(false);
const loading = ref(false);
const selectionMode = ref(false);
const selectedImageIds = ref<Set<number>>(new Set());
const selectedImage = ref<Image | null>(null);
const wheelNavigationAt = ref(0);
const {
  favoriteCount,
  favoriteItems,
  isFavorite,
  toggleFavorite,
} = useLocalFavorites<Image>("compucyto:image-favorites");

const likedImages = computed(() =>
  favoriteItems.value
    .map((favoriteImage) => {
      return (
        store.images.find((image) => image.id === favoriteImage.id) ??
        normalizeImage(favoriteImage)
      );
    })
    .filter((image) => Boolean(image.filename)),
);

const visibleImages = computed(() => {
  const images = store.images.slice(0, 60);

  if (!likedOnly.value) {
    return images;
  }

  return likedImages.value;
});

const selectedImages = computed(() =>
  visibleImages.value.filter((image) => selectedImageIds.value.has(image.id)),
);

const selectedImageCount = computed(() => selectedImageIds.value.size);

const allVisibleImagesSelected = computed(
  () =>
    visibleImages.value.length > 0 &&
    visibleImages.value.every((image) => selectedImageIds.value.has(image.id)),
);

const navigationImages = computed(() => {
  if (
    selectedImage.value &&
    !visibleImages.value.some((image) => image.id === selectedImage.value?.id)
  ) {
    return [selectedImage.value, ...visibleImages.value];
  }

  return visibleImages.value;
});

const selectedImageIndex = computed(() => {
  if (!selectedImage.value) {
    return -1;
  }

  return navigationImages.value.findIndex(
    (image) => image.id === selectedImage.value?.id,
  );
});

const getAdjacentImage = (offset: number): Image | null => {
  const images = navigationImages.value;

  if (!selectedImage.value || images.length < 2 || selectedImageIndex.value < 0) {
    return null;
  }

  const nextIndex = selectedImageIndex.value + offset;

  if (nextIndex < 0 || nextIndex >= images.length) {
    return null;
  }

  return images[nextIndex];
};

const previousImage = computed(() => getAdjacentImage(-1));
const nextImage = computed(() => getAdjacentImage(1));
const modalImagePosition = computed(() => {
  if (selectedImageIndex.value < 0) {
    return "";
  }

  return `${selectedImageIndex.value + 1} of ${navigationImages.value.length}`;
});

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

const viewImage = (image: Image) => {
  selectedImage.value = image;
};

const closeImage = () => {
  selectedImage.value = null;
};

const toggleSelectionMode = () => {
  selectionMode.value = !selectionMode.value;

  if (!selectionMode.value) {
    selectedImageIds.value = new Set();
  }
};

const isImageSelected = (imageId: number): boolean => {
  return selectedImageIds.value.has(imageId);
};

const toggleImageSelection = (imageId: number) => {
  const nextSelectedIds = new Set(selectedImageIds.value);

  if (nextSelectedIds.has(imageId)) {
    nextSelectedIds.delete(imageId);
  } else {
    nextSelectedIds.add(imageId);
  }

  selectedImageIds.value = nextSelectedIds;
};

const toggleSelectAllImages = () => {
  if (allVisibleImagesSelected.value) {
    selectedImageIds.value = new Set();
    return;
  }

  selectedImageIds.value = new Set(visibleImages.value.map((image) => image.id));
};

const showPreviousImage = () => {
  if (previousImage.value) {
    selectedImage.value = previousImage.value;
  }
};

const showNextImage = () => {
  if (nextImage.value) {
    selectedImage.value = nextImage.value;
  }
};

const handleImageWheel = (event: WheelEvent) => {
  const delta =
    Math.abs(event.deltaX) > Math.abs(event.deltaY)
      ? event.deltaX
      : event.deltaY;

  if (Math.abs(delta) < 25 || Date.now() - wheelNavigationAt.value < 350) {
    return;
  }

  wheelNavigationAt.value = Date.now();

  if (delta > 0) {
    showNextImage();
    return;
  }

  showPreviousImage();
};

const handleImageKeydown = (event: KeyboardEvent) => {
  if (!selectedImage.value) {
    return;
  }

  if (event.key === "Escape") {
    closeImage();
  } else if (event.key === "ArrowLeft") {
    showPreviousImage();
  } else if (event.key === "ArrowRight") {
    showNextImage();
  }
};

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  console.error("Failed to load image:", img.src);
  img.style.display = "none";
  const parent = img.parentElement;
  if (parent) {
    parent.classList.add(
      "flex",
      "items-center",
      "justify-center",
      "flex-col",
      "text-center",
      "p-2",
    );
    const fallback = document.createElement("span");
    fallback.className = "break-all text-xs text-slate-500";
    fallback.textContent = img.alt;
    parent.appendChild(fallback);
  }
};

const deleteImage = async (imageId: number): Promise<boolean> => {
  if (!confirm("Are you sure you want to delete this image?")) {
    return false;
  }

  try {
    store.addLog(`Deleting image ${imageId}...`, "info");
    await imageAPI.deleteImage(imageId);
    store.addLog(`Image ${imageId} deleted successfully`, "success");
    await loadImages();
    return true;
  } catch (error: any) {
    console.error("Failed to delete image:", error);
    store.addLog(`Failed to delete image: ${error.message}`, "error");
    return false;
  }
};

const deleteSelectedImages = async () => {
  const imagesToDelete = selectedImages.value;

  if (imagesToDelete.length === 0) {
    return;
  }

  if (
    !confirm(
      `Delete ${imagesToDelete.length} selected image${
        imagesToDelete.length === 1 ? "" : "s"
      }? This cannot be undone.`,
    )
  ) {
    return;
  }

  const failedImageIds: number[] = [];

  store.addLog(`Deleting ${imagesToDelete.length} selected images...`, "info");

  for (const image of imagesToDelete) {
    try {
      await imageAPI.deleteImage(image.id);
    } catch (error: any) {
      console.error("Failed to delete image:", error);
      failedImageIds.push(image.id);
    }
  }

  if (failedImageIds.length > 0) {
    store.addLog(
      `Deleted ${imagesToDelete.length - failedImageIds.length} images. Failed: ${failedImageIds.join(", ")}`,
      "warning",
    );
  } else {
    store.addLog(`Deleted ${imagesToDelete.length} selected images`, "success");
  }

  selectedImageIds.value = new Set();
  await loadImages();
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

const downloadSelectedImages = () => {
  const imagesToDownload = selectedImages.value;

  if (imagesToDownload.length === 0) {
    return;
  }

  imagesToDownload.forEach((image, index) => {
    window.setTimeout(() => {
      downloadFile(getImageUrl(image.filename), image.filename);
    }, index * 150);
  });

  store.addLog(
    `Started download for ${imagesToDownload.length} selected images`,
    "success",
  );
};

const deleteSelectedImage = async () => {
  if (!selectedImage.value) {
    return;
  }

  const deleted = await deleteImage(selectedImage.value.id);
  if (deleted) {
    closeImage();
  }
};

const loadImages = async () => {
  loading.value = true;
  try {
    console.log("[FRONTEND] Loading images with filter:", photoFilter.value);
    store.addLog(
      `Loading ${photoFilter.value === "mine" ? "your" : "all"} images from database...`,
      "info",
    );
    const result = await imageAPI.listImages({
      limit: 60,
      page: 1,
      filter: photoFilter.value,
    });
    console.log("[FRONTEND] Received images:", {
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
      "success",
    );
  } catch (error: any) {
    console.error("[FRONTEND] Failed to load images:", error);
    store.addLog(`Failed to load images: ${error.message}`, "error");
  } finally {
    loading.value = false;
  }
};

const handleImageCaptured = () => {
  store.addLog("New image captured, refreshing gallery...", "info");
  loadImages();
};

onMounted(() => {
  loadImages();
  window.addEventListener("image-captured", handleImageCaptured);
  window.addEventListener("keydown", handleImageKeydown);
});

onUnmounted(() => {
  window.removeEventListener("image-captured", handleImageCaptured);
  window.removeEventListener("keydown", handleImageKeydown);
});

watch(photoFilter, () => {
  selectedImageIds.value = new Set();
  loadImages();
});

watch(likedOnly, () => {
  selectedImageIds.value = new Set();
});
</script>
