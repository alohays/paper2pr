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
--                                         size cover; poster becomes the
--                                         background-image (shown before the
--                                         video has a frame, and in print)
--
-- Wired in Quarto/_quarto.yml (filters:), so every deck under Quarto/ gets it.

local DIVIDER_BG = "#012169"   -- $primary-blue in clean-academic.scss

local function set_default(attrs, key, value)
  if attrs[key] == nil or attrs[key] == "" then
    attrs[key] = value
  end
end

function Header(h)
  if h.level ~= 2 then return nil end

  if h.classes:includes("divider") then
    set_default(h.attributes, "background-color", DIVIDER_BG)
  end

  if h.classes:includes("video-full") then
    local src = h.attributes["video"]
    if src and src ~= "" then
      set_default(h.attributes, "background-video", src)
      set_default(h.attributes, "background-video-loop", "true")
      set_default(h.attributes, "background-video-muted", "true")
      set_default(h.attributes, "background-size", "cover")
      h.attributes["video"] = nil
    end
    local poster = h.attributes["poster"]
    if poster and poster ~= "" then
      set_default(h.attributes, "background-image", poster)
      set_default(h.attributes, "background-size", "cover")
      h.attributes["poster"] = nil
    end
  end
  return h
end
