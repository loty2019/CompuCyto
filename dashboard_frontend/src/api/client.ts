import axios from "axios";
import type {
  SystemStatus,
  HealthCheck,
  Position,
  CameraSettings,
  CaptureRequest,
  CaptureResponse,
  MoveRequest,
  MoveResponse,
  ImageListResponse,
  Image,
  JobCreate,
  Job,
  JobListResponse,
  PositionCreate,
  SavedPosition,
  PositionListResponse,
  Video,
  VideoListResponse,
} from "@/types";

// Declare global window type for logging
declare global {
  interface Window {
    __logToConsole?: (
      message: string,
      type: "info" | "success" | "error" | "warning",
    ) => void;
  }
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  user: {
    id: number;
    email: string;
    username: string;
    role: string;
    profile?: {
      id: number;
      userId: number;
      fullName?: string;
      bio?: string;
      avatarUrl?: string;
      preferences?: Record<string, any>;
    };
  };
}

// Use root so that calls to '/api/v1/...' are proxied by Vite to the backend
const API_BASE_URL = import.meta.env.VITE_API_URL || "/";

// Global Pi IP address (used for direct local connections when env vars are missing)
const PI_IP_ADDRESS = "192.168.100.1";

// Python camera service URL
const PYTHON_CAMERA_URL =
  import.meta.env.VITE_PYTHON_CAMERA_URL || "/camera-api";

// Pi-API URL for direct GPIO control (lights, PSU, etc.)
const PI_API_URL = import.meta.env.VITE_PI_API_URL || "/pi-api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Separate client for Python camera service (direct calls)
const pythonClient = axios.create({
  baseURL: PYTHON_CAMERA_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Separate client for Pi-API (GPIO control)
const piClient = axios.create({
  baseURL: PI_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to include JWT token and log requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Log API request
    const method = config.method?.toUpperCase() || "REQUEST";
    const url = config.url || "";
    const logMessage = `${method} ${url}`;

    // Add to console log (will be picked up by microscope store)
    if (window.__logToConsole) {
      window.__logToConsole(logMessage, "info");
    }

    return config;
  },
  (error) => {
    // Log request error
    if (window.__logToConsole) {
      window.__logToConsole(`Request failed: ${error.message}`, "error");
    }
    return Promise.reject(error);
  },
);

// Add response interceptor to handle 401 errors and log responses
apiClient.interceptors.response.use(
  (response) => {
    // Log successful response
    const method = response.config.method?.toUpperCase() || "REQUEST";
    const url = response.config.url || "";
    const status = response.status;
    const logMessage = ` ${method} ${url} - ${status}`;

    if (window.__logToConsole) {
      window.__logToConsole(logMessage, "success");
    }

    return response;
  },
  (error) => {
    // Log error response
    const method = error.config?.method?.toUpperCase() || "REQUEST";
    const url = error.config?.url || "unknown";
    const status = error.response?.status || "Network Error";
    const message = error.response?.data?.message || error.message;
    const logMessage = ` ${method} ${url} - ${status}: ${message}`;

    if (window.__logToConsole) {
      window.__logToConsole(logMessage, "error");
    }

    if (error.response?.status === 401) {
      // Clear auth data on unauthorized
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      // Redirect to login if not already there
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  },
);

// Add same interceptors for Python client (direct camera access)
pythonClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    const method = config.method?.toUpperCase() || "REQUEST";
    const url = config.url || "";
    const logMessage = `${method} [Python] ${url}`;

    if (window.__logToConsole) {
      window.__logToConsole(logMessage, "info");
    }

    return config;
  },
  (error) => {
    if (window.__logToConsole) {
      window.__logToConsole(`Python request failed: ${error.message}`, "error");
    }
    return Promise.reject(error);
  },
);

pythonClient.interceptors.response.use(
  (response) => {
    const method = response.config.method?.toUpperCase() || "REQUEST";
    const url = response.config.url || "";
    const status = response.status;
    const logMessage = ` ${method} [Python] ${url} - ${status}`;

    if (window.__logToConsole) {
      window.__logToConsole(logMessage, "success");
    }

    return response;
  },
  (error) => {
    const method = error.config?.method?.toUpperCase() || "REQUEST";
    const url = error.config?.url || "unknown";
    const status = error.response?.status || "Network Error";
    const message = error.response?.data?.detail || error.message;
    const logMessage = ` ${method} [Python] ${url} - ${status}: ${message}`;

    if (window.__logToConsole) {
      window.__logToConsole(logMessage, "error");
    }

    // Handle 401 from Python service same as main API
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  },
);

// Add interceptors for Pi-API client (GPIO control)
piClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    const method = config.method?.toUpperCase() || "REQUEST";
    const url = config.url || "";
    const logMessage = `${method} [Pi] ${url}`;

    if (window.__logToConsole) {
      window.__logToConsole(logMessage, "info");
    }

    return config;
  },
  (error) => {
    if (window.__logToConsole) {
      window.__logToConsole(`Pi-API request failed: ${error.message}`, "error");
    }
    return Promise.reject(error);
  },
);

