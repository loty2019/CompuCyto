<template>
  <main class="relative min-h-screen overflow-hidden bg-slate-100 text-slate-950">
    <div class="microscope-field" aria-hidden="true">
      <div
        v-for="cell in backgroundCells"
        :key="cell.id"
        class="cell-particle"
        :class="cell.variant"
        :style="{
          '--x': `${cell.x}%`,
          '--y': `${cell.y}%`,
          '--size': `${cell.size}px`,
          '--delay': `${cell.delay}s`,
          '--duration': `${cell.duration}s`,
          '--drift-x': `${cell.driftX}px`,
          '--drift-y': `${cell.driftY}px`,
          '--opacity': String(cell.opacity),
        }"
      >
        <span />
      </div>
    </div>

    <div class="relative z-10 mx-auto flex min-h-screen max-w-6xl flex-col px-4 py-5 sm:px-6">
      <header class="flex flex-col gap-4 border-b border-slate-300 pb-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex min-w-0 items-center gap-4">
          <img
            :src="linkLogo"
            alt="Link Biosystems logo"
            class="brand-logo-tile h-16 w-16 sm:h-20 sm:w-20"
          />
          <div class="min-w-0">
            <h1 class="text-3xl font-black tracking-tight text-slate-950 sm:text-4xl">CytoCore</h1>
            <p class="text-xs font-bold uppercase tracking-[0.18em] text-teal-700">
              LinkBiosystems
            </p>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <div class="lab-badge rounded-md border-emerald-200 bg-emerald-50 text-emerald-800">
            Local profiles
          </div>
          <div class="lab-badge rounded-md">
            Media preserved
          </div>
        </div>
      </header>

      <section class="flex flex-1 flex-col justify-center py-8">
        <div class="mb-5 flex flex-col gap-3 border-b border-slate-300 pb-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h2 class="text-2xl font-black tracking-tight">Select operator profile</h2>
            <p class="mt-1 text-sm text-slate-500">
              Open the microscope dashboard with the right operator attached to this session.
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <button
              v-if="authStore.profiles.length > 0"
              type="button"
              class="lab-button lab-button-secondary"
              @click="manageProfiles = !manageProfiles"
            >
              {{ manageProfiles ? 'Done' : 'Manage profiles' }}
            </button>
            <button
              v-if="!showProfileForm"
              type="button"
              class="lab-button lab-button-primary"
              @click="showProfileForm = true"
            >
              Add Profile
            </button>
          </div>
        </div>

        <section
          v-if="showProfileForm"
          class="lab-panel mb-5 border-slate-300 p-5"
        >
          <div class="mb-4 flex items-start justify-between gap-4">
            <div>
              <h3 class="text-lg font-black tracking-tight">Add operator profile</h3>
              <p class="mt-1 text-sm text-slate-500">
                This name will be used for image and video ownership in the dashboard.
              </p>
            </div>
            <button
              type="button"
              class="lab-button lab-button-secondary"
              @click="cancelCreateProfile"
            >
              Cancel
            </button>
          </div>

          <form class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_220px_auto]" @submit.prevent="createProfile">
            <div>
              <label for="profile-name" class="mb-2 block text-sm font-bold text-slate-700">
                Profile name
              </label>
              <input
                id="profile-name"
                ref="profileInput"
                v-model="profileName"
                type="text"
                required
                minlength="3"
                maxlength="40"
                class="w-full rounded-md border border-slate-300 px-3 py-2.5 text-sm font-semibold outline-none focus:border-slate-600 focus:ring-2 focus:ring-slate-200"
                placeholder="Example: Dr. Chen"
              />
            </div>

            <div>
              <label for="profile-icon" class="mb-2 block text-sm font-bold text-slate-700">
                Icon
              </label>
              <select
                id="profile-icon"
                v-model="profileIcon"
                class="w-full rounded-md border border-slate-300 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700 outline-none focus:border-slate-600 focus:ring-2 focus:ring-slate-200"
              >
                <option value="microscope">Microscope</option>
                <option value="slide">Slide</option>
                <option value="cells">Cells</option>
                <option value="flask">Flask</option>
              </select>
            </div>

            <button
              type="submit"
              class="lab-button lab-button-primary self-end px-5 py-2.5 text-sm"
            >
              Save Profile
            </button>
          </form>

          <div class="mt-4 flex items-center gap-3 rounded-md border border-slate-200 bg-slate-50 p-3">
            <div class="grid h-12 w-12 shrink-0 place-items-center rounded-full border border-slate-300 bg-white text-slate-700">
              <ScienceIcon :name="profileIcon" />
            </div>
            <div class="min-w-0">
              <div class="truncate font-black">{{ profileName || 'New operator profile' }}</div>
              <div class="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">
                Operator
              </div>
            </div>
          </div>
        </section>

        <div
          v-if="errorMessage"
          class="lab-alert lab-alert-danger mb-4 text-sm"
        >
          {{ errorMessage }}
        </div>

        <div
          v-if="authStore.profiles.length === 0"
          class="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center"
        >
          <div class="mx-auto mb-4 grid h-16 w-16 place-items-center rounded-full border border-slate-300 bg-slate-50 text-slate-600">
            <ScienceIcon name="microscope" />
          </div>
          <h3 class="text-lg font-black">No profiles yet</h3>
          <p class="mt-1 text-sm text-slate-500">
            Add a profile before opening the microscope dashboard.
          </p>
          <button
            type="button"
            class="lab-button lab-button-primary mt-4"
            @click="showProfileForm = true"
          >
            Add Profile
          </button>
        </div>

        <div v-else class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="profile in authStore.profiles"
            :key="profile.id"
            class="group relative flex min-h-32 items-center gap-4 rounded-lg border border-slate-300 bg-white p-5 pr-14 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-slate-500 hover:shadow-md"
          >
            <button
              type="button"
              class="absolute inset-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500"
              :aria-label="`Open ${profile.username}`"
              @click="chooseProfile(profile.id)"
            />
            <div class="relative grid h-16 w-16 shrink-0 place-items-center rounded-full border border-slate-300 bg-slate-50 text-slate-700">
              <ScienceIcon :name="profile.avatarIcon" />
            </div>
            <div class="relative min-w-0">
              <div class="truncate text-lg font-black">{{ profile.username }}</div>
              <div class="mt-1 flex flex-wrap items-center gap-2">
                <span class="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">
                  {{ profile.role }}
                </span>
                <span class="rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-slate-500">
                  Local
                </span>
              </div>
            </div>
            <button
              v-if="manageProfiles"
              type="button"
              class="lab-button lab-button-secondary absolute right-3 top-3 z-10 min-h-[28px] px-2 py-1 text-[11px] text-red-700 hover:border-red-300 hover:bg-red-50"
              :aria-label="`Delete ${profile.username}`"
              @click="deleteProfile(profile.id, profile.username)"
            >
              Delete
            </button>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { defineComponent, h, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import linkLogo from '@/assets/link-biosystems-logo.png'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const profileName = ref('')
const profileIcon = ref<'microscope' | 'slide' | 'cells' | 'flask'>('microscope')
const errorMessage = ref('')
const showProfileForm = ref(false)
const manageProfiles = ref(false)
const profileInput = ref<HTMLInputElement | null>(null)
const backgroundCells = [
  { id: 1, x: 9, y: 18, size: 112, delay: -4, duration: 22, driftX: 28, driftY: -18, opacity: 0.52, variant: 'cell-a' },
  { id: 2, x: 24, y: 73, size: 76, delay: -10, duration: 28, driftX: -20, driftY: 26, opacity: 0.42, variant: 'cell-b' },
  { id: 3, x: 42, y: 12, size: 54, delay: -2, duration: 18, driftX: 18, driftY: 22, opacity: 0.36, variant: 'cell-c' },
  { id: 4, x: 61, y: 81, size: 130, delay: -15, duration: 32, driftX: -30, driftY: -16, opacity: 0.38, variant: 'cell-a' },
  { id: 5, x: 78, y: 24, size: 92, delay: -7, duration: 26, driftX: 24, driftY: 18, opacity: 0.44, variant: 'cell-b' },
  { id: 6, x: 90, y: 63, size: 62, delay: -12, duration: 20, driftX: -18, driftY: -24, opacity: 0.32, variant: 'cell-c' },
  { id: 7, x: 16, y: 48, size: 44, delay: -1, duration: 16, driftX: 14, driftY: 18, opacity: 0.28, variant: 'cell-c' },
  { id: 8, x: 53, y: 46, size: 84, delay: -18, duration: 30, driftX: -26, driftY: 20, opacity: 0.26, variant: 'cell-b' },
  { id: 9, x: 73, y: 6, size: 38, delay: -8, duration: 17, driftX: -12, driftY: 14, opacity: 0.28, variant: 'cell-c' },
  { id: 10, x: 35, y: 91, size: 52, delay: -13, duration: 21, driftX: 16, driftY: -22, opacity: 0.3, variant: 'cell-a' },
  { id: 11, x: 5, y: 58, size: 66, delay: -21, duration: 27, driftX: 22, driftY: 14, opacity: 0.28, variant: 'cell-b' },
  { id: 12, x: 13, y: 88, size: 34, delay: -6, duration: 15, driftX: -10, driftY: -18, opacity: 0.24, variant: 'cell-c' },
  { id: 13, x: 29, y: 30, size: 48, delay: -19, duration: 19, driftX: 16, driftY: -14, opacity: 0.3, variant: 'cell-a' },
  { id: 14, x: 47, y: 68, size: 42, delay: -9, duration: 18, driftX: -14, driftY: 18, opacity: 0.24, variant: 'cell-c' },
  { id: 15, x: 57, y: 28, size: 68, delay: -24, duration: 25, driftX: 20, driftY: 16, opacity: 0.25, variant: 'cell-b' },
  { id: 16, x: 68, y: 57, size: 46, delay: -5, duration: 17, driftX: -16, driftY: -18, opacity: 0.22, variant: 'cell-c' },
  { id: 17, x: 84, y: 43, size: 118, delay: -22, duration: 34, driftX: -28, driftY: 12, opacity: 0.3, variant: 'cell-a' },
  { id: 18, x: 96, y: 14, size: 40, delay: -3, duration: 16, driftX: -18, driftY: 20, opacity: 0.24, variant: 'cell-c' },
  { id: 19, x: 88, y: 84, size: 72, delay: -17, duration: 24, driftX: 16, driftY: -20, opacity: 0.26, variant: 'cell-b' },
  { id: 20, x: 43, y: 99, size: 96, delay: -11, duration: 31, driftX: -20, driftY: -24, opacity: 0.22, variant: 'cell-a' },
  { id: 21, x: 3, y: 7, size: 52, delay: -14, duration: 20, driftX: 18, driftY: 18, opacity: 0.24, variant: 'cell-c' },
  { id: 22, x: 67, y: 3, size: 74, delay: -26, duration: 29, driftX: -18, driftY: 16, opacity: 0.21, variant: 'cell-b' },
  { id: 23, x: 22, y: 8, size: 32, delay: -16, duration: 14, driftX: 12, driftY: 12, opacity: 0.24, variant: 'cell-c' },
  { id: 24, x: 99, y: 72, size: 104, delay: -28, duration: 33, driftX: -30, driftY: -12, opacity: 0.24, variant: 'cell-a' },
]

const iconPaths = {
  microscope: [
    'M14 3h4v3h-4z',
    'M9 18h10',
    'M11 21h6',
    'M10 18a7 7 0 0 1 7-7',
    'M13 6l3 3-5 5-3-3z',
    'M6 14l4 4',
  ],
  slide: [
    'M5 7h14v10H5z',
    'M8 10h4',
    'M8 14h8',
    'M16 10h1',
  ],
  cells: [
    'M9 10a3 3 0 1 0 0.01 0',
    'M15 15a3 3 0 1 0 0.01 0',
    'M15 7a2 2 0 1 0 0.01 0',
    'M11 12l2 1',
  ],
  flask: [
    'M10 3h4',
    'M11 3v5l-5 9a3 3 0 0 0 2.6 4.5h6.8A3 3 0 0 0 18 17l-5-9V3',
    'M8 16h8',
  ],
}

const ScienceIcon = defineComponent({
  props: {
    name: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    return () =>
      h(
        'svg',
        {
          xmlns: 'http://www.w3.org/2000/svg',
          viewBox: '0 0 24 24',
          fill: 'none',
          stroke: 'currentColor',
          'stroke-width': '1.8',
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          class: 'h-8 w-8',
          'aria-hidden': 'true',
        },
        (iconPaths[props.name as keyof typeof iconPaths] || iconPaths.microscope).map((d) =>
          h('path', { d }),
        ),
      )
  },
})

onMounted(async () => {
  if (!authStore.initialized) {
    await authStore.initializeAuth()
  } else {
    await authStore.refreshProfiles()
  }
})

watch(showProfileForm, async (isOpen) => {
  if (isOpen) {
    await nextTick()
    profileInput.value?.focus()
  }
})

const chooseProfile = async (profileId: number) => {
  const result = await authStore.selectProfile(profileId)

  if (result.success) {
    router.push((route.query.redirect as string) || '/')
  }
}

const createProfile = async () => {
  errorMessage.value = ''
  const result = await authStore.createProfile(profileName.value, profileIcon.value)

  if (result.success) {
    profileName.value = ''
    showProfileForm.value = false
    manageProfiles.value = false
    router.push((route.query.redirect as string) || '/')
  } else {
    errorMessage.value = result.error || 'Could not create profile'
  }
}

const cancelCreateProfile = () => {
  profileName.value = ''
  errorMessage.value = ''
  showProfileForm.value = false
}

const deleteProfile = async (profileId: number, username: string) => {
  errorMessage.value = ''

  const confirmed = confirm(
    `Delete the profile "${username}"? Existing photos and videos will stay in the gallery.`,
  )

  if (!confirmed) {
    return
  }

  const result = await authStore.deleteProfile(profileId)

  if (!result.success) {
    errorMessage.value = result.error || 'Could not delete profile'
  }
}
</script>

<style scoped>
.microscope-field {
  position: absolute;
  inset: 0;
  overflow: hidden;
  background:
    radial-gradient(circle at 22% 20%, rgba(100, 116, 139, 0.12), transparent 28%),
    radial-gradient(circle at 76% 22%, rgba(148, 163, 184, 0.1), transparent 30%),
    radial-gradient(circle at 58% 86%, rgba(113, 128, 120, 0.1), transparent 32%),
    linear-gradient(135deg, #fbfaf7 0%, #f2f5f2 48%, #f8fafc 100%);
}

.microscope-field::before {
  content: "";
  position: absolute;
  inset: -20%;
  background-image:
    linear-gradient(rgba(15, 23, 42, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(15, 23, 42, 0.035) 1px, transparent 1px);
  background-size: 52px 52px;
  mask-image: radial-gradient(circle at 50% 45%, black 0%, transparent 68%);
}

.microscope-field::after {
  content: "";
  position: absolute;
  inset: 7%;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 999px;
  box-shadow:
    inset 0 0 80px rgba(71, 85, 105, 0.06),
    0 0 120px rgba(15, 23, 42, 0.08);
  opacity: 0.7;
}

.cell-particle {
  --x: 50%;
  --y: 50%;
  --size: 80px;
  --delay: 0s;
  --duration: 24s;
  --drift-x: 20px;
  --drift-y: 20px;
  --opacity: 0.4;
  position: absolute;
  left: var(--x);
  top: var(--y);
  width: var(--size);
  height: var(--size);
  opacity: var(--opacity);
  transform: translate(-50%, -50%);
  animation: cell-drift var(--duration) ease-in-out var(--delay) infinite alternate;
}

.cell-particle span {
  position: absolute;
  inset: 0;
  border: 1px solid rgba(71, 85, 105, 0.22);
  border-radius: 48% 52% 46% 54% / 56% 44% 52% 48%;
  background:
    radial-gradient(circle at 36% 38%, rgba(75, 85, 99, 0.13) 0 9%, transparent 10%),
    radial-gradient(circle at 62% 58%, rgba(120, 128, 118, 0.1) 0 14%, transparent 15%),
    rgba(255, 255, 255, 0.36);
  box-shadow:
    inset 0 0 22px rgba(71, 85, 105, 0.08),
    0 12px 42px rgba(15, 23, 42, 0.06);
  animation: cell-pulse 8s ease-in-out infinite alternate;
}

.cell-b span {
  border-color: rgba(100, 116, 139, 0.2);
  border-radius: 56% 44% 50% 50% / 42% 56% 44% 58%;
  background:
    radial-gradient(circle at 44% 42%, rgba(82, 82, 91, 0.12) 0 12%, transparent 13%),
    radial-gradient(circle at 68% 62%, rgba(107, 114, 128, 0.08) 0 10%, transparent 11%),
    rgba(255, 255, 255, 0.28);
}

.cell-c span {
  border-color: rgba(15, 23, 42, 0.16);
  border-radius: 999px;
  background:
    radial-gradient(circle at 50% 50%, rgba(75, 85, 99, 0.14) 0 18%, transparent 19%),
    rgba(255, 255, 255, 0.24);
}

@keyframes cell-drift {
  from {
    transform: translate(-50%, -50%) translate(0, 0) rotate(0deg);
  }

  to {
    transform: translate(-50%, -50%) translate(var(--drift-x), var(--drift-y)) rotate(14deg);
  }
}

@keyframes cell-pulse {
  from {
    transform: scale(0.96);
  }

  to {
    transform: scale(1.04);
  }
}

@media (prefers-reduced-motion: reduce) {
  .cell-particle,
  .cell-particle span {
    animation: none;
  }
}
</style>
