import axios from 'axios'
import { useAuthStore } from 'src/stores/auth'

// Always use relative /api/* paths.
// - In dev: Vite proxy forwards /api/* → localhost:5000
// - In production: Netlify redirect rule forwards /api/* → Render backend
// This means NO hardcoded backend URL needed in the frontend at all.
const api = axios.create({
    baseURL: '',
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
            window.location.href = '/#/login'
        }
        return Promise.reject(error)
    }
)

export default api
export { api }
