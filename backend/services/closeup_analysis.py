# DEMAISON_CLOSEUP_V44_ANALYSIS
"""
Step 1 of the Close-up pipeline: choose the feature BEFORE generating the image.

V43 changes (feature selection only; framing/prompt/generation code is untouched)
-------------------------------------------------------------------------------
Before: ONE guess from Gemini was trusted blindly (and ranked "hardware" above signature
features such as a map, dial or pattern), so the close-up could land on a clasp or a plain
panel instead of what makes the product recognisable.

Now:
  1. Gemini proposes up to 3 DIFFERENT candidate features with boxes and a distinctiveness
     score, led by the feature a shopper would recognise this product by.
  2. Python scores every box on the real pixels (detail density relative to the whole
     product, size, not-too-plain, not-the-whole-product) and combines it with Gemini's score.
  3. The best candidates are cropped and an independent Gemini request checks that the crop
     really shows the named feature, completely, and that it is distinctive. The first
     candidate that passes is used.
  4. If nothing passes, the function returns None and the caller falls back to the single
     request mode (the model chooses from the full photos). It never raises and never loops.

Cost: still one analysis request plus at most MAX_VERIFY small text-only verification
requests, all on the cheap text model. The paid image request is unchanged.
Dependencies: Pillow, NumPy (google-genai objects are passed in by the caller).
"""

import json
import re
from io import BytesIO

import numpy as np
from PIL import Image

MAX_CANDIDATES = 3
MAX_VERIFY = 2
MIN_VERIFY_CONFIDENCE = 0.6

ANALYSIS_PROMPT = """You are a product-photography art director. The attached images (numbered 0, 1, 2 ... in the order supplied) show ONE real product from different views.

Choose up to 3 DIFFERENT real features that could each make a premium macro detail photograph for an online store, best first.
Rank by how DISTINCTIVE the feature is for THIS product: (1) the signature feature a shopper would recognise this product by (a pattern, engraving, map, dial, inlay, weave, stitching, cutwork, ornament, unusual structure); (2) functional hardware or construction (closure, lid, cap, hinge, handle, spout, latch, clasp, knob, joint); (3) edges and transitions (rim, bevel, seam, frame, corner, base).
Never choose a large smooth uniform surface, the whole product, or anything not clearly visible and sharp in the images. Candidates must be physically different parts, not the same part twice. If the product is plain, choose its most informative real construction details.

For each candidate pick the image where the feature is clearest and largest and give a bounding box:
- "box_2d" = [ymin, xmin, ymax, xmax], integers normalised to 0-1000 on that image.
- The box must contain the COMPLETE feature including the part it attaches to, with nothing cut off, and must not include large unrelated areas.
- "distinctiveness" = 0.0-1.0: how recognisable and information-rich this feature is. "confidence" = 0.0-1.0: how sure you are the box is correct.

Reply with ONLY one JSON object, no markdown, in exactly this form:
{"product_type": "...", "candidates": [{"feature_name": "3-6 words", "feature_description": "max 30 words describing only what is visibly there: shapes, finish, colour, parts", "image_index": 0, "box_2d": [0, 0, 0, 0], "distinctiveness": 0.0, "confidence": 0.0}]}"""

VERIFY_PROMPT = """The attached image is a crop of a product photograph, prepared as the reference for a macro detail photo of this feature: "{name}" ({desc}).

Judge the crop honestly:
- "shows_feature": does the crop clearly show that named feature?
- "complete": is the whole feature inside the crop, not cut off by the edge?
- "distinctive": is it a visually distinctive, information-rich detail (pattern, ornament, mechanism, texture, structure), NOT a plain smooth surface, a blurry area, background, or just the generic body of the product?
- "sharp_enough": is it resolved well enough to be re-photographed without inventing detail?

Reply with ONLY this JSON:
{{"shows_feature": true, "complete": true, "distinctive": true, "sharp_enough": true, "confidence": 0.0, "issue": "max 15 words or empty"}}"""

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


