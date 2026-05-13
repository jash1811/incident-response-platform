/**
 * User API service layer.
 */
import { api } from 'src/boot/axios'

export const userService = {
  list(params = {}) {
    return api.get('/api/users', { params })
  },

  create(payload) {
    return api.post('/api/users', payload)
  },
}
