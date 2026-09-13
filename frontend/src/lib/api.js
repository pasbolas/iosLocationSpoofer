// API client communicating exclusively with localhost backend
const API_BASE = '/api';

export async function fetchStatus() {
  const res = await fetch(`${API_BASE}/status`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail?.message || 'Failed to fetch status');
  }
  return res.json();
}

export async function fetchDevices() {
  const res = await fetch(`${API_BASE}/devices`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const detail = errorData.detail || {};
    const err = new Error(detail.message || 'Failed to fetch devices');
    err.code = detail.code;
    err.solution = detail.solution;
    throw err;
  }
  return res.json();
}

export async function setDeviceLocation(udid, latitude, longitude, locationName = null) {
  const res = await fetch(`${API_BASE}/location`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      udid,
      latitude: parseFloat(latitude),
      longitude: parseFloat(longitude),
      location_name: locationName,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const detail = errorData.detail || {};
    const err = new Error(detail.message || 'Failed to set location');
    err.code = detail.code || 'UNKNOWN_ERROR';
    err.solution = detail.solution;
    throw err;
  }

  return res.json();
}

export async function stopDeviceLocation(udid = null) {
  const url = udid ? `${API_BASE}/location?udid=${encodeURIComponent(udid)}` : `${API_BASE}/location`;
  const res = await fetch(url, {
    method: 'DELETE',
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const detail = errorData.detail || {};
    const err = new Error(detail.message || 'Failed to stop location simulation');
    err.code = detail.code;
    err.solution = detail.solution;
    throw err;
  }

  return res.json();
}

export async function geocodeSearch(query) {
  if (!query || query.trim().length < 2) return [];
  try {
    const res = await fetch(`${API_BASE}/geocode?q=${encodeURIComponent(query)}`);
    if (!res.ok) return [];
    return res.json();
  } catch (err) {
    console.warn('Geocoding search failed:', err);
    return [];
  }
}

export async function revealDeveloperMode(udid = null) {
  const url = udid ? `${API_BASE}/device/reveal-dev-mode?udid=${encodeURIComponent(udid)}` : `${API_BASE}/device/reveal-dev-mode`;
  const res = await fetch(url, { method: 'POST' });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail?.message || 'Failed to reveal Developer Mode');
  }
  return res.json();
}

