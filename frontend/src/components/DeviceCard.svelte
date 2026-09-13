<script>
  import { devices, selectedDevice, errorModal } from '../lib/stores.js';
  import { revealDeveloperMode } from '../lib/api.js';

  export let onRefresh;

  let isRevealing = false;
  let revealSuccess = false;
  let revealError = null;

  async function handleRevealDevMode() {
    if (!$selectedDevice) return;
    isRevealing = true;
    revealSuccess = false;
    revealError = null;
    try {
      await revealDeveloperMode($selectedDevice.udid);
      revealSuccess = true;
    } catch (err) {
      revealError = err.message || 'Failed to reveal Developer Mode';
    } finally {
      isRevealing = false;
    }
  }

  function selectTargetDevice(dev) {
    selectedDevice.set(dev);
    revealSuccess = false;
    revealError = null;
  }

  function showHelp(code) {
    if (code === 'DEVELOPER_MODE') {
      errorModal.set({
        code: 'DEVELOPER_MODE_DISABLED',
        message: 'Developer Mode toggle must be enabled on iOS 16+.',
        solution: '1. Click "⚡ Reveal Toggle on iPhone" in the card below.\n2. On iPhone: Open Settings > Privacy & Security.\n3. Scroll down to Developer Mode and toggle it ON.\n4. Restart iPhone, unlock it, and tap "Turn On".',
      });
    } else if (code === 'NO_DEVICE') {
      errorModal.set({
        code: 'DEVICE_NOT_FOUND',
        message: 'No iOS devices detected via USB.',
        solution: '1. Connect iPhone with a USB data cable.\n2. Unlock screen.\n3. Tap "Trust This Computer" on iPhone and enter passcode.\n4. Click "Scan USB" above.',
      });
    }
  }
</script>

