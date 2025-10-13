<template>
  <div class="light-control card">
    <h3>Microscope Light</h3>
    
    <!-- Loading state -->
    <div v-if="loading" class="loading">
      <span class="spinner"></span>
      Loading light status...
    </div>
    
    <!-- Controls -->
    <div v-else class="controls">
      <!-- On/Off Toggle Button -->
      <button 
        @click="toggleLight"
        :class="['toggle-btn', { 'light-on': isLightOn }]"
        :disabled="isToggling"
      >
        <span class="icon">{{ isLightOn ? '💡' : '⚫' }}</span>
        <span class="label">{{ isLightOn ? 'Light ON' : 'Light OFF' }}</span>
      </button>
      
      <!-- Brightness Control (only shown when light is on) -->
      <div v-if="isLightOn" class="brightness-control">
        <label for="brightness">Brightness: {{ brightness }}%</label>
        <input 
          id="brightness"
          type="range" 
          min="0" 
          max="100" 
          v-model.number="brightness"
          @change="setBrightness"
          class="brightness-slider"
        />
      </div>
      
      <!-- Last updated timestamp -->
      <div class="status-info">
        Last updated: {{ lastUpdated }}
      </div>
    </div>
    
    <!-- Error message -->
    <div v-if="error" class="error-message">
      ⚠️ {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/api/client';

// State
const isLightOn = ref(false);
const brightness = ref(100);
const loading = ref(true);
const isToggling = ref(false);
const error = ref('');
const lastUpdateTime = ref<Date | null>(null);

// Computed property for formatted timestamp
const lastUpdated = computed(() => {
  if (!lastUpdateTime.value) return 'Never';
  return lastUpdateTime.value.toLocaleTimeString();
});

/**
 * Load initial light status when component mounts
 */
onMounted(async () => {
  await fetchLightStatus();
});

/**
 * Fetch current light status from backend
 */
async function fetchLightStatus() {
  try {
    loading.value = true;
    error.value = '';
    
    const response = await apiClient.get('/api/v1/microscope/light/status');
    
    isLightOn.value = response.data.isOn;
    brightness.value = response.data.brightness || 100;
    lastUpdateTime.value = new Date();
  } catch (err: any) {
    console.error('Failed to fetch light status:', err);
    error.value = err.response?.data?.message || 'Failed to connect to microscope';
  } finally {
    loading.value = false;
  }
}

/**
 * Toggle light on/off
 */
async function toggleLight() {
  try {
    isToggling.value = true;
    error.value = '';
    
    const response = await apiClient.post('/api/v1/microscope/light/toggle');
    
    isLightOn.value = response.data.isOn;
    brightness.value = response.data.brightness || 100;
    lastUpdateTime.value = new Date();
  } catch (err: any) {
    console.error('Failed to toggle light:', err);
    error.value = err.response?.data?.message || 'Failed to toggle light';
    
    // Refresh actual state on error
    await fetchLightStatus();
  } finally {
    isToggling.value = false;
  }
}

/**
 * Set brightness to specific value
 */
async function setBrightness() {
  try {
    error.value = '';
    
    const response = await apiClient.post('/api/v1/microscope/light/set', {
      isOn: true, // Turn on if not already on
      brightness: brightness.value,
    });
    
    isLightOn.value = response.data.isOn;
    brightness.value = response.data.brightness;
    lastUpdateTime.value = new Date();
  } catch (err: any) {
    console.error('Failed to set brightness:', err);
    error.value = err.response?.data?.message || 'Failed to adjust brightness';
    
    // Refresh actual state on error
    await fetchLightStatus();
  }
}
</script>

<style scoped>
.light-control {
  padding: 1.5rem;
  border-radius: 8px;
  background: var(--color-background-soft);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.light-control h3 {
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
  color: var(--color-heading);
}

.loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text-muted);
}

.spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-text);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  border: 2px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-background);
  color: var(--color-text);
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.toggle-btn:active:not(:disabled) {
  transform: translateY(0);
}

.toggle-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle-btn.light-on {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #000;
  border-color: #ffc700;
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
}

.toggle-btn .icon {
  font-size: 1.5rem;
}

.brightness-control {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.brightness-control label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text);
}

.brightness-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: var(--color-border);
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}

.brightness-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-text);
  cursor: pointer;
  transition: all 0.2s ease;
}

.brightness-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
  background: var(--color-heading);
}

.brightness-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-text);
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.brightness-slider::-moz-range-thumb:hover {
  transform: scale(1.2);
  background: var(--color-heading);
}

.status-info {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  text-align: right;
}

.error-message {
  margin-top: 0.5rem;
  padding: 0.75rem;
  border-radius: 4px;
  background: #fee;
  color: #c00;
  font-size: 0.9rem;
  border: 1px solid #fcc;
}
</style>