piClient.interceptors.response.use(
  (response) => {
    const method = response.config.method?.toUpperCase() || "REQUEST";
    const url = response.config.url || "";
    const status = response.status;
    const logMessage = ` ${method} [Pi] ${url} - ${status}`;

    if (window.__logToConsole) {
      window.__logToConsole(logMessage, "success");
    }

    return response;
  },
  (error) => {
    const method = error.config?.method?.toUpperCase() || "REQUEST";
    const url = error.config?.url || "unknown";
    const status = error.response?.status || "Network Error";
    const message = error.response?.data?.detail || error.message;
    const logMessage = ` ${method} [Pi] ${url} - ${status}: ${message}`;

    if (window.__logToConsole) {
      window.__logToConsole(logMessage, "error");
    }

    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  },
);

// Auth endpoints
export const authAPI = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const { data } = await apiClient.post<AuthResponse>(
      "/api/v1/auth/login",
      credentials,
    );
    return data;
  },

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const { data } = await apiClient.post<AuthResponse>(
      "/api/v1/auth/register",
      userData,
    );
    return data;
  },

  async getProfile(): Promise<AuthResponse["user"]> {
    const { data } = await apiClient.get<AuthResponse["user"]>(
      "/api/v1/auth/profile",
    );
    return data;
  },
};

// Control endpoints
export const controlAPI = {
  async getStatus(): Promise<SystemStatus> {
    const { data } = await apiClient.get<SystemStatus>("/api/v1/stage/status");
    return data;
  },

  async getHealth(): Promise<HealthCheck> {
    const { data } = await apiClient.get<HealthCheck>("/api/v1/health");
    return data;
  },

  async captureImage(request: CaptureRequest): Promise<CaptureResponse> {
    const { data } = await apiClient.post<CaptureResponse>(
      "/api/v1/camera/capture",
      request,
    );
    return data;
  },

  async moveStage(request: MoveRequest): Promise<MoveResponse> {
    const { data } = await apiClient.post<MoveResponse>(
      "/api/v1/stage/move",
      request,
    );
    return data;
  },

  async getPosition(): Promise<Position> {
    const { data } = await apiClient.get<Position>("/api/v1/stage/position");
    return data;
  },

  async homeStage(): Promise<{ status: string; message: string }> {
    const { data } = await apiClient.post("/api/v1/stage/home");
    return data;
  },

  async emergencyStop(): Promise<{ status: string; message: string }> {
    const { data } = await apiClient.post("/api/v1/stage/stop");
    return data;
  },

  async getCameraSettings(): Promise<CameraSettings> {
    // Direct call to Python camera service (bypasses NestJS proxy)
    const { data } = await pythonClient.get<CameraSettings>("/settings");
    return data;
  },

  async updateCameraSettings(settings: Partial<CameraSettings>): Promise<void> {
    // Direct call to Python camera service (bypasses NestJS proxy)
    await pythonClient.put("/settings", settings);
  },

  // Get video stream URL (direct from Python)
  getVideoStreamUrl(): string {
    return `${PYTHON_CAMERA_URL}/video/feed`;
  },

  // Video recording - direct Python calls
  async startVideoRecording(params?: {
    duration?: number;
    playbackFrameRate?: number;
    decimation?: number;
  }): Promise<{ success: boolean; message: string; filename?: string }> {
    const { data } = await pythonClient.post("/video/record/start", null, {
      params: {
        duration: params?.duration,
        playback_frame_rate: params?.playbackFrameRate,
        decimation: params?.decimation,
      },
    });
    return data;
  },

  async getVideoRecordingStatus(): Promise<{
    is_recording: boolean;
    elapsed?: number;
    metadata?: Record<string, any>;
  }> {
    const { data } = await pythonClient.get("/video/record/status");
    return data;
  },

  async cancelVideoRecording(): Promise<{ success: boolean; message: string }> {
    const { data } = await pythonClient.post("/video/record/cancel");
    return data;
  },
};

// Image endpoints
export const imageAPI = {
  async listImages(params?: {
    skip?: number;
    limit?: number;
    job_id?: number;
    start_date?: string;
    end_date?: string;
    filter?: "mine" | "all";
    page?: number;
  }): Promise<ImageListResponse> {
    const { data } = await apiClient.get<any>("/api/v1/images", { params });
    // Transform NestJS response format to expected format
    return {
      images: data.data || [],
      total: data.pagination?.total || 0,
      skip: ((data.pagination?.page || 1) - 1) * (data.pagination?.limit || 20),
      limit: data.pagination?.limit || 20,
    };
  },

  async getImage(imageId: number): Promise<Image> {
    const { data } = await apiClient.get<Image>(`/api/v1/images/${imageId}`);
    return data;
  },

  async deleteImage(
    imageId: number,
  ): Promise<{ success: boolean; message: string }> {
    const { data } = await apiClient.delete(`/api/v1/images/${imageId}`);
    return data;
  },

  async cleanupMissingImages(): Promise<{
    success: boolean;
    message: string;
    removedCount: number;
  }> {
    const { data } = await apiClient.delete("/api/v1/images/cleanup/missing");
    return data;
  },
};

