import axios from 'axios';
import { getToken } from '../utils/tokenStorage';

const client = axios.create({
  baseURL: 'https://api.logistiq.com', // ou localhost para dev
});

client.interceptors.request.use(config => {
  const token = getToken();
  if (token && config.headers) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

export default client;
