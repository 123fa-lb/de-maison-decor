# DEMAISON_LIFESTYLE_SCALE_V4
"""
Lifestyle category: real-world scale control (pure Python + two small Gemini TEXT requests).

PROBLEM
-------
Image models place a product in a room by "looking right", not by measuring. The product is
often drawn too large or too small next to chairs, cups, books or doors, and the old prompt
only appended a vague sentence ("keep believable proportions") that was buried in a long stack
of overlapping lifestyle instructions.

WHAT THIS MODULE DOES
---------------------
  1. parse_dimensions_cm()   seller dimensions -> centimetres (validated, unit aware).
  2. plan_lifestyle_scale()  ONE text-only Gemini request looks at the photos and returns the
                             product type, how it is placed (floor / tabletop / wall ...), a
                             typical size estimate (ONLY used when the seller gave no usable
                             dimensions) and which everyday anchor objects belong in such a scene.
                             Python then does the maths: product size vs. standard-size anchors
                             (seat height, mug, book, door ...) taken from a generic table.
  3. build_lifestyle_prompt() ONE authoritative prompt with explicit size ratios, camera
                             guidance and fidelity rules. It REPLACES the older stacked lifestyle
                             prompts for this category (they contradicted each other).
  4. verify_lifestyle_result() after generation, a second text request estimates the product's
                             apparent real size from the scene and checks product fidelity;
                             Python compares it with the expected size.

LIMITS: a diffusion/image model cannot be forced to a metric scale. This reduces scale errors
substantially (explicit ratios + a verified retry) but is not a guarantee. When the seller gives
no dimensions, the size is an ESTIMATE from the photo and is labelled as such in the logs.
Nothing here is specific to one product.
"""

import json
import re
from io import BytesIO

UNIT_TO_CM = {"cm": 1.0, "mm": 0.1, "in": 2.54, "m": 100.0, "ft": 30.48}
_UNIT_ALIASES = {"inch": "in", "inches": "in", '"': "in", "centimeter": "cm", "centimeters": "cm",
                 "centimetre": "cm", "centimetres": "cm", "millimeter": "mm", "millimeters": "mm",
                 "meter": "m", "meters": "m", "metre": "m", "metres": "m", "feet": "ft", "foot": "ft"}

# Generic everyday objects with typical real sizes in cm (height unless noted).
# Not product-specific; used as scale anchors.
REFERENCE_CM = {
    "armchair seat height": 43, "dining chair seat height": 45, "sofa seat height": 43,
    "sofa back height": 85, "bar stool seat height": 65, "coffee table height": 45,
    "side table height": 55, "dining table height": 75, "desk height": 75,
    "console table height": 80, "bedside table height": 60, "kitchen counter height": 90,
    "mattress top height": 55, "standard interior door height": 200, "door handle height": 100,
    "window sill height": 90, "floor lamp height": 150, "table lamp height": 50,
    "coffee mug height": 9.5, "tea cup height": 6.5, "drinking glass height": 14,
    "hardcover book height": 24, "wine bottle height": 30, "dinner plate diameter": 27,
    "closed laptop width": 33, "potted houseplant height": 60, "framed picture height": 40,
    "standing adult height": 170, "throw pillow width": 45,
}


def _num_text(value):
    raw = str(value or "").strip().replace(",", ".")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", raw):
        return None
    number = float(raw)
    return number if 0 < number <= 100000 else None


def parse_dimensions_cm(width, height, depth, unit="cm"):
    """-> {"width": cm|None, "height": cm|None, "depth": cm|None, "unit": str}. Never raises."""
    u = str(unit or "cm").strip().lower()
    u = _UNIT_ALIASES.get(u, u)
    if u not in UNIT_TO_CM:
        u = "cm"
    out = {"unit": u}
    for name, value in (("width", width), ("height", height), ("depth", depth)):
        number = _num_text(value)
        out[name] = round(number * UNIT_TO_CM[u], 2) if number is not None else None
    return out


def _fmt_cm(cm):
    return f"{cm:.0f} cm" if cm >= 10 else f"{cm:.1f} cm"


