import axios from 'axios';

// Lógica para decidir quem chamar
const baseURL =
  import.meta.env.VITE_API_URL ??
  'https://logistiq2-6fb648247d8f.herokuapp.com';
console.log("API Base URL:", baseURL);

const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      // Opcional: só redireciona se não estiver já na tela de login
      if (!window.location.pathname.includes('/login')) {
         window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;