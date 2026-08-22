-- series.lua: the course-series shortcodes.
--
-- A lecture deck that belongs to a course declares `series: <course>` in its
-- YAML front matter (new_deck.py --series writes it). Everything these
-- shortcodes print comes from the series lock
-- Figures/lectures/_series/<course>/series.json, which scripts/series_assets.py
-- writes from Quarto/lectures/_series/<course>.yml; the slide never carries a
-- date, a title or a URL that could drift from the yml. Same pattern as the
-- video shortcodes (video-manifest.lua reads videos.json).
--
--   {{< semester-map >}}            the timeline with this deck's week ringed
--                                   as "today": the session whose `deck` is the
--                                   current deck name (Quarto/<genre>/<deck>.qmd)
--   {{< semester-map week=4 >}}     ... forced to week 4 (a fixture, a recap)
--   {{< semester-map plain=true >}} ... nothing highlighted
--       The SVG is inlined, not linked: an <img> SVG cannot use the page's web
--       fonts, so the map's text would render in the browser's serif default;
--       inline, `font-family: inherit` really is the theme font. Emitted as
--       <figure class="semester-map">...svg...</figure>.
--   {{< series-qr >}}               the question-wall block:
--       <div class="qr-block"><img class="qr" src=RELPATH/qr-qa.svg ...>
--       <div class="qr-meta"><span class="qr-tool">Wooclap</span>
--       <span class="qr-code">code PLACEHOLDER</span>
--       <span class="qr-url">app.wooclap.com/PLACEHOLDER</span></div></div>
--   {{< series-field key >}}        inline text of a scalar field: course,
--                                   code, term, institution, room, time,
--                                   instructor, co_instructor, course_page,
--                                   lms_note, qa_tool.name, notation.policy ...
--   {{< series-rules >}}            a bullet list of `rules`
--   {{< series-session key >}}      this deck's session (or week=NN): key is
--                                   title | date | short_date | presenter | week |
--                                   kind | tag | index | prior_title | prior_date |
--                                   prior_short_date | prior_presenter | prior_week |
--                                   prior_kind | prior_index | prior_tag
--
-- Failures are render failures, never empty output: no `series:` in the
-- metadata, no lock file, an unknown key, a session that has no prior, all
-- abort with one "(E) series:" line. Inside `quarto render` the global
-- `error` is a non-throwing logger (Quarto redefines it), so the abort is
-- assert(false, msg), as in video-manifest.lua.
--
-- Paths: the repo root is the directory above Quarto/ in the input path; the
-- lock is <root>/Figures/lectures/_series/<course>/series.json; RELPATH is
-- the relative path from the input file's directory to that directory
-- (../../Figures/lectures/_series/<course> from Quarto/lectures/, one more
-- ../ from a fixture under Quarto/_fixtures/<dir>/). The deployed tree keeps
-- the same shape (slides/<genre>/ next to Figures/), so the link survives.
--
-- Wired for every deck under Quarto/<genre>/ by Quarto/_quarto.yml
-- (format.revealjs.shortcodes, next to video-card.lua). Fixtures and the
-- shared include slides live outside the project and repeat it.

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

local function relpath(target, from)
  local a, b = split(target), split(from)
  local i = 1
  while i <= #a and i <= #b and a[i] == b[i] do i = i + 1 end
  local out = {}
  for _ = i, #b do out[#out + 1] = ".." end
  for j = i, #a do out[#out + 1] = a[j] end
  if #out == 0 then return "." end
  return table.concat(out, "/")
end

local function escape(s)
  s = tostring(s or "")
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function read_file(path)
  local f = io.open(path, "r")
  if not f then return nil end
  local text = f:read("a")
  f:close()
  return text
end

local function arg_string(v)
  if v == nil then return "" end
  return pandoc.utils.stringify(v)
end

