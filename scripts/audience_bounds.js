// Executed by browser QA on a settled audience frame. Source text stays in the tab.
(() => {
  const slide = Reveal.getCurrentSlide();
  const screen = {left: 0, top: 0, right: innerWidth, bottom: innerHeight};
  const clips = value => ['hidden', 'clip', 'auto', 'scroll'].includes(value);
  const intersect = (box, element, target) => {
    const css = getComputedStyle(element);
    if (clips(css.overflowX)) {
      box.left = Math.max(box.left, target.left);
      box.right = Math.min(box.right, target.right);
    }
    if (clips(css.overflowY)) {
      box.top = Math.max(box.top, target.top);
      box.bottom = Math.min(box.bottom, target.bottom);
    }
  };
  for (let parent = slide; parent; parent = parent.parentElement) {
    intersect(screen, parent, parent.getBoundingClientRect());
  }

  const losses = new Set();
  const ignored = 'aside.notes, script, style, .sr-only, .visually-hidden, .katex, mjx-container, math, [aria-hidden="true"], [role="presentation"]';
  function inspect(el, rect, kind) {
    if (rect.width < 2 || rect.height < 2) return;
    const box = {left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom};
    // A source image can deliberately be zoomed into a smaller teaching panel.
    // Measure the portion that the panel promises to show. A slide-sized
    // container is the audience frame and cannot excuse off-slide material.
    for (let parent = el.parentElement; parent && parent !== slide; parent = parent.parentElement) {
      const crop = parent.getBoundingClientRect();
      if (crop.width >= .9 * (screen.right-screen.left) &&
          crop.height >= .75 * (screen.bottom-screen.top)) continue;
      intersect(box, parent, crop);
    }
    if (box.right <= box.left || box.bottom <= box.top) return;
    const outside = Math.max(screen.left-box.left, box.right-screen.right,
                             screen.top-box.top, box.bottom-screen.bottom);
    // Range boxes include ascenders, descenders and rounding outside glyph ink.
    const tolerance = kind === 'text' ? Math.max(5, rect.height * .30) : 8;
    if (outside > tolerance) losses.add(kind);
  }
  const visible = el => !el.closest(ignored) &&
    el.checkVisibility({checkOpacity: true, checkVisibilityCSS: true});
  for (const el of slide.querySelectorAll('img, video, svg')) {
    if (visible(el) && !el.parentElement.closest('svg')) inspect(el, el.getBoundingClientRect(), 'figure or video');
  }
  const words = document.createTreeWalker(slide, NodeFilter.SHOW_TEXT);
  const range = new Range();
  while (words.nextNode()) {
    const node = words.currentNode, el = node.parentElement;
    // A vector drawing owns its internal coordinate system; measure its outer
    // box above. Off-frame SVG labels can be intentional animation states.
    if (!node.textContent.trim() || !el || el.closest('svg') || !visible(el)) continue;
    range.selectNodeContents(node);
    for (const rect of range.getClientRects()) inspect(el, rect, 'text');
  }
  return [...losses];
})()