// Job endpoints
export const jobAPI = {
  async listJobs(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    job_type?: string;
  }): Promise<JobListResponse> {
    const { data } = await apiClient.get<JobListResponse>("/jobs", { params });
    return data;
  },

  async createJob(job: JobCreate): Promise<Job> {
    const { data } = await apiClient.post<Job>("/jobs", job);
    return data;
  },

  async getJob(jobId: number): Promise<Job> {
    const { data } = await apiClient.get<Job>(`/jobs/${jobId}`);
    return data;
  },

  async updateJob(jobId: number, updates: { status?: string }): Promise<Job> {
    const { data } = await apiClient.patch<Job>(`/jobs/${jobId}`, updates);
    return data;
  },

  async deleteJob(jobId: number): Promise<void> {
    await apiClient.delete(`/jobs/${jobId}`);
  },
};

// Position endpoints
export const positionAPI = {
  async listPositions(): Promise<PositionListResponse> {
    const { data } = await apiClient.get<PositionListResponse>("/positions");
    return data;
  },

  async createPosition(position: PositionCreate): Promise<SavedPosition> {
    const { data } = await apiClient.post<SavedPosition>(
      "/positions",
      position,
    );
    return data;
  },

  async getPosition(positionId: number): Promise<SavedPosition> {
    const { data } = await apiClient.get<SavedPosition>(
      `/positions/${positionId}`,
    );
    return data;
  },

  async gotoPosition(positionId: number): Promise<void> {
    await apiClient.post(`/positions/${positionId}/goto`);
  },

  async deletePosition(positionId: number): Promise<void> {
    await apiClient.delete(`/positions/${positionId}`);
  },
};

// Video endpoints
export const videoAPI = {
  async listVideos(params?: {
    filter?: "mine" | "all";
    page?: number;
    limit?: number;
  }): Promise<VideoListResponse> {
    const { data } = await apiClient.get<VideoListResponse>("/api/v1/videos", {
      params,
    });
    // Ensure videos array exists for backwards compatibility
    return {
      ...data,
      videos: data.data || [],
      total: data.pagination?.total || 0,
    };
  },

  async getVideo(videoId: number): Promise<Video> {
    const { data } = await apiClient.get<Video>(`/api/v1/videos/${videoId}`);
    return data;
  },

  async deleteVideo(
    videoId: number,
  ): Promise<{ success: boolean; message: string; videoId: number }> {
    const { data } = await apiClient.delete(`/api/v1/videos/${videoId}`);
    return data;
  },
};

// Pi-API types
interface LEDState {
  is_on: boolean;
  pin: number;
}

interface ToggleResponse {
  success: boolean;
  is_on: boolean;
  pin: number;
  message: string;
}

interface ClosetState {
  is_open: boolean;
  pin: number;
  label: string;
}

// Pi-API endpoints (direct GPIO control - bypasses NestJS)
export const piAPI = {
  // LED Lamp (main microscope light)
  async getLedLampState(): Promise<LEDState> {
    const { data } = await piClient.get<LEDState>("/led-lamp/state");
    return data;
  },

  async toggleLedLamp(): Promise<ToggleResponse> {
    const { data } = await piClient.post<ToggleResponse>("/led-lamp/toggle");
    return data;
  },

  // LED FLR (fluorescence light)
  async getLedFlrState(): Promise<LEDState> {
    const { data } = await piClient.get<LEDState>("/led-flr/state");
    return data;
  },

  async toggleLedFlr(): Promise<ToggleResponse> {
    const { data } = await piClient.post<ToggleResponse>("/led-flr/toggle");
    return data;
  },

  // PSU (power supply unit)
  async getPsuState(): Promise<LEDState> {
    const { data } = await piClient.get<LEDState>("/psu/state");
    return data;
  },

  async togglePsu(): Promise<ToggleResponse> {
    const { data } = await piClient.post<ToggleResponse>("/psu/toggle");
    return data;
  },

  // Scanning mode
  async startScan(): Promise<ToggleResponse> {
    const { data } = await piClient.post<ToggleResponse>("/scan/start");
    return data;
  },

  async stopScan(): Promise<ToggleResponse> {
    const { data } = await piClient.post<ToggleResponse>("/scan/stop");
    return data;
  },

  // Closet sensor
  async getClosetState(): Promise<ClosetState> {
    const { data } = await piClient.get<ClosetState>("/closet/state");
    return data;
  },

  // System shutdown
  async shutdown(): Promise<{ success: boolean; message: string }> {
    const { data } = await piClient.post("/system/shutdown");
    return data;
  },
};

// Helper to construct image/video URLs
export const getImageUrl = (filename: string): string => {
  return `${PYTHON_CAMERA_URL}/captures/${filename}`;
};

export const getVideoUrl = (filename: string): string => {
  return `${PYTHON_CAMERA_URL}/videos/${filename}`;
};

// Export the base URL for components that need it
export const CAMERA_BASE_URL = PYTHON_CAMERA_URL;

export default apiClient;
