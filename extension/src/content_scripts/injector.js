/**
 * Prompt Verse – injector.js
 * Injects a Refine button into AI platform pages.
 */
(function () {
  'use strict';

  if (document.getElementById('promptvault-refine')) return;

  const REFINE_ID = 'promptvault-refine';
  const TOAST_ID  = 'promptvault-toast';

  // ── Styles ──────────────────────────────────────────────────────────────────

  const style = document.createElement('style');
  style.id = 'promptvault-styles';
  style.textContent = `
    #${REFINE_ID} {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 2147483647;
      display: flex;
      align-items: center;
      gap: 6px;
      background: #059669;
      color: #ffffff;
      border: none;
      border-radius: 50px;
      padding: 10px 16px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 600;
      font-family: Inter, system-ui, sans-serif;
      box-shadow: 0 4px 14px rgba(5, 150, 105, 0.45);
      transition: transform 0.15s ease, background 0.15s ease, opacity 0.15s ease;
      user-select: none;
      line-height: 1;
    }
    #${REFINE_ID}:hover { background: #047857; transform: scale(1.05); }
    #${REFINE_ID}:active { transform: scale(0.97); }
    #${REFINE_ID}:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
    #${REFINE_ID} .pv-spin {
      display: inline-block;
      animation: pv-spin 0.8s linear infinite;
    }
    @keyframes pv-spin { to { transform: rotate(360deg); } }

    #${TOAST_ID} {
      position: fixed;
      bottom: 80px;
      right: 24px;
      z-index: 2147483647;
      background: #1e1e2e;
      color: #cdd6f4;
      border: 1px solid #313244;
      border-radius: 10px;
      padding: 10px 14px;
      font-size: 13px;
      font-family: Inter, system-ui, sans-serif;
      max-width: 320px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.5);
      opacity: 0;
      transform: translateY(8px);
      transition: opacity 0.2s ease, transform 0.2s ease;
      pointer-events: none;
    }
    #${TOAST_ID}.pv-toast-show { opacity: 1; transform: translateY(0); }
    #${TOAST_ID}.pv-toast-error { border-color: #f38ba8; background: #2a1a1e; }
    #${TOAST_ID}.pv-toast-success { border-color: #a6e3a1; }
    #${TOAST_ID} .pv-toast-score {
      font-weight: 700;
      color: #a6e3a1;
      margin-left: 4px;
    }
  `;

  // ── Refine Button ───────────────────────────────────────────────────────────

  const refineBtn = document.createElement('button');
  refineBtn.id = REFINE_ID;
  refineBtn.setAttribute('aria-label', 'Refine prompt with AI');
  refineBtn.innerHTML = `<span>✨</span><span>Refine</span>`;

  // ── Toast ────────────────────────────────────────────────────────────────────

  const toast = document.createElement('div');
  toast.id = TOAST_ID;

  let toastTimer = null;
  function showToast(msg, type = 'success') {
    toast.innerHTML = msg;
    toast.className = `pv-toast-${type}`;
    void toast.offsetWidth;
    toast.classList.add('pv-toast-show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('pv-toast-show'), 4000);
  }

  // ── Refine Logic ────────────────────────────────────────────────────────────

  refineBtn.addEventListener('click', async (e) => {
    e.stopPropagation();

    const currentText = (typeof window.__pv_read_input === 'function')
      ? window.__pv_read_input()
      : '';

    if (!currentText || !currentText.trim()) {
      showToast('✏️ Type something in the AI input first, then click Refine.', 'error');
      return;
    }

    if (!chrome.runtime?.id) {
      showToast('⚠️ Page reload needed — extension was updated.', 'error');
      return;
    }

    refineBtn.disabled = true;
    refineBtn.innerHTML = `<span class="pv-spin">⟳</span><span>Refining…</span>`;

    try {
      const result = await chrome.runtime.sendMessage({
        type: 'REFINE_PROMPT',
        payload: { text: currentText, style: 'professional' },
      });

      if (!result || result.error) {
        showToast(`❌ ${result?.error || 'No response from backend.'}`, 'error');
        return;
      }

      if (!result.refined) {
        showToast('❌ No refined text returned.', 'error');
        return;
      }

      if (typeof window.__pv_inject === 'function') {
        window.__pv_inject(result.refined);
      }

      let scoreHtml = '';
      if (result.score_before != null && result.score_after != null) {
        const diff = result.score_after - result.score_before;
        const sign = diff >= 0 ? '+' : '';
        scoreHtml = ` <span class="pv-toast-score">${sign}${diff} (${result.score_before}→${result.score_after})</span>`;
      }
      showToast(`✨ Prompt refined!${scoreHtml}`, 'success');

      const settingsResp = await chrome.runtime.sendMessage({ type: 'GET_SETTINGS' });
      if (settingsResp?.settings?.autoSubmit) {
        setTimeout(() => {
          if (typeof window.__pv_submit === 'function') window.__pv_submit();
        }, 300);
      }

    } catch (err) {
      showToast(`❌ ${err.message}`, 'error');
    } finally {
      refineBtn.disabled = false;
      refineBtn.innerHTML = `<span>✨</span><span>Refine</span>`;
    }
  });

  // ── Mount ───────────────────────────────────────────────────────────────────

  function getRoot() {
    return document.documentElement || document.body;
  }

  function mount() {
    const root = getRoot();
    root.appendChild(style);
    root.appendChild(refineBtn);
    root.appendChild(toast);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }

  // SPA re-mount guard
  setInterval(() => {
    if (!document.getElementById(REFINE_ID)) {
      const root = getRoot();
      root.appendChild(refineBtn);
      root.appendChild(toast);
    }
  }, 1000);

})();
