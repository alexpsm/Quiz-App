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
  uploadAvatar: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/users/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  leaderboard: (limit = 50) => api.get(`/users/leaderboard?limit=${limit}`),
  clubLeaderboard: (club) => api.get(`/users/club-leaderboard${club ? `?club=${encodeURIComponent(club)}` : ''}`),
  myRank: () => api.get('/users/my-rank'),
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
  randomCategories: () => api.get('/questions/random-categories'),
};

export const games = {
  matchmake: () => api.post('/games/matchmake'),
  quickPlay: () => api.post('/games/quick-play'),
  clubChallenge: () => api.post('/games/club-challenge'),
  createInvite: () => api.post('/games/invite'),
  joinGame: (inviteCode) => api.post(`/games/join/${inviteCode}`),
  createInviteBet: (betAmount) => api.post(`/games/invite-bet?bet_amount=${betAmount}`),
  joinBetGame: (inviteCode) => api.post(`/games/join-bet/${inviteCode}`),
  list: () => api.get('/games'),
  history: (limit = 20) => api.get(`/games/history?limit=${limit}`),
  get: (gameId) => api.get(`/games/${gameId}`),
  selectCategory: (gameId, category) => api.post(`/games/${gameId}/select-category`, null, { params: { category } }),
  submitAnswer: (gameId, data) => api.post(`/games/${gameId}/answer`, data),
  botPlay: (gameId) => api.post(`/games/${gameId}/bot-play`),
};

export const challengesApi = {
  weekly: () => api.get('/challenges/weekly'),
  start: (challengeId) => api.post(`/challenges/${challengeId}/start`),
};

export const leagues = {
  list: (leagueType) => api.get(`/leagues${leagueType ? `?league_type=${leagueType}` : ''}`),
  create: (data) => api.post('/leagues', data),
  get: (leagueId) => api.get(`/leagues/${leagueId}`),
  join: (leagueId) => api.post(`/leagues/${leagueId}/join`),
  joinByCode: (inviteCode) => api.post(`/leagues/join-code/${inviteCode}`),
  leave: (leagueId) => api.post(`/leagues/${leagueId}/leave`),
};

export default api;
