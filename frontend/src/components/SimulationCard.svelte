<script>
  import { selectedDevice, simulation, selectedLocation, showToast, errorModal } from '../lib/stores.js';
  import { setDeviceLocation, stopDeviceLocation } from '../lib/api.js';

  let loading = false;

  async function handleSetLocation() {
    if (!$selectedDevice) {
      showToast('Please connect an iPhone first', 'error');
      return;
    }

    loading = true;
    try {
      const res = await setDeviceLocation(
        $selectedDevice.udid,
        $selectedLocation.latitude,
        $selectedLocation.longitude,
        $selectedLocation.name
      );
      simulation.set(res);
      showToast(`Location set to ${$selectedLocation.name || 'custom coordinates'}`, 'success');
    } catch (err) {
      errorModal.set({
        code: err.code || 'LOCATION_SIMULATION_FAILED',
        message: err.message || 'Failed to simulate location',
        solution: err.solution || 'Ensure device is unlocked, trusted, and has Developer Mode enabled.',
      });
    } finally {
      loading = false;
    }
  }

  async function handleStopSimulation() {
    loading = true;
    try {
      const res = await stopDeviceLocation($selectedDevice?.udid);
      simulation.set(res);
      showToast('Simulation stopped: Real GPS restored', 'info');
    } catch (err) {
      showToast(err.message || 'Failed to stop simulation', 'error');
    } finally {
      loading = false;
    }
  }
</script>

<div class="glass-panel simulation-container">
  <div class="simulation-header">
    <div class="header-left">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="sim-icon">
        <circle cx="12" cy="12" r="10" />
        <line x1="2" y1="12" x2="22" y2="12" />
        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
      </svg>
      <h2>Simulation Control</h2>
    </div>

    <!-- Active State Pill -->
    {#if $simulation.active}
      <span class="badge badge-simulating">
        <span class="pulse-circle"></span>
        ACTIVE
      </span>
    {:else}
      <span class="badge badge-neutral">
        Real GPS
      </span>
    {/if}
  </div>

  <!-- Selected Target Location Details -->
  <div class="target-location-box">
    <div class="target-top">
      <span class="target-tag">Target Location</span>
      <span class="coord-pill mono">
        {$selectedLocation.latitude.toFixed(4)}, {$selectedLocation.longitude.toFixed(4)}
      </span>
    </div>
    <div class="target-name">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
        <circle cx="12" cy="10" r="3" />
      </svg>
      <span title={$selectedLocation.name}>{$selectedLocation.name}</span>
    </div>
  </div>

  <!-- Active Simulation Readout if active -->
  {#if $simulation.active}
    <div class="active-readout-banner">
      <div class="banner-title">
        <span class="pulse-circle"></span>
        <span>SIMULATED LOCATION ACTIVE</span>
      </div>
      <div class="banner-coords mono">
        Lat: {$simulation.latitude?.toFixed(5)} | Lon: {$simulation.longitude?.toFixed(5)}
      </div>
    </div>
  {/if}

  <!-- Action Buttons -->
  <div class="actions-grid">
    <button
      class="glass-button btn-primary btn-action"
      on:click={handleSetLocation}
      disabled={loading || !$selectedDevice}
    >
      {#if loading}
        <span class="spinner"></span>
        <span>Applying...</span>
      {:else}
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
          <polygon points="5 3 19 12 5 21 5 3" />
        </svg>
        <span>Set Location</span>
      {/if}
    </button>

    <button
      class="glass-button btn-danger btn-action"
      on:click={handleStopSimulation}
      disabled={loading || !$simulation.active}
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
        <rect x="6" y="6" width="12" height="12" rx="2" />
      </svg>
      <span>Stop Simulation</span>
    </button>
  </div>
</div>

<style>
  .simulation-container {
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .simulation-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .sim-icon {
    color: var(--accent-cyan);
  }

  h2 {
    font-size: 0.95rem;
    font-weight: 600;
    color: #f1f5f9;
  }

  .target-location-box {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 12px 14px;
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
  }

  .target-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .target-tag {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-muted);
  }

  .coord-pill {
    font-size: 0.72rem;
    font-family: var(--font-mono);
    padding: 2px 7px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.05);
    color: #94a3b8;
  }

  .target-name {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 0.88rem;
    font-weight: 500;
    color: #f8fafc;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .target-name svg {
    color: var(--accent-rose);
    flex-shrink: 0;
  }

  .active-readout-banner {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 10px 12px;
    border-radius: var(--radius-md);
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.4);
    box-shadow: 0 0 15px rgba(16, 185, 129, 0.15);
  }

  .banner-title {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: #34d399;
  }

  .banner-coords {
    font-size: 0.74rem;
    color: #a7f3d0;
  }

  .actions-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }

  .btn-action {
    width: 100%;
    padding: 11px 14px;
  }

  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: #ffffff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
