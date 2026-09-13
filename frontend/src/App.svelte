<script>
  import { onMount, onDestroy } from 'svelte';
  import Header from './components/Header.svelte';
  import DeviceCard from './components/DeviceCard.svelte';
  import SimulationCard from './components/SimulationCard.svelte';
  import FavoritesCard from './components/FavoritesCard.svelte';
  import Map from './components/Map.svelte';
  import ErrorModal from './components/ErrorModal.svelte';
  import {
    devices,
    selectedDevice,
    simulation,
    usbmuxdRunning,
    toast,
  } from './lib/stores.js';
  import { fetchStatus } from './lib/api.js';

  let mapComponent;
  let statusPollInterval;

  async function loadSystemStatus() {
    try {
      const data = await fetchStatus();
      usbmuxdRunning.set(data.usbmuxd_running);
      devices.set(data.devices || []);
      simulation.set(data.simulation);

      // Auto-select first device if none selected or selected is gone
      const currentSelected = $selectedDevice;
      if (data.devices && data.devices.length > 0) {
        if (!currentSelected || !data.devices.some(d => d.udid === currentSelected.udid)) {
          selectedDevice.set(data.devices[0]);
        } else {
          // Update device properties
          const updated = data.devices.find(d => d.udid === currentSelected.udid);
          if (updated) selectedDevice.set(updated);
        }
      } else {
        selectedDevice.set(null);
      }
    } catch (err) {
      console.warn('Status poll error:', err);
    }
  }

  onMount(() => {
    loadSystemStatus();
    // Poll every 4 seconds for device plug/unplug updates
    statusPollInterval = setInterval(loadSystemStatus, 4000);
  });

  onDestroy(() => {
    if (statusPollInterval) clearInterval(statusPollInterval);
  });

  function handleSelectFavorite(lat, lng, name) {
    if (mapComponent) {
      mapComponent.flyToLocation(lat, lng, name);
    }
  }
</script>

<div class="app-layout">
  <Header onRefresh={loadSystemStatus} />

  <main class="content-body">
    <!-- Left Sidebar Controls -->
    <aside class="sidebar-panel">
      <DeviceCard onRefresh={loadSystemStatus} />
      <SimulationCard />
      <FavoritesCard onSelectLocation={handleSelectFavorite} />
    </aside>

    <!-- Right Interactive Map -->
    <section class="map-section">
      <Map bind:this={mapComponent} />
    </section>
  </main>

  <!-- Error / Help Modal -->
  <ErrorModal onRetry={loadSystemStatus} />

  <!-- Toast Notification Alert -->
  {#if $toast}
    <div class="toast-banner {$toast.type}">
      {#if $toast.type === 'success'}
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      {:else if $toast.type === 'error'}
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
      {:else}
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12.01" y2="8" />
        </svg>
      {/if}
      <span>{$toast.message}</span>
    </div>
  {/if}
</div>

<style>
  .app-layout {
    display: flex;
    flex-direction: column;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background-color: var(--bg-primary);
  }

  .content-body {
    display: flex;
    flex: 1;
    overflow: hidden;
    position: relative;
  }

  .sidebar-panel {
    width: 390px;
    flex-shrink: 0;
    height: 100%;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 14px;
    padding: 16px;
    background: rgba(10, 14, 23, 0.75);
    backdrop-filter: blur(16px);
    border-right: 1px solid var(--border-subtle);
    z-index: 10;
  }

  .map-section {
    flex: 1;
    height: 100%;
    position: relative;
  }

  /* Responsive layout on narrow tablets */
  @media (max-width: 900px) {
    .content-body {
      flex-direction: column-reverse;
    }
    .sidebar-panel {
      width: 100%;
      height: 45%;
      border-right: none;
      border-top: 1px solid var(--border-subtle);
    }
    .map-section {
      height: 55%;
    }
  }

  /* Toast Notification */
  .toast-banner {
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 18px;
    border-radius: var(--radius-full);
    font-size: 0.85rem;
    font-weight: 500;
    backdrop-filter: blur(12px);
    box-shadow: var(--shadow-lg);
    z-index: 3000;
    animation: toastIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .toast-banner.success {
    background: rgba(16, 185, 129, 0.9);
    color: #ffffff;
    border: 1px solid #34d399;
  }

  .toast-banner.error {
    background: rgba(244, 63, 94, 0.9);
    color: #ffffff;
    border: 1px solid #fb7185;
  }

  .toast-banner.info {
    background: rgba(30, 41, 59, 0.95);
    color: #f1f5f9;
    border: 1px solid var(--border-active);
  }

  @keyframes toastIn {
    from {
      opacity: 0;
      transform: translate(-50%, 14px) scale(0.96);
    }
    to {
      opacity: 1;
      transform: translate(-50%, 0) scale(1);
    }
  }
</style>
