-- The topic list lives in the deck. The same ordered list anchors every chapter.
local function escape(s)
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function as_text(value)
  return value and pandoc.utils.stringify(value) or ""
end

local function agenda(args, kwargs, meta)
  local topics = meta["w13-agenda"]
  local chapter = tonumber(as_text(args[1]))
  assert(topics and chapter and chapter >= 0 and chapter < #topics, "Unknown W13 chapter")
  local overlay = as_text(args[2]) == "overlay"
  local kind = overlay and "w13-agenda-overlay" or "w13-agenda-page"
  local html = {string.format('<div class="%s" data-agenda-chapter="%d" role="group" aria-label="Lecture agenda">', kind, chapter)}
  if overlay then
    -- Only the sentinel is a fragment. The list stays accessible while visible.
    table.insert(html, '<span class="fragment w13-agenda-exit" data-fragment-index="0" aria-hidden="true"></span>')
    table.insert(html, '<h2>Today’s lecture</h2>')
  end
  table.insert(html, '<ol class="w13-agenda-list" start="0">')
  for i, topic in ipairs(topics) do
    local current = i - 1 == chapter and ' aria-current="step"' or ''
    table.insert(html, string.format('<li%s><span class="w13-chapter-number" aria-hidden="true">%02d</span><span>%s</span></li>',
      current, i - 1, escape(as_text(topic))))
  end
  table.insert(html, '</ol></div>')
  return pandoc.RawBlock("html", table.concat(html, "\n"))
end

-- Embed the publisher stills only in the local classroom rendition.
-- The standard render retains the English explanations and links to the originals.
local function photo(args, kwargs, meta)
  if as_text(meta["w13-local-clips"]) ~= "true" then return {} end
  local slug, alt = as_text(args[1]), as_text(args[2])
  assert(slug:match("^[a-z0-9-]+$") and alt ~= "", "W13 photo needs an asset name and alt text")
  local directory = quarto.doc.input_file:match("^(.*)/") or "."
  local path = directory .. "/../../Figures/lectures/dgist-2026f-w13/videos/stills/" .. slug .. ".jpg"
  local file = assert(io.open(path, "rb"), "Missing W13 classroom photograph: " .. path)
  local bytes = file:read("a")
  file:close()
  local html = string.format('<div class="w13-photo" data-w13-photo="%s"><img src="data:image/jpeg;base64,%s" alt="%s"></div>',
    slug, quarto.base64.encode(bytes), escape(alt))
  return pandoc.RawBlock("html", html)
end

return { ["w13-agenda"] = agenda, ["w13-photo"] = photo }