def parse_candidates(text, n_images):
    """Parse the model reply into a list of validated candidate dicts (best-first)."""
    if not text:
        return []
    match = re.search(r"\{.*\}", str(text), re.S)
    if not match:
        return []
    try:
        data = json.loads(match.group(0))
    except (json.JSONDecodeError, TypeError, ValueError):
        return []
    if not isinstance(data, dict):
        return []
    raw = data.get("candidates")
    if not isinstance(raw, list):          # tolerate the legacy single-feature reply
        raw = [data] if "box_2d" in data else []
    out = []
    for item in raw[:MAX_CANDIDATES]:
        if not isinstance(item, dict):
            continue
        item = dict(item)
        item.setdefault("product_type", data.get("product_type", ""))
        parsed = parse_analysis(json.dumps(item), n_images)
        if parsed is None:
            continue
        for key in ("distinctiveness",):
            try:
                parsed[key] = max(0.0, min(1.0, float(item.get(key, parsed["confidence"]))))
            except (TypeError, ValueError):
                parsed[key] = parsed["confidence"]
        if not parsed.get("product_type"):
            parsed["product_type"] = _clean(data.get("product_type"), 60)
        out.append(parsed)
    return out


def _decode_images(ref_parts):
    """PIL images from the already-built google-genai image parts (JPEG bytes)."""
    images = []
    for part in ref_parts:
        blob = getattr(getattr(part, "inline_data", None), "data", None) or getattr(part, "data", None)
        if not blob:
            continue
        try:
            images.append(Image.open(BytesIO(blob)).convert("RGB"))
        except Exception:
            continue
    return images


def _detail(gray):
    """Edge/texture richness: variance of a Laplacian plus gradient energy."""
    if gray.shape[0] < 8 or gray.shape[1] < 8:
        return 0.0
    g = gray.astype(np.float32)
    lap = (4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:])
    gx = np.abs(np.diff(g, axis=1)).mean()
    gy = np.abs(np.diff(g, axis=0)).mean()
    return float(lap.var() ** 0.5 + 2.0 * (gx + gy))


def score_candidate(images, cand):
    """
    Pixel-based sanity score in 0..1 for one candidate box. Pure Python/NumPy, offline.
    Returns (score, metrics). score 0 means "reject".
    """
    if not images:
        return 0.5, {"note": "no_pixels"}
    im = images[min(cand["image_index"], len(images) - 1)]
    w, h = im.size
    ymin, xmin, ymax, xmax = cand["box_2d"]
    x0, x1 = int(xmin / 1000.0 * w), int(xmax / 1000.0 * w)
    y0, y1 = int(ymin / 1000.0 * h), int(ymax / 1000.0 * h)
    if x1 - x0 < 16 or y1 - y0 < 16:
        return 0.0, {"reason": "box_too_small"}
    gray = np.asarray(im.convert("L"))
    share = ((x1 - x0) * (y1 - y0)) / float(w * h)
    if share > 0.70:
        return 0.0, {"reason": "box_is_whole_product", "share": round(share, 2)}
    # Compare the candidate with the typical busy region of the whole photo, using the
    # most detailed 40 percent of tiles as the baseline (backdrops would otherwise
    # make everything look "detailed").
    tile = 48
    tiles = []
    for ty in range(0, max(1, h - tile), tile):
        for tx in range(0, max(1, w - tile), tile):
            tiles.append(_detail(gray[ty:ty + tile, tx:tx + tile]))
    tiles.sort(reverse=True)
    baseline = float(np.mean(tiles[: max(1, int(len(tiles) * 0.4))])) if tiles else 1.0
    region = _detail(gray[y0:y1, x0:x1])
    density = region / max(baseline, 1e-3)
    contrast = float(gray[y0:y1, x0:x1].std())
    score = min(1.0, density / 1.2)
    if contrast < 8.0:
        score *= 0.3                       # nearly uniform area
    if share < 0.01:
        score *= 0.5
    if share > 0.35:
        score *= 0.6                       # nearly the whole product: not a "detail"
    return round(score, 3), {"detail_density": round(density, 2), "contrast": round(contrast, 1),
                             "share": round(share, 3)}


