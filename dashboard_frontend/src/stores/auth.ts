import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

interface UserProfile {
  id: number
  email: string
  username: string
  role: string
  avatarIcon: 'microscope' | 'slide' | 'cells' | 'flask'
  profile?: {
    id: number
    userId: number
    fullName?: string
    avatarUrl?: string
    preferences?: Record<string, any>
  }
}

const PROFILE_STORAGE_KEY = 'cytocore_profiles'
const ACTIVE_PROFILE_KEY = 'cytocore_active_profile'

const profileIcons: UserProfile['avatarIcon'][] = ['microscope', 'slide', 'cells', 'flask']
const oldSeedProfileEmails = new Set([
  'operator@cytocore.local',
  'researcher@cytocore.local',
  'technician@cytocore.local',
  'guest@cytocore.local',
])

const parseProfiles = (): UserProfile[] => {
  const storedProfiles = localStorage.getItem(PROFILE_STORAGE_KEY)

  if (!storedProfiles) {
    localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify([]))
    return []
  }

  try {
    const parsed = JSON.parse(storedProfiles)
    if (!Array.isArray(parsed) || parsed.length === 0) {
      return []
    }

    if (parsed.some((profile) => !profile.avatarIcon)) {
      localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify([]))
      return []
    }

    const migratedProfiles = parsed
      .filter((profile) => !oldSeedProfileEmails.has(String(profile.email || '').toLowerCase()))
      .map((profile, index) => ({
        id: profile.id || index + 1,
        email: profile.email || `operator${index + 1}@cytocore.local`,
        username: profile.username || `Operator ${index + 1}`,
        role: profile.role || 'operator',
        avatarIcon: profile.avatarIcon || profileIcons[index % profileIcons.length],
        profile: profile.profile,
      }))

    if (migratedProfiles.length !== parsed.length) {
      localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(migratedProfiles))
      const activeProfileId = Number(localStorage.getItem(ACTIVE_PROFILE_KEY))
      const activeStillExists = migratedProfiles.some((profile) => profile.id === activeProfileId)

      if (!activeStillExists) {
        localStorage.removeItem(ACTIVE_PROFILE_KEY)
        localStorage.removeItem('user')
      }
    }

    return migratedProfiles
  } catch {
    localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify([]))
    return []
  }
}

const syncProfileWithBackend = async (profile: UserProfile): Promise<UserProfile> => {
  try {
    const response = await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: profile.email,
        username: profile.username,
        password: 'local-profile',
      }),
    })

    if (!response.ok) {
      return profile
    }

    const data = await response.json()
    const backendUser = data.user

    if (!backendUser?.id) {
      return profile
    }

    return {
      ...profile,
      id: backendUser.id,
      email: backendUser.email || profile.email,
      username: backendUser.username || profile.username,
      profile: {
        ...profile.profile,
        id: backendUser.id,
        userId: backendUser.id,
        fullName: backendUser.profile?.fullName || profile.username,
      },
    }
  } catch {
    return profile
  }
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserProfile | null>(null)
  const profiles = ref<UserProfile[]>([])
  const token = ref<string | null>(null)
  const initialized = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const currentUser = computed(() => user.value)

  const persistProfiles = () => {
    localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profiles.value))
  }

  const setActiveProfile = (profile: UserProfile) => {
    user.value = profile
    token.value = 'local-profile'
    localStorage.setItem(ACTIVE_PROFILE_KEY, String(profile.id))
    localStorage.setItem('user', JSON.stringify(profile))
    localStorage.removeItem('access_token')

    if (window.__logToConsole) {
      window.__logToConsole(`Profile selected: ${profile.username}`, 'success')
    }
  }

  const initializeAuth = () => {
    profiles.value = parseProfiles()

    const activeProfileId = Number(localStorage.getItem(ACTIVE_PROFILE_KEY))
    const activeProfile = profiles.value.find((profile) => profile.id === activeProfileId)

    if (activeProfile) {
      setActiveProfile(activeProfile)
    }

    initialized.value = true
  }

  const selectProfile = async (profileId: number) => {
    const profile = profiles.value.find((item) => item.id === profileId)

    if (!profile) {
      return { success: false, error: 'Profile not found' }
    }

    const syncedProfile = await syncProfileWithBackend(profile)
    profiles.value = profiles.value.map((item) =>
      item.id === profile.id ? syncedProfile : item,
    )
    persistProfiles()
    setActiveProfile(syncedProfile)
    return { success: true }
  }

  const createProfile = async (name: string, avatarIcon: UserProfile['avatarIcon'] = 'microscope') => {
    const username = name.trim()

    if (username.length < 3) {
      return { success: false, error: 'Name must be at least 3 characters' }
    }

    const nextId = Math.max(0, ...profiles.value.map((profile) => profile.id)) + 1
    const profile: UserProfile = {
      id: nextId,
      email: `${username.toLowerCase().replace(/[^a-z0-9]+/g, '.')}@cytocore.local`,
      username,
      role: 'operator',
      avatarIcon,
      profile: {
        id: nextId,
        userId: nextId,
        fullName: username,
      },
    }

    const syncedProfile = await syncProfileWithBackend(profile)
    profiles.value = [...profiles.value, syncedProfile]
    persistProfiles()
    setActiveProfile(syncedProfile)

    return { success: true }
  }

  const login = async (profileIdOrName: number | string) => {
    if (typeof profileIdOrName === 'number') {
      return selectProfile(profileIdOrName)
    }

    const profile = profiles.value.find(
      (item) => item.username.toLowerCase() === profileIdOrName.toLowerCase(),
    )

    return profile ? selectProfile(profile.id) : { success: false, error: 'Profile not found' }
  }

  const register = async (_email: string, username: string) => {
    return createProfile(username)
  }

  const logout = () => {
    if (window.__logToConsole && user.value) {
      window.__logToConsole(`Profile closed: ${user.value.username}`, 'info')
    }

    user.value = null
    token.value = null
    localStorage.removeItem(ACTIVE_PROFILE_KEY)
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  const getProfile = async () => {
    return user.value
      ? { success: true }
      : { success: false, error: 'No profile selected' }
  }

  return {
    user,
    profiles,
    token,
    initialized,
    isAuthenticated,
    currentUser,
    profileIcons,
    initializeAuth,
    selectProfile,
    createProfile,
    login,
    register,
    logout,
    getProfile,
  }
})
