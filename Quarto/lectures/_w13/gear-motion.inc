<script>
// One measured angle drives both painted marks and the completed-turn counts.
document.addEventListener("DOMContentLoaded", () => {
  const slide = document.getElementById("gear-tradeoff");
  const pair = slide.querySelector("#w13-gear-pair");
  const motor = pair.querySelector(".input");
  const joint = pair.querySelector(".output");
  const motorCount = pair.querySelector(".motor-count");
  const jointCount = pair.querySelector(".joint-count");
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
  const jointTurns = ["0", "⅓", "⅔", "1"];
  const turnDuration = 1600;
  let position = 0;
  let target = 0;
  let frame = 0;
  let lastTime = 0;

  function paint() {
    motor.setAttribute("transform", "rotate(" + 360 * position + ")");
    joint.setAttribute("transform", "rotate(" + -120 * position + ")");
    const completed = Math.floor(position);
    if (motorCount.textContent !== String(completed)) {
      motorCount.textContent = completed;
      jointCount.textContent = jointTurns[completed];
    }
    slide.classList.toggle("w13-turns-finished", position === 3);
  }

  function settle(turns) {
    cancelAnimationFrame(frame);
    frame = 0;
    position = target = turns;
    paint();
  }

  function animate(now) {
    position = Math.min(target, position + (now - lastTime) / turnDuration);
    lastTime = now;
    paint();
    frame = position < target ? requestAnimationFrame(animate) : 0;
  }

  function requestedTurns() {
    return pair.querySelectorAll(".gear-turn.visible").length;
  }

  function syncTurn() {
    if (Reveal.getCurrentSlide() !== slide) return;
    const next = requestedTurns();
    if (reducedMotion.matches || next < target) {
      settle(next);
    } else if (next > target) {
      target = next;
      if (!frame) {
        lastTime = performance.now();
        frame = requestAnimationFrame(animate);
      }
    }
  }

  function enterSlide() {
    settle(Reveal.getCurrentSlide() === slide ? requestedTurns() : 0);
  }

  Reveal.on("fragmentshown", syncTurn);
  Reveal.on("fragmenthidden", syncTurn);
  Reveal.on("slidechanged", enterSlide);
  Reveal.on("ready", enterSlide);
  reducedMotion.addEventListener("change", enterSlide);
  if (Reveal.isReady()) enterSlide();
});
</script>
