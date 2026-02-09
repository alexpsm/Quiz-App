import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const auth = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  processSession: (sessionId) => api.get(`/auth/session?session_id=${sessionId}`),
  me: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
};

export const users = {
  updateProfile: (data) => api.put('/users/me', data),
  leaderboard: (limit = 50) => api.get(`/users/leaderboard?limit=${limit}`),
  clubLeaderboard: (club) => api.get(`/users/club-leaderboard${club ? `?club=${encodeURIComponent(club)}` : ''}`),
  search: (query) => api.get(`/users/search?q=${query}`),
};

export const clubs = {
  getAll: () => api.get('/clubs'),
  getList: () => api.get('/clubs/list'),
};

export const questions = {
  list: (category, limit = 100) => api.get(`/questions${category ? `?category=${category}` : ''}`, { params: { limit } }),
  create: (data, password) => api.post('/questions', data, { params: { password } }),
  categories: () => api.get('/questions/categories'),
};

export const games = {
  matchmake: () => api.post('/games/matchmake'),
  clubChallenge: () => api.post('/games/club-challenge'),
  createInvite: () => api.post('/games/invite'),
  joinGame: (inviteCode) => api.post(`/games/join/${inviteCode}`),
  list: () => api.get('/games'),
  get: (gameId) => api.get(`/games/${gameId}`),
  selectCategory: (gameId, category) => api.post(`/games/${gameId}/select-category`, null, { params: { category } }),
  submitAnswer: (gameId, data) => api.post(`/games/${gameId}/answer`, data),
};

export default api;