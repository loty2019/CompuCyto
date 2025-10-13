# Quick Visual Guide: Vue ↔️ NestJS Communication

## The Simple Version

```
┌──────────────┐                    ┌──────────────┐
│     USER     │                    │   DATABASE   │
└──────┬───────┘                    └──────▲───────┘
       │                                   │
       │ 1. Clicks "Login"                 │
       ↓                                   │
┌──────────────┐                           │
│  Login.vue   │                           │
│  Component   │                           │
└──────┬───────┘                           │
       │                                   │
       │ 2. Calls authStore.login()        │
       ↓                                   │
┌──────────────┐                           │
│  auth.ts     │                           │
│  Pinia Store │                           │
└──────┬───────┘                           │
       │                                   │
       │ 3. Calls authAPI.login()          │
       ↓                                   │
┌──────────────┐                           │
│  client.ts   │                           │
│  Axios HTTP  │                           │
└──────┬───────┘                           │
       │                                   │
       │ 4. POST /api/v1/auth/login        │
       │    Body: { email, password }      │
       ↓                                   │
┌──────────────┐                           │
│  Vite Proxy  │                           │
│  Port 5173   │                           │
└──────┬───────┘                           │
       │                                   │
       │ 5. Forwards to port 3000          │
       ↓                                   │
┌──────────────┐                           │
│ auth.controller.ts                       │
│ NestJS       │                           │
└──────┬───────┘                           │
       │                                   │
       │ 6. Calls authService.login()      │
       ↓                                   │
┌──────────────┐                           │
│ auth.service.ts                          │
│ Business Logic                           │
└──────┬───────┘                           │
       │                                   │
       │ 7. Validates & queries DB         │
       └───────────────────────────────────┘
       ┌───────────────────────────────────┐
       │ 8. Returns user + JWT token       │
       ↓                                   
┌──────────────┐                           
│ auth.service │                           
└──────┬───────┘                           
       │ 9. Generates JWT                  
       ↓                                   
┌──────────────┐                           
│ auth.controller                          
└──────┬───────┘                           
       │ 10. Sends HTTP response           
       │     { access_token, user }        
       ↓                                   
┌──────────────┐                           
│  Vite Proxy  │                           
└──────┬───────┘                           
       │ 11. Returns to Vue                
       ↓                                   
┌──────────────┐                           
│  client.ts   │                           
│  Axios       │                           
└──────┬───────┘                           
       │ 12. Response interceptor runs     
       ↓                                   
┌──────────────┐                           
│  auth.ts     │                           
│  Store       │                           
└──────┬───────┘                           
       │ 13. Saves token to localStorage   
       │     Updates state                 
       ↓                                   
┌──────────────┐                           
│  Login.vue   │                           
└──────┬───────┘                           
       │ 14. Redirects to home             
       ↓                                   
┌──────────────┐                           
│     USER     │                           
│   Logged In! │                           
└──────────────┘                           
```

---

## The Tech Stack

```
┌─────────────────────────────────────┐
│         FRONTEND (Port 5173)        │
├─────────────────────────────────────┤
│  Vue 3          - UI Framework      │
│  Pinia          - State Management  │
│  Vue Router     - Navigation        │
│  Axios          - HTTP Client       │
│  TypeScript     - Type Safety       │
│  Tailwind CSS   - Styling           │
│  Vite           - Build Tool        │
└─────────────────────────────────────┘
                  │
                  │ HTTP Requests
                  │ (JSON)
                  ↓
┌─────────────────────────────────────┐
│         BACKEND (Port 3000)         │
├─────────────────────────────────────┤
│  NestJS         - Framework         │
│  TypeScript     - Language          │
│  JWT            - Authentication    │
│  bcrypt         - Password Hashing  │
│  TypeORM        - Database ORM      │
│  class-validator - Validation       │
│  PostgreSQL     - Database          │
└─────────────────────────────────────┘
```

---

## HTTP Request Example

### What Vue Sends:
```http
POST /api/v1/auth/login HTTP/1.1
Host: localhost:5173
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### What NestJS Receives (after Vite proxy):
```http
POST /api/v1/auth/login HTTP/1.1
Host: localhost:3000
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### What NestJS Sends Back:
```http
HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: http://localhost:5173

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "testuser",
    "role": "user"
  }
}
```

---

## JWT Token Flow

### 1. Login Request (No Token):
```
Vue → POST /api/v1/auth/login
      { email, password }
      
NestJS → Validates credentials
      → Generates JWT token
      → Returns: { access_token, user }
```

### 2. Vue Stores Token:
```javascript
localStorage.setItem('access_token', 'eyJhbGc...')
```

### 3. Subsequent Requests (With Token):
```
Vue → GET /api/v1/control/status
      Headers: {
        Authorization: 'Bearer eyJhbGc...'
      }
      
NestJS → Validates JWT token
      → Extracts user ID from token
      → Processes request
      → Returns data
```

---

## File Locations

```
CompuCyto/
├── frontend-vue/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts         ← HTTP client & API functions
│   │   ├── stores/
│   │   │   └── auth.ts           ← Authentication state
│   │   ├── views/
│   │   │   ├── Login.vue         ← Login UI
│   │   │   └── Register.vue      ← Register UI
│   │   └── router/
│   │       └── index.ts          ← Route guards
│   └── vite.config.ts            ← Proxy configuration
│
└── Nest/
    └── src/
        ├── auth/
        │   ├── auth.controller.ts  ← Login/Register endpoints
        │   ├── auth.service.ts     ← Authentication logic
        │   └── strategies/
        │       └── jwt.strategy.ts ← JWT validation
        └── main.ts                 ← CORS configuration
```

---

## The Three Key Files

### 1. Frontend API Client (`client.ts`):
```typescript
const apiClient = axios.create({
  baseURL: '/',
  headers: { 'Content-Type': 'application/json' }
})

// Auto-add JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### 2. Vite Proxy (`vite.config.ts`):
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:3000',
      changeOrigin: true
    }
  }
}
```

### 3. NestJS CORS (`main.ts`):
```typescript
app.enableCors({
  origin: ['http://localhost:5173'],
  credentials: true
})
```

---

## Common Questions

**Q: Why do we need a proxy?**
A: In development, Vue (5173) and NestJS (3000) are on different ports. The browser blocks cross-origin requests by default. The Vite proxy tricks the browser by making it think all requests go to 5173.

**Q: What happens in production?**
A: You build Vue (`npm run build`) and serve the static files from NestJS or nginx. Everything runs on the same origin, no proxy needed.

**Q: Where is the JWT token stored?**
A: In localStorage in the browser. It's automatically added to all requests by the Axios interceptor.

**Q: How does NestJS know who's making the request?**
A: The JWT token contains the user ID. NestJS decodes it and attaches the user to the request object.

**Q: What if the token expires?**
A: NestJS returns 401 Unauthorized. The response interceptor catches this, clears localStorage, and redirects to login.

---

## Summary

**Simple Answer:**
- Vue makes HTTP requests using Axios
- Vite proxy forwards them to NestJS
- NestJS processes and returns JSON
- Axios receives the response
- Vue updates the UI

**With Authentication:**
- User logs in → Gets JWT token
- Token stored in localStorage
- Token automatically added to all requests
- NestJS validates token on protected routes

**It's just HTTP!** 🌐