def _clean(text, limit):
    text = re.sub(r"[\x00-\x1f\x7f]", " ", str(text or ""))
    return re.sub(r"\s+", " ", text).strip()[:limit]


PLACEMENTS = ("floor_standing", "tabletop", "wall_mounted", "hanging", "handheld", "wearable", "other")

PLAN_PROMPT = """You are a prop stylist and product-scale expert. The attached photographs show ONE real product (a single SKU).

Tell me, based only on what is visible and on how products of this type are normally sized:
1. "product_type": short name.
2. "placement": exactly one of {placements} (how it is normally used/placed in a room).
3. "estimated_size_cm": {{"width": n, "height": n, "depth": n}} - your best estimate of this product's real overall size in centimetres (it is only used if the seller gave no dimensions).
4. "size_confidence": 0.0-1.0.
5. "settings": up to 3 short descriptions of natural, premium settings suited to THIS product.
6. "anchors": 2 to 4 everyday objects that would naturally appear in such a scene, chosen ONLY from this list: {anchors}.
7. "components": list of the product's visible parts (so none are invented or dropped), max 8 short items.

Return ONLY this JSON:
{{"product_type": "", "placement": "", "estimated_size_cm": {{"width": 0, "height": 0, "depth": 0}}, "size_confidence": 0.0, "settings": [""], "anchors": [""], "components": [""]}}"""


