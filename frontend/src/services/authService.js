/**
 * Auth API service layer.
 */
import { api } from 'src/boot/axios'

export const authService = {
  login(email, password) {
    return api.post('/api/auth/login', { email, password })
  },

  register(payload) {
    return api.post('/api/auth/register', payload)
  },
}
