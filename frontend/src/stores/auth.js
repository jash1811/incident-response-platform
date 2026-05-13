import { defineStore } from 'pinia'
import { api } from 'src/boot/axios'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('token') || null,
        user: JSON.parse(localStorage.getItem('user') || 'null'),
        loading: false,
        error: null,
    }),

    getters: {
        isAuthenticated: (state) => !!state.token,
        isAdmin: (state) => state.user?.role === 'admin',
        isManager: (state) => state.user?.role === 'manager',
        canManageIncidents: (state) =>
            ['admin', 'manager'].includes(state.user?.role),
        currentUser: (state) => state.user,
    },

    actions: {
        async login(email, password) {
            this.loading = true
            this.error = null
            try {
                const res = await api.post('/api/auth/login', { email, password })
                this.token = res.data.access_token
                this.user = res.data.user
                localStorage.setItem('token', this.token)
                localStorage.setItem('user', JSON.stringify(this.user))
                return true
            } catch (err) {
                this.error = err.response?.data?.error || 'Login failed'
                return false
            } finally {
                this.loading = false
            }
        },

        async register(payload) {
            this.loading = true
            this.error = null
            try {
                const res = await api.post('/api/auth/register', payload)
                this.token = res.data.access_token
                this.user = res.data.user
                localStorage.setItem('token', this.token)
                localStorage.setItem('user', JSON.stringify(this.user))
                return true
            } catch (err) {
                this.error = err.response?.data?.error || 'Registration failed'
                return false
            } finally {
                this.loading = false
            }
        },

        logout() {
            this.token = null
            this.user = null
            localStorage.removeItem('token')
            localStorage.removeItem('user')
        },
    },
})
