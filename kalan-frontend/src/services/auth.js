import { apiClient } from './apiClient'

export const register = (data) => apiClient.post('/api/v1/auth/register', data)
export const login = (data) => apiClient.post('/api/v1/auth/login', data)
export const refresh = () => apiClient.post('/api/v1/auth/refresh', undefined)
export const logout = () => apiClient.post('/api/v1/auth/logout', undefined)
export const me = () => apiClient.get('/api/v1/auth/me')