import { computed, ref, watch } from "vue";

type FavoriteItem = {
  id: number;
};

export function useLocalFavorites<T extends FavoriteItem>(storageKey: string) {
  const favoriteItems = ref<T[]>([]);

  try {
    const stored = localStorage.getItem(storageKey);
    const parsed = stored ? JSON.parse(stored) : [];

    if (Array.isArray(parsed)) {
      favoriteItems.value = parsed
        .map((item) => (Number.isInteger(item) ? { id: item } : item))
        .filter((item): item is T => Number.isInteger(item?.id));
    }
  } catch {
    favoriteItems.value = [];
  }

  const favoriteIdSet = computed(
    () => new Set(favoriteItems.value.map((item) => item.id)),
  );
  const favoriteCount = computed(() => favoriteItems.value.length);

  const isFavorite = (id: number) => favoriteIdSet.value.has(id);

  const toggleFavorite = (item: T) => {
    if (isFavorite(item.id)) {
      favoriteItems.value = favoriteItems.value.filter(
        (favoriteItem) => favoriteItem.id !== item.id,
      );
      return;
    }

    favoriteItems.value = [item, ...favoriteItems.value];
  };

  watch(
    favoriteItems,
    (items) => {
      localStorage.setItem(storageKey, JSON.stringify(items));
    },
    { deep: true },
  );

  return {
    favoriteCount,
    favoriteItems,
    isFavorite,
    toggleFavorite,
  };
}
