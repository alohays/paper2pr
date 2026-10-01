// DGIST W06: start each physical slide's local speaker notes at the top.
(function () {
  'use strict';

  // Receiver frames have their own deck copy. Deployed, stripped decks have
  // no notes, so this helper has no work and never creates note content.
  if (/receiver/i.test(window.location.search) ||
      !document.querySelector('.reveal .slides aside.notes, .reveal .slides [data-notes]')) {
    return;
  }

  let connection = null;
  const stateEvents = ['slidechanged', 'fragmentshown', 'fragmenthidden',
    'overviewshown', 'overviewhidden', 'paused', 'resumed'];

  function messageData(event) {
    if (typeof event.data !== 'string') return null;
    try {
      const data = JSON.parse(event.data);
      return data && data.namespace === 'reveal-notes' ? data : null;
    } catch (_) {
      return null;
    }
  }

  function slideKey(state) {
    if (!state || !Number.isInteger(state.indexh) || state.indexh < 0) return null;
    const vertical = state.indexv === undefined ? 0 : state.indexv;
    if (!Number.isInteger(vertical) || vertical < 0) return null;
    // Deliberately exclude indexf: a fragment is still the same reading page.
    return state.indexh + ':' + vertical;
  }

  function disconnect() {
    if (!connection) return;
    const previous = connection;
    connection = null;
    previous.observer.disconnect();
    try {
      stateEvents.forEach(function (name) { previous.deck.off(name, previous.onState); });
      previous.popup.removeEventListener('pagehide', disconnect);
      previous.controls.removeEventListener('scroll', previous.onScroll);
    } catch (_) {
      // A closed or navigated popup may no longer be same-origin.
    }
  }

  function connect(event) {
    const data = messageData(event);
    if (!data || (data.type !== 'connected' && data.type !== 'heartbeat')) return;

    const popup = event.source;
    let popupDocument;
    let controls;
    let notes;
    let value;
    try {
      // Use the official handshake's source, never a replacement window.open.
      // The about:blank URL's reported origin need not describe its inherited
      // document origin. Check the browser-supplied message origin and DOM access.
      if (!popup || popup === window || popup.closed || popup.opener !== window ||
          event.origin !== window.location.origin) return;
      popupDocument = popup.document;
      if (connection && connection.popup === popup && connection.document === popupDocument) return;
      controls = popupDocument.querySelector('#speaker-controls');
      notes = popupDocument.querySelector('.speaker-controls-notes');
      value = popupDocument.querySelector('.speaker-controls-notes .value');
      if (!controls || !notes || !value ||
          !popupDocument.querySelector('#current-slide iframe') ||
          !popupDocument.querySelector('#upcoming-slide iframe')) return;
    } catch (_) {
      return;
    }

    disconnect();
    const deck = window.Reveal;
    let currentState = deck.getState();
    let currentKey = slideKey(currentState);
    let resetPending = false;
    let readingTop = 0;

    function onScroll() {
      // A presenter may scroll while Reveal is waiting to render its next
      // throttled state. Keep the latest reading position, not a stale snapshot.
      readingTop = controls.scrollTop;
    }

    function classifyState() {
      const nextKey = slideKey(currentState);
      if (nextKey !== null && nextKey !== currentKey) {
        currentKey = nextKey;
        resetPending = true;
      }
    }

    function onState() {
      // Parent Reveal events run before its posted message can reach the popup.
      // A popup message listener can run AFTER the note mutation microtask, even
      // with capture enabled, so it cannot reliably classify this update.
      currentState = deck.getState();
      readingTop = controls.scrollTop;
      classifyState();
    }

    const observer = new MutationObserver(function () {
      // Read the public state here as well: initial/reconnection posts need not
      // emit a parent slide event, and no late popup event can leave stale state.
      currentState = deck.getState();
      classifyState();
      // Reveal's speaker renderer throttles state updates by 200 ms. Wait for
      // that renderer to replace/hide the notes before resetting its scroller.
      // Preserve the live reading offset for fragments after replacing the
      // note DOM; a physical slide change takes priority over that offset.
      controls.scrollTop = resetPending ? 0 : readingTop;
      readingTop = controls.scrollTop;
      resetPending = false;
    });

    connection = { popup, document: popupDocument, deck, controls, observer, onState, onScroll };
    stateEvents.forEach(function (name) { deck.on(name, onState); });
    popup.addEventListener('pagehide', disconnect);
    controls.addEventListener('scroll', onScroll, { passive: true });
    observer.observe(value, { childList: true, subtree: true });
    observer.observe(notes, { attributes: true, attributeFilter: ['class'] });
    // Covers a new window, reopening, and the heartbeat after a deck reload.
    // Repeated heartbeats of the same document return above and preserve scroll.
    controls.scrollTop = 0;
  }

  window.addEventListener('message', connect);
  window.addEventListener('pagehide', disconnect);
}());
