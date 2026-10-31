# DEMAISON_CLOSEUP_V41_ANALYSIS
"""
Step 1 of the Close-up pipeline: choose the feature BEFORE generating the image.

One small TEXT-ONLY Gemini request (no image output, no retry) reads the seller's
reference photos and returns the most distinctive real feature plus a bounding box.
The box is turned into a generous, complete, square reference crop that is sent to
the image request as the first reference, so the image model is SHOWN the framing
instead of being asked to guess it.

Safety properties
  * Optional: DEMAISON_CLOSEUP_ANALYSIS=0 disables it (single-request behaviour).
  * Any failure (network, bad JSON, unusable box) returns None and the caller
    falls back to the single image request. There is never a second attempt.
  * Model output is treated as DATA: lengths are limited and control characters
    stripped before it is placed in the image prompt.
Dependencies: Pillow only (google-genai objects are passed in by the caller).
"""

import json
import re

from PIL import Image

ANALYSIS_PROMPT = """You are a product-photography art director. The attached images (numbered 0, 1, 2 ... in the order supplied) show ONE real product from different views.

Choose the single most distinctive REAL feature that would make the best premium macro detail photograph for an online store.
Rank candidates: (1) functional hardware or construction such as closure, lid, cap, hinge, handle, spout, latch, clasp, knob, joint; (2) crafted surface such as carving, engraving, embossing, inlay, weave, stitching, cutwork, pattern; (3) edges and transitions such as rim, bevel, seam, frame, corner, base.
Never choose a large smooth uniform surface, the whole product, or anything not clearly visible in the images. If the product is plain, choose the most informative real construction detail.

Pick the image where that feature is clearest and largest, and give a bounding box for it:
- "box_2d" = [ymin, xmin, ymax, xmax], integers normalised to 0-1000 on that image.
- The box must contain the COMPLETE feature including the part it attaches to, with nothing cut off, but must not include large unrelated areas (such as a long plain body).

Reply with ONLY one JSON object, no markdown, in exactly this form:
{"product_type": "...", "feature_name": "3-6 words", "feature_description": "max 30 words describing only what is visibly there: shapes, finish, colour, parts", "image_index": 0, "box_2d": [0, 0, 0, 0], "confidence": 0.0}"""


def _clean(text, limit):
    text = re.sub(r"[\x00-\x1f\x7f]", " ", str(text or ""))
    return re.sub(r"\s+", " ", text).strip()[:limit]


def parse_analysis(text, n_images):
    """Parse and validate the model reply. Returns a dict or None."""
    if not text:
        return None
    match = re.search(r"\{.*\}", str(text), re.S)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        box = [float(v) for v in data["box_2d"]]
        if len(box) != 4:
            return None
        ymin, xmin, ymax, xmax = [min(1000.0, max(0.0, v)) for v in box]
        if ymax - ymin < 40 or xmax - xmin < 40:  # < 4% of the image: unusable
            return None
        idx = int(data.get("image_index", 0))
        if not 0 <= idx < max(1, n_images):
            idx = 0
        name = _clean(data.get("feature_name"), 80)
        if not name:
            return None
        try:
            conf = max(0.0, min(1.0, float(data.get("confidence", 0.5))))
        except (TypeError, ValueError):
            conf = 0.5
        return {
            "product_type": _clean(data.get("product_type"), 60),
            "feature_name": name,
            "feature_description": _clean(data.get("feature_description"), 300),
            "image_index": idx,
            "box_2d": [ymin, xmin, ymax, xmax],
            "confidence": conf,
        }
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def feature_crop(images, analysis, out_min=1024, out_max=2048):
    """
    Build a square reference crop that fully contains the feature box with generous
    context (feature ~75 percent of the crop). Returns (PIL.Image or None, info).
    None means "no useful crop" (the box is nearly the whole image); the caller
    then sends only the full reference photos.
    """
    if not images or not analysis:
        return None, {"reason": "no_input"}
    im = images[min(analysis["image_index"], len(images) - 1)]
    w, h = im.size
    ymin, xmin, ymax, xmax = analysis["box_2d"]
    x0, x1 = xmin / 1000.0 * w, xmax / 1000.0 * w
    y0, y1 = ymin / 1000.0 * h, ymax / 1000.0 * h
    bw, bh = x1 - x0, y1 - y0

    if (bw * bh) / float(w * h) > 0.70:
        return None, {"reason": "box_covers_most_of_image"}

    # Square window around the feature. It may be larger than the photo (wide or tall
    # features such as a long rim): the part outside the photo is filled with the
    # photo's own backdrop colour, so the feature is never cut off.
    side = max(bw, bh) * 1.30
    side = max(side, 0.22 * min(w, h))
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    left = cx - side / 2.0
    top = cy - side / 2.0
    if side <= w:
        left = min(max(left, 0.0), w - side)
    if side <= h:
        top = min(max(top, 0.0), h - side)

    S = int(round(side))
    l0, t0 = int(round(left)), int(round(top))
    patch = max(4, int(min(w, h) * 0.05))
    corners = [im.crop((0, 0, patch, patch)), im.crop((w - patch, 0, w, patch)),
               im.crop((0, h - patch, patch, h)), im.crop((w - patch, h - patch, w, h))]
    px = [p for c in corners for p in c.getdata()]
    px.sort(key=lambda v: sum(v))
    backdrop = px[len(px) // 2]
    canvas = Image.new("RGB", (S, S), backdrop)
    sx0, sy0 = max(l0, 0), max(t0, 0)
    sx1, sy1 = min(l0 + S, w), min(t0 + S, h)
    canvas.paste(im.crop((sx0, sy0, sx1, sy1)), (sx0 - l0, sy0 - t0))
    crop = canvas
    if crop.width < out_min:
        crop = crop.resize((out_min, out_min), Image.LANCZOS)
    elif crop.width > out_max:
        crop = crop.resize((out_max, out_max), Image.LANCZOS)
    return crop, {
        "source_image": analysis["image_index"],
        "crop_box": [l0, t0, l0 + S, t0 + S],
        "feature_share_of_crop": round(max(bw, bh) / side, 2),
    }


def analyze_feature(client, types, ref_parts, model, note=""):
    """ONE text-only request. Returns a validated dict or None. Never raises, never retries."""
    try:
        prompt = ANALYSIS_PROMPT
        if note and note.strip():
            prompt += "\nSeller note (context only): " + _clean(note, 300)
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Content(
                    role="user",
                    parts=list(ref_parts) + [types.Part.from_text(text=prompt)],
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        usage = getattr(response, "usage_metadata", None)
        result = parse_analysis(getattr(response, "text", None), len(ref_parts))
        print(
            "[MAISON STUDIO] closeup analysis: "
            f"tokens_in={getattr(usage, 'prompt_token_count', '?')} "
            f"tokens_out={getattr(usage, 'candidates_token_count', '?')} result={result}",
            flush=True,
        )
        return result
    except Exception as exc:  # network, quota, model-name, SDK differences...
        print(f"[MAISON STUDIO] closeup analysis unavailable ({exc}); using single-request mode", flush=True)
        return None
