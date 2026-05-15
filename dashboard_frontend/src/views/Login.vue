<template>
  <main class="min-h-screen bg-slate-100 text-slate-950">
    <div class="mx-auto flex min-h-screen max-w-5xl flex-col px-4 py-5 sm:px-6">
      <header class="flex items-center justify-between border-b border-slate-300 pb-4">
        <div>
          <h1 class="text-2xl font-black tracking-tight">CytoCore</h1>
          <p class="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
            LinkBiosystems
          </p>
        </div>
        <div class="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-xs font-bold text-slate-600">
          Profile selection
        </div>
      </header>

      <section class="flex flex-1 flex-col justify-center py-8">
        <div class="mb-5 flex flex-col gap-3 border-b border-slate-300 pb-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h2 class="text-xl font-black tracking-tight">Select operator profile</h2>
            <p class="mt-1 text-sm text-slate-500">
              Choose the person responsible for the microscope session and captured images.
            </p>
          </div>

          <button
            v-if="!showProfileForm"
            type="button"
            class="rounded-md bg-slate-950 px-4 py-2 text-sm font-black text-white transition hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-500"
            @click="showProfileForm = true"
          >
            Add Profile
          </button>

        </div>

        <section
          v-if="showProfileForm"
          class="mb-5 rounded-lg border border-slate-300 bg-white p-5 shadow-sm"
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
              class="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-xs font-black text-slate-600 transition hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-slate-400"
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
              class="self-end rounded-md bg-slate-950 px-5 py-2.5 text-sm font-black text-white transition hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-500"
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
          class="mb-4 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700"
        >
          {{ errorMessage }}
        </div>

        <div
          v-if="authStore.profiles.length === 0"
          class="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center shadow-sm"
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
            class="mt-4 rounded-md bg-slate-950 px-4 py-2 text-sm font-black text-white transition hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-500"
            @click="showProfileForm = true"
          >
            Add Profile
          </button>
        </div>

        <div v-else class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <button
            v-for="profile in authStore.profiles"
            :key="profile.id"
            type="button"
            class="flex min-h-32 items-center gap-4 rounded-lg border border-slate-300 bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-slate-500 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-slate-500"
            @click="chooseProfile(profile.id)"
          >
            <div class="grid h-16 w-16 shrink-0 place-items-center rounded-full border border-slate-300 bg-slate-50 text-slate-700">
              <ScienceIcon :name="profile.avatarIcon" />
            </div>
            <div class="min-w-0">
              <div class="truncate text-lg font-black">{{ profile.username }}</div>
              <div class="mt-1 text-xs font-bold uppercase tracking-[0.14em] text-slate-400">
                {{ profile.role }}
              </div>
            </div>
          </button>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { defineComponent, h, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const profileName = ref('')
const profileIcon = ref<'microscope' | 'slide' | 'cells' | 'flask'>('microscope')
const errorMessage = ref('')
const showProfileForm = ref(false)
const profileInput = ref<HTMLInputElement | null>(null)

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
</script>
