# NestJS Endpoints - Where They're Declared

## 🎯 Quick Answer

**All endpoints are declared in CONTROLLER files** using decorators like `@Get()`, `@Post()`, `@Put()`, `@Delete()`.

## 📁 Controller Files Location

```
Nest/src/
├── auth/
│   └── auth.controller.ts          ← Authentication endpoints
├── camera/
│   └── camera.controller.ts        ← Camera control endpoints
├── stage/
│   └── stage.controller.ts         ← Stage movement endpoints
├── microscope/
│   └── microscope.controller.ts    ← Light/focus endpoints
├── users/
│   └── users.controller.ts         ← User management endpoints
├── property/
│   └── property.controller.ts      ← Property endpoints
└── common/
    └── controllers/
        └── health.controller.ts    ← Health check endpoint
```

---

## 🗺️ Complete Endpoint Map

### 1. **Authentication** (`auth.controller.ts`)
**Base path**: `/api/v1/auth`

```typescript
@Controller('api/v1/auth')
export class AuthController {
  
  @Post('register')              // POST /api/v1/auth/register
  async register() { ... }
  
  @Post('login')                 // POST /api/v1/auth/login
  async login() { ... }
  
  @Get('profile')                // GET /api/v1/auth/profile
  @UseGuards(JwtAuthGuard)       // 🔒 Protected
  async getProfile() { ... }
}
```

**Endpoints:**
- `POST /api/v1/auth/register` - Create new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/profile` - Get current user profile (protected)

---

### 2. **Camera** (`camera.controller.ts`)
**Base path**: `/api/v1/camera`

```typescript
@Controller('api/v1/camera')
@UseGuards(JwtAuthGuard)         // 🔒 All endpoints protected
export class CameraController {
  
  @Post('capture')               // POST /api/v1/camera/capture
  async capture() { ... }
  
  @Get('settings')               // GET /api/v1/camera/settings
  async getSettings() { ... }
  
  @Put('settings')               // PUT /api/v1/camera/settings
  async updateSettings() { ... }
  
  @Get('preview')                // GET /api/v1/camera/preview
  async getPreview() { ... }
}
```

**Endpoints:**
- `POST /api/v1/camera/capture` - Capture image
- `GET /api/v1/camera/settings` - Get camera settings
- `PUT /api/v1/camera/settings` - Update camera settings
- `GET /api/v1/camera/preview` - Get camera preview stream

---

### 3. **Stage** (`stage.controller.ts`)
**Base path**: `/api/v1/stage`

```typescript
@Controller('api/v1/stage')
@UseGuards(JwtAuthGuard)         // 🔒 All endpoints protected
export class StageController {
  
  @Post('move')                  // POST /api/v1/stage/move
  async move() { ... }
  
  @Get('position')               // GET /api/v1/stage/position
  async getPosition() { ... }
  
  @Post('home')                  // POST /api/v1/stage/home
  async home() { ... }
  
  @Post('stop')                  // POST /api/v1/stage/stop
  async emergencyStop() { ... }
  
  @Get('limits')                 // GET /api/v1/stage/limits
  async getLimits() { ... }
}
```

**Endpoints:**
- `POST /api/v1/stage/move` - Move stage to position
- `GET /api/v1/stage/position` - Get current position
- `POST /api/v1/stage/home` - Home all axes
- `POST /api/v1/stage/stop` - Emergency stop
- `GET /api/v1/stage/limits` - Get safety limits

---

### 4. **Microscope** (`microscope.controller.ts`)
**Base path**: `/api/v1/microscope`

```typescript
@Controller('api/v1/microscope')
@UseGuards(JwtAuthGuard)         // 🔒 All endpoints protected
export class MicroscopeController {
  
  @Get('light/status')           // GET /api/v1/microscope/light/status
  async getLightStatus() { ... }
  
  @Post('light/set')             // POST /api/v1/microscope/light/set
  async setLight() { ... }
}
```

**Endpoints:**
- `GET /api/v1/microscope/light/status` - Get light status
- `POST /api/v1/microscope/light/set` - Set light on/off/brightness

---

### 5. **Health Check** (`health.controller.ts`)
**Base path**: `/api/v1/health`

```typescript
@Controller('api/v1/health')
export class HealthController {
  
  @Get()                         // GET /api/v1/health
  async check() { ... }          // 🔓 Public (no auth required)
}
```

**Endpoints:**
- `GET /api/v1/health` - System health check (public)

---

### 6. **Users** (`users.controller.ts`)
**Base path**: `/api/v1/users`

```typescript
@Controller('api/v1/users')
@UseGuards(JwtAuthGuard)         // 🔒 All endpoints protected
export class UsersController {
  
  @Get()                         // GET /api/v1/users
  async findAll() { ... }
  
  @Get(':id')                    // GET /api/v1/users/:id
  async findOne() { ... }
  
  @Put(':id')                    // PUT /api/v1/users/:id
  async update() { ... }
  
  @Delete(':id')                 // DELETE /api/v1/users/:id
  async remove() { ... }
}
```

**Endpoints:**
- `GET /api/v1/users` - List all users
- `GET /api/v1/users/:id` - Get user by ID
- `PUT /api/v1/users/:id` - Update user
- `DELETE /api/v1/users/:id` - Delete user

---

## 🔍 How to Read Controller Decorators

### Base Path:
```typescript
@Controller('api/v1/auth')   ← This is the base path
```

### HTTP Methods:
```typescript
@Get()        ← GET request
@Post()       ← POST request
@Put()        ← PUT request
@Patch()      ← PATCH request
@Delete()     ← DELETE request
```

### Route Parameters:
```typescript
@Get(':id')   ← GET /api/v1/users/123
              ← :id becomes a parameter

