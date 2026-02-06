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
    if (error.response?.status === 503) {
      // Redireciona para a página de manutenção
      if (!window.location.pathname.includes('/maintenance')) {
        // Limpa token e dados de usuário para evitar loops de erro
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        sessionStorage.clear();
        window.location.href = '/maintenance';
      }
    }
    return Promise.reject(error);
  }
);

export default api;