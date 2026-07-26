/* PR-561 RoboTTT: bridge RevealJS fragments to the animation widgets.
 *
 * Each widget ships its own Play / Step / Restart controls. Rather than
 * re-implement navigation, we let RevealJS own it: a slide carries
 * (beats - 1) empty .beat-driver fragments, and whenever the visible-fragment
 * count changes we drive the widget's own Step button to match. That gives
 * clicker support, correct backwards navigation, and the native
 * "fragments exhausted -> next slide" behaviour, with the original stepper
 * untouched underneath.
 */
(function () {
  "use strict";

  var STEP = 'button[aria-label="Step to next beat"]';
  var RESTART = 'button[aria-label="Restart animation"]';

  function widgetIn(section) {
    return section ? section.querySelector(".rttt-widget") : null;
  }

  /* How long to let a beat play before freezing it, in ms. The widgets' Step
     button lands on the *first* frame of a beat, which is the emptiest one;
     letting it run briefly means each press animates into place and then
     holds. Every beat in every widget is at least 2.2s, so this never spills
     into the next one. */
  var HOLD_MS = 1700;

  function playPauseBtn(widget) {
    return widget.querySelector(".rttt-controls button");
  }

  /* Put the widget on beat `target`, let it settle, then freeze. */
  function seek(widget, target) {
    var step = widget.querySelector(STEP);
    var restart = widget.querySelector(RESTART);
    if (!step || !restart) return;

    if (widget._holdTimer) clearTimeout(widget._holdTimer);

    restart.click();                       // beat 0, and playing
    var play = playPauseBtn(widget);
    if (play && /pause/i.test(play.textContent)) play.click();

    for (var i = 0; i < target; i++) step.click();   // Step also pauses
    widget.dataset.beat = target;

    play = playPauseBtn(widget);
    if (play && /play/i.test(play.textContent)) play.click();
    widget._holdTimer = setTimeout(function () {
      var b = playPauseBtn(widget);
      if (b && /pause/i.test(b.textContent)) b.click();
    }, HOLD_MS);
  }

  function sync(section) {
    var w = widgetIn(section);
    if (!w || !w.dataset.beats || w.dataset.beats === "0") return;
    var shown = section.querySelectorAll(".beat-driver.visible").length;
    if (w.dataset.beat === String(shown)) return;
    seek(w, shown);
  }

  function pauseAllExcept(section) {
    document.querySelectorAll(".rttt-widget").forEach(function (w) {
      if (section && section.contains(w)) return;
      var play = w.querySelector(".rttt-controls button");
      if (play && /pause/i.test(play.textContent)) play.click();
    });
  }

  function auditOverflow(reveal) {
    var secs = [].slice.call(
      document.querySelectorAll(".reveal .slides > section"));
    var rows = [], i = 0;
    (function step() {
      if (i >= secs.length) {
        var pre = document.createElement("pre");
        pre.id = "overflow-audit";
        pre.textContent = JSON.stringify(rows);
        document.body.appendChild(pre);
        return;
      }
      reveal.slide(i, 0);
      setTimeout(function () {
        var s = secs[i];
        var body = s.querySelector(":scope > .slidebody");
        var fill = null;
        if (body) {
          var inner = 0;
          [].forEach.call(body.children, function (c) {
            var st = window.getComputedStyle(c);
            if (st.position === "absolute" || st.display === "none") return;
            inner += c.getBoundingClientRect().height / (reveal.getScale() || 1);
          });
          var avail = body.getBoundingClientRect().height /
            (reveal.getScale() || 1);
          fill = avail > 0 ? Math.round((inner / avail) * 100) : null;
        }
        rows.push({
          i: i,
          id: s.id || "(title)",
          content: s.scrollHeight,
          box: s.clientHeight,
          over: Math.max(0, s.scrollHeight - s.clientHeight),
          shown: s.classList.contains("present"),
          at: reveal.getIndices().h,
          fill: fill
        });
        i++;
        step();
      }, 90);
    })();
  }

  function attach(reveal) {
    function onChange(ev) {
      var section = (ev && (ev.currentSlide ||
        (ev.fragment && ev.fragment.closest("section")))) ||
        reveal.getCurrentSlide();
      if (!section) return;
      pauseAllExcept(section);
      sync(section);
    }
    /* ?slide=N jumps straight to a slide. Used for headless review captures;
       harmless in a live talk. */
    var jump = /[?&]slide=(\d+)/.exec(window.location.search);
    if (jump) {
      /* Re-assert: on widget-heavy slides RevealJS's own hash/layout pass can
         land after ours and snap back to slide 0. */
      var want = parseInt(jump[1], 10);
      [0, 250, 700, 1500].forEach(function (d) {
        setTimeout(function () {
          if (reveal.getIndices().h !== want) reveal.slide(want, 0);
        }, d);
      });
    }

    /* ?audit=1 walks every slide and reports content height, so overflow can
       be measured in one headless run instead of 42 screenshots. */
    if (/[?&]audit=1/.test(window.location.search)) auditOverflow(reveal);

    reveal.on("ready", onChange);
    reveal.on("slidechanged", onChange);
    reveal.on("fragmentshown", onChange);
    reveal.on("fragmenthidden", onChange);
    onChange(null);
  }

  /* Quarto boots Reveal itself; wait for it rather than racing. */
  var tries = 0;
  var t = setInterval(function () {
    if (window.Reveal && window.Reveal.isReady && window.Reveal.isReady()) {
      clearInterval(t);
      attach(window.Reveal);
    } else if (++tries > 200) {
      clearInterval(t);
    }
  }, 50);
})();
