import api from './client'

export const login = (data) => api.post('/auth/login', data)
export const registerCustomer = (data) => api.post('/auth/register/customer', data)
export const registerDealer = (data) => api.post('/auth/register/dealer', data)
export const requestPasswordReset = (identifier) => api.post('/auth/forgot-password', { identifier })
export const resetPassword = (data) => api.post('/auth/reset-password', data)
export const fetchCurrentUser = () => api.get('/auth/me')
