import { writable } from 'svelte/store';

// Default presets
const DEFAULT_FAVORITES = [
  { id: '1', name: 'Dublin City Centre', latitude: 53.3498, longitude: -6.2603 },
  { id: '2', name: 'Times Square, New York', latitude: 40.7580, longitude: -73.9855 },
  { id: '3', name: 'Eiffel Tower, Paris', latitude: 48.8584, longitude: 2.2945 },
  { id: '4', name: 'Shibuya Crossing, Tokyo', latitude: 35.6595, longitude: 139.7005 },
  { id: '5', name: 'Big Ben, London', latitude: 51.5007, longitude: -0.1246 },
  { id: '6', name: 'Sydney Opera House', latitude: -33.8568, longitude: 151.2153 },
];

function loadStoredFavorites() {
  try {
    const raw = localStorage.getItem('locsim_favorites');
    if (raw) return JSON.parse(raw);
  } catch (e) {
    console.error('Failed to load favorites from localStorage', e);
  }
  return DEFAULT_FAVORITES;
}

export const devices = writable([]);
export const selectedDevice = writable(null);
export const usbmuxdRunning = writable(true);

export const simulation = writable({
  active: false,
  latitude: null,
  longitude: null,
  udid: null,
  location_name: null,
  started_at: null,
});

export const selectedLocation = writable({
  latitude: 53.3498,
  longitude: -6.2603,
  name: 'Dublin, Ireland',
});

export const favorites = writable(loadStoredFavorites());

// Persist favorites changes
favorites.subscribe((val) => {
  try {
    localStorage.setItem('locsim_favorites', JSON.stringify(val));
  } catch (e) {
    console.error('Failed to save favorites to localStorage', e);
  }
});

export const errorModal = writable(null); // { code, message, solution }
export const toast = writable(null); // { type: 'success' | 'error' | 'info', message: string }

export function showToast(message, type = 'success') {
  toast.set({ message, type });
  setTimeout(() => {
    toast.set(null);
  }, 4000);
}
