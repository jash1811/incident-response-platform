import { defineStore } from 'pinia'
import { api } from 'src/boot/axios'

export const useIncidentStore = defineStore('incidents', {
    state: () => ({
        incidents: [],
        currentIncident: null,
        comments: [],
        activity: [],
        pagination: null,
        loading: false,
        error: null,
    }),

    actions: {
        async fetchIncidents(params = {}) {
            this.loading = true
            this.error = null
            try {
                const res = await api.get('/api/incidents', { params })
                this.incidents = res.data.incidents
                this.pagination = res.data.pagination
            } catch (err) {
                this.error = err.response?.data?.error || 'Failed to load incidents'
            } finally {
                this.loading = false
            }
        },

        async fetchIncident(id) {
            this.loading = true
            this.error = null
            try {
                const res = await api.get(`/api/incidents/${id}`)
                this.currentIncident = res.data.incident
                return res.data.incident
            } catch (err) {
                this.error = err.response?.data?.error || 'Failed to load incident'
                return null
            } finally {
                this.loading = false
            }
        },

        async createIncident(payload) {
            this.loading = true
            this.error = null
            try {
                const res = await api.post('/api/incidents', payload)
                return { success: true, incident: res.data.incident }
            } catch (err) {
                this.error = err.response?.data?.error || 'Failed to create incident'
                return { success: false, error: this.error }
            } finally {
                this.loading = false
            }
        },

        async updateIncident(id, payload) {
            this.loading = true
            this.error = null
            try {
                const res = await api.put(`/api/incidents/${id}`, payload)
                this.currentIncident = res.data.incident
                return { success: true, incident: res.data.incident }
            } catch (err) {
                const errMsg = err.response?.data?.error || 'Failed to update incident'
                this.error = errMsg
                return { success: false, error: errMsg }
            } finally {
                this.loading = false
            }
        },

        async resolveIncident(id, version) {
            this.loading = true
            try {
                const res = await api.patch(`/api/incidents/${id}/resolve`, { version })
                this.currentIncident = res.data.incident
                return { success: true }
            } catch (err) {
                return { success: false, error: err.response?.data?.error || 'Failed to resolve' }
            } finally {
                this.loading = false
            }
        },

        async assignIncident(id, assignedTo, version) {
            this.loading = true
            try {
                const res = await api.patch(`/api/incidents/${id}/assign`, {
                    assigned_to: assignedTo,
                    version,
                })
                this.currentIncident = res.data.incident
                return { success: true }
            } catch (err) {
                return { success: false, error: err.response?.data?.error || 'Failed to assign' }
            } finally {
                this.loading = false
            }
        },

        async fetchComments(incidentId) {
            try {
                const res = await api.get(`/api/incidents/${incidentId}/comments`)
                this.comments = res.data.comments
            } catch (err) {
                console.error('Failed to fetch comments', err)
            }
        },

        async addComment(incidentId, comment) {
            try {
                const res = await api.post(`/api/incidents/${incidentId}/comments`, { comment })
                this.comments.push(res.data.comment)
                return { success: true }
            } catch (err) {
                return { success: false, error: err.response?.data?.error || 'Failed to add comment' }
            }
        },

        async fetchActivity(incidentId) {
            try {
                const res = await api.get(`/api/incidents/${incidentId}/activity`)
                this.activity = res.data.activity
            } catch (err) {
                console.error('Failed to fetch activity', err)
            }
        },
    },
})
