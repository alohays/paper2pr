-- inline-svg.lua: {{< inline-svg path [width=64%] [class=extra] >}}
--
-- Inlines an SVG file into the slide instead of linking it. An <img> SVG
-- cannot use the page's web fonts, so a chart whose text asks for the theme
-- font ("Source Sans Pro") renders in the browser's fallback (Helvetica on a
-- Mac, Arial on the classroom PC) and looks nothing like the slide around
-- it. Inlined, `font-family` resolves against the page and the theme's CSS
-- variables (--accent, --accent2, --chart-muted) reach the shapes. Same
-- reasoning as the semester map in series.lua, which is why the map is
-- inlined too.
--
--   {{< inline-svg ../../Figures/lectures/deck/chart.svg >}}
--   {{< inline-svg ../../Figures/lectures/deck/chart.svg width="80%" >}}
--   {{< inline-svg ../../Figures/lectures/deck/chart.svg class="wide" >}}
--
-- emits
--
--   <figure class="chart-figure [extra]" style="width:W;max-width:W">
--     <svg ...>...</svg>
--   </figure>
--
-- The path is relative to the deck, like an image path. `width` overrides
-- the theme's 64 percent (figure.chart-figure); the theme sizes the inlined
-- <svg> to the figure (width 100 percent, height auto from the viewBox), so
-- the file needs a viewBox and should carry no width/height attributes.
--
-- Two things the SVG author must do, because once inlined the file is part
-- of the page: (1) give the root <svg> an id and scope every selector in its
-- <style> with it (`#s13-ilsvrc text {...}`, not `text {...}`), or the
-- rules leak into the whole deck and collide across charts; (2) keep the
-- ids of <title>, <desc>, markers and gradients unique per file (two inlined
-- charts with id="title" is invalid HTML and breaks aria-labelledby).
--
-- Failures are render failures: a missing file aborts with one "(E)
-- inline-svg:" line (assert(false), as in series.lua; Quarto redefines
-- `error` as a non-throwing logger inside a render).
--
-- Wired for every deck under Quarto/<genre>/ by Quarto/_quarto.yml
-- (format.revealjs.shortcodes).

local function fail(msg)
  if quarto and quarto.log and quarto.log.error then
    quarto.log.error(msg)
  end
  assert(false, msg)
end

local function dirname(p)
  return p:match("^(.*)/[^/]*$") or "."
end

local function escape(s)
  s = tostring(s or "")
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function arg_string(v)
  if v == nil then return "" end
  return pandoc.utils.stringify(v)
end

local function inline_svg(args, kwargs, meta)
  local rel = arg_string(args[1])
  if rel == "" then
    fail("inline-svg: needs a path ({{< inline-svg ../../Figures/<genre>/<deck>/chart.svg >}})")
  end
  local path = rel
  if rel:sub(1, 1) ~= "/" then
    path = dirname(quarto.doc.input_file) .. "/" .. rel
  end
  local f = io.open(path, "r")
  if not f then
    fail("inline-svg: no such file " .. path .. " (path is relative to the deck, like an image)")
  end
  local svg = f:read("a")
  f:close()
  -- The XML prolog and a DOCTYPE are not HTML; strip them. Everything else
  -- (the <svg> element, its <style>, <title>, <desc>) is valid inline SVG.
  svg = svg:gsub("^%s*<%?xml[^>]*%?>%s*", "")
  svg = svg:gsub("^%s*<!DOCTYPE[^>]*>%s*", "")
  if not svg:match("^%s*<svg[%s>]") then
    fail("inline-svg: " .. path .. " does not start with an <svg> element")
  end
  local classes = "chart-figure"
  local extra = arg_string(kwargs["class"])
  if extra ~= "" then classes = classes .. " " .. extra end
  local width = arg_string(kwargs["width"])
  local style = ""
  if width ~= "" then
    style = ' style="width:' .. escape(width) .. ';max-width:' .. escape(width) .. ';"'
  end
  local html = '<figure class="' .. classes .. '"' .. style
    .. ' data-inline-svg="' .. escape(rel) .. '">\n' .. svg .. '\n</figure>'
  return pandoc.RawBlock("html", html)
end

return {
  ["inline-svg"] = inline_svg,
}
