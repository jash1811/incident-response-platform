import axios from 'axios'
import { useAuthStore } from 'src/stores/auth'

// In dev: VITE_API_URL is empty so baseURL is '' and the vite proxy handles /api/*
// In production: VITE_API_URL is the full Render backend URL
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '',
    timeout: 15000,
})

// Attach JWT token to every request
api.interceptors.request.use(
    (config) => {
        const authStore = useAuthStore()
        if (authStore.token) {
            config.headers.Authorization = `Bearer ${authStore.token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

// Handle 401 globally — clear auth and redirect to login
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            const authStore = useAuthStore()
            authStore.logout()
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

export default api
export { api }
