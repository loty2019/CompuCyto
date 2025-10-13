# NestJS API Endpoint Tree - Visual Map

```
http://localhost:3000
│
├── /api/v1/auth (Authentication)
│   ├── POST   /register          🔓 Public - Create new user
│   ├── POST   /login             🔓 Public - Login & get JWT token  
│   └── GET    /profile           🔒 Protected - Get current user
│
├── /api/v1/camera (Camera Control)
│   ├── POST   /capture           🔒 Protected - Capture image
│   ├── GET    /settings          🔒 Protected - Get camera settings
│   ├── PUT    /settings          🔒 Protected - Update settings
│   └── GET    /preview           🔒 Protected - Get preview stream
│
├── /api/v1/stage (Stage Movement)
│   ├── POST   /move              🔒 Protected - Move to position
│   ├── GET    /position          🔒 Protected - Get current position
│   ├── POST   /home              🔒 Protected - Home all axes
│   ├── POST   /stop              🔒 Protected - Emergency stop
│   └── GET    /limits            🔒 Protected - Get safety limits
│
├── /api/v1/microscope (Hardware Control)
│   ├── GET    /light/status      🔒 Protected - Get light status
│   └── POST   /light/set         🔒 Protected - Control light
│
├── /api/v1/users (User Management)
│   ├── GET    /                  🔒 Protected - List all users
│   ├── GET    /:id               🔒 Protected - Get user by ID
│   ├── PUT    /:id               🔒 Protected - Update user
│   └── DELETE /:id               🔒 Protected - Delete user
│
└── /api/v1/health (System Health)
    └── GET    /                  🔓 Public - Health check

───────────────────────────────────────────────────────
📚 Swagger Documentation: http://localhost:3000/api-docs
───────────────────────────────────────────────────────

Legend:
🔓 Public    - No authentication required
🔒 Protected - Requires JWT token in Authorization header
```

---

## File to Endpoint Mapping

```
Nest/src/
│
├── auth/
│   └── auth.controller.ts ──────────┐
│       @Controller('api/v1/auth')   │
│       ├── @Post('register')        ├─→ POST /api/v1/auth/register
│       ├── @Post('login')           ├─→ POST /api/v1/auth/login
│       └── @Get('profile')          └─→ GET  /api/v1/auth/profile
│
├── camera/
│   └── camera.controller.ts ────────┐
│       @Controller('api/v1/camera') │
│       ├── @Post('capture')         ├─→ POST /api/v1/camera/capture
│       ├── @Get('settings')         ├─→ GET  /api/v1/camera/settings
│       ├── @Put('settings')         ├─→ PUT  /api/v1/camera/settings
│       └── @Get('preview')          └─→ GET  /api/v1/camera/preview
│
├── stage/
│   └── stage.controller.ts ─────────┐
│       @Controller('api/v1/stage')  │
│       ├── @Post('move')            ├─→ POST /api/v1/stage/move
│       ├── @Get('position')         ├─→ GET  /api/v1/stage/position
│       ├── @Post('home')            ├─→ POST /api/v1/stage/home
│       ├── @Post('stop')            ├─→ POST /api/v1/stage/stop
│       └── @Get('limits')           └─→ GET  /api/v1/stage/limits
│
├── microscope/
│   └── microscope.controller.ts ────┐
│       @Controller('api/v1/microscope')
│       ├── @Get('light/status')     ├─→ GET  /api/v1/microscope/light/status
│       └── @Post('light/set')       └─→ POST /api/v1/microscope/light/set
│
├── users/
│   └── users.controller.ts ─────────┐
│       @Controller('api/v1/users')  │
│       ├── @Get()                   ├─→ GET    /api/v1/users
│       ├── @Get(':id')              ├─→ GET    /api/v1/users/:id
│       ├── @Put(':id')              ├─→ PUT    /api/v1/users/:id
│       └── @Delete(':id')           └─→ DELETE /api/v1/users/:id
│
└── common/controllers/
    └── health.controller.ts ────────┐
        @Controller('api/v1/health') │
        └── @Get()                   └─→ GET  /api/v1/health
```

---

## Request Flow Through Files

### Example: Login Request

```
1. HTTP Request
   POST /api/v1/auth/login
   Body: { email: "...", password: "..." }
   │
   ↓
2. auth.controller.ts
   @Post('login')
   async login(@Body() loginDto: LoginDto) {
   │
   ↓
3. login.dto.ts
   Validates: email format, password length
   │
   ↓
4. auth.service.ts
   login(loginDto: LoginDto) {
   │
   ↓
5. users.service.ts
   findByEmail(email: string)
   │
   ↓
6. user.entity.ts
   Database query via TypeORM
   │
   ↓
7. user.entity.ts
   validatePassword(password: string)
   │
   ↓
8. auth.service.ts
   Generate JWT token
   │
   ↓
9. auth.controller.ts
   Return { access_token, user }
   │
   ↓
10. HTTP Response
    200 OK
    { "access_token": "...", "user": {...} }
```