def rank_candidates(images, cands):
    """Combine Gemini's distinctiveness/confidence with the pixel score. Best first."""
    ranked = []
    for c in cands:
        px, metrics = score_candidate(images, c)
        if px <= 0.0:
            continue
        combined = 0.45 * c.get("distinctiveness", 0.5) + 0.20 * c.get("confidence", 0.5) + 0.35 * px
        c = dict(c)
        c["pixel_score"], c["metrics"], c["combined"] = px, metrics, round(combined, 3)
        ranked.append(c)
    ranked.sort(key=lambda c: c["combined"], reverse=True)
    return ranked


def verify_candidate(client, types, images, cand, model):
    """Independent text-only check on the actual reference crop. Returns (ok, info)."""
    crop, info = feature_crop(images, cand)
    if crop is None:
        return True, {"note": "no_crop_needed_" + str(info.get("reason", ""))}
    buf = BytesIO()
    crop.thumbnail((1024, 1024))
    crop.save(buf, "JPEG", quality=90)
    prompt = VERIFY_PROMPT.format(name=_clean(cand["feature_name"], 80),
                                  desc=_clean(cand.get("feature_description"), 200) or "see image")
    response = client.models.generate_content(
        model=model,
        contents=[types.Content(role="user", parts=[
            types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg"),
            types.Part.from_text(text=prompt)])],
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0),
    )
    m = re.search(r"\{.*\}", str(getattr(response, "text", "") or ""), re.S)
    if not m:
        return False, {"reason": "unparseable"}
    try:
        data = json.loads(m.group(0))
        conf = max(0.0, min(1.0, float(data.get("confidence", 0))))
    except (TypeError, ValueError, json.JSONDecodeError):
        return False, {"reason": "unparseable"}
    ok = (data.get("shows_feature") is True and data.get("complete") is True
          and data.get("distinctive") is True and data.get("sharp_enough") is not False
          and conf >= MIN_VERIFY_CONFIDENCE)
    return ok, {"confidence": conf, "issue": _clean(data.get("issue"), 100)}


def analyze_feature(client, types, ref_parts, model, note=""):
    """
    Returns a validated dict (same keys as before, plus 'verified' and 'considered') or None.
    Never raises. At most 1 analysis + MAX_VERIFY verification text requests.
    """
    try:
        prompt = ANALYSIS_PROMPT
        if note and note.strip():
            prompt += "\nSeller note (context only): " + _clean(note, 300)
        response = client.models.generate_content(
            model=model,
            contents=[types.Content(role="user",
                                    parts=list(ref_parts) + [types.Part.from_text(text=prompt)])],
            config=types.GenerateContentConfig(response_mime_type="application/json",
                                               temperature=0.2),
        )
        usage = getattr(response, "usage_metadata", None)
        cands = parse_candidates(getattr(response, "text", None), len(ref_parts))
        images = _decode_images(ref_parts)
        ranked = rank_candidates(images, cands)
        print("[MAISON STUDIO] closeup analysis: "
              f"tokens_in={getattr(usage, 'prompt_token_count', '?')} "
              f"tokens_out={getattr(usage, 'candidates_token_count', '?')} "
              f"candidates={[(c['feature_name'], c['combined']) for c in ranked]}", flush=True)
        if not ranked:
            return None
        for cand in ranked[:MAX_VERIFY]:
            try:
                ok, info = verify_candidate(client, types, images, cand, model)
            except Exception as exc:
                ok, info = False, {"reason": f"verify_failed: {exc}"}
            print(f"[MAISON STUDIO] closeup verify {cand['feature_name']!r}: ok={ok} {info}", flush=True)
            if ok:
                cand["verified"] = True
                cand["considered"] = [c["feature_name"] for c in ranked]
                return cand
        # Nothing passed independent verification: do NOT force a doubtful crop.
        print("[MAISON STUDIO] closeup: no candidate passed verification; "
              "using single-request mode", flush=True)
        return None
    except Exception as exc:  # network, quota, model-name, SDK differences...
        print(f"[MAISON STUDIO] closeup analysis unavailable ({exc}); using single-request mode",
              flush=True)
        return None