def parse_plan(text):
    """Validate the model reply. Returns a dict or None."""
    m = re.search(r"\{.*\}", str(text or ""), re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    placement = _clean(data.get("placement"), 30).lower().replace("-", "_").replace(" ", "_")
    if placement not in PLACEMENTS:
        placement = "other"
    est = {}
    raw_est = data.get("estimated_size_cm")
    for key in ("width", "height", "depth"):
        v = raw_est.get(key) if isinstance(raw_est, dict) else None
        if isinstance(v, (int, float)) and not isinstance(v, bool) and 0.3 <= v <= 1000:
            est[key] = float(v)
    try:
        conf = max(0.0, min(1.0, float(data.get("size_confidence", 0.0))))
    except (TypeError, ValueError):
        conf = 0.0
    anchors = [a for a in (data.get("anchors") or []) if isinstance(a, str) and a in REFERENCE_CM][:4]
    return {
        "product_type": _clean(data.get("product_type"), 60) or "product",
        "placement": placement,
        "estimated_cm": est,
        "size_confidence": conf,
        "settings": [_clean(s, 80) for s in (data.get("settings") or []) if isinstance(s, str)][:3],
        "anchors": anchors,
        "components": [_clean(c, 50) for c in (data.get("components") or []) if isinstance(c, str)][:8],
    }


def resolve_size(plan, dims):
    """
    Combine seller dimensions (authoritative) with the estimate (fallback).
    Returns {"cm": {"width","height","depth"} (None where unknown), "source": seller|estimated|unknown,
             "largest": cm or None}
    """
    est = (plan or {}).get("estimated_cm", {}) if plan else {}
    conf = (plan or {}).get("size_confidence", 0.0) if plan else 0.0
    seller = {k: dims.get(k) for k in ("width", "height", "depth")}
    have = {k: v for k, v in seller.items() if v}
    if have:
        sized = dict(seller)
        # Fill the missing axes from the estimate, scaled so the proportions stay consistent.
        ratios = [have[k] / est[k] for k in have if est.get(k)]
        factor = (sum(ratios) / len(ratios)) if ratios else None
        for k in sized:
            if not sized[k] and factor and est.get(k):
                sized[k] = round(est[k] * factor, 1)
        known = [v for v in sized.values() if v]
        return {"cm": sized, "source": "seller", "largest": max(known) if known else None}
    if est and conf >= 0.5:
        return {"cm": {k: est.get(k) for k in ("width", "height", "depth")}, "source": "estimated",
                "largest": max(est.values())}
    return {"cm": {"width": None, "height": None, "depth": None}, "source": "unknown", "largest": None}


def anchor_ratios(size, anchors):
    """Lines such as 'a coffee mug (9.5 cm) is 15 percent of the product's tallest dimension'."""
    lines = []
    largest = size.get("largest")
    if not largest:
        return lines
    for name in anchors:
        ref = REFERENCE_CM[name]
        ratio = largest / ref
        if ratio >= 1.0:
            lines.append(f"- {name} ({_fmt_cm(ref)}): the product's largest dimension is "
                         f"{ratio:.2f}x that, so the product must look {'larger than' if ratio > 1.15 else 'about as large as'} it.")
        else:
            lines.append(f"- {name} ({_fmt_cm(ref)}): it is {1 / ratio:.1f}x the product's largest "
                         f"dimension, so the product must look clearly SMALLER than it.")
    return lines


_CAMERA = {
    "floor_standing": "Eye-level camera about 1.1-1.3 m above the floor, standing 2.5-3.5 m away, 35-50 mm equivalent lens. The product's base clearly touches the floor with a soft contact shadow and the full product is visible.",
    "tabletop": "Camera slightly above the surface (about 25-40 cm above it), 80-120 cm from the product, 50 mm equivalent lens, no wide-angle distortion. The product rests on a real table, shelf or counter whose edge and legs are in frame so its size reads correctly.",
    "wall_mounted": "Camera square-on to the wall at about 1.4 m height, 2.5 m away, 35-50 mm lens. Show furniture beneath or beside it so the size reads correctly.",
    "hanging": "Camera at eye level 2-3 m away, 35-50 mm lens; show the ceiling/wall fixing and nearby furniture for scale.",
    "handheld": "Natural in-use scene with a hand or an everyday surface; 50-85 mm lens, no exaggerated closeness.",
    "wearable": "Natural lifestyle scene on a surface or a person, 50-85 mm lens; keep true size relative to a hand or body part.",
    "other": "Natural eye-level camera, 35-50 mm equivalent lens, 2-3 m away, product fully visible and grounded on a real surface.",
}


def build_lifestyle_prompt(note="", plan=None, dims=None):
    dims = dims or {}
    plan = plan or {}
    size = resolve_size(plan, dims) if (plan or any(dims.get(k) for k in ("width", "height", "depth"))) else \
        {"cm": {}, "source": "unknown", "largest": None}
    placement = plan.get("placement", "other")
    parts = ["""You are a commercial interior and product photographer. The attached photographs show ONE real product (a single SKU). They are the only source of truth for what it looks like.

TASK
Produce ONE premium, photorealistic, square 1:1 LIFESTYLE photograph of this exact product in a natural, tasteful real-world setting, as an editorial home or lifestyle magazine would shoot it. The product is the hero but must obey real-world physical scale."""]

    # ---- size block -------------------------------------------------------
    if size["source"] == "seller":
        c = size["cm"]
        txt = ", ".join(f"{n} {_fmt_cm(c[n])}" for n in ("width", "height", "depth") if c.get(n))
        parts.append(f"""
REAL PHYSICAL SIZE (seller-provided, authoritative)
The product measures: {txt}. Treat these as hard physical constraints. Never scale the product up or down to fill the frame; the room, furniture and props must be sized around it.""")
    elif size["source"] == "estimated":
        c = size["cm"]
        txt = ", ".join(f"{n} about {_fmt_cm(c[n])}" for n in ("width", "height", "depth") if c.get(n))
        parts.append(f"""
REAL PHYSICAL SIZE (estimated for this type of product; the seller gave no dimensions)
The product measures roughly: {txt}. Keep it at this everyday size relative to furniture and objects.""")
    else:
        parts.append("""
REAL PHYSICAL SIZE (unknown)
No dimensions are available. Show the product at the ordinary size products of its type have, and use only a few scale-sensitive comparison objects.""")

    ratios = anchor_ratios(size, plan.get("anchors", []))
    if ratios:
        parts.append("\nSCALE RELATIONSHIPS TO RESPECT\n" + "\n".join(ratios) + """
Use ordinary real-world sizes for every other object (chairs, tables, cups, books, plants, doors, people). If any object looks wrong next to the product, the product's size is wrong: fix the scene, never stretch the product.""")

    parts.append("\nCAMERA AND PERSPECTIVE\n" + _CAMERA.get(placement, _CAMERA["other"]) + """
One consistent perspective and horizon for the whole scene; the product sits on the same floor/surface plane as the furniture around it, with correct contact shadows, and light, colour temperature and reflections that match the room.""")

    setting = "; ".join(plan.get("settings", [])[:1])
    parts.append("\nSETTING\nChoose a setting that suits this product's real function" +
                 (f" (for example: {setting})" if setting else "") +
                 ". Calm, premium, uncluttered, warm natural light, realistic depth of field. No plain white studio background, no collage, no grid, no borders, no text, no labels, no watermarks.")

    comp = plan.get("components") or []
    parts.append("\nPRODUCT FIDELITY (overrides style)\nKeep the product's exact design, colours, material, finish, proportions, silhouette, number of parts and details" +
                 (f" (visible parts: {', '.join(comp)})" if comp else "") +
                 ". Do not add, remove, resize or redesign any part, pattern, logo or mechanism. Do not invent accessories that are part of the product. Props are separate objects and must not be mistaken for product parts.")
    parts.append("\nOUTPUT\nOne finished full-bleed photograph, square 1:1, product fully visible and clearly the hero.")
    cleaned = " ".join(str(note or "").split())[:600]
    if cleaned:
        parts.append("\nSELLER NOTES (facts only; do not add marketing claims or text to the image): " + cleaned)
    return "".join(parts)


def plan_lifestyle_scale(client, types, ref_parts, model, width="", height="", depth="", unit="cm", note=""):
    """
    ONE text-only Gemini request. Returns {"plan": dict|None, "dims": dict, "size": dict}.
    Never raises; on any failure plan is None and the prompt still uses seller dimensions.
    """
    dims = parse_dimensions_cm(width, height, depth, unit)
    plan = None
    try:
        prompt = PLAN_PROMPT.format(placements=", ".join(PLACEMENTS), anchors="; ".join(REFERENCE_CM))
        if note and note.strip():
            prompt += "\nSeller note (context only): " + _clean(note, 300)
        response = client.models.generate_content(
            model=model,
            contents=[types.Content(role="user",
                                    parts=list(ref_parts) + [types.Part.from_text(text=prompt)])],
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1),
        )
        plan = parse_plan(getattr(response, "text", None))
    except Exception as exc:
        print(f"[MAISON STUDIO] lifestyle scale analysis unavailable ({exc}); using seller dimensions only",
              flush=True)
    size = resolve_size(plan, dims)
    print(f"[MAISON STUDIO] lifestyle scale plan: type={(plan or {}).get('product_type')!r} "
          f"placement={(plan or {}).get('placement')!r} size_source={size['source']} "
          f"largest_cm={size['largest']} anchors={(plan or {}).get('anchors')}", flush=True)
    return {"plan": plan, "dims": dims, "size": size}


