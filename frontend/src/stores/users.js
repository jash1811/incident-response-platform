import { defineStore } from 'pinia'
import { api } from 'src/boot/axios'

export const useUsersStore = defineStore('users', {
    state: () => ({
        users: [],
        pagination: null,
        loading: false,
        error: null,
    }),

    actions: {
        async fetchUsers(params = {}) {
            this.loading = true
            this.error = null
            try {
                const res = await api.get('/api/users', { params })
                this.users = res.data.users
                this.pagination = res.data.pagination
            } catch (err) {
                this.error = err.response?.data?.error || 'Failed to load users'
            } finally {
                this.loading = false
            }
        },

        async createUser(payload) {
            this.loading = true
            this.error = null
            try {
                const res = await api.post('/api/users', payload)
                this.users.unshift(res.data.user)
                return { success: true, user: res.data.user }
            } catch (err) {
                this.error = err.response?.data?.error || 'Failed to create user'
                return { success: false, error: this.error }
            } finally {
                this.loading = false
            }
        },
    },
})
