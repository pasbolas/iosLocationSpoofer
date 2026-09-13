<script>
  import { errorModal } from '../lib/stores.js';

  export let onRetry;

  function close() {
    errorModal.set(null);
  }

  function handleRetry() {
    close();
    if (onRetry) onRetry();
  }
</script>

{#if $errorModal}
  <div class="modal-backdrop" on:click={close}>
    <div class="glass-panel modal-card" on:click|stopPropagation>
      <div class="modal-header">
        <div class="icon-circle">
          {#if $errorModal.code === 'USBMUXD_NOT_FOUND'}
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="2" width="20" height="8" rx="2" ry="2" />
              <rect x="2" y="14" width="20" height="8" rx="2" ry="2" />
              <line x1="6" y1="6" x2="6.01" y2="6" />
              <line x1="6" y1="18" x2="6.01" y2="18" />
            </svg>
          {:else if $errorModal.code === 'DEVELOPER_MODE_DISABLED'}
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
          {:else if $errorModal.code === 'DEVICE_LOCKED'}
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
          {:else}
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          {/if}
        </div>

        <div class="modal-title-group">
          <h3>{$errorModal.code.replace(/_/g, ' ')}</h3>
          <span class="error-msg">{$errorModal.message}</span>
        </div>

        <button class="modal-close-btn" on:click={close}>✕</button>
      </div>

      {#if $errorModal.solution}
        <div class="modal-body">
          <div class="solution-header">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 11 12 14 22 4" />
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
            </svg>
            <span>Recommended Steps</span>
          </div>
          <div class="solution-content">
            {#each $errorModal.solution.split('\n') as step}
              <p>{step}</p>
            {/each}
          </div>
        </div>
      {/if}

      <div class="modal-footer">
        <button class="glass-button" on:click={close}>Dismiss</button>
        <button class="glass-button btn-primary" on:click={handleRetry}>Retry</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    animation: fadeIn 0.2s ease;
  }

  .modal-card {
    width: 480px;
    max-width: 90vw;
    background: rgba(15, 23, 42, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .modal-header {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 20px;
    border-bottom: 1px solid var(--border-subtle);
  }

  .icon-circle {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: rgba(244, 63, 94, 0.15);
    border: 1px solid rgba(244, 63, 94, 0.3);
    color: var(--accent-rose);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .modal-title-group {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  h3 {
    font-size: 1.05rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.01em;
  }

  .error-msg {
    font-size: 0.84rem;
    color: var(--text-secondary);
  }

  .modal-close-btn {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 1.1rem;
    cursor: pointer;
    padding: 2px 6px;
    border-radius: 4px;
  }

  .modal-close-btn:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.08);
  }

  .modal-body {
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    background: rgba(0, 0, 0, 0.2);
  }

  .solution-header {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.76rem;
    font-weight: 600;
    color: var(--accent-cyan);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .solution-content {
    font-size: 0.82rem;
    color: #cbd5e1;
    line-height: 1.5;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .modal-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
    padding: 14px 20px;
    background: rgba(15, 23, 42, 0.8);
    border-top: 1px solid var(--border-subtle);
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: scale(0.96); }
    to { opacity: 1; transform: scale(1); }
  }
</style>
