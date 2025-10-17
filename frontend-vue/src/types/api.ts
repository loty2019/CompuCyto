// API Response Types

export interface SystemStatus {
  camera: "connected" | "disconnected";
  stage: "connected" | "disconnected";
  database: "connected" | "disconnected";
  raspberryPi: "connected" | "disconnected";
  queue: "running" | "stopped";
}

export interface HealthCheck {
  status: string;
  checks: {
    database: boolean;
    pythonCamera: boolean;
    raspberryPi: boolean;
    redis: boolean;
  };
  timestamp: string;
}

export interface Position {
  x: number;
  y: number;
  z: number;
  is_moving?: boolean;
}

export interface CameraSettings {
  exposure: number;
  exposureMin: number;
  exposureMax: number;
  gain: number;
  gainMin: number;
  gainMax: number;
  gamma: number;
  gammaMin: number;
  gammaMax: number;
  gammaSupported: boolean;
  autoExposure: boolean;
  autoExposureSupported: boolean;
  resolution: {
    width: number;
    height: number;
  };
  connected: boolean;
  streaming: boolean;
  available_resolutions?: Array<{
    width: number;
    height: number;
  }>;
}

export interface CaptureRequest {
  exposure?: number;
  gain?: number;
  gamma?: number;
}

export interface CaptureResponse {
  success: boolean;
  imageId: number | null;
  databaseSaved: boolean;
  warning: string | null;
  filename: string;
  filepath: string;
  capturedAt: string;
  exposureTime: number;
  gain: number;
  gamma: number;
  fileSize: number;
  width: number;
  height: number;
  metadata: Record<string, any>;
}

export interface MoveRequest {
  x?: number;
  y?: number;
  z?: number;
  relative: boolean;
}

export interface MoveResponse {
  status: string;
  target_position: Position;
}

export interface User {
  id: number;
  username: string;
  email?: string;
}

export interface Image {
  id: number;
  filename: string;
  thumbnail_path: string | null;
  captured_at: string;
  x_position: number | null;
  y_position: number | null;
  z_position: number | null;
  exposure_time: number | null;
  gain: number | null;
  file_size: number | null;
  width: number | null;
  height: number | null;
  job_id: number | null;
  user?: User;
  metadata?: Record<string, any>;
}

export interface ImageListResponse {
  total: number;
  skip: number;
  limit: number;
  images: Image[];
}

export interface Job {
  id: number;
  name: string;
  description: string | null;
  job_type: "timelapse" | "grid" | "zstack" | "manual";
  status:
    | "pending"
    | "running"
    | "paused"
    | "completed"
    | "failed"
    | "cancelled";
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  progress: number;
  total_steps: number | null;
  parameters: Record<string, any>;
  error_message: string | null;
  retry_count: number;
}

export interface JobCreate {
  name: string;
  description?: string;
  job_type: "timelapse" | "grid" | "zstack";
  parameters: Record<string, any>;
}

export interface JobListResponse {
  total: number;
  jobs: Job[];
}

export interface SavedPosition {
  id: number;
  name: string;
  description: string | null;
  x_position: number;
  y_position: number;
  z_position: number;
  camera_settings: Record<string, any>;
  created_at: string;
}

export interface PositionCreate {
  name: string;
  description?: string;
  x_position: number;
  y_position: number;
  z_position: number;
  camera_settings?: Record<string, any>;
}

export interface PositionListResponse {
  positions: SavedPosition[];
}

// WebSocket Message Types

export interface WSMessage {
  type:
    | "position"
    | "job_progress"
    | "image_captured"
    | "status"
    | "error"
    | "echo";
  data: any;
}

export interface WSPositionMessage {
  type: "position";
  data: Position;
}

export interface WSJobProgressMessage {
  type: "job_progress";
  data: {
    job_id: number;
    progress: number;
    total_steps: number;
    status: string;
  };
}

export interface WSImageCapturedMessage {
  type: "image_captured";
  data: {
    image_id: number;
    filename: string;
    thumbnail_path: string;
  };
}

export interface WSStatusMessage {
  type: "status";
  data: {
    camera: string;
    stage: string;
  };
}

export interface WSErrorMessage {
  type: "error";
  data: {
    component: string;
    message: string;
    severity: string;
  };
}
