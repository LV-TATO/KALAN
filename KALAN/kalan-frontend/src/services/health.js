import { apiClient } from './apiClient'

export function checkBackendHealth() {
  return apiClient.get('/health')
}