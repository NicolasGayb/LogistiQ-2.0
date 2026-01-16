import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = proccess.env.EXPO_PUBLIC_API_URL;

export async function apiFetch(
  url: string,
  options: RequestInit = {}
){
  const token = await AsyncStorage.getItem('access_token');

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...API_URL(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${url}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    await AsyncStorage.removeItem('access_token');
    // navegação para login será tratada no AuthContext
  }

  return response;
}
