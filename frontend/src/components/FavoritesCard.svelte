<script>
  import { favorites, selectedLocation, showToast } from '../lib/stores.js';

  export let onSelectLocation;

  let adding = false;
  let customName = '';

  function chooseFavorite(fav) {
    selectedLocation.set({
      latitude: fav.latitude,
      longitude: fav.longitude,
      name: fav.name,
    });
    if (onSelectLocation) {
      onSelectLocation(fav.latitude, fav.longitude, fav.name);
    }
  }

  function startAdding() {
    customName = $selectedLocation.name || '';
    adding = true;
  }

  function saveCurrentAsFavorite() {
    if (!customName.trim()) return;
    const newFav = {
      id: Date.now().toString(),
      name: customName.trim(),
      latitude: $selectedLocation.latitude,
      longitude: $selectedLocation.longitude,
    };
    favorites.update(list => [newFav, ...list]);
    adding = false;
    customName = '';
    showToast(`Saved "${newFav.name}" to favorites`, 'success');
  }

  function deleteFavorite(id, e) {
    e.stopPropagation();
    favorites.update(list => list.filter(item => item.id !== id));
  }
</script>

<div class="glass-panel favorites-container">
  <div class="favorites-header">
    <div class="header-left">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="fav-icon">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
      </svg>
      <h2>Favorites & Presets</h2>
    </div>

    {#if !adding}
      <button class="add-button" on:click={startAdding} title="Bookmark current coordinates">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        <span>Add Pin</span>
      </button>
    {/if}
  </div>

  <!-- Inline Add Bookmark Input -->
  {#if adding}
    <div class="add-form">
      <input
        type="text"
        class="glass-input add-input"
        placeholder="Name this spot (e.g. Home, College)"
        bind:value={customName}
        on:keydown={(e) => e.key === 'Enter' && saveCurrentAsFavorite()}
        autofocus
      />
      <div class="add-actions">
        <button class="glass-button btn-primary btn-sm" on:click={saveCurrentAsFavorite}>Save</button>
        <button class="glass-button btn-sm" on:click={() => adding = false}>Cancel</button>
      </div>
    </div>
  {/if}

  <!-- Favorites List -->
  <div class="favorites-scroll">
    {#each $favorites as fav (fav.id)}
      <div
        class="favorite-item"
        class:selected={$selectedLocation.latitude === fav.latitude && $selectedLocation.longitude === fav.longitude}
        on:click={() => chooseFavorite(fav)}
      >
        <div class="fav-content">
          <div class="fav-name">{fav.name}</div>
          <div class="fav-coords mono">{fav.latitude.toFixed(3)}, {fav.longitude.toFixed(3)}</div>
        </div>

        <button
          class="btn-delete"
          on:click={(e) => deleteFavorite(fav.id, e)}
          title="Remove favorite"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
    {/each}
  </div>
</div>

<style>
  .favorites-container {
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    flex: 1;
    min-height: 0; /* Allow inner scrolling */
  }

  .favorites-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .fav-icon {
    color: var(--accent-amber);
  }

  h2 {
    font-size: 0.95rem;
    font-weight: 600;
    color: #f1f5f9;
  }

  .add-button {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: var(--radius-sm);
    background: rgba(245, 158, 11, 0.12);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.3);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .add-button:hover {
    background: rgba(245, 158, 11, 0.22);
  }

  .add-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 10px;
    border-radius: var(--radius-md);
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid var(--border-subtle);
  }

  .add-input {
    font-size: 0.8rem;
    padding: 7px 10px;
  }

  .add-actions {
    display: flex;
    gap: 6px;
    justify-content: flex-end;
  }

  .btn-sm {
    padding: 4px 10px;
    font-size: 0.75rem;
  }

  .favorites-scroll {
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding-right: 4px;
    max-height: 220px;
  }

  .favorite-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    border-radius: var(--radius-md);
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.18s ease;
  }

  .favorite-item:hover {
    background: rgba(255, 255, 255, 0.07);
    border-color: rgba(255, 255, 255, 0.1);
    transform: translateX(2px);
  }

  .favorite-item.selected {
    background: rgba(59, 130, 246, 0.15);
    border-color: rgba(59, 130, 246, 0.4);
  }

  .fav-content {
    display: flex;
    flex-direction: column;
    gap: 2px;
    overflow: hidden;
  }

  .fav-name {
    font-size: 0.82rem;
    font-weight: 500;
    color: #e2e8f0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .fav-coords {
    font-size: 0.7rem;
    color: var(--text-muted);
  }

  .btn-delete {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0.6;
    transition: all 0.15s ease;
  }

  .btn-delete:hover {
    color: var(--accent-rose);
    background: rgba(244, 63, 94, 0.15);
    opacity: 1;
  }
</style>
