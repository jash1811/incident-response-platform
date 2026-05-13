import axios from 'axios'
import { useAuthStore } from 'src/stores/auth'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
    timeout: 15000,
})

// Request interceptor – attach JWT
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

// Response interceptor – handle 401
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            const authStore = useAuthStore()
            authStore.logout()
            // Redirect handled by router guard
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

export default api
export { api }
