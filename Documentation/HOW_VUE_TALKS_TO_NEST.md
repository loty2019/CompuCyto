# How Vue Communicates with NestJS - Complete Explanation

## 🌐 Overview: The Communication Flow

Your CompuCyto application has **two separate servers** that communicate via HTTP:

```
┌─────────────────────┐         HTTP Requests        ┌─────────────────────┐
│   Vue Frontend      │  ───────────────────────────> │   NestJS Backend    │
│   localhost:5173    │                               │   localhost:3000    │
│                     │  <───────────────────────────  │                     │
│  (User Interface)   │      HTTP Responses + JWT     │   (API + Database)  │
└─────────────────────┘                               └─────────────────────┘
```

## 🔧 The 5 Key Components

### 1. **Vite Proxy** (Development Only)
**Location**: `frontend-vue/vite.config.ts`

```typescript
server: {
  port: 5173,
  proxy: {
    '/api': {
      // Proxy API requests to the NestJS backend
      target: 'http://localhost:3000',
      changeOrigin: true
    }
  }
}
```

**What it does:**
- When Vue app makes a request to `/api/v1/auth/login`
- Vite intercepts it and forwards to `http://localhost:3000/api/v1/auth/login`
- This prevents CORS errors during development
- **Only works in development** (npm run dev)

---

### 2. **Axios HTTP Client**
**Location**: `frontend-vue/src/api/client.ts`

```typescript
import axios from 'axios'

// Create axios instance
const apiClient = axios.create({
  baseURL: '/',  // Uses Vite proxy in dev
  headers: {
    'Content-Type': 'application/json'
  }
})
```

**What it does:**
- Axios is a library for making HTTP requests (like fetch but better)
- Creates a reusable HTTP client with default settings
- All API calls use this client

---

### 3. **Request Interceptor** (Automatic JWT Token)
**Location**: `frontend-vue/src/api/client.ts`

```typescript
// Add JWT token to every request automatically
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)
```

**What it does:**
- **BEFORE** sending any request, this runs automatically
- Grabs the JWT token from localStorage
- Adds it to the request headers: `Authorization: Bearer eyJhbGc...`
- Backend uses this to identify who you are

---

### 4. **Response Interceptor** (Auto-Logout on 401)
**Location**: `frontend-vue/src/api/client.ts`

```typescript
// Handle unauthorized responses
apiClient.interceptors.response.use(
  (response) => response,  // Success - pass through
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

**What it does:**
- **AFTER** receiving a response, this runs automatically
- If status code is 401 (Unauthorized), logs user out
- Redirects to login page
- Handles expired tokens gracefully

---

### 5. **API Functions** (Organized Endpoints)
**Location**: `frontend-vue/src/api/client.ts`

```typescript
export const authAPI = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const { data } = await apiClient.post<AuthResponse>(
      '/api/v1/auth/login', 
      credentials
    )
    return data
  },

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const { data } = await apiClient.post<AuthResponse>(
      '/api/v1/auth/register', 
      userData
    )
    return data
  }
}

export const controlAPI = {
  async getStatus(): Promise<SystemStatus> {
    const { data } = await apiClient.get<SystemStatus>(
      '/api/v1/control/status'
    )
    return data
  }
}
```

**What it does:**
- Organizes all API calls into logical groups
- Makes it easy to call from Vue components
- Provides TypeScript type safety

---

## 🔄 Complete Request Flow Example

### Example: User Logs In

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: User enters email & password in Login.vue              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Component calls auth store                              │
│                                                                  │
│   const result = await authStore.login(                         │
│     'user@example.com',                                         │
│     'password123'                                               │
│   )                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Auth store calls API function                           │
│   (stores/auth.ts)                                              │
│                                                                  │
│   const response = await authAPI.login({                        │
│     email: 'user@example.com',                                  │
│     password: 'password123'                                     │
│   })                                                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Axios makes POST request                                │
│   (api/client.ts)                                               │
│                                                                  │
│   POST http://localhost:5173/api/v1/auth/login                 │
│   Headers: { 'Content-Type': 'application/json' }              │
│   Body: {                                                        │
│     "email": "user@example.com",                                │
│     "password": "password123"                                   │
│   }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Vite Proxy forwards to NestJS                          │
│   (vite.config.ts)                                              │
│                                                                  │
│   Sees "/api" in URL                                            │
│   Forwards to: http://localhost:3000/api/v1/auth/login        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: NestJS receives request                                 │
│   (Nest/src/auth/auth.controller.ts)                           │
│                                                                  │
│   @Post('api/v1/auth/login')                                   │
│   async login(@Body() loginDto: LoginDto) {                    │
│     // Validates email & password                               │
│     // Generates JWT token                                      │
│     return {                                                     │
│       access_token: 'eyJhbGciOiJIUzI1NiIs...',                 │
│       user: { id: 1, email: '...', ... }                       │
│     }                                                            │
│   }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: NestJS sends response back                              │
│                                                                  │
│   HTTP 200 OK                                                    │
│   {                                                              │
│     "access_token": "eyJhbGciOiJIUzI1NiIs...",                 │
│     "user": {                                                    │
│       "id": 1,                                                   │
│       "email": "user@example.com",                              │
│       "username": "testuser",                                   │
│       "role": "user"                                            │
│     }                                                            │
│   }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 8: Axios receives response                                 │
│                                                                  │
│   Response interceptor runs (no error, passes through)          │
│   Returns data to authAPI.login()                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 9: Auth store processes response                           │
│   (stores/auth.ts)                                              │
│                                                                  │
│   token.value = response.access_token                           │
│   user.value = response.user                                    │
│   localStorage.setItem('access_token', token)                   │
│   localStorage.setItem('user', JSON.stringify(user))            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 10: Login.vue receives success                             │
│                                                                  │
│   if (result.success) {                                         │
│     router.push('/')  // Redirect to home                       │
│   }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Authenticated Requests (with JWT Token)

After login, all requests include the JWT token:

```
┌─────────────────────────────────────────────────────────────────┐
│ User clicks "Get Camera Status" button                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Component calls: const status = await controlAPI.getStatus()   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Request interceptor AUTOMATICALLY adds JWT token:               │
│                                                                  │
│   GET /api/v1/control/status                                    │
│   Headers: {                                                     │
│     'Content-Type': 'application/json',                         │
│     'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIs...'          │
│   }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ NestJS receives request with JWT token                          │
│                                                                  │
│   @UseGuards(JwtAuthGuard)                                      │
│   @Get('status')                                                │
│   async getStatus() {                                           │
│     // JWT guard validates token                                │
│     // Extracts user from token                                 │
│     // Allows request to proceed                                │
│   }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ CORS (Cross-Origin Resource Sharing)

