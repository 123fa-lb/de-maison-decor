# DEMAISON_INFOGRAPHIC_PROMPT_V5
"""
ONE authoritative Gemini prompt for the Infographic category (pure function, no API calls).

It replaces the stack of overlapping late-appended infographic blocks that previously sat
inside studio_generator.generate() (PREMIUM_ACCURACY_V5, FACTUAL_ACCURACY, CONNECTOR_ACCURACY_V6,
PREMIUM_CONNECTORS_V2, TITLE_CENTER_V1). Those blocks:
  * hard-coded a globe / clock / wooden-corner example into every infographic prompt, which
    biased unrelated products and told the model where lines "should" go;
  * asked the image model to draw the connector lines itself, which is exactly what produced
    arrows pointing at the wrong features; and
  * dropped the seller's note from the final request.

FINAL DECISION (V5): the infographic has NO arrows or connector lines at all. Nothing is drawn,
erased or corrected afterwards: Gemini's finished image is delivered as generated.
"""

_PROMPT = """You are an art director producing ONE finished, premium, photorealistic e-commerce INFOGRAPHIC for the real product shown in the attached photographs. The photographs are the only source of truth for what the product looks like.

VISUAL QUALITY (non-negotiable)
- Luxury editorial advertising photograph: a rich, realistic, softly blurred lifestyle environment that suits THIS product, warm natural directional light, believable depth of field, realistic contact shadows and reflections, true materials and textures.
- The hero product is large, sharp and fully visible, physically standing in the scene (not pasted onto a panel), occupying roughly the left 60-65 percent of the frame.
- NO white or plain catalogue background, NO white side panel, NO flat template look, NO outer border, NO rectangular photo boxes.
- Output: one square 1:1 image. Nothing important touches the canvas edge.

PRODUCT FIDELITY
- Keep the exact silhouette, proportions, colours, materials, finish, number of parts, patterns and engravings of the real product. Do not redesign it or invent parts.

DETAIL CALLOUTS (circular magnifiers)
- Show two or three vertically stacked, large round photographic magnifier insets in a column on the right, each with a thin light border and a short caption directly beneath it.
- Each inset must be a true magnified view of a DIFFERENT real, clearly visible physical feature of the hero product AS IT IS RENDERED in this same image (same shape, same pattern, same colours, same part). Never show a generic or lookalike detail, and never a feature that is not visible on the hero.
- Choose features that are visually distinctive and located in clearly different places on the product. Prefer genuinely distinctive features (pattern, engraving, dial, texture, hardware, joinery, edge, finish) over plain surfaces. Use fewer insets if fewer genuine features exist.
- Keep a clear gap between the hero product and the circle column; insets must not overlap the hero product, each other or their captions. Order the insets top to bottom roughly in the order their features appear on the product, and make each caption name the exact detail shown (for example the pattern, material or part).

NO ARROWS OR CONNECTORS (final design decision)
- Do NOT draw any connector lines, leader lines, pointer lines, arrows, dots or endpoints anywhere in the image. The circular insets stand on their own, each identified by its caption. Leave the space between the hero and the insets as clean photographic background.

TYPOGRAPHY
- A large elegant editorial serif headline centred at the TOP of the canvas, with a smaller subtitle directly below it, also centred, inside safe margins.
- Use the seller-provided product name only if one is given below; otherwise a short, truthful generic title for the product type.
- Short, refined, correctly spelled captions that describe only what is visibly there. No garbled, cropped or overlapping text.
- Optional: a small row of two or three minimalist line-art icons with short captions at the bottom, only if they are truthful. No made-up claims.

TRUTHFULNESS
- Never invent materials, certifications, performance or marketing claims (for example waterproof, durable, handcrafted, BPA-free) unless the seller notes below state them. If unsure, omit the words.

Generate ONE complete image only: no collage, no multi-panel sheet."""


def build_infographic_prompt(note=""):
    prompt = _PROMPT
    cleaned = " ".join(str(note or "").split())[:600]
    if cleaned:
        prompt += ("\n\nSELLER NOTES (verified facts only; may be used for the title and captions; "
                   "do not add claims beyond them): " + cleaned)
    return prompt
