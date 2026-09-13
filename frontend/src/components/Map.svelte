<script>
  import { onMount, onDestroy } from 'svelte';
  import L from 'leaflet';
  import { selectedLocation, simulation, showToast } from '../lib/stores.js';
  import { geocodeSearch } from '../lib/api.js';

  let mapElement;
  let map;
  let marker;
  let searchQuery = '';
  let searchResults = [];
  let isSearching = false;
  let searchTimeout = null;
  let mouseCoords = null;

  // Custom Sleek Glowing Pin Marker Icon
  const createPinIcon = (isSimulating = false) => {
    return L.divIcon({
      className: 'custom-pin-wrapper',
      html: `
        <div class="pin-marker ${isSimulating ? 'simulating' : ''}">
          <div class="pin-pulse"></div>
          <div class="pin-body">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z" fill="#3b82f6" stroke="#ffffff" />
              <circle cx="12" cy="10" r="3" fill="#ffffff" />
            </svg>
          </div>
          <div class="pin-shadow"></div>
        </div>
      `,
      iconSize: [40, 48],
      iconAnchor: [20, 42],
      popupAnchor: [0, -40],
    });
  };

  onMount(() => {
    // Initialize map centered at Dublin or current selectedLocation
    map = L.map(mapElement, {
      zoomControl: true,
      attributionControl: false,
    }).setView([$selectedLocation.latitude, $selectedLocation.longitude], 13);

    // Standard OpenStreetMap tiles (no API keys or watermarks)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);

    // Place initial draggable marker
    marker = L.marker([$selectedLocation.latitude, $selectedLocation.longitude], {
      icon: createPinIcon($simulation.active),
      draggable: true,
    }).addTo(map);

    // Marker drag end
    marker.on('dragend', async (e) => {
      const { lat, lng } = e.target.getLatLng();
      updateSelectedCoords(lat, lng, `Pin: ${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    });

    // Map click drops pin
    map.on('click', (e) => {
      const { lat, lng } = e.latlng;
      marker.setLatLng([lat, lng]);
      updateSelectedCoords(lat, lng, `Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`);
    });

    // Mouse coordinates readout
    map.on('mousemove', (e) => {
      mouseCoords = {
        lat: e.latlng.lat.toFixed(4),
        lng: e.latlng.lng.toFixed(4),
      };
    });

    // Invalidate size in case of flex resize
    setTimeout(() => {
      map.invalidateSize();
    }, 200);
  });

  onDestroy(() => {
    if (map) {
      map.remove();
    }
  });

  function updateSelectedCoords(lat, lng, name) {
    selectedLocation.set({
      latitude: parseFloat(lat.toFixed(6)),
      longitude: parseFloat(lng.toFixed(6)),
      name,
    });
  }

  // Reactive updates when selectedLocation changes externally (e.g. from favorites)
  export function flyToLocation(lat, lng, name = null) {
    if (!map || !marker) return;
    marker.setLatLng([lat, lng]);
    map.flyTo([lat, lng], 14, { duration: 1.2 });
    if (name) {
      selectedLocation.update(s => ({ ...s, latitude: lat, longitude: lng, name }));
    }
  }

  // Update marker icon when simulation state toggles
  $: if (marker) {
    marker.setIcon(createPinIcon($simulation.active));
  }

  // Debounced search
  function handleSearchInput() {
    clearTimeout(searchTimeout);
    if (!searchQuery || searchQuery.trim().length < 2) {
      searchResults = [];
      isSearching = false;
      return;
    }

    isSearching = true;
    searchTimeout = setTimeout(async () => {
      try {
        const results = await geocodeSearch(searchQuery);
        searchResults = results;
      } finally {
        isSearching = false;
      }
    }, 350);
  }

  function pickSearchResult(result) {
    flyToLocation(result.latitude, result.longitude, result.display_name);
    searchQuery = '';
    searchResults = [];
  }

  function flyToActiveSim() {
    if ($simulation.active && $simulation.latitude && $simulation.longitude) {
      flyToLocation($simulation.latitude, $simulation.longitude, $simulation.location_name);
    }
  }
</script>

<div class="map-wrapper">
  <!-- Interactive Leaflet Map Container -->
  <div bind:this={mapElement} class="map-container"></div>

  <!-- Floating Search Bar -->
  <div class="floating-search-box glass-panel">
    <div class="search-input-row">
      <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
      <input
        type="text"
        class="search-input"
        placeholder="Search city, address, or landmark..."
        bind:value={searchQuery}
        on:input={handleSearchInput}
      />
      {#if isSearching}
        <span class="mini-spinner"></span>
      {:else if searchQuery}
        <button class="clear-btn" on:click={() => { searchQuery = ''; searchResults = []; }}>
          ✕
        </button>
      {/if}
    </div>

    <!-- Dropdown Autocomplete Results -->
    {#if searchResults.length > 0}
      <div class="search-dropdown glass-panel">
        {#each searchResults as item}
          <div class="search-result-item" on:click={() => pickSearchResult(item)}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
              <circle cx="12" cy="10" r="3" />
            </svg>
            <div class="result-text">
              <span class="result-name">{item.name}</span>
              <span class="result-desc">{item.display_name}</span>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Quick Center to Active Sim Button -->
  {#if $simulation.active}
    <button class="floating-sim-button glass-button" on:click={flyToActiveSim} title="Jump to currently simulated GPS location">
      <span class="pulse-circle"></span>
      <span>Simulated Spot</span>
    </button>
  {/if}

  <!-- Coordinate HUD readout at bottom right -->
  {#if mouseCoords}
    <div class="coord-hud mono glass-panel">
      <span>Lat: {mouseCoords.lat}</span>
      <span class="sep">•</span>
      <span>Lon: {mouseCoords.lng}</span>
    </div>
  {/if}
</div>

<style>
  .map-wrapper {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
  }

  .map-container {
    width: 100%;
    height: 100%;
  }

  /* Floating Search Bar */
  .floating-search-box {
    position: absolute;
    top: 20px;
    left: 20px;
    width: 360px;
    max-width: calc(100% - 40px);
    z-index: 1000;
    padding: 6px 12px;
    background: rgba(14, 19, 31, 0.88);
  }

  .search-input-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .search-icon {
    color: var(--text-muted);
    flex-shrink: 0;
  }

  .search-input {
    width: 100%;
    background: transparent;
    border: none;
    outline: none;
    font-size: 0.88rem;
    color: #ffffff;
    font-family: var(--font-main);
  }

  .search-input::placeholder {
    color: var(--text-muted);
  }

  .clear-btn {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 0.85rem;
    padding: 2px 4px;
  }

  .clear-btn:hover {
    color: #ffffff;
  }

  .mini-spinner {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-top-color: var(--accent-cyan);
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Dropdown results */
  .search-dropdown {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    width: 100%;
    max-height: 260px;
    overflow-y: auto;
    background: rgba(15, 23, 42, 0.95);
    border-radius: var(--radius-md);
    padding: 6px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .search-result-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .search-result-item:hover {
    background: rgba(59, 130, 246, 0.2);
  }

  .search-result-item svg {
    color: var(--accent-rose);
    flex-shrink: 0;
  }

  .result-text {
    display: flex;
    flex-direction: column;
    gap: 2px;
    overflow: hidden;
  }

  .result-name {
    font-size: 0.84rem;
    font-weight: 600;
    color: #ffffff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .result-desc {
    font-size: 0.72rem;
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  /* Floating Sim button */
  .floating-sim-button {
    position: absolute;
    bottom: 30px;
    left: 20px;
    z-index: 1000;
    padding: 8px 14px;
    background: rgba(16, 185, 129, 0.2);
    border-color: #10b981;
    color: #34d399;
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35);
  }

  .floating-sim-button:hover {
    background: rgba(16, 185, 129, 0.35);
  }

  /* Coord HUD */
  .coord-hud {
    position: absolute;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
    padding: 6px 12px;
    border-radius: var(--radius-sm);
    font-size: 0.72rem;
    color: var(--text-secondary);
    background: rgba(10, 14, 23, 0.85);
    display: flex;
    gap: 8px;
    align-items: center;
    pointer-events: none;
  }

  .sep {
    color: var(--text-muted);
  }

  /* Custom Pin Global Leaflet Styles */
  :global(.custom-pin-wrapper) {
    background: transparent !important;
    border: none !important;
  }

  :global(.pin-marker) {
    position: relative;
    width: 40px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: grab;
    transition: transform 0.2s ease;
  }

  :global(.pin-marker:active) {
    cursor: grabbing;
    transform: scale(1.15) translateY(-4px);
  }

  :global(.pin-body) {
    position: relative;
    z-index: 2;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.6));
  }

  :global(.pin-pulse) {
    position: absolute;
    bottom: 4px;
    left: 10px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: rgba(59, 130, 246, 0.4);
    animation: pulse-ring 2s infinite cubic-bezier(0.2, 0, 0.4, 1);
    z-index: 1;
  }

  :global(.pin-marker.simulating .pin-pulse) {
    background: rgba(16, 185, 129, 0.6);
  }

  :global(.pin-marker.simulating .pin-body svg path) {
    fill: #10b981 !important;
  }

  @keyframes pulse-ring {
    0% {
      transform: scale(0.5);
      opacity: 0.9;
    }
    100% {
      transform: scale(2.4);
      opacity: 0;
    }
  }

  :global(.map-container .leaflet-tile-pane) {
    filter: brightness(0.65) invert(1) contrast(3) hue-rotate(200deg) saturate(0.3) brightness(0.75);
  }
</style>
