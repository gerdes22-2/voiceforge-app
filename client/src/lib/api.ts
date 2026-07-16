import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const projectApi = {
  getProjects: () => api.get('/projects/'),
  createProject: (data: any) => api.post('/projects/', data),
};

export const modelApi = {
  getModels: () => api.get('/voice-models/'), // Note: adjust route if needed
  approveModel: (id: string, status: string) => api.post(`/voice-models/${id}/status`, { status }),
};

export const jobsApi = {
  getJobs: () => api.get('/jobs/'), // Assuming a jobs endpoint exists
};

export const authApi = {
  login: (data: any) => api.post('/auth/login', data), // form-data for OAuth2PasswordRequestForm
};

export const feedbackApi = {
  submitFeedback: (data: any) => api.post('/feedbacks/', data),
};
