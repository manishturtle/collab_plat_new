// API configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8020/api';
const TENANT_SLUG = 'bingo_travels'; // Hardcoded tenant slug
// const AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUwMTU3NzA2LCJpYXQiOjE3NTAxNTQxMDYsImp0aSI6ImI5MGEzNDhlY2Y2MTQ4OTM4ZjliMWVhYTU3OWRkYjJmIiwidXNlcl9pZCI6MSwidGVuYW50X2lkIjoiNTIxIiwic2NoZW1hX25hbWUiOiJiaW5nb190cmF2ZWxzIn0.n8IJmf75MWf4Qhyb2DPSwM_hkACD3Fgpkb9vmXWWayY';
// const AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUwMTYxODQ1LCJpYXQiOjE3NTAxNTgyNDUsImp0aSI6IjJjOGNmNzdlNTkzODQ3MGI5NjczMzFkMzE4MThlNzcxIiwidXNlcl9pZCI6MSwidGVuYW50X2lkIjoiNTIxIiwic2NoZW1hX25hbWUiOiJiaW5nb190cmF2ZWxzIn0.D1kt9RY2ObJfjwBeHJ46vF12xG3il0Uz4EPftnZawVo'
// const AUTH_TOKEN= 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUwMTY1NTc2LCJpYXQiOjE3NTAxNjE5NzYsImp0aSI6IjkzNTRkZjY1Y2E3YTQ4NmE4NTNmN2Q4MzExYTJhOGFkIiwidXNlcl9pZCI6MSwidGVuYW50X2lkIjoiNTIxIiwic2NoZW1hX25hbWUiOiJiaW5nb190cmF2ZWxzIn0.6ZLLjfPeJLYTkEVMWfOTOfuyv7RohN226Og2o0TuJog'
// const AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUwMTY4OTc5LCJpYXQiOjE3NTAxNjUzNzksImp0aSI6IjIyMWI0ODhhNDRiMTRlZjJhNTZkNzRmOWU4ZmJiZGY1IiwidXNlcl9pZCI6MSwidGVuYW50X2lkIjoiNTIxIiwic2NoZW1hX25hbWUiOiJiaW5nb190cmF2ZWxzIn0.sQJnMbo0htf_wifKQ857mnePgVJyiUCoEygZkZ_AxB0'
  //  const AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUwMTc2MzU5LCJpYXQiOjE3NTAxNzI3NTksImp0aSI6ImMwMDA5YjYyMTE2MDQwYmFiZjhiMGE5ZTc4Y2ExMDYxIiwidXNlcl9pZCI6MSwidGVuYW50X2lkIjoiNTIxIiwic2NoZW1hX25hbWUiOiJiaW5nb190cmF2ZWxzIn0.WCQ_7kAtnT8MhdmMb8xvL5MCbn9qD4bQt0aXYHypcUE'
  const AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUwMzU4MzMzLCJpYXQiOjE3NTAxODU1MzMsImp0aSI6ImFiNzI5NTQwNDQ2YzQyNGQ4ZjM3NWJjM2FkZTY4MDg0IiwidXNlcl9pZCI6MSwidGVuYW50X2lkIjoiNTIxIiwic2NoZW1hX25hbWUiOiJiaW5nb190cmF2ZWxzIn0.o1-IUkui_4R0FEfNtbL2XT67Y6KPXqb0KdwhEN3Z-Yc'

/**
 * Get base URL for chat API endpoints
 */
const getChatApiUrl = (path: string): string => {
  return `${API_BASE_URL}/chat/${TENANT_SLUG}${path}`;
};

/**
 * Get base URL for shared API endpoints (like users)
 */
const getSharedApiUrl = (path: string): string => {
  return `${API_BASE_URL}/${TENANT_SLUG}${path}`;
};

export const getApiUrl = (path: string, type: 'chat' | 'shared' = 'chat'): string => {
  return type === 'chat' ? getChatApiUrl(path) : getSharedApiUrl(path);
};

export const getAuthHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${AUTH_TOKEN}`,
});

export const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8002/ws';

export const getWsUrl = (path: string): string => {
  return `${WS_BASE_URL}/chat/${TENANT_SLUG}${path}`;
};
