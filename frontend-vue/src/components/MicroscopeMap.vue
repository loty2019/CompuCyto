<template>
  <div class="bg-white p-5 rounded-lg shadow-md">
    <h2 class="text-lg font-bold text-gray-700 mb-4">Position Map</h2>
    
    <div class="map-container">
      <svg 
        class="microscope-map" 
        viewBox="0 0 400 300" 
        xmlns="http://www.w3.org/2000/svg"
      >
        <!-- Gradient definitions -->
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#dbeafe" stroke-width="1"/>
          </pattern>
          
          <linearGradient id="stageGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#f0f9ff;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#e0f2fe;stop-opacity:1" />
          </linearGradient>
          
          <linearGradient id="microscopeGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#60a5fa;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:1" />
          </linearGradient>
          
          <filter id="shadow">
            <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.3"/>
          </filter>
          
          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        <!-- Background -->
        <rect width="400" height="300" fill="#f8fafc" />
        <rect width="400" height="300" fill="url(#grid)" />
        
        <!-- Microscope stage boundaries with shadow -->
        <rect 
          x="20" 
          y="20" 
          width="360" 
          height="260" 
          fill="url(#stageGradient)" 
          stroke="#3b82f6" 
          stroke-width="2"
          rx="8"
          filter="url(#shadow)"
        />
        
        <!-- Corner decorations -->
        <circle cx="25" cy="25" r="3" fill="#3b82f6" opacity="0.5"/>
        <circle cx="375" cy="25" r="3" fill="#3b82f6" opacity="0.5"/>
        <circle cx="25" cy="275" r="3" fill="#3b82f6" opacity="0.5"/>
        <circle cx="375" cy="275" r="3" fill="#3b82f6" opacity="0.5"/>
        
        <!-- Center cross (home position) with glow -->
        <g filter="url(#glow)">
          <circle cx="200" cy="150" r="6" fill="none" stroke="#f59e0b" stroke-width="2" opacity="0.6"/>
          <line x1="200" y1="135" x2="200" y2="165" stroke="#f59e0b" stroke-width="2" stroke-dasharray="4,4"/>
          <line x1="185" y1="150" x2="215" y2="150" stroke="#f59e0b" stroke-width="2" stroke-dasharray="4,4"/>
        </g>
        <text x="200" y="180" font-size="11" fill="#78716c" text-anchor="middle" font-weight="600">⌂ Home</text>
        
        <!-- Axis labels with better styling -->
        <g font-size="13" fill="#1e40af" font-weight="bold">
          <text x="365" y="155" text-anchor="end">+X →</text>
          <text x="35" y="155">← -X</text>
          <text x="200" y="40" text-anchor="middle">↑ +Y</text>
          <text x="200" y="270" text-anchor="middle">-Y ↓</text>
        </g>
        
        <!-- Current position marker (microscope/camera) -->
        <g :transform="`translate(${markerX}, ${markerY})`">
          <!-- Shadow for microscope -->
          <rect 
            x="-15" 
            y="-18" 
            width="30" 
            height="40" 
            fill="#000000" 
            opacity="0.15"
            rx="3"
            transform="translate(1, 2)"
          />
          
          <!-- Microscope rectangle with gradient -->
          <rect 
            x="-15" 
            y="-20" 
            width="30" 
            height="40" 
            fill="url(#microscopeGradient)" 
            stroke="#1e40af" 
            stroke-width="2.5"
            rx="3"
            filter="url(#shadow)"
          />
          
          <!-- Microscope lens effect -->
          <circle cx="0" cy="-8" r="6" fill="#1e3a8a" opacity="0.4"/>
          <circle cx="0" cy="-8" r="3" fill="#3b82f6" opacity="0.6"/>
          
          <!-- Position dot in center with glow -->
          <circle cx="0" cy="0" r="4" fill="#fbbf24" stroke="#f59e0b" stroke-width="2" filter="url(#glow)"/>
          
          <!-- Pulsing effect when moving -->
          <g v-if="isMoving">
            <circle 
              cx="0" 
              cy="0" 
              r="8" 
              fill="none" 
              stroke="#3b82f6" 
              stroke-width="3"
              opacity="0.6"
            >
              <animate attributeName="r" from="8" to="25" dur="1.2s" repeatCount="indefinite"/>
              <animate attributeName="opacity" from="0.6" to="0" dur="1.2s" repeatCount="indefinite"/>
            </circle>
            <circle 
              cx="0" 
              cy="0" 
              r="8" 
              fill="none" 
              stroke="#60a5fa" 
              stroke-width="2"
              opacity="0.4"
            >
              <animate attributeName="r" from="8" to="25" dur="1.2s" begin="0.3s" repeatCount="indefinite"/>
              <animate attributeName="opacity" from="0.4" to="0" dur="1.2s" begin="0.3s" repeatCount="indefinite"/>
            </circle>
          </g>
        </g>
        
        <!-- Position coordinates display with modern design -->
        <g>
          <rect x="135" y="282" width="130" height="28" fill="#1e293b" rx="6" filter="url(#shadow)"/>
          <text x="200" y="301" font-size="12" fill="#ffffff" text-anchor="middle" font-family="monospace" font-weight="600">
            X: {{ currentX.toFixed(1) }}  Y: {{ currentY.toFixed(1) }}
          </text>
        </g>
      </svg>
    </div>
    
    <div class="mt-4">
      <div class="flex items-center gap-3 bg-gradient-to-br from-white to-gray-50 rounded-lg p-3 border border-gray-200 max-w-[200px] shadow-sm hover:border-blue-300 hover:shadow-md transition-all duration-200">
        <div class="flex items-center justify-center w-10 h-10 text-2xl bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg">
          {{ isMoving ? '🔄' : '✓' }}
        </div>
        <div class="flex-1">
          <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Status</div>
          <div :class="['text-sm font-bold leading-tight', isMoving ? 'text-blue-600 animate-pulse' : 'text-green-600']">
            {{ isMoving ? 'Moving' : 'Idle' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useMicroscopeStore } from '@/stores/microscope'

const store = useMicroscopeStore()

// Placeholder max values (these will need to be updated when you know the actual range)
const maxX = 10000  // placeholder: max steps in X direction
const maxY = 8000   // placeholder: max steps in Y direction

// Get current position from store
const currentX = computed(() => store.position.x)
const currentY = computed(() => store.position.y)
const isMoving = computed(() => store.position.is_moving)

// Map dimensions
const mapWidth = 360   // SVG map width (minus borders)
const mapHeight = 260  // SVG map height (minus borders)
const mapCenterX = 200 // Center X in SVG (20 + 360/2)
const mapCenterY = 150 // Center Y in SVG (20 + 260/2)

// Convert real position to SVG coordinates
const markerX = computed(() => {
  // Scale from real position to map coordinates
  // Home (0,0) maps to center (200, 150)
  const scaledX = (currentX.value / maxX) * (mapWidth / 2)
  return mapCenterX + scaledX
})

const markerY = computed(() => {
  // Y axis is inverted in SVG (positive Y goes down)
  const scaledY = (currentY.value / maxY) * (mapHeight / 2)
  return mapCenterY - scaledY  // Subtract because SVG Y is inverted
})
</script>

<style scoped>
.map-container {
  @apply mb-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200 overflow-hidden shadow-md;
}

.microscope-map {
  @apply w-full h-auto block;
}
</style>