---

## Protected Endpoint Flow

### Example: Capture Image (Requires Auth)

```
1. HTTP Request
   POST /api/v1/camera/capture
   Headers: { Authorization: "Bearer eyJhbGc..." }
   Body: { exposure: 100, gain: 1.5 }
   │
   ↓
2. jwt-auth.guard.ts
   Validates JWT token
   Extracts user from token
   │
   ↓
3. camera.controller.ts
   @UseGuards(JwtAuthGuard)  ← Guard passed!
   @Post('capture')
   async capture(@Body() captureDto: CaptureDto) {
   │
   ↓
4. capture.dto.ts
   Validates: exposure range, gain range
   │
   ↓
5. camera.service.ts
   capture(captureDto: CaptureDto)
   │
   ↓
6. Python Camera Service (External)
   HTTP call to localhost:8001
   │
   ↓
7. camera.service.ts
   Receives image data from Python
   │
   ↓
8. camera.controller.ts
   Return image metadata
   │
   ↓
9. HTTP Response
   200 OK
   { "success": true, "imageId": "...", ... }
```

---

## How Vue Calls These Endpoints

### Frontend API Client (`client.ts`)

```typescript
// Maps to NestJS endpoints

export const authAPI = {
  login(credentials) {
    // Calls: POST /api/v1/auth/login
    return apiClient.post('/api/v1/auth/login', credentials)
  },
  
  register(userData) {
    // Calls: POST /api/v1/auth/register
    return apiClient.post('/api/v1/auth/register', userData)
  },
  
  getProfile() {
    // Calls: GET /api/v1/auth/profile
    return apiClient.get('/api/v1/auth/profile')
  }
}

export const cameraAPI = {
  capture(settings) {
    // Calls: POST /api/v1/camera/capture
    return apiClient.post('/api/v1/camera/capture', settings)
  },
  
  getSettings() {
    // Calls: GET /api/v1/camera/settings
    return apiClient.get('/api/v1/camera/settings')
  }
}

export const stageAPI = {
  move(position) {
    // Calls: POST /api/v1/stage/move
    return apiClient.post('/api/v1/stage/move', position)
  },
  
  getPosition() {
    // Calls: GET /api/v1/stage/position
    return apiClient.get('/api/v1/stage/position')
  }
}
```

---

## Testing Endpoints

### 1. Using Swagger UI
```
Navigate to: http://localhost:3000/api-docs

1. Find the endpoint you want to test
2. Click "Try it out"
3. Fill in parameters
4. For protected endpoints: Click "Authorize" and enter JWT token
5. Click "Execute"
6. See the response
```

### 2. Using curl
```bash
# Login
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Use JWT token for protected endpoint
curl -X GET http://localhost:3000/api/v1/camera/settings \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### 3. Using Vue Frontend
```typescript
// In your Vue component
const result = await cameraAPI.capture({
  exposure: 100,
  gain: 1.5
})
```

---

## Quick Reference

| What | Where | Pattern |
|------|-------|---------|
| **All endpoints** | `*.controller.ts` files | `@Get()`, `@Post()`, etc. |
| **Route path** | `@Controller('path')` | Class decorator |
| **HTTP method** | `@Get()`, `@Post()`, etc. | Method decorator |
| **Request body** | `@Body()` parameter | Method parameter |
| **URL params** | `@Param('id')` | Method parameter |
| **Query params** | `@Query()` | Method parameter |
| **Protection** | `@UseGuards(JwtAuthGuard)` | Requires JWT |
| **Validation** | DTO files | `*.dto.ts` |
| **Business logic** | Service files | `*.service.ts` |

---

## Common Patterns

### Get all items
```typescript
@Get()
async findAll() { ... }
// GET /api/v1/resource
```

### Get single item by ID
```typescript
@Get(':id')
async findOne(@Param('id') id: string) { ... }
// GET /api/v1/resource/123
```

### Create item
```typescript
@Post()
async create(@Body() createDto: CreateDto) { ... }
// POST /api/v1/resource
```

### Update item
```typescript
@Put(':id')
async update(@Param('id') id: string, @Body() updateDto: UpdateDto) { ... }
// PUT /api/v1/resource/123
```

### Delete item
```typescript
@Delete(':id')
async remove(@Param('id') id: string) { ... }
// DELETE /api/v1/resource/123
```

---

**TL;DR**: Look in `*.controller.ts` files - that's where ALL endpoints are declared! Each `@Get()`, `@Post()`, etc. decorator creates a route.
