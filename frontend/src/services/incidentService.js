/**
 * Incident API service layer.
 * Wraps raw axios calls so stores stay clean.
 * TODO: add request cancellation tokens for search debouncing
 */
import { api } from 'src/boot/axios'

export const incidentService = {
  list(params = {}) {
    return api.get('/api/incidents', { params })
  },

  get(id) {
    return api.get(`/api/incidents/${id}`)
  },

  create(payload) {
    return api.post('/api/incidents', payload)
  },

  update(id, payload) {
    return api.put(`/api/incidents/${id}`, payload)
  },

  resolve(id, version) {
    return api.patch(`/api/incidents/${id}/resolve`, { version })
  },

  assign(id, assignedTo, version) {
    return api.patch(`/api/incidents/${id}/assign`, {
      assigned_to: assignedTo,
      version,
    })
  },

  getComments(incidentId, params = {}) {
    return api.get(`/api/incidents/${incidentId}/comments`, { params })
  },

  addComment(incidentId, comment) {
    return api.post(`/api/incidents/${incidentId}/comments`, { comment })
  },

  getActivity(incidentId) {
    return api.get(`/api/incidents/${incidentId}/activity`)
  },
}