-- -> repo root, input dir, deck name (nil when the input is not Quarto/<genre>/<deck>.qmd)
local function locate()
  local input = quarto.doc.input_file
  local root = input:match("^(.*)/Quarto/")
  if not root then
    fail("series: " .. input .. " is not under a Quarto/ directory; the series "
      .. "lock is found relative to it")
  end
  -- Quarto/<genre>/<deck>.qmd, where <genre> is a real genre directory (not
  -- _fixtures/ or another underscore directory, which is outside the project).
  local genre, deck = input:match("^.*/Quarto/([^_/][^/]*)/([^/]+)%.qmd$")
  return root, dirname(input), deck
end

local cache = {}

-- -> { course, data, figdir, rel, deck, session (or nil) }
local function load(meta)
  local course = meta and meta["series"] and pandoc.utils.stringify(meta["series"]) or ""
  if course == "" then
    fail("series: this deck uses a series shortcode but declares no `series: <course>` "
      .. "in its YAML front matter (new_deck.py --series writes it)")
  end
  local root, input_dir, deck = locate()
  local key = course .. "\0" .. input_dir
  if cache[key] then return cache[key] end
  local figdir = root .. "/Figures/lectures/_series/" .. course
  local lock = figdir .. "/series.json"
  local text = read_file(lock)
  if not text then
    fail("series: no lock file at " .. lock .. " (run: python3 scripts/series_assets.py "
      .. course .. ")")
  end
  local ok, data = pcall(quarto.json.decode, text)
  if not ok or type(data) ~= "table" or type(data.sessions) ~= "table" then
    fail("series: " .. lock .. " is not a series.json written by series_assets.py")
  end
  local session = nil
  if deck then
    for _, s in ipairs(data.sessions) do
      if s.deck and s.deck ~= "" and s.deck == deck then session = s end
    end
  end
  local loaded = {
    course = course, data = data, figdir = figdir, deck = deck,
    rel = relpath(figdir, input_dir), session = session,
  }
  cache[key] = loaded
  return loaded
end

local function session_by_index(data, idx)
  for _, s in ipairs(data.sessions) do
    if tonumber(s.index) == idx then return s end
  end
  return nil
end

