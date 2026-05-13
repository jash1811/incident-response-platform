/**
 * Dashboard API service layer.
 */
import { api } from 'src/boot/axios'

export const dashboardService = {
  getStats() {
    return api.get('/api/dashboard/stats')
  },
}
