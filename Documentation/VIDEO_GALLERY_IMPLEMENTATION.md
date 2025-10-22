# Video Gallery Implementation

## Overview

Created a video gallery component similar to the image gallery to display and manage recorded microscope videos.

## Files Created/Modified

### New Files

1. **`frontend-vue/src/components/VideoGallery.vue`**
   - Video gallery component with grid layout
   - Filter toggle (My Videos / All Videos)
   - Cleanup mode for deleting videos
   - Video player modal with metadata display
   - Duration and file size display

### Modified Files

1. **`frontend-vue/src/types/api.ts`**
   - Added `Video` interface with all video metadata fields
   - Added `VideoListResponse` interface

2. **`frontend-vue/src/api/client.ts`**
   - Added `videoAPI` with:
     - `listVideos()` - List videos with pagination and filtering
     - `getVideo()` - Get single video details
     - `deleteVideo()` - Delete video

3. **`frontend-vue/src/stores/microscope.ts`**
   - Added `videos` state array
   - Added `recentVideos` computed property
   - Added `addVideo()` and `setVideos()` actions

4. **`frontend-vue/src/views/Home.vue`**
   - Added VideoGallery component
   - Updated layout to show image and video galleries side-by-side

## Features

### Video Gallery Component

- **Grid Layout**: Videos displayed in responsive grid (200px minimum width)
- **Video Thumbnails**: Shows video thumbnail or placeholder icon
- **Duration Badge**: Displays video duration in MM:SS format
- **File Size Display**: Shows file size in MB/KB
- **User Filter**: Toggle between "My Videos" and "All Videos"
- **Cleanup Mode**: Enable to delete videos with confirmation
- **Video Player Modal**: Click video to play in full-screen modal with:
  - Video controls (play, pause, seek, volume)
  - Metadata display (duration, size, resolution, recorded date)
  - Close button

### Backend Integration

- Videos served from Python backend at `http://localhost:8001/videos/`
- NestJS API endpoint: `GET /api/v1/videos`
  - Supports pagination (`page`, `limit`)
  - Supports filtering (`mine`, `all`)
- NestJS API endpoint: `DELETE /api/v1/videos/:id`
  - Users can only delete their own videos
  - Admins can delete any video

## Video Recording Event

The component listens for a `video-recorded` custom event to auto-refresh the gallery when new videos are recorded.

To dispatch this event after recording:

```javascript
window.dispatchEvent(
  new CustomEvent("video-recorded", {
    detail: { videoId: 123, filename: "recording_xyz.avi" },
  })
);
```

## API Response Format

### List Videos Response

```json
{
  "data": [
    {
      "id": 1,
      "filename": "recording_20251022_120811_231.avi",
      "thumbnailPath": null,
      "capturedAt": "2025-10-22T12:08:11.231Z",
      "duration": 30.5,
      "frameRate": 25,
      "captureFrameRate": 30,
      "xPosition": 100.5,
      "yPosition": 200.3,
      "zPosition": 10.0,
      "exposureTime": 100,
      "gain": 1.5,
      "gamma": 1.0,
      "fileSize": 15456789,
      "width": 1920,
      "height": 1080,
      "encodingFormat": "H264",
      "containerFormat": "AVI",
      "metadata": {},
      "userId": 1,
      "jobId": null,
      "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
      }
    }
  ],
  "pagination": {
    "total": 50,
    "page": 1,
    "limit": 20,
    "totalPages": 3
  }
}
```

## Usage

The video gallery is automatically displayed on the home page alongside the image gallery. Users can:

1. **View Videos**: See all their recorded videos in a grid
2. **Filter Videos**: Toggle between personal videos and all users' videos
3. **Play Videos**: Click any video to play in modal player
4. **Delete Videos**: Enable cleanup mode to delete unwanted videos
5. **View Metadata**: See duration, file size, and recording details

## File Storage

Videos are stored in:

- **Backend**: `backend-python/videos/`
- **URL**: `http://localhost:8001/videos/filename.avi`

## Next Steps

Potential enhancements:

1. Generate video thumbnails from first frame
2. Add video download button
3. Add video sharing/export functionality
4. Add video trimming/editing tools
5. Add video compression options
6. Implement video search/filtering by date range
7. Add video metadata editing (title, description, tags)