-- The session a shortcode is about: week=NN if given, else the deck's own.
local function current_session(ctx, kwargs, what)
  local week = arg_string(kwargs["week"])
  if week ~= "" then
    local idx = tonumber(week)
    local s = idx and session_by_index(ctx.data, idx)
    if not s then
      fail("series: " .. what .. ": week=" .. week .. " is not a session of "
        .. ctx.course .. " (1.." .. #ctx.data.sessions .. ")")
    end
    return s
  end
  if ctx.session then return ctx.session end
  return nil
end

local function field_of(tbl, key)
  local cur = tbl
  for part in key:gmatch("[^.]+") do
    if type(cur) ~= "table" then return nil end
    cur = cur[part]
  end
  return cur
end

-- {{< semester-map [week=NN] [plain=true] >}}
local function semester_map(args, kwargs, meta)
  local ctx = load(meta)
  local plain = arg_string(kwargs["plain"])
  local file, alt
  local s = nil
  if plain ~= "true" and plain ~= "1" and plain ~= "yes" then
    s = current_session(ctx, kwargs, "semester-map")
  end
  if s then
    file = string.format("semester-map-w%02d.svg", tonumber(s.index))
    alt = string.format("Semester timeline, week %02d highlighted", tonumber(s.index))
  else
    file = "semester-map.svg"
    alt = "Semester timeline"
  end
  local svg = read_file(ctx.figdir .. "/" .. file)
  if not svg then
    fail("series: no " .. file .. " in " .. ctx.figdir
      .. " (run: python3 scripts/series_assets.py " .. ctx.course .. ")")
  end
  svg = svg:gsub("^%s*<%?xml[^>]*%?>%s*", "")
  local html = '<figure class="semester-map" data-series="' .. escape(ctx.course)
    .. '" data-map="' .. escape(file) .. '" aria-label="' .. escape(alt) .. '">\n'
    .. svg .. '</figure>'
  return pandoc.RawBlock("html", html)
end

-- {{< series-qr >}}
local function series_qr(args, kwargs, meta)
  local ctx = load(meta)
  local qa = ctx.data.qa_tool or {}
  local url = tostring(qa.url or "")
  local shown = url:gsub("^https?://", ""):gsub("/$", "")
  local html = table.concat({
    '<div class="qr-block">',
    '<img class="qr" src="' .. escape(ctx.rel .. "/qr-qa.svg")
      .. '" alt="QR code for the question wall">',
    '<div class="qr-meta">',
    '<span class="qr-tool">' .. escape(qa.name) .. '</span> ',
    '<span class="qr-code">code ' .. escape(qa.code) .. '</span>',
    '<span class="qr-url">' .. escape(shown) .. '</span>',
    '</div>',
    '</div>',
  }, "")
  return pandoc.RawBlock("html", html)
end

-- {{< series-field key >}}
local function series_field(args, kwargs, meta)
  local ctx = load(meta)
  local key = arg_string(args[1])
  if key == "" then fail("series: series-field needs a key ({{< series-field course >}})") end
  local v = field_of(ctx.data, key)
  if v == nil or type(v) == "table" then
    fail("series: series-field: no scalar field '" .. key .. "' in " .. ctx.course
      .. " (course, code, term, institution, room, time, instructor, co_instructor, "
      .. "course_page, lms_note, qa_tool.name, qa_tool.url, qa_tool.code, "
      .. "notation.policy, notation.note)")
  end
  return pandoc.Inlines({ pandoc.Str(tostring(v)) })
end

-- {{< series-rules >}}
local function series_rules(args, kwargs, meta)
  local ctx = load(meta)
  local rules = ctx.data.rules
  if type(rules) ~= "table" or #rules == 0 then
    fail("series: " .. ctx.course .. " has no rules list")
  end
  local items = {}
  for _, r in ipairs(rules) do
    items[#items + 1] = { pandoc.Plain({ pandoc.Str(tostring(r)) }) }
  end
  return pandoc.BulletList(items)
end

local SESSION_KEYS = {
  title = true, date = true, short_date = true, presenter = true, week = true,
  kind = true, index = true, tag = true,
  prior_title = true, prior_date = true, prior_short_date = true,
  prior_presenter = true, prior_week = true, prior_kind = true,
  prior_index = true, prior_tag = true,
}

-- {{< series-session key [week=NN] >}}
local function series_session(args, kwargs, meta)
  local ctx = load(meta)
  local key = arg_string(args[1])
  if not SESSION_KEYS[key] then
    local known = {}
    for k in pairs(SESSION_KEYS) do known[#known + 1] = k end
    table.sort(known)
    fail("series: series-session: unknown key '" .. key .. "' (known: "
      .. table.concat(known, ", ") .. ")")
  end
  local s = current_session(ctx, kwargs, "series-session")
  if not s then
    fail("series: series-session: " .. (ctx.deck or quarto.doc.input_file)
      .. " is not the deck of any session in " .. ctx.course
      .. " (set `deck:` on the session in the series yml, or pass week=NN)")
  end
  local target, field = s, key
  if key:sub(1, 6) == "prior_" then
    field = key:sub(7)
    local p = s.prior_index and session_by_index(ctx.data, tonumber(s.prior_index))
    if not p then
      fail("series: series-session: session " .. tostring(s.index) .. " (" .. tostring(s.title)
        .. ") has no prior session in " .. ctx.course)
    end
    target = p
  end
  local v = target[field]
  if v == nil then v = "" end
  return pandoc.Inlines({ pandoc.Str(tostring(v)) })
end

return {
  ["semester-map"] = semester_map,
  ["series-qr"] = series_qr,
  ["series-field"] = series_field,
  ["series-rules"] = series_rules,
  ["series-session"] = series_session,
}
