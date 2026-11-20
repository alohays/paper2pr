<script>
// One measured angle drives the disc, the sensor light, the count and the clock.
document.addEventListener("DOMContentLoaded", () => {
  const slide = document.getElementById("wheel-encoder");
  if (!slide) return;
  const figure = slide.querySelector("#w13-encoder-count");
  const trigger = slide.querySelector(".w13-count-run");
  if (!figure || !trigger) return;
  const rotor = figure.querySelector(".enc-rotor");
  const sensor = figure.querySelector(".enc-sensor");
  const count = figure.querySelector(".enc-count");
  const clock = figure.querySelector(".enc-clock");
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
  const duration = 1000;
  const sweep = 270;
  const pitch = 45;
  let frame = 0;
  let started = 0;

  function paint(progress) {
    const angle = sweep * progress;
    rotor.setAttribute("transform", "rotate(" + angle + ")");
    count.textContent = Math.floor(angle / pitch + 1e-6);
    clock.textContent = (progress * duration / 1000).toFixed(1) + " s";
    const offset = angle % pitch;
    sensor.classList.toggle("lit", Math.min(offset, pitch - offset) < 7);
  }

  function settle(progress) {
    cancelAnimationFrame(frame);
    frame = 0;
    paint(progress);
  }

  function step(now) {
    const progress = Math.min(1, (now - started) / duration);
    paint(progress);
    frame = progress < 1 ? requestAnimationFrame(step) : 0;
  }

  function requested() {
    return trigger.classList.contains("visible");
  }

  function enterSlide() {
    settle(Reveal.getCurrentSlide() === slide && requested() ? 1 : 0);
  }

  Reveal.on("fragmentshown", event => {
    const shown = event.fragments || [event.fragment];
    if (!shown.includes(trigger)) return;
    if (reducedMotion.matches) return settle(1);
    settle(0);
    started = performance.now();
    frame = requestAnimationFrame(step);
  });
  Reveal.on("fragmenthidden", () => {
    if (Reveal.getCurrentSlide() === slide) settle(requested() ? 1 : 0);
  });
  Reveal.on("slidechanged", enterSlide);
  Reveal.on("ready", enterSlide);
  reducedMotion.addEventListener("change", enterSlide);
  if (Reveal.isReady()) enterSlide();
});
</script>
