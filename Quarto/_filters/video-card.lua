-- video-card.lua: {{< video-card slug >}} and {{< video-caption slug >}}.
--
-- Both read the deck's videos.json (see video-manifest.lua for where that is
-- and how a slug resolves) and emit raw HTML; the slide never carries a URL.
--
--   {{< video-card slug >}}
--   {{< video-card slug class="extra" >}}
--     <figure class="video-card video-inline extra">
--       <video class="video-inline" poster=POSTER preload="auto"
--              muted playsinline loop data-autoplay>
--         <source data-src=SRC type="video/mp4">
--       </video>
--       <img class="video-poster-print" src=POSTER alt="">   (print only)
--       <figcaption class="video-caption[ fragment]">
--         <span class="video-caption-title">title</span>
--         <span class="video-caption-meta">publisher · Aug 2026 · label · 1x speed</span>
--       </figcaption>                                        (unless caption: none)
--     </figure>
--
--   {{< video-caption slug >}}
--     <div class="video-caption[ fragment]">...same two spans...</div>
--     For a `## {.video-full video="@slug"}` slide, whose clip is the reveal
--     background; nothing is emitted when the entry says caption: none.
--
-- Why data-autoplay + data-src, not the HTML autoplay attribute (measured in
-- headless Chrome, 2026-08-19): with `autoplay`, every clip in the deck starts
-- downloading and playing the moment the page opens, hidden, and a clip that
-- reveal paused on leaving its slide stays frozen when the presenter comes
-- back to it (reveal only restarts `data-autoplay` media). With `data-autoplay`
-- reveal plays the clip when the slide is shown and again on every return,
-- pauses it on leaving; `<source data-src>` is reveal's lazy-load hook, so the
-- bytes are fetched only for slides within viewDistance (3) of the current
-- one; `preload="auto"` is what makes that fetch reach loadeddata, which
-- reveal waits for before it plays (preload="none" never plays on desktop).
--
-- Two cards side by side: wrap them in `::: {.two-up}` (the theme lays the
-- div out as a flex row, 48 percent each). The shortcode pass cannot see its
-- neighbours, so the row container is the author's, not the shortcode's.
--
-- SRC / POSTER are the Release URLs from videos.json, or the local relative
-- files when the entry is local_only (media_prep.py --local).
--
-- Wired for every deck under Quarto/<genre>/ by Quarto/_quarto.yml
-- (format.revealjs.shortcodes). Fixtures under Quarto/_fixtures/ are outside
-- the project and declare `shortcodes: [../_filters/video-card.lua]` plus
-- `video-manifest:` themselves. Quarto 1.8 registers shortcode handlers only
-- from `shortcodes:`; a file listed under `filters:` runs as a filter and its
-- handlers are never seen (tested 2026-08-19, see AGENTS.md).

local manifest = dofile(quarto.utils.resolve_path("video-manifest.lua"))

local function arg_string(v)
  if v == nil then return "" end
  return pandoc.utils.stringify(v)
end

local function video_card(args, kwargs, meta)
  local entry = manifest.resolve(meta, arg_string(args[1]))
  local classes = "video-card video-inline"
  local extra = arg_string(kwargs["class"])
  if extra ~= "" then classes = classes .. " " .. extra end
  local src, poster = manifest.escape(entry.src), manifest.escape(entry.poster)
  local html = {
    '<figure class="' .. classes .. '" data-video-slug="' .. manifest.escape(entry.slug) .. '">',
    '<video class="video-inline" poster="' .. poster
      .. '" preload="auto" muted playsinline loop data-autoplay>',
    '<source data-src="' .. src .. '" type="video/mp4">',
    '</video>',
    '<img class="video-poster-print" src="' .. poster .. '" alt="">',
  }
  local cap = manifest.caption_html(entry, "figcaption")
  if cap then html[#html + 1] = cap end
  html[#html + 1] = '</figure>'
  return pandoc.RawBlock("html", table.concat(html, "\n"))
end

local function video_caption(args, kwargs, meta)
  local entry = manifest.resolve(meta, arg_string(args[1]))
  local cap = manifest.caption_html(entry, "div")
  if not cap then return pandoc.Blocks({}) end
  return pandoc.RawBlock("html", cap)
end

return {
  ["video-card"] = video_card,
  ["video-caption"] = video_caption,
}
