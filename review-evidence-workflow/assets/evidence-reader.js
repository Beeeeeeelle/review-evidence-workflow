/* Shared by the original pilot interface and the portable review skill. */
(function (root) {
  'use strict';
  // Only typographic normalization: never approximate or semantic quote matching.
  const normalize = text => String(text || '').normalize('NFKD').toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
  function locate(words, quote) {
    const target = normalize(quote);
    if (target.length < 12) return { status: 'unmatched', boxes: [] };
    let text = '', spans = [];
    for (const word of words || []) {
      const start = text.length;
      text += normalize(word.text);
      spans.push({ start, end: text.length, word });
    }
    const start = text.indexOf(target);
    if (start < 0) return { status: 'unmatched', boxes: [] };
    if (text.indexOf(target, start + 1) >= 0) return { status: 'ambiguous', boxes: [] };
    const end = start + target.length;
    const chosen = spans.filter(s => s.end > start && s.start < end);
    // Reject matches that start/end inside a word; line-end hyphenation remains supported.
    if (chosen[0].start !== start || chosen[chosen.length - 1].end !== end) return { status: 'unmatched', boxes: [] };
    const lines = new Map();
    for (const { word: w } of chosen) {
      const old = lines.get(w.line);
      if (!old) lines.set(w.line, { x: w.x, y: w.y, w: w.w, h: w.h });
      else { const right = Math.max(old.x + old.w, w.x + w.w), bottom = Math.max(old.y + old.h, w.y + w.h); old.x = Math.min(old.x, w.x); old.y = Math.min(old.y, w.y); old.w = right - old.x; old.h = bottom - old.y; }
    }
    return { status: 'matched', boxes: [...lines.values()] };
  }
  function attach({ image, stage, pane, workspace, rail, storageKey = 'evidence-reader-width', breakpoint = 1120, codingMin = 430 }) {
    const page = document.createElement('div'); page.className = 'source-page';
    image.before(page); page.append(image);
    const highlights = document.createElement('div'); highlights.className = 'source-highlights'; highlights.setAttribute('aria-hidden', 'true'); page.append(highlights);
    const status = document.createElement('div'); status.className = 'source-status'; status.setAttribute('role', 'status'); status.setAttribute('aria-live', 'polite');
    pane.querySelector('.pdf-toolbar').after(status);
    const handle = document.createElement('div'); handle.className = 'pdf-divider'; handle.tabIndex = 0;
    handle.setAttribute('role', 'separator'); handle.setAttribute('aria-orientation', 'vertical'); handle.setAttribute('aria-label', 'Resize PDF panel'); handle.setAttribute('aria-controls', pane.id);
    handle.title = 'Drag to resize PDF · arrow keys adjust · double-click resets'; pane.before(handle);
    let desired = 0, dragging = false;
    try { desired = Number(localStorage.getItem(storageKey)) || 0; } catch (_) {}
    function size(value, save = true) {
      if (window.innerWidth <= breakpoint) { workspace.style.removeProperty('grid-template-columns'); return; }
      const available = workspace.clientWidth - rail.getBoundingClientRect().width - 10;
      const max = Math.max(320, available - codingMin), width = Math.round(Math.max(320, Math.min(max, value || window.innerWidth * .4)));
      workspace.style.gridTemplateColumns = `${rail.getBoundingClientRect().width}px minmax(0,1fr) 10px ${width}px`;
      handle.setAttribute('aria-valuemin', '320'); handle.setAttribute('aria-valuemax', String(Math.round(max))); handle.setAttribute('aria-valuenow', String(width)); handle.setAttribute('aria-valuetext', `PDF width ${width} pixels`);
      if (save) { desired = width; try { localStorage.setItem(storageKey, String(width)); } catch (_) {} }
    }
    handle.addEventListener('pointerdown', e => { if (e.button !== 0) return; dragging = true; handle.setPointerCapture(e.pointerId); document.body.classList.add('resizing-pdf'); e.preventDefault(); });
    handle.addEventListener('pointermove', e => { if (dragging) size(workspace.getBoundingClientRect().right - e.clientX - 5); });
    const stop = () => { dragging = false; document.body.classList.remove('resizing-pdf'); };
    handle.addEventListener('pointerup', stop); handle.addEventListener('pointercancel', stop); handle.addEventListener('lostpointercapture', stop);
    handle.addEventListener('dblclick', () => size(window.innerWidth * .4));
    handle.addEventListener('keydown', e => { let value = Number(handle.getAttribute('aria-valuenow')); if (e.key === 'ArrowLeft') value += e.shiftKey ? 80 : 20; else if (e.key === 'ArrowRight') value -= e.shiftKey ? 80 : 20; else if (e.key === 'Home') value = 320; else if (e.key === 'End') value = Number(handle.getAttribute('aria-valuemax')); else return; e.preventDefault(); size(value); });
    window.addEventListener('resize', () => size(desired, false)); size(desired, false);
    return {
      zoom(value) { page.style.width = `${value}%`; },
      clear(message = '') { highlights.replaceChildren(); status.textContent = message; },
      show(words, quote) {
        highlights.replaceChildren();
        if (!quote) { status.textContent = 'Scroll to read · drag the divider to resize'; return; }
        const result = locate(words, quote);
        status.textContent = result.status === 'matched' ? 'Source quotation located · highlighted in yellow' : result.status === 'ambiguous' ? 'Page opened · quotation occurs more than once; check the source' : 'Page opened · exact quotation not located; check the source';
        for (const b of result.boxes) { const mark = document.createElement('span'); mark.className = 'source-highlight'; Object.assign(mark.style, { left: `${b.x * 100}%`, top: `${b.y * 100}%`, width: `${b.w * 100}%`, height: `${b.h * 100}%` }); highlights.append(mark); }
        const first = highlights.firstElementChild;
        if (first) { const a = first.getBoundingClientRect(), s = stage.getBoundingClientRect(); stage.scrollTo({ top: stage.scrollTop + a.top - s.top - 90, left: Math.max(0, stage.scrollLeft + a.left - s.left - 35), behavior: 'auto' }); }
      }
    };
  }
  const api = { locate, normalize, attach };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.EvidenceReader = api;
})(typeof window !== 'undefined' ? window : this);
