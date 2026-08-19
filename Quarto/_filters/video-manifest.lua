-- video-manifest.lua: the one reader of a deck's videos.json.
--
-- Shared by video-card.lua (the {{< video-card >}} / {{< video-caption >}}
-- shortcodes) and slide-types.lua (the `video="@slug"` form of .video-full);
-- both load it with dofile(quarto.utils.resolve_path("video-manifest.lua")),
-- so the lookup rules and the caption wording live in exactly one place.
--
-- Where the lock file is:
--   * document metadata `video-manifest: <path>` (relative to the qmd) wins;
--     fixtures under Quarto/_fixtures/ use it because they live outside
--     Figures/;
--   * otherwise Quarto/<genre>/<deck>.qmd -> Figures/<genre>/<deck>/videos.json
--     (scripts/media_prep.py writes that file from videos.yml).
--
-- What an entry resolves to:
--   entry.src     release_url, or the local relative path when the entry is
--                 marked local_only (media_prep.py --local, authoring before
--                 the Release exists; check_site_assets.py refuses to deploy it)
--   entry.poster  poster_url, or the local poster in the same case
--   entry.label   the plain autonomy wording (table below; scripts/media_prep.py
--                 carries the same table and scripts/test_media.py compares them)
--   entry.month   "Aug 2026" from published "2026-08"
--
-- A missing lock file or slug is a render error, never an empty card.

local M = {}

M.AUTONOMY_LABEL = {
  autonomous = "autonomous",
  claimed    = "autonomy claimed",
  teleop     = "teleoperated",
  unknown    = "autonomy not stated",
}

local MONTHS = { "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" }

-- Abort the render. Inside `quarto render` the global `error` is NOT Lua's:
-- Quarto's filter runtime (share/filters/main.lua) redefines it as a
-- non-throwing logger, so `error(msg)` would print "ERROR ..." and return,
-- and execution would carry on past the failure (M.load would go on to decode
-- nil, callers would index nil). `assert` is left alone by Quarto, so
-- assert(false, msg) raises for real in both contexts: a render (exit 1, no
-- output written) and `quarto pandoc lua` (scripts/test_media.py). The
-- message is logged first so it appears once in Quarto's own red "(E)" line
-- before the traceback.
local function fail(msg)
  if quarto and quarto.log and quarto.log.error then
    quarto.log.error(msg)
  end
  assert(false, msg)
end

local function dirname(p)
  return p:match("^(.*)/[^/]*$") or "."
end

local function split(p)
  local parts = {}
  for part in p:gmatch("[^/]+") do
    if part == ".." then
      table.remove(parts)
    elseif part ~= "." then
      parts[#parts + 1] = part
    end
  end
  return parts
end

-- relpath("/r/Figures/lectures/w02/videos", "/r/Quarto/lectures")
--   -> "../../Figures/lectures/w02/videos"
function M.relpath(target, from)
  local a, b = split(target), split(from)
  local i = 1
  while i <= #a and i <= #b and a[i] == b[i] do i = i + 1 end
  local out = {}
  for _ = i, #b do out[#out + 1] = ".." end
  for j = i, #a do out[#out + 1] = a[j] end
  if #out == 0 then return "." end
  return table.concat(out, "/")
end

function M.escape(s)
  s = tostring(s or "")
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

function M.month_text(published)
  local y, m = tostring(published or ""):match("^(%d%d%d%d)%-(%d%d)$")
  if not y then return tostring(published or "") end
  local name = MONTHS[tonumber(m)]
  if not name then return tostring(published) end
  return name .. " " .. y
end

local function read_file(path)
  local f = io.open(path, "r")
  if not f then return nil end
  local text = f:read("a")
  f:close()
  return text
end

-- -> absolute lock path, absolute directory of the qmd being rendered
function M.manifest_path(meta)
  local input = quarto.doc.input_file
  local input_dir = dirname(input)
  local override = meta and meta["video-manifest"]
  if override then
    local p = pandoc.utils.stringify(override)
    if p:sub(1, 1) ~= "/" then p = input_dir .. "/" .. p end
    return p, input_dir
  end
  local root, genre, name = input:match("^(.*)/Quarto/([^/]+)/([^/]+)%.qmd$")
  if not root then
    fail("video-manifest: " .. input .. " is not at Quarto/<genre>/<deck>.qmd; "
      .. "set `video-manifest: <path to videos.json>` in the document metadata")
  end
  return root .. "/Figures/" .. genre .. "/" .. name .. "/videos.json", input_dir
end

local cache = {}

function M.load(meta)
  local path, input_dir = M.manifest_path(meta)
  if cache[path] then return cache[path] end
  local text = read_file(path)
  if not text then
    fail("video-manifest: no lock file at " .. path
      .. " (run: python3 scripts/media_prep.py <deck>)")
  end
  local ok, data = pcall(quarto.json.decode, text)
  if not ok or type(data) ~= "table" or type(data.videos) ~= "table" then
    fail("video-manifest: " .. path .. " is not a videos.json written by media_prep.py")
  end
  local by_slug = {}
  local videos_dir = dirname(path) .. "/videos"
  for _, v in ipairs(data.videos) do
    if v.slug then
      v.label = M.AUTONOMY_LABEL[v.autonomy] or M.AUTONOMY_LABEL.unknown
      v.month = M.month_text(v.published)
      v.speed = v.speed or "1x"
      v.caption = v.caption or "visible"
      if v.local_only then
        local rel = M.relpath(videos_dir, input_dir)
        v.src = rel .. "/" .. v.file
        v.poster = rel .. "/" .. v.poster_file
      else
        v.src = v.release_url
        v.poster = v.poster_url
      end
      by_slug[v.slug] = v
    end
  end
  local loaded = { path = path, input_dir = input_dir, by_slug = by_slug, data = data }
  cache[path] = loaded
  return loaded
end

function M.resolve(meta, slug)
  slug = tostring(slug or ""):gsub("^@", "")
  if slug == "" then
    fail("video-manifest: a slug is required ({{< video-card <slug> >}} or video=\"@<slug>\")")
  end
  local lock = M.load(meta)
  local entry = lock.by_slug[slug]
  if not entry then
    local known = {}
    for k in pairs(lock.by_slug) do known[#known + 1] = k end
    table.sort(known)
    fail("video-manifest: no clip with slug '" .. slug .. "' in " .. lock.path
      .. " (known: " .. table.concat(known, ", ") .. ")")
  end
  return entry
end

-- The caption strip: title left, meta right. `tag` is "figcaption" inside a
-- card, "div" on a .video-full slide. nil when the entry says caption: none.
function M.caption_html(entry, tag)
  if entry.caption == "none" then return nil end
  local cls = "video-caption"
  if entry.caption == "fragment" then cls = cls .. " fragment" end
  local meta = M.escape(entry.publisher) .. " &middot; " .. M.escape(entry.month)
    .. " &middot; " .. M.escape(entry.label) .. " &middot; " .. M.escape(entry.speed) .. " speed"
  return "<" .. tag .. ' class="' .. cls .. '">'
    .. '<span class="video-caption-title">' .. M.escape(entry.title) .. "</span>"
    .. '<span class="video-caption-meta">' .. meta .. "</span>"
    .. "</" .. tag .. ">"
end

return M