RESULT_PROMPT = """Images 1..{n} are REFERENCE photographs of one real product. The LAST image is a generated lifestyle photograph that must show that product at its true real-world scale.

1. Find the product in the lifestyle photo. Using ordinary sizes of the objects around it (chairs, tables, cups, books, plants, doors, people), estimate the product's LARGEST real dimension in centimetres as it appears in the scene: "apparent_largest_cm".
2. "scene_plausible": are the OTHER objects in the scene plausibly sized relative to each other (no giant cups, doll-sized chairs)?
3. "same_product": does the product match the references in design, colour, material and proportions?
4. "invented_parts": are there parts or components on the product that the references do not have?
5. "white_background": is the scene a plain white/empty studio background instead of a real setting?
{expected}
Return ONLY this JSON:
{{"apparent_largest_cm": 0, "scene_plausible": true, "same_product": true, "invented_parts": false, "white_background": false, "confidence": 0.0, "notes": "max 25 words"}}"""

SCALE_TOLERANCE = (0.65, 1.55)   # apparent / true size that is still acceptable ("meaningful" mismatch only)
MIN_ACTION_CONFIDENCE = 0.70     # below this the reviewer is too unsure to justify a paid retry


def evaluate_result(data, size):
    """
    Pure function: reviewer answers + expected size -> verdict dict (unit-testable).

    POLICY (V4): a corrected second image is requested ONLY for a meaningful SCALE problem:
      * the product's apparent size is far from its true size, judged only when the SELLER gave
        dimensions (an estimated size compared with an estimated size is noise), or
      * surrounding objects are clearly out of proportion to each other.
    Fidelity observations (different product, invented parts, white background) are recorded as
    `advisory` for the logs but never trigger a paid retry.
    """
    problems, advisory = [], []
    ratio = None
    try:
        conf = max(0.0, min(1.0, float(data.get("confidence", 0.5))))
    except (TypeError, ValueError):
        conf = 0.5
    apparent = data.get("apparent_largest_cm")
    if (size.get("source") == "seller" and size.get("largest") and isinstance(apparent, (int, float))
            and not isinstance(apparent, bool) and apparent > 0):
        ratio = float(apparent) / float(size["largest"])
        lo, hi = SCALE_TOLERANCE
        if ratio > hi:
            problems.append(f"the product looks about {ratio:.1f}x too large for the room (it appears ~{apparent:.0f} cm "
                            f"but is {_fmt_cm(size['largest'])}); shrink it relative to the furniture or enlarge the surroundings")
        elif ratio < lo:
            problems.append(f"the product looks about {1 / ratio:.1f}x too small (it appears ~{apparent:.0f} cm "
                            f"but is {_fmt_cm(size['largest'])}); make it larger relative to the furniture or shrink the surroundings")
    if data.get("scene_plausible") is False:
        problems.append("some surrounding objects have unrealistic sizes relative to the product")
    for key, text in (("same_product", "product may differ from the reference"),
                      ("invented_parts", "product may have parts not in the reference"),
                      ("white_background", "plain white background")):
        if (key == "same_product" and data.get(key) is False) or (key != "same_product" and data.get(key) is True):
            advisory.append(text)
    passed = not problems or conf < MIN_ACTION_CONFIDENCE
    correction = ""
    if problems:
        correction = ("CORRECTION FROM QUALITY REVIEW OF THE PREVIOUS ATTEMPT: " + "; ".join(problems) +
                      ". Change ONLY the apparent size relationship between the product and its surroundings. "
                      "Keep the product's shape, colour, material, design and proportions exactly as in the "
                      "reference photographs, and keep the same premium photographic look and setting.")
    return {"passed": passed, "ratio": None if ratio is None else round(ratio, 2),
            "issues": problems, "advisory": advisory, "correction": correction, "confidence": conf}