async findOne(@Param('id') id: string) {
  // Access the ID from URL
}
```

### Request Body:
```typescript
@Post('login')
async login(@Body() loginDto: LoginDto) {
  // loginDto contains the JSON from request body
}
```

### Protection (Authentication):
```typescript
@UseGuards(JwtAuthGuard)   ← Requires JWT token
// Can be on class (all methods) or individual method
```

---

## 📊 Complete Endpoint Summary

### Public Endpoints (No Auth Required):
```
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/health
```

### Protected Endpoints (JWT Required):
```
Authentication:
  GET  /api/v1/auth/profile

Camera:
  POST /api/v1/camera/capture
  GET  /api/v1/camera/settings
  PUT  /api/v1/camera/settings
  GET  /api/v1/camera/preview

Stage:
  POST /api/v1/stage/move
  GET  /api/v1/stage/position
  POST /api/v1/stage/home
  POST /api/v1/stage/stop
  GET  /api/v1/stage/limits

Microscope:
  GET  /api/v1/microscope/light/status
  POST /api/v1/microscope/light/set

Users:
  GET    /api/v1/users
  GET    /api/v1/users/:id
  PUT    /api/v1/users/:id
  DELETE /api/v1/users/:id
```

---

## 🎨 Anatomy of a Controller

```typescript
// 1. Imports
import { Controller, Get, Post, Body } from '@nestjs/common';

// 2. Swagger docs
@ApiTags('Auth')

// 3. Base path
@Controller('api/v1/auth')

// 4. Global guards (optional)
@UseGuards(JwtAuthGuard)

// 5. Controller class
export class AuthController {
  
  // 6. Dependency injection
  constructor(private authService: AuthService) {}
  
  // 7. Endpoint methods
  @Post('login')                    // HTTP method + path
  @ApiOperation({ ... })            // Swagger docs
  @ApiResponse({ ... })             // Response docs
  async login(                      // Method name
    @Body() loginDto: LoginDto      // Parameters
  ) {
    return this.authService.login(loginDto);  // Business logic
  }
}
```

---

## 🔧 How Endpoints Are Registered

### 1. Controller is created
```typescript
// auth.controller.ts
@Controller('api/v1/auth')
export class AuthController { ... }
```

### 2. Controller is added to Module
```typescript
// auth.module.ts
@Module({
  controllers: [AuthController],  ← Register controller
  providers: [AuthService],
  exports: [AuthService]
})
export class AuthModule {}
```

### 3. Module is imported in App Module
```typescript
// app.module.ts
@Module({
  imports: [
    AuthModule,        ← Import module with controller
    CameraModule,
    StageModule,
    // ... other modules
  ]
})
export class AppModule {}
```

### 4. NestJS automatically creates routes
When the app starts, NestJS:
- Scans all controllers
- Registers all decorated methods as routes
- Sets up middleware, guards, interceptors
- Makes endpoints available

---

## 🔎 How to Find Endpoints

### Method 1: Check Controllers
Look in `src/*/` for `*.controller.ts` files

### Method 2: Swagger Documentation
Visit: `http://localhost:3000/api-docs`
- See all endpoints
- Try them out
- View request/response schemas

### Method 3: Search for Decorators
```bash
# Find all GET endpoints
grep -r "@Get" src/

# Find all POST endpoints
grep -r "@Post" src/

# Find all controllers
find src/ -name "*.controller.ts"
```

### Method 4: Check App Logs
When NestJS starts, it logs all routes:
```
[Nest] 12345  - 10/10/2025, 10:30:45 AM     LOG [RoutesResolver] AuthController {/api/v1/auth}:
[Nest] 12345  - 10/10/2025, 10:30:45 AM     LOG [RouterExplorer] Mapped {/api/v1/auth/register, POST} route
[Nest] 12345  - 10/10/2025, 10:30:45 AM     LOG [RouterExplorer] Mapped {/api/v1/auth/login, POST} route
```

---

## 🎯 Quick Reference Table

| Feature | File Type | Example |
|---------|-----------|---------|
| **Endpoints** | `*.controller.ts` | `auth.controller.ts` |
| **Business Logic** | `*.service.ts` | `auth.service.ts` |
| **Validation** | `dto/*.dto.ts` | `login.dto.ts` |
| **Database Models** | `entities/*.entity.ts` | `user.entity.ts` |
| **Module Config** | `*.module.ts` | `auth.module.ts` |
| **Guards** | `guards/*.guard.ts` | `jwt-auth.guard.ts` |

---

## 💡 Pro Tips

1. **Follow the pattern**: `{feature}/{feature}.controller.ts`
2. **Use Swagger**: Best way to see all endpoints
3. **Controllers = Routes**: Each controller defines a group of related endpoints
4. **Decorators define behavior**: `@Get()`, `@Post()`, `@UseGuards()`, etc.
5. **Check module imports**: If a controller doesn't work, check if its module is imported

---

## 🚀 Example: Adding a New Endpoint

Want to add `GET /api/v1/camera/status`?

```typescript
// In camera.controller.ts

@Get('status')                     // Add this
@ApiOperation({ 
  summary: 'Get camera status' 
})
async getStatus() {
  return this.cameraService.getStatus();
}
```

That's it! NestJS automatically:
- Creates the route
- Adds it to Swagger docs
- Applies class-level guards
- Makes it available at `GET /api/v1/camera/status`

---

**TL;DR**: All endpoints are in `*.controller.ts` files, defined using decorators like `@Get()` and `@Post()`. Check Swagger docs at `/api-docs` to see them all!