**The Problem:**
- Vue: `http://localhost:5173`
- NestJS: `http://localhost:3000`
- Different ports = different origins = browser blocks requests!

**The Solution:**

### Development:
1. **Vite Proxy** - Forwards `/api` requests to port 3000
2. **NestJS CORS** - Allows requests from `http://localhost:5173`

### Production:
- Build Vue app: `npm run build`
- Serve static files from NestJS or nginx
- Single origin = no CORS issues

---

## 📦 Data Flow Diagram

```
Vue Component (Login.vue)
        ↓ calls method
Pinia Store (auth.ts)
        ↓ calls API function
API Client (client.ts)
        ↓ makes HTTP request
Axios Library
        ↓ sends to
Vite Proxy (dev only)
        ↓ forwards to
NestJS Controller
        ↓ calls
NestJS Service
        ↓ queries
Database
        ↓ returns data
NestJS Service
        ↓ returns
NestJS Controller
        ↓ sends response
Axios Library
        ↓ returns data
API Client
        ↓ returns
Pinia Store
        ↓ updates state
Vue Component
        ↓ re-renders
User sees result!
```

---

## 🔍 How to See Communication in Action

### Chrome DevTools:

1. Open DevTools (F12)
2. Go to **Network** tab
3. Login to your app
4. Look for request to `/api/v1/auth/login`
5. Click on it to see:
   - **Request Headers** (includes Content-Type)
   - **Request Payload** (email & password)
   - **Response** (JWT token & user data)
   - **Response Headers** (status code, CORS headers)

### For Authenticated Requests:
1. Stay on Network tab
2. Click any button (e.g., "Get Status")
3. Look at request to `/api/v1/control/status`
4. See **Authorization** header with JWT token!

---

## 🎯 Key Takeaways

1. **Vue and NestJS are separate applications**
   - Vue (frontend) runs on port 5173
   - NestJS (backend) runs on port 3000

2. **They communicate via HTTP requests**
   - Vue uses Axios to make requests
   - NestJS receives requests via controllers

3. **Vite Proxy bridges them in development**
   - Prevents CORS errors
   - Forwards `/api` requests to port 3000

4. **JWT tokens authenticate requests**
   - Stored in localStorage after login
   - Automatically added to all requests
   - Backend validates token on protected routes

5. **Interceptors add smart behavior**
   - Request interceptor: Adds JWT token
   - Response interceptor: Handles errors

6. **Type safety with TypeScript**
   - Interfaces define request/response shapes
   - Compile-time checking prevents bugs

---

## 📝 Real Code Examples

### Vue Component Makes Request:
```typescript
// In Login.vue
const handleLogin = async () => {
  const result = await authStore.login(email.value, password.value)
  if (result.success) {
    router.push('/')
  }
}
```

### Store Calls API:
```typescript
// In stores/auth.ts
const login = async (email: string, password: string) => {
  const response = await authAPI.login({ email, password })
  token.value = response.access_token
  user.value = response.user
}
```

### API Makes HTTP Request:
```typescript
// In api/client.ts
export const authAPI = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const { data } = await apiClient.post('/api/v1/auth/login', credentials)
    return data
  }
}
```

### NestJS Receives Request:
```typescript
// In Nest/src/auth/auth.controller.ts
@Post('login')
async login(@Body() loginDto: LoginDto) {
  return this.authService.login(loginDto)
}
```

---

**That's how Vue talks to NestJS! 🚀**

It's like a conversation:
- Vue asks questions (HTTP requests)
- NestJS answers (HTTP responses)
- JWT tokens prove identity
- Axios handles the communication
- Vite proxy bridges them in development
