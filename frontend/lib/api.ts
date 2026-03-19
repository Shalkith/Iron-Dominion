// API client for the game backend.

const API_BASE = '/api';

async function fetchApi(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Auth API
export const authApi = {
  register: (username: string, password: string) =>
    fetchApi('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  login: (username: string, password: string) =>
    fetchApi('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  logout: () =>
    fetchApi('/auth/logout', { method: 'POST' }),

  me: () =>
    fetchApi('/auth/me'),
};

// Game API
export const gameApi = {
  getMap: () =>
    fetchApi('/game/map'),

  getMapWithOwners: () =>
    fetchApi('/game/map/with-owners'),

  getMyTiles: () =>
    fetchApi('/game/my-tiles'),

  claimTile: (x: number, y: number) =>
    fetchApi('/game/claim', {
      method: 'POST',
      body: JSON.stringify({ x, y }),
    }),

  attackTile: (x: number, y: number) =>
    fetchApi('/game/attack', {
      method: 'POST',
      body: JSON.stringify({ x, y }),
    }),

  spawn: () =>
    fetchApi('/game/spawn', { method: 'POST' }),

  getAttackLogs: () =>
    fetchApi('/game/attack-logs'),

  getLeaderboard: () =>
    fetchApi('/game/leaderboard'),
};

// Alliance API
export const allianceApi = {
  getMyAlliances: () =>
    fetchApi('/alliances/my'),

  getPendingRequests: () =>
    fetchApi('/alliances/requests/pending'),

  sendRequest: (toPlayerId: number) =>
    fetchApi('/alliances/request', {
      method: 'POST',
      body: JSON.stringify({ to_player_id: toPlayerId }),
    }),

  acceptRequest: (requestId: number) =>
    fetchApi(`/alliances/accept/${requestId}`, { method: 'POST' }),

  rejectRequest: (requestId: number) =>
    fetchApi(`/alliances/reject/${requestId}`, { method: 'POST' }),

  getPlayers: () =>
    fetchApi('/alliances/players'),
};
