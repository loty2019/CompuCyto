# Video Recording Feature Implementation

## Overview

This document describes the complete video recording feature added to the CompuCyto microscope system. The feature allows users to record videos directly from the Pixelink camera with configurable parameters.

## Implementation Summary

### 1. Backend - Python Camera Service

#### Video Recording Methods (pixelink_camera.py)

- **`start_video_recording()`** - Initiates video recording using PixeLink API's `getEncodedClip`
  - Parameters: save_path, duration (seconds), playback_frame_rate (fps), decimation
  - Uses H.264 encoding format
  - Returns metadata with recording parameters
- **`stop_video_recording()`** - Finalizes video and converts to AVI format
  - Converts H.264 intermediate file to AVI using `formatClip`
  - Cleans up temporary files
  - Returns complete metadata with file info
- **`cancel_video_recording()`** - Cancels ongoing recording

- **`_get_effective_frame_rate()`** - Gets camera's actual frame rate

#### API Endpoints (main.py)

- **POST /video/record/start** - Start recording
  - Query params: duration, playback_frame_rate, decimation
  - Pauses live streaming during recording
- **POST /video/record/stop** - Stop and finalize recording
  - Converts and saves video file
  - Resumes live streaming if it was active
- **POST /video/record/cancel** - Cancel ongoing recording
- **GET /video/record/status** - Get current recording status
- **GET /videos/list** - List all recorded videos

#### File Storage

- Videos saved to `backend-python/videos/` folder
- Format: `recording_YYYYMMDD_HHMMSS_mmm.avi`
- Static file serving at `http://localhost:8001/videos/`

### 2. Backend - NestJS Service

#### Video Entity (video.entity.ts)

Database schema for video metadata:

- id, jobId, userId
- filename, thumbnailPath
- capturedAt, duration
- frameRate, captureFrameRate
- position (x, y, z)
- camera settings (exposureTime, gain, gamma)
- fileSize, width, height
- encodingFormat, containerFormat
- metadata (jsonb)

#### Videos Module

- **VideosModule** - Module configuration
- **VideosService** - Database operations
  - `findVideos()` - Query with pagination and user filtering
  - `deleteVideo()` - Delete video file and database entry
  - Auto-cleanup of missing video files
- **VideosController** - REST API endpoints
  - `GET /api/v1/videos` - List videos with filtering
  - `DELETE /api/v1/videos/:id` - Delete video

#### Database Migration

- Migration file: `1729600000000-CreateVideosTable.ts`
- Creates `videos` table with proper indexes and foreign keys
- Links to `users` and `jobs` tables

### 3. Frontend - Vue.js

#### CameraControl.vue Updates

Added "Record Video" button with:

- Toggle functionality (Start/Stop)
- Recording timer display
- Visual feedback (green when ready, red when recording)
- Automatic timer updates every 100ms

#### Recording Flow

1. User clicks "Record Video" button
2. Calls Python API to start recording (30s default duration)
3. Shows elapsed time during recording
4. User clicks "Stop Recording" or waits for auto-stop
5. Video is finalized and saved
6. Success message with file info shown

#### User Interface

- Button positioned below "Capture Image"
- Color-coded: Green (ready), Red (recording)
- Shows elapsed time during recording
- Integrated with existing log system

## Technical Details

### Video Recording Process

1. **Initialization**
   - Ensure camera stream is active
   - Get effective camera frame rate
   - Calculate number of frames to capture
   - Configure H.264 encoding parameters

2. **Capture**
   - Use `PxLApi.getEncodedClip()` for async capture
   - Callback function tracks progress
   - Intermediate H.264 file created

3. **Finalization**
   - Wait for capture completion
   - Convert H.264 to AVI format
   - Clean up temporary files
   - Generate metadata

### Default Parameters

- **Duration**: 30 seconds
- **Playback Frame Rate**: 25 fps
- **Decimation**: 1 (all frames)
- **Encoding**: H.264
- **Container**: AVI

### File Locations

- **Python Videos**: `backend-python/videos/`
- **Video Entity**: `Nest/src/videos/entities/video.entity.ts`
- **Videos Module**: `Nest/src/videos/`
- **Migration**: `Nest/src/migrations/1729600000000-CreateVideosTable.ts`
- **Frontend Component**: `frontend-vue/src/components/CameraControl.vue`

## Database Schema

### videos Table

```sql
CREATE TABLE videos (
  id SERIAL PRIMARY KEY,
  job_id INTEGER REFERENCES jobs(id) ON DELETE SET NULL,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  filename VARCHAR UNIQUE NOT NULL,
  thumbnail_path VARCHAR,
  captured_at TIMESTAMP NOT NULL,
  duration FLOAT,
  frame_rate FLOAT,
  capture_frame_rate FLOAT,
  x_position FLOAT,
  y_position FLOAT,
  z_position FLOAT,
  exposure_time INTEGER,
  gain FLOAT,
  gamma FLOAT,
  file_size BIGINT,
  width INTEGER,
  height INTEGER,
  encoding_format VARCHAR,
  container_format VARCHAR,
  metadata JSONB DEFAULT '{}'
);

CREATE INDEX IDX_videos_job_id_captured_at ON videos(job_id, captured_at);
CREATE INDEX IDX_videos_user_id_captured_at ON videos(user_id, captured_at);
CREATE INDEX IDX_videos_captured_at ON videos(captured_at);
```

## Entity Relationships

### Updated Entities

- **Job** - Added `videos: Video[]` relationship
- **User** - Added `videos: Video[]` relationship
- **Video** - Linked to Job and User entities

## Future Enhancements

Possible improvements:

1. Configurable recording parameters in UI
2. Video preview/playback in gallery
3. Thumbnail generation from first frame
4. Progress bar during recording
5. Multiple recording profiles (fast motion, slow motion)
6. Video editing/trimming capabilities
7. Export to different formats

## Usage Instructions

### Recording a Video

1. Start the camera live feed (if not already running)
2. Adjust camera settings as needed
3. Click "Record Video" button
4. Video will record for 30 seconds (or until manually stopped)
5. Click "Stop Recording" to finalize early
6. Video saved with timestamp in filename

### Accessing Recorded Videos

- Videos stored in `backend-python/videos/` folder
- Accessible via browser at `http://localhost:8001/videos/filename.avi`
- Database records in `videos` table
- Can be queried via NestJS API: `GET /api/v1/videos`

### Running Database Migration

```bash
cd Nest
npm run migration:run
```

## Testing Checklist

- [x] Start video recording
- [x] Stop video recording manually
- [x] Recording timer updates
- [x] Video file created successfully
- [x] Video metadata saved to database
- [x] List videos endpoint
- [x] Delete video endpoint
- [ ] Auto-stop after duration
- [ ] Cancel recording
- [ ] Multiple consecutive recordings
- [ ] Recording with different parameters
- [ ] Error handling (no camera, disk full, etc.)

## Dependencies

### Python Backend

- pixelinkWrapper (PixeLink SDK)
- FastAPI
- Pathlib

### NestJS Backend

- TypeORM
- PostgreSQL with jsonb support

### Frontend

- Vue 3 Composition API
- TypeScript

## Notes

- Video recording automatically pauses live streaming to prevent conflicts
- Stream resumes after recording completes
- H.264 encoding provides good compression (typically 5-20 MB for 30s @ 1280x1024)
- Real camera required - simulated mode not supported for video recording
- Camera must be streaming for recording to work
