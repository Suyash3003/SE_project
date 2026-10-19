import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  try {
    const session = JSON.parse(localStorage.getItem('paintflow_session'))
    if (session?.token) config.headers.Authorization = `Bearer ${session.token}`
  } catch {
    localStorage.removeItem('paintflow_session')
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) localStorage.removeItem('paintflow_session')
    return Promise.reject(error)
  },
)

export default api
