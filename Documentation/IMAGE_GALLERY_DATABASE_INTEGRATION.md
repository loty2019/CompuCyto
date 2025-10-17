# Image Gallery Database Integration

## Overview

The ImageGallery component now properly queries the NestJS backend to fetch images from the database.

## Implementation Details

### Frontend Changes

#### 1. API Client (`frontend-vue/src/api/client.ts`)

- **Updated endpoint**: Changed from `/images` to `/api/v1/images` to match NestJS routing
- **Response transformation**: Converts NestJS response format to expected frontend format
  ```typescript
  {
    data: [...],           // NestJS format
    pagination: {...}
  }
  ```
  to
  ```typescript
  {
    images: [...],         // Frontend format
    total: number,
    skip: number,
    limit: number
  }
  ```

#### 2. ImageGallery Component (`frontend-vue/src/components/ImageGallery.vue`)

- **Loading state**: Added `loading` ref to show loading indicator
- **User feedback**: Logs when loading images and shows count on success
- **Filter support**: Properly sends `filter` parameter ('mine' or 'all')
- **Page parameter**: Explicitly sends `page: 1` for initial load
- **Error handling**: Catches and logs errors to user console
- **Empty state**: Shows "No images found" when no images are returned

### Backend Structure (NestJS)

#### Images Controller (`Nest/src/images/images.controller.ts`)

- **Route**: `GET /api/v1/images`
- **Authentication**: Requires JWT token
- **Query Parameters**:
  - `filter`: 'mine' (default) | 'all'
  - `page`: number (default: 1)
  - `limit`: number (default: 20)

#### Images Service (`Nest/src/images/images.service.ts`)

- Queries database using TypeORM
- Joins with user table to include user information
- Filters by userId when `filter='mine'`
- Returns all images when `filter='all'`
- Orders by `capturedAt` descending (newest first)
- Implements pagination

### Data Flow

1. **Component Loads** → Calls `loadImages()`
2. **API Request** → `GET /api/v1/images?limit=20&page=1&filter=mine`
3. **JWT Auth** → Token from localStorage attached automatically
4. **Backend Query** → NestJS queries PostgreSQL database
5. **Response Transform** → API client converts response format
6. **Store Update** → Images stored in Pinia store
7. **UI Update** → Component displays images from store

### Features

✅ **User Filtering**: Toggle between "My Photos" and "All Photos"  
✅ **Authentication**: JWT token required for all requests  
✅ **Loading States**: Shows "Loading images..." while fetching  
✅ **User Attribution**: Shows username on images when viewing "All Photos"  
✅ **Error Handling**: Displays errors in console log  
✅ **Pagination Ready**: Backend supports pagination (limit 20 currently)  
✅ **Database Backed**: All images come from PostgreSQL database

### Testing

To test the integration:

1. **Start the backend**: Ensure NestJS server is running
2. **Login**: Authenticate to get JWT token
3. **Capture Image**: Use the camera to capture and save an image
4. **Check Gallery**: Images should appear automatically
5. **Toggle Filter**: Switch between "My Photos" and "All Photos"

### Database Query Example

The backend executes queries similar to:

```sql
SELECT
  image.*,
  user.id as "user_id",
  user.username,
  user.email
FROM images image
LEFT JOIN users user ON user.id = image.userId
WHERE image.userId = $1  -- When filter='mine'
ORDER BY image.capturedAt DESC
LIMIT 20 OFFSET 0
```

## Next Steps

Potential enhancements:

- [ ] Display actual image thumbnails instead of just IDs
- [ ] Implement infinite scroll or pagination controls
- [ ] Add image preview/modal on click
- [ ] Add filter by date range
- [ ] Add search functionality
- [ ] Show metadata on hover
- [ ] Implement image deletion from gallery
