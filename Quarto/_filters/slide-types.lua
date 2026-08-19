-- slide-types.lua: slide-type shorthands for the paper2pr themes.
--
-- Reveal paints `data-background-*` on the full viewport, outside the scaled
-- slide canvas, so full-bleed slide types go through background attributes
-- instead of stretched CSS boxes. Authors write the class; this filter adds
-- the attributes. Anything the author sets explicitly wins.
--
--   ## {.divider}                      -> background-color = divider colour
--   ## {.video-full video="<src>" poster="<img>"}
--                                      -> background-video = <src>, looped, muted,
--                                         size cover; the poster travels as
--                                         data-background-poster and a small
--                                         script (included once, after the body)
--                                         paints it under the background video
--                                         (shown before the video has a frame,
--                                         and in print). It must NOT become
--                                         data-background-image: reveal 5.1
--                                         loads a background image *instead of*
--                                         the video when both are set (loadSlide:
--                                         if image ... else if video), so the
--                                         WP0 form never played (found 2026-08-19
--                                         in headless Chrome; the poster looked
--                                         like the clip). poster without video
--                                         still becomes the background-image.
--   ## {.video-full video="@<slug>"}   -> the clip named <slug> in the deck's
--                                         videos.json (Figures/<genre>/<deck>/,
--                                         written by scripts/media_prep.py):
--                                         background-video = its release_url,
--                                         background-image = its poster_url (or
--                                         the local files when the entry is
--                                         local_only). A plain path still works
--                                         as before. The lookup is shared with
--                                         the video-card shortcodes through
--                                         video-manifest.lua; an unknown slug or
--                                         a missing videos.json fails the render.
--
-- Wired in Quarto/_quarto.yml (filters:), so every deck under Quarto/ gets it.
-- The metadata is needed for the @slug lookup (`video-manifest:` override), so
-- the filter runs as a Pandoc-level walk that carries doc.meta down to each
-- header; pandoc would otherwise hand Meta to a filter after the blocks.

local DIVIDER_BG = "#012169"   -- $primary-blue in clean-academic.scss

local manifest = nil           -- loaded on first @slug, never otherwise
local needs_poster_script = false

local function set_default(attrs, key, value)
  if attrs[key] == nil or attrs[key] == "" then
    attrs[key] = value
  end
end

local function resolve_at(ref, meta)
  if not manifest then
    manifest = dofile(quarto.utils.resolve_path("video-manifest.lua"))
  end
  return manifest.resolve(meta, ref)
end

local function header(h, meta)
  if h.level ~= 2 then return nil end

  if h.classes:includes("divider") then
    set_default(h.attributes, "background-color", DIVIDER_BG)
  end

  if h.classes:includes("video-full") then
    local src = h.attributes["video"]
    local poster = h.attributes["poster"]
    if src and src:sub(1, 1) == "@" then
      local entry = resolve_at(src, meta)
      src = entry.src
      if not poster or poster == "" then poster = entry.poster end
      h.attributes["video-slug"] = entry.slug   -- pandoc writes data-video-slug
    end
    if src and src ~= "" then
      set_default(h.attributes, "background-video", src)
      set_default(h.attributes, "background-video-loop", "true")
      set_default(h.attributes, "background-video-muted", "true")
      set_default(h.attributes, "background-size", "cover")
      h.attributes["video"] = nil
      if poster and poster ~= "" then
        set_default(h.attributes, "background-poster", poster)
        h.attributes["poster"] = nil
        needs_poster_script = true
      end
    elseif poster and poster ~= "" then
      set_default(h.attributes, "background-image", poster)
      set_default(h.attributes, "background-size", "cover")
      h.attributes["poster"] = nil
    end
  end
  return h
end

-- Paints data-background-poster under reveal's background video, and keeps
-- the present background clip playing (see ensurePlaying). Reveal keeps
-- one .slide-background-content per slide from init; the <video> is appended
-- into it lazily (within viewDistance) and is transparent until its first
-- frame, so a CSS background-image on the content element shows first, and
-- again in print where the video is hidden. unloadSlide may clear the style,
-- hence the re-apply on every slidechanged.
local POSTER_SCRIPT = [[
<script>
(function () {
  function applyPosters() {
    if (!window.Reveal || !Reveal.getSlideBackground) return;
    document.querySelectorAll('.reveal .slides section[data-background-poster]').forEach(function (s) {
      var poster = s.getAttribute('data-background-poster');
      var bg = Reveal.getSlideBackground(s);
      var content = bg && bg.querySelector('.slide-background-content');
      if (!content) return;
      if (!content.style.backgroundImage) {
        content.style.backgroundImage = 'url("' + poster + '")';
        content.style.backgroundSize = content.style.backgroundSize || 'cover';
        content.style.backgroundPosition = content.style.backgroundPosition || 'center';
      }
      var v = content.querySelector('video');
      if (v && !v.getAttribute('poster')) v.setAttribute('poster', poster);
    });
  }
  // Reveal 5.1 re-runs slide() on its own hashchange right after a
  // navigation, which pauses the present background video and replays it
  // only if readyState > 1 at that instant; the replay's seek to 0 can leave
  // readyState at 1 for a moment (more often with a remote source), and then
  // reveal waits for a loadeddata that never comes: the clip sits frozen on
  // the slide the presenter just came back to (measured 2026-08-19). After
  // each change, make sure the present background clip is playing.
  function ensurePlaying() {
    if (Reveal.isPaused && Reveal.isPaused()) return;
    if (Reveal.isOverview && Reveal.isOverview()) return;
    document.querySelectorAll('.backgrounds .slide-background.present').forEach(function (bg) {
      bg.querySelectorAll(':scope > .slide-background-content > video').forEach(function (v) {
        if (!v.paused) return;
        var tryPlay = function () {
          if (!v.closest('.present')) return;
          var p = v.play();
          if (p && p.catch) p.catch(function () {});
        };
        if (v.readyState >= 2) tryPlay();
        else v.addEventListener('canplay', tryPlay, { once: true });
      });
    });
  }
  function arm() {
    applyPosters();
    ensurePlaying();
    Reveal.on('slidechanged', function () {
      applyPosters();
      setTimeout(ensurePlaying, 300);
    });
  }
  if (window.Reveal && Reveal.isReady && Reveal.isReady()) { arm(); }
  else if (window.Reveal && Reveal.on) { Reveal.on('ready', arm); }
  else { document.addEventListener('DOMContentLoaded', function () { if (window.Reveal) Reveal.on('ready', arm); }); }
})();
</script>
]]

function Pandoc(doc)
  local meta = doc.meta
  local blocks = doc.blocks:walk({
    Header = function(h) return header(h, meta) end,
  })
  if needs_poster_script and quarto.doc.is_format("revealjs") then
    quarto.doc.include_text("after-body", POSTER_SCRIPT)
  end
  return pandoc.Pandoc(blocks, meta)
end
