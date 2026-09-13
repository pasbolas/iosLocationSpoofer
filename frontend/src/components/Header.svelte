<script>
  import { onMount } from 'svelte';
  import { devices, usbmuxdRunning, showToast } from '../lib/stores.js';
  import { fetchStatus } from '../lib/api.js';

  export let onRefresh;

  let deferredPrompt = null;
  let canInstall = false;
  let refreshing = false;

  onMount(() => {
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      canInstall = true;
    });
  });

  async function handleInstall() {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      canInstall = false;
      showToast('App installed successfully!', 'success');
    }
    deferredPrompt = null;
  }

  async function triggerRefresh() {
    refreshing = true;
    try {
      await onRefresh();
      showToast('Device status refreshed', 'info');
    } finally {
      setTimeout(() => {
        refreshing = false;
      }, 500);
    }
  }
</script>

<header class="header-container">
  <div class="brand-area">
    <div class="logo-wrapper">
      <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z" />
        <circle cx="12" cy="10" r="3" />
      </svg>
    </div>
    <div class="title-group">
      <div class="title-row">
        <h1>iPhone Location Simulator</h1>
        <span class="version-tag">PWA v1.0</span>
      </div>
      <p class="subtitle">Windows-native virtual location via Apple developer services</p>
    </div>
  </div>

  <div class="actions-area">
    <!-- Live USB Daemon Indicator -->
    <div class="status-indicator">
      {#if $usbmuxdRunning}
        <span class="status-dot online"></span>
        <span class="status-label">Apple Mobile Service: Active</span>
      {:else}
        <span class="status-dot offline"></span>
        <span class="status-label error">Service Offline</span>
      {/if}
    </div>

    <!-- PWA Install Button -->
    {#if canInstall}
      <button class="glass-button btn-install" on:click={handleInstall}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
        <span>Install PWA</span>
      </button>
    {/if}

    <!-- Refresh Button -->
    <button class="glass-button" on:click={triggerRefresh} title="Scan for connected USB devices" disabled={refreshing}>
      <svg class="refresh-icon {refreshing ? 'spin' : ''}" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
      </svg>
      <span>Scan USB</span>
    </button>
  </div>
</header>

<style>
  .header-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 24px;
    background: rgba(14, 19, 31, 0.85);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border-subtle);
    z-index: 100;
  }

  .brand-area {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .logo-wrapper {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(59, 130, 246, 0.3) 100%);
    border: 1px solid rgba(59, 130, 246, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #38bdf8;
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.25);
  }

  .logo-icon {
    width: 22px;
    height: 22px;
  }

  .title-group {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .title-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  h1 {
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.01em;
  }

  .version-tag {
    font-size: 0.7rem;
    font-family: var(--font-mono);
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.08);
    color: var(--accent-cyan);
    border: 1px solid rgba(6, 182, 212, 0.3);
  }

  .subtitle {
    font-size: 0.78rem;
    color: var(--text-secondary);
  }

  .actions-area {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-full);
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-secondary);
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .status-dot.online {
    background-color: var(--accent-emerald);
    box-shadow: 0 0 8px var(--accent-emerald);
  }

  .status-dot.offline {
    background-color: var(--accent-rose);
    box-shadow: 0 0 8px var(--accent-rose);
  }

  .status-label.error {
    color: var(--accent-rose);
  }

  .btn-install {
    background: rgba(59, 130, 246, 0.15);
    border-color: rgba(59, 130, 246, 0.4);
    color: #60a5fa;
  }

  .btn-install:hover {
    background: rgba(59, 130, 246, 0.25);
  }

  .refresh-icon.spin {
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
