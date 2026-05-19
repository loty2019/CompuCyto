<template>
  <div class="lab-panel">
    <div class="lab-panel-header">
      <div>
        <h2 class="lab-title">Job Control</h2>
        <p class="mt-1 text-xs text-slate-500">Automated acquisition routines</p>
      </div>
      <span class="lab-count">{{ store.activeJobs.length }}</span>
    </div>

    <div class="mb-4 flex flex-wrap gap-2">
      <button @click="createTimelapse" class="lab-button lab-button-secondary">Timelapse</button>
      <button @click="createGrid" class="lab-button lab-button-secondary">Grid Scan</button>
      <button @click="createZStack" class="lab-button lab-button-secondary">Z-Stack</button>
    </div>

    <div v-if="store.activeJobs.length > 0" class="mt-4 border-t border-slate-200 pt-3">
      <h3 class="mb-2.5 text-xs font-black uppercase tracking-wide text-slate-500">Active Jobs</h3>
      <div
        v-for="job in store.activeJobs"
        :key="job.id"
        class="border-t border-slate-200 py-3 first:border-t-0 first:pt-0 last:pb-0"
      >
        <div class="mb-2 flex items-center justify-between gap-3">
          <strong class="truncate text-sm text-slate-950">{{ job.name }}</strong>
          <span class="lab-badge shrink-0">{{ job.job_type }}</span>
        </div>
        <div class="mb-2 flex items-center gap-2.5">
          <div class="h-2 flex-1 overflow-hidden rounded-full bg-slate-200">
            <div
              class="h-full bg-teal-500 transition-all duration-300"
              :style="{ width: `${(job.progress / (job.total_steps || 1)) * 100}%` }"
            ></div>
          </div>
          <span class="min-w-[60px] font-mono text-xs text-slate-600">{{ job.progress }}/{{ job.total_steps }}</span>
        </div>
        <div class="flex flex-wrap gap-1.5">
          <button
            v-if="job.status === 'running'"
            @click="pauseJob(job.id)"
            class="lab-button lab-button-secondary min-h-[30px]"
          >
            Pause
          </button>
          <button
            v-if="job.status === 'paused'"
            @click="resumeJob(job.id)"
            class="lab-button lab-button-secondary min-h-[30px]"
          >
            Resume
          </button>
          <button @click="cancelJob(job.id)" class="lab-button lab-button-danger min-h-[30px]">Cancel</button>
        </div>
      </div>
    </div>
    <div v-else class="border-t border-slate-200 py-6 text-center text-sm text-slate-500">
      <p>No active jobs</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMicroscopeStore } from "@/stores/microscope";
import { jobAPI } from "@/api/client";
import type { JobCreate } from "@/types";

const store = useMicroscopeStore();

async function createJob(job: JobCreate) {
  try {
    const created = await jobAPI.createJob(job);
    store.addJob(created);
    store.addLog(`Job created: ${job.name}`, "success");
  } catch (error: any) {
    store.addLog(`Job creation failed: ${error.message}`, "error");
  }
}

async function createTimelapse() {
  await createJob({
    name: "Test Timelapse",
    job_type: "timelapse",
    parameters: {
      interval: 5,
      duration: 60,
      exposure: 100,
      gain: 1.0,
    },
  });
}

async function createGrid() {
  await createJob({
    name: "Test Grid Scan",
    job_type: "grid",
    parameters: {
      start_x: 0,
      end_x: 500,
      step_x: 100,
      start_y: 0,
      end_y: 500,
      step_y: 100,
      z_position: 0,
      exposure: 100,
      gain: 1.0,
    },
  });
}

async function createZStack() {
  await createJob({
    name: "Test Z-Stack",
    job_type: "zstack",
    parameters: {
      x_position: 0,
      y_position: 0,
      start_z: 0,
      end_z: 200,
      step_z: 50,
      exposure: 100,
      gain: 1.0,
    },
  });
}

async function pauseJob(jobId: number) {
  try {
    await jobAPI.updateJob(jobId, { status: "paused" });
    store.updateJob(jobId, { status: "paused" });
    store.addLog(`Job ${jobId} paused`, "info");
  } catch (error: any) {
    store.addLog(`Failed to pause job: ${error.message}`, "error");
  }
}

async function resumeJob(jobId: number) {
  try {
    await jobAPI.updateJob(jobId, { status: "running" });
    store.updateJob(jobId, { status: "running" });
    store.addLog(`Job ${jobId} resumed`, "info");
  } catch (error: any) {
    store.addLog(`Failed to resume job: ${error.message}`, "error");
  }
}

async function cancelJob(jobId: number) {
  try {
    await jobAPI.updateJob(jobId, { status: "cancelled" });
    store.updateJob(jobId, { status: "cancelled" });
    store.addLog(`Job ${jobId} cancelled`, "warning");
  } catch (error: any) {
    store.addLog(`Failed to cancel job: ${error.message}`, "error");
  }
}
</script>