def verify_lifestyle_result(client, types, model, ref_parts, generated_image, size):
    """Text-only Gemini request + pure evaluation. Never raises."""
    try:
        buf = BytesIO()
        im = generated_image.convert("RGB")
        im.thumbnail((1280, 1280))
        im.save(buf, "JPEG", quality=90)
        expected = ""
        if size.get("largest"):
            expected = (f"(For information only: the true size is about {_fmt_cm(size['largest'])}. "
                        "Do NOT copy this number; estimate from the picture alone.)\n")
        parts = list(ref_parts)[:3] + [types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg"),
                                       types.Part.from_text(text=RESULT_PROMPT.format(
                                           n=len(list(ref_parts)[:3]), expected=expected))]
        response = client.models.generate_content(
            model=model, contents=[types.Content(role="user", parts=parts)],
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0),
        )
        m = re.search(r"\{.*\}", str(getattr(response, "text", "") or ""), re.S)
        data = json.loads(m.group(0)) if m else None
        if not isinstance(data, dict):
            return {"passed": True, "issues": [], "correction": "", "ratio": None, "checked": False}
        verdict = evaluate_result(data, size)
        verdict["checked"] = True
        return verdict
    except Exception as exc:
        print(f"[MAISON STUDIO] lifestyle result check unavailable ({exc})", flush=True)
        return {"passed": True, "issues": [], "correction": "", "ratio": None, "checked": False}
