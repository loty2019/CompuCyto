<template>
  <div class="bg-white p-5 rounded-lg shadow-md">
    <h2 class="text-lg font-bold text-gray-700 mb-4">⚙️ Job Control</h2>

    <div class="flex gap-2 mb-4">
      <button @click="createTimelapse" class="btn-job">⏱️ Timelapse</button>
      <button @click="createGrid" class="btn-job">🔲 Grid Scan</button>
      <button @click="createZStack" class="btn-job">📚 Z-Stack</button>
    </div>

    <div v-if="store.activeJobs.length > 0" class="mt-4">
      <h3 class="text-sm text-gray-600 mb-2.5">Active Jobs</h3>
      <div v-for="job in store.activeJobs" :key="job.id" class="bg-gray-100 p-3 rounded mb-2.5">
        <div class="flex justify-between items-center mb-2">
          <strong>{{ job.name }}</strong>
          <span class="bg-blue-500 text-white px-2 py-0.5 rounded-sm text-xs">{{ job.job_type }}</span>
        </div>
        <div class="flex items-center gap-2.5 mb-2">
          <div class="flex-1 h-2 bg-gray-300 rounded overflow-hidden">
            <div
              class="h-full bg-green-500 transition-all duration-300"
              :style="{ width: `${(job.progress / (job.total_steps || 1)) * 100}%` }"
            ></div>
          </div>
          <span class="text-xs text-gray-600 min-w-[60px]">{{ job.progress }}/{{ job.total_steps }}</span>
        </div>
        <div class="flex gap-1.5">
          <button @click="pauseJob(job.id)" v-if="job.status === 'running'" class="btn-job-action">Pause</button>
          <button @click="resumeJob(job.id)" v-if="job.status === 'paused'" class="btn-job-action">Resume</button>
          <button @click="cancelJob(job.id)" class="btn-job-cancel">Cancel</button>
        </div>
      </div>
    </div>
    <div v-else class="text-center p-5 text-gray-400">
      <p>No active jobs</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMicroscopeStore } from '@/stores/microscope'
import { jobAPI } from '@/api/client'
import type { JobCreate } from '@/types'

const store = useMicroscopeStore()

async function createJob(job: JobCreate) {
  try {
    const created = await jobAPI.createJob(job)
    store.addJob(created)
    store.addLog(`Job created: ${job.name}`, 'success')
  } catch (error: any) {
    store.addLog(`Job creation failed: ${error.message}`, 'error')
  }
}

async function createTimelapse() {
  await createJob({
    name: 'Test Timelapse',
    job_type: 'timelapse',
    parameters: {
      interval: 5,
      duration: 60,
      exposure: 100,
      gain: 1.0
    }
  })
}

async function createGrid() {
  await createJob({
    name: 'Test Grid Scan',
    job_type: 'grid',
    parameters: {
      start_x: 0,
      end_x: 500,
      step_x: 100,
      start_y: 0,
      end_y: 500,
      step_y: 100,
      z_position: 0,
      exposure: 100,
      gain: 1.0
    }
  })
}

async function createZStack() {
  await createJob({
    name: 'Test Z-Stack',
    job_type: 'zstack',
    parameters: {
      x_position: 0,
      y_position: 0,
      start_z: 0,
      end_z: 200,
      step_z: 50,
      exposure: 100,
      gain: 1.0
    }
  })
}

async function pauseJob(jobId: number) {
  try {
    await jobAPI.updateJob(jobId, { status: 'paused' })
    store.updateJob(jobId, { status: 'paused' })
    store.addLog(`Job ${jobId} paused`, 'info')
  } catch (error: any) {
    store.addLog(`Failed to pause job: ${error.message}`, 'error')
  }
}

async function resumeJob(jobId: number) {
  try {
    await jobAPI.updateJob(jobId, { status: 'running' })
    store.updateJob(jobId, { status: 'running' })
    store.addLog(`Job ${jobId} resumed`, 'info')
  } catch (error: any) {
    store.addLog(`Failed to resume job: ${error.message}`, 'error')
  }
}

async function cancelJob(jobId: number) {
  try {
    await jobAPI.updateJob(jobId, { status: 'cancelled' })
    store.updateJob(jobId, { status: 'cancelled' })
    store.addLog(`Job ${jobId} cancelled`, 'warning')
  } catch (error: any) {
    store.addLog(`Failed to cancel job: ${error.message}`, 'error')
  }
}
</script>

<style scoped>
.btn-job {
  @apply px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors font-medium;
}

.btn-job-action {
  @apply px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors;
}

.btn-job-cancel {
  @apply px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors;
}
</style>