# --------------------------------------------------------------------------- #
# Result check: did the generated close-up stay faithful to the real product?
# --------------------------------------------------------------------------- #
RESULT_PROMPT = """Image 1 is the REFERENCE: a real product photograph (or a crop of it) showing the feature "{name}". Image 2 is a newly generated macro close-up that must show the SAME real feature of the SAME product.

Judge strictly:
- "same_feature": does Image 2 show the same physical feature as Image 1 (same pattern/ornament/structure, same material, finish and colour)?
- "invented_details": does Image 2 add or change patterns, text, parts, engravings or mechanisms that are not in Image 1?
- "complete": is the main feature fully inside the frame rather than cut off?
- "sharp": is the feature crisp and realistic (not blurry, smeared or plasticky)?

Reply with ONLY this JSON:
{{"same_feature": true, "invented_details": false, "complete": true, "sharp": true, "confidence": 0.0, "issues": "max 20 words or empty"}}"""


def verify_closeup_result(client, types, model, reference_image, generated_image, analysis):
    """
    Returns {"passed": bool, "issues": str, "correction": str}. Never raises.
    `reference_image`/`generated_image` are PIL images. Text-only Gemini request.
    """
    try:
        def part(im):
            buf = BytesIO()
            im = im.convert("RGB")
            im.thumbnail((1280, 1280))
            im.save(buf, "JPEG", quality=90)
            return types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg")
        name = _clean((analysis or {}).get("feature_name"), 80) or "the most distinctive feature"
        response = client.models.generate_content(
            model=model,
            contents=[types.Content(role="user", parts=[
                part(reference_image), part(generated_image),
                types.Part.from_text(text=RESULT_PROMPT.format(name=name))])],
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0),
        )
        m = re.search(r"\{.*\}", str(getattr(response, "text", "") or ""), re.S)
        data = json.loads(m.group(0)) if m else None
        if not isinstance(data, dict):
            return {"passed": True, "issues": [], "correction": "", "checked": False}
        conf = max(0.0, min(1.0, float(data.get("confidence", 0.5))))
        problems, advisory = [], []
        if data.get("same_feature") is False:
            problems.append("it is not the same feature as the reference")
        if data.get("invented_details") is True:
            problems.append("it contains patterns/parts/text that are not in the reference")
        if data.get("complete") is False:
            advisory.append("the feature is cut off by the frame")
        if data.get("sharp") is False:
            advisory.append("the feature is not very sharp")
        # Only a wrong feature or invented detail justifies a paid retry (and only if the
        # reviewer is reasonably sure); framing/sharpness notes are logged, not retried.
        passed = not problems or conf < 0.7
        correction = ""
        if problems:
            correction = ("CORRECTION FROM QUALITY REVIEW OF THE PREVIOUS ATTEMPT: "
                          + "; ".join(problems) + ". Reproduce ONLY what is visible in the first "
                          "reference image, keep the entire feature inside the frame with a margin, "
                          "and render it crisp. Do not add anything.")
        return {"passed": passed, "issues": problems, "advisory": advisory,
                "correction": correction, "confidence": conf, "checked": True}
    except Exception as exc:
        print(f"[MAISON STUDIO] closeup result check unavailable ({exc})", flush=True)
        return {"passed": True, "issues": [], "correction": "", "checked": False}