<div class="glass-panel card-container">
  <div class="card-header">
    <div class="header-left">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="device-icon">
        <rect x="5" y="2" width="14" height="20" rx="3" ry="3" />
        <line x1="12" y1="18" x2="12.01" y2="18" />
      </svg>
      <h2>Connected Device</h2>
    </div>
    {#if $devices.length > 0}
      <span class="device-count-badge">{$devices.length} Detected</span>
    {/if}
  </div>

  {#if $devices.length === 0}
    <!-- Empty State -->
    <div class="empty-state">
      <div class="empty-icon-wrapper">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
          <rect x="5" y="2" width="14" height="20" rx="3" ry="3" />
          <path d="M12 18h.01M9 6h6" />
        </svg>
      </div>
      <div class="empty-info">
        <h3>No iPhone Detected</h3>
        <p>Connect your iPhone via USB, unlock the screen, and trust this PC.</p>
      </div>
      <button class="glass-button btn-guide" on:click={() => showHelp('NO_DEVICE')}>
        View Setup Guide
      </button>
    </div>
  {:else}
    <!-- Active Device Display -->
    {#if $devices.length > 1}
      <div class="device-selector">
        <label for="device-select">Select Target:</label>
        <select
          id="device-select"
          class="glass-input"
          value={$selectedDevice?.udid}
          on:change={(e) => {
            const chosen = $devices.find(d => d.udid === e.target.value);
            if (chosen) selectTargetDevice(chosen);
          }}
        >
          {#each $devices as dev}
            <option value={dev.udid}>{dev.name} ({dev.model})</option>
          {/each}
        </select>
      </div>
    {/if}

    {#if $selectedDevice}
      <div class="device-details">
        <div class="device-main-row">
          <div class="device-title-block">
            <span class="device-name">{$selectedDevice.name}</span>
            <span class="model-badge">{$selectedDevice.model}</span>
          </div>
          <span class="ios-badge">iOS {$selectedDevice.ios_version}</span>
        </div>

        <div class="device-meta-grid">
          <!-- UDID -->
          <div class="meta-item">
            <span class="meta-label">UDID</span>
            <span class="meta-value mono" title={$selectedDevice.udid}>
              {$selectedDevice.udid.substring(0, 8)}...{$selectedDevice.udid.substring($selectedDevice.udid.length - 6)}
            </span>
          </div>

          <!-- Pairing Status -->
          <div class="meta-item">
            <span class="meta-label">Pairing</span>
            <span class="meta-value">
              {#if $selectedDevice.paired}
                <span class="badge badge-ready">Trusted</span>
              {:else}
                <span class="badge badge-warning">Untrusted</span>
              {/if}
            </span>
          </div>

          <!-- Developer Mode -->
          <div class="meta-item full-width">
            <div class="dev-mode-row">
              <span class="meta-label">Developer Mode</span>
              {#if $selectedDevice.developer_mode === 'Ready'}
                <span class="badge badge-ready">Ready</span>
              {:else if $selectedDevice.developer_mode === 'Disabled'}
                <button class="badge-button" on:click={() => showHelp('DEVELOPER_MODE')}>
                  <span class="badge badge-warning">Action Required (Enable)</span>
                </button>
              {:else}
                <span class="badge badge-neutral">{$selectedDevice.developer_mode}</span>
              {/if}
            </div>

            {#if $selectedDevice.developer_mode !== 'Ready'}
              <div class="dev-reveal-box">
                <p class="dev-reveal-hint">Don't see "Developer Mode" in Settings &gt; Privacy &amp; Security?</p>
                <button 
                  class="btn-reveal-action"
                  on:click={handleRevealDevMode}
                  disabled={isRevealing}
                >
                  {#if isRevealing}
                    <span class="spinner-small"></span> Sending command...
                  {:else}
                    ⚡ Reveal Toggle on iPhone
                  {/if}
                </button>

                {#if revealSuccess}
                  <div class="reveal-alert success">
                    <span>✓ <strong>Revealed!</strong> Open <strong>Settings &gt; Privacy &amp; Security</strong>, scroll down to <strong>Developer Mode</strong>, turn ON &amp; restart.</span>
                  </div>
                {/if}
                {#if revealError}
                  <div class="reveal-alert error">
                    <span>⚠️ {revealError}</span>
                  </div>
                {/if}
              </div>
            {/if}
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>

<style>
  .card-container {
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #e2e8f0;
  }

  .device-icon {
    color: var(--accent-blue);
  }

  h2 {
    font-size: 0.95rem;
    font-weight: 600;
    color: #f1f5f9;
  }

  .device-count-badge {
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: var(--radius-full);
    background: rgba(59, 130, 246, 0.15);
    color: #93c5fd;
    border: 1px solid rgba(59, 130, 246, 0.3);
  }

  /* Empty State */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 16px 10px;
    gap: 12px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: var(--radius-md);
    border: 1px dashed var(--border-subtle);
  }

  .empty-icon-wrapper {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.04);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
  }

  .empty-info h3 {
    font-size: 0.88rem;
    font-weight: 600;
    color: #cbd5e1;
    margin-bottom: 4px;
  }

  .empty-info p {
    font-size: 0.76rem;
    color: var(--text-muted);
    line-height: 1.4;
  }

  .btn-guide {
    font-size: 0.78rem;
    padding: 6px 14px;
    color: var(--accent-cyan);
    border-color: rgba(6, 182, 212, 0.3);
    background: rgba(6, 182, 212, 0.08);
  }

  /* Active Details */
  .device-selector {
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 0.78rem;
    color: var(--text-secondary);
  }

  .device-details {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .device-main-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }

  .device-title-block {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .device-name {
    font-size: 0.95rem;
    font-weight: 700;
    color: #ffffff;
  }

  .model-badge {
    font-size: 0.72rem;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 6px;
    background: rgba(59, 130, 246, 0.2);
    color: #93c5fd;
    border: 1px solid rgba(59, 130, 246, 0.3);
  }

  .ios-badge {
    font-size: 0.72rem;
    font-family: var(--font-mono);
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.08);
    color: #e2e8f0;
  }

  .device-meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    padding-top: 10px;
    border-top: 1px solid var(--border-subtle);
  }

  .meta-item {
    display: flex;
    flex-direction: column;
    gap: 3px;
  }

  .meta-item.full-width {
    grid-column: span 2;
  }

  .dev-mode-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .meta-label {
    font-size: 0.7rem;
    font-weight: 500;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .meta-value {
    font-size: 0.8rem;
    color: var(--text-secondary);
  }

  .meta-value.mono {
    font-family: var(--font-mono);
    font-size: 0.75rem;
  }

  .badge-button {
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
  }

  .dev-reveal-box {
    margin-top: 8px;
    padding: 10px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px dashed rgba(245, 158, 11, 0.35);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .dev-reveal-hint {
    font-size: 0.74rem;
    color: #fbbf24;
    line-height: 1.3;
  }

  .btn-reveal-action {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.3));
    border: 1px solid rgba(245, 158, 11, 0.5);
    color: #fef3c7;
    font-size: 0.76rem;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    transition: all 0.15s ease;
  }

  .btn-reveal-action:hover:not(:disabled) {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.35), rgba(217, 119, 6, 0.45));
    border-color: rgba(245, 158, 11, 0.8);
    transform: translateY(-1px);
  }

  .btn-reveal-action:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .reveal-alert {
    font-size: 0.72rem;
    padding: 6px 8px;
    border-radius: 6px;
    line-height: 1.35;
  }

  .reveal-alert.success {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #a7f3d0;
  }

  .reveal-alert.error {
    background: rgba(239, 68, 68, 0.12);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #fca5a5;
  }

  .spinner-small {
    width: 12px;
    height: 12px;
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
