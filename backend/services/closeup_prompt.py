# DEMAISON_CLOSEUP_V42_PROMPT
"""
Single authoritative prompt for the Close-up category (Close-up ONLY).
Pure function, no dependencies, no API calls: testable offline.
"""

_HEAD = """You are a commercial product-detail photographer. The attached photographs show ONE real product (a single SKU). They are the only source of truth for what it looks like.

TASK
Produce ONE square 1:1 premium MACRO product-detail photograph of this exact product, built around one distinctive real feature. A viewer must be able to inspect that feature as if holding the product under a magnifier."""

_CHOOSE = """
STEP 1 - CHOOSE THE FEATURE (decide silently, write no analysis)
Look across ALL reference photographs and pick the one feature with the most visual information that is clearly resolved in at least one reference. Rank: (1) functional hardware or construction (closure, lid, cap, hinge, handle, spout, latch, clasp, knob, joint); (2) crafted surface (carving, engraving, embossing, inlay, weave, stitching, cutwork, pattern, glaze, grain); (3) edges and transitions (rim, bevel, seam, frame, corner). Reject large smooth surfaces and anything you would have to imagine. If the product is plain, choose its most informative real construction detail. Never borrow features from any other product."""

_CHOSEN = """
CHOSEN FEATURE (already decided; do not choose another)
Feature: {name}.
What is visibly there: {desc}
{crop_line}"""

_CROP_LINE = "IMAGE ORDER: the FIRST attached image is a tight reference crop of exactly this feature. Reproduce its geometry, finish and colour faithfully and render it far sharper and larger. The remaining images show the whole product for context only."

_FRAME = """
STEP 2 - FRAME THE SHOT (this is a macro, NOT a product portrait)
- Macro look, roughly 100 mm lens equivalent, camera close to the feature, the same viewpoint family as the references (a slight three-quarter angle is fine), natural orientation, no wide-angle distortion.
- The COMPLETE feature, from where it starts to where it ends, sits fully inside the frame with a clear margin of 6-10 percent on every side. Nothing important touches or crosses the edge.
- The feature occupies about 60-75 percent of the frame, centred with natural balance. Real adjacent geometry (neck, shoulder, mounting point, neighbouring surface) fills the rest and falls away softly.
- Do NOT show the long body of the product. Plain, unfeatured body surface may fill no more than about one sixth of the frame. No empty band of backdrop above the subject. Never a full-product view or a half-product portrait.

STEP 3 - PHOTOGRAPHIC QUALITY
- The whole selected feature is crisp (focus-stacked look), with real micro-texture and clean defined edges. Only distant context may soften.
- Large soft key light plus a thin rim or edge light so contours separate from the backdrop; controlled specular highlights. On black or dark products use grazing and rim light so form, texture, seams and edges read clearly, without lifting black to grey and without flat lighting.
- True colours and true finish. No waxy smoothing, no sharpening halos, no noise, no invented texture.
- Background: seamless clean WHITE studio backdrop, fading at most to very light grey. Never a mid-grey or dark backdrop. Only a subtle natural shadow. No props, surfaces, hands or scenery.

FIDELITY (overrides every style instruction above)
- Keep the exact geometry, proportions, colours, material, finish, number of parts and construction of the real product.
- Do not add, remove or redesign any part, pattern, seam, mechanism, logo or text.
- If a small detail is not clearly resolved in the references, render only what is visible, softly and truthfully; never fabricate it.

OUTPUT
One finished photograph, square 1:1. No text, labels, watermarks, arrows, circles, borders, collage or multi-panel layout."""


_CROP_ONLY = """You are a commercial product-detail photographer retouching and re-photographing ONE detail of a real product for an online store.

The attached image is a tight reference photograph of that detail: {name}. What is visibly there: {desc}

TASK
Re-photograph EXACTLY this view as a premium square 1:1 macro product-detail photograph, as if shot with a 100 mm macro lens on a professional studio set.

KEEP (do not change)
- The same camera angle, the same framing and the same scale. The feature stays LARGE, about 70-75 percent of the frame, fully visible with a margin of 8-12 percent on every side.
- The exact geometry, proportions, colours, finish, parts and construction shown. Do not add, remove or redesign anything.
- Where the product continues beyond the bottom or side edge of the reference, let it simply continue out of the frame. Do NOT zoom out, do NOT complete the rest of the product, do NOT add a long body or any other part.

IMPROVE
- Crisp focus across the whole feature, real micro-texture, clean defined edges. No waxy smoothing, no sharpening halos, no noise, no invented texture.
- Professional studio lighting: large soft key light plus a thin rim or edge light that separates the product from the backdrop. On black or dark products use grazing and rim light so seams, edges, texture and form are clearly readable, without turning black to grey.
- Replace the background with a seamless clean WHITE studio backdrop (at most a very light grey fade) and a subtle natural shadow. Remove dust, fingerprints and stray reflections from the backdrop. No props, surfaces, hands or scenery.
- If a tiny detail is not clearly resolved in the reference, keep it soft and truthful; never fabricate it.

OUTPUT
One finished photograph, square 1:1. No text, labels, watermarks, arrows, circles, borders, collage or multi-panel layout."""


def _line(value, limit):
    return " ".join(str(value or "").split())[:limit]


def build_closeup_prompt(note="", analysis=None, has_crop=False, crop_only=False):
    """Complete Close-up prompt. `analysis` is the validated dict from closeup_analysis."""
    if crop_only and analysis and analysis.get("feature_name"):
        prompt = _CROP_ONLY.format(
            name=_line(analysis["feature_name"], 80),
            desc=_line(analysis.get("feature_description"), 300) or "see the image",
        )
        cleaned = (note or "").strip()
        if cleaned:
            prompt += "\n\nSELLER NOTES (facts only; do not add marketing claims or text to the image): " + cleaned[:600]
        return prompt
    prompt = _HEAD
    if analysis and analysis.get("feature_name"):
        prompt += _CHOSEN.format(
            name=_line(analysis["feature_name"], 80),
            desc=_line(analysis.get("feature_description"), 300) or "see the references",
            crop_line=_CROP_LINE if has_crop else "",
        )
    else:
        prompt += _CHOOSE
    prompt += _FRAME
    cleaned = (note or "").strip()
    if cleaned:
        prompt += "\n\nSELLER NOTES (facts only; do not add marketing claims or text to the image): " + cleaned[:600]
    return prompt
