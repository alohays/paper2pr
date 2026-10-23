// Each clip plays once within the lecture clock. Controls allow a deliberate replay.
(() => {
  const configure = () => {
    for (const video of document.querySelectorAll('figure.video-card video')) {
      video.loop = false;
      video.removeAttribute('loop');
      video.controls = true;
    }
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', configure, { once: true });
  } else {
    configure();
  }
})();

// Presenter-controlled diagrams follow Reveal fragments, including backward navigation.
(() => {
  const sync = (event) => {
    const animate = event && ['fragmentshown', 'fragmenthidden'].includes(event.type);
    for (const root of document.querySelectorAll('.mechanism')) {
      const step = root.querySelectorAll('.build-step.visible').length;
      root.dataset.step = String(step);
      for (const panel of root.querySelectorAll('[data-panel-step]')) {
        panel.classList.toggle('is-active', Number(panel.dataset.panelStep) === step);
      }
      for (const cursor of root.querySelectorAll('[data-move-x]')) {
        const positions = cursor.dataset.moveX.split(',').map(Number);
        // A slide entry is a reset, not elapsed physical time.
        cursor.style.transition = animate ? '' : 'none';
        cursor.style.transform = `translateX(${positions[Math.min(step, positions.length - 1)]}px)`;
      }
    }
  };
  const attach = () => {
    if (!window.Reveal) return;
    for (const event of ['ready', 'slidechanged', 'fragmentshown', 'fragmenthidden']) {
      window.Reveal.on(event, sync);
    }
    sync();
  };
  if (window.Reveal) attach();
  else window.addEventListener('load', attach, { once: true });
})();
