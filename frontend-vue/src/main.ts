import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
app.use(router)

app.mount('#app')

// Set up global logging function after pinia is initialized
import { useMicroscopeStore } from './stores/microscope'

// Wait for the app to mount, then set up logging
setTimeout(() => {
  const microscopeStore = useMicroscopeStore()
  
  window.__logToConsole = (message: string, type: 'info' | 'success' | 'error' | 'warning') => {
    microscopeStore.addLog(message, type)
  }
  
  // Log that the app is ready
  microscopeStore.addLog('🚀 Application started', 'success')
}, 0)
