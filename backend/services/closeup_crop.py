# DEMAISON_CLOSEUP_V40_FINALIZE
"""
Close-up post-processing.

What changed
------------
The previous version of this module chose a crop window by edge density and then
cut the Gemini image down to ~70-76% of its size. That is exactly what removed the
important feature (edge density is highest on silhouettes, text and noise, not on
the most meaningful feature). Framing is now decided ONLY by the Gemini prompt.

This module never crops and never discards pixels:

  * finalize_closeup(): guarantees a square image by PADDING (edge replication) if
    the model returned a non-square image. Already-square images pass through
    untouched at native resolution.
  * assess_closeup(): fast, local, advisory quality heuristics. It NEVER changes
    the image and NEVER triggers another API request. Flags are for logging and
    for the X-Closeup-QA response header only.

Dependencies: Pillow and NumPy (both already used by the project).
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageOps

_TILE = 32
_FG_DISTANCE = 30.0  # RGB distance from background colour to count as subject


def _to_rgb(image: Image.Image) -> Image.Image:
    return ImageOps.exif_transpose(image).convert("RGB")


def _border_color(arr: np.ndarray) -> np.ndarray:
    h, w = arr.shape[:2]
    t = max(2, int(min(h, w) * 0.02))
    ring = np.concatenate(
        [
            arr[:t].reshape(-1, 3),
            arr[-t:].reshape(-1, 3),
            arr[:, :t].reshape(-1, 3),
            arr[:, -t:].reshape(-1, 3),
        ]
    )
    return np.median(ring, axis=0)


def finalize_closeup(image: Image.Image):
    """Return (square_rgb_image, report). Never crops; pads only when not square."""
    im = _to_rgb(image)
    w, h = im.size
    report = {"action": "none", "input_size": [w, h], "output_size": [w, h]}

    if w == h:
        return im, report

    side = max(w, h)
    left = (side - w) // 2
    right = side - w - left
    top = (side - h) // 2
    bottom = side - h - top

    arr = np.asarray(im)
    padded = np.pad(arr, ((top, bottom), (left, right), (0, 0)), mode="edge")
    out = Image.fromarray(padded, "RGB")
    report.update(action="padded_to_square", output_size=[side, side])
    return out, report


def _tile_stat(values: np.ndarray, fn) -> np.ndarray:
    h, w = values.shape
    th, tw = h // _TILE, w // _TILE
    if th == 0 or tw == 0:
        return np.zeros((0, 0), dtype=np.float32)
    v = values[: th * _TILE, : tw * _TILE].reshape(th, _TILE, tw, _TILE)
    return fn(v)


def assess_closeup(image: Image.Image, analysis_size: int = 768) -> dict:
    """Advisory heuristics only. Thresholds are conservative starting values."""
    im = _to_rgb(image)
    w, h = im.size
    scale = analysis_size / float(max(w, h))
    if scale < 1.0:
        im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)

    arr = np.asarray(im, dtype=np.float32)
    gray = arr @ np.array([0.299, 0.587, 0.114], dtype=np.float32)

    bg = _border_color(arr)
    # The prompt asks for a light studio backdrop. If most of the frame border is
    # dark, the subject is running off the edges (normal for a macro) and the
    # border median would wrongly be the product colour: use the light pixels instead.
    if float(bg @ np.array([0.299, 0.587, 0.114])) < 120.0:
        light = gray > 170.0
        if float(light.mean()) >= 0.03:
            bg = np.median(arr[light], axis=0)
        else:
            bg = None  # no visible backdrop: the whole frame is subject
    if bg is None:
        fg = np.ones(gray.shape, dtype=bool)
    else:
        dist = np.sqrt(((arr - bg) ** 2).sum(axis=2))
        fg = dist > _FG_DISTANCE
    fg_fraction = float(fg.mean())

    # Laplacian (edge-replicated so it matches the image shape).
    g = np.pad(gray, 1, mode="edge")
    lap = 4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]

    fg_tiles = _tile_stat(fg.astype(np.float32), lambda v: v.mean(axis=(1, 3))) > 0.5
    lap_var = _tile_stat(lap, lambda v: v.var(axis=(1, 3)))
    gray_std = _tile_stat(gray, lambda v: v.std(axis=(1, 3)))

    if fg_tiles.size and fg_tiles.any():
        sharp_p90 = float(np.percentile(lap_var[fg_tiles], 90))
        plain_ratio = float((gray_std[fg_tiles] < 3.0).mean())
    else:
        sharp_p90 = float(lap.var())
        plain_ratio = 1.0

    ring = max(2, int(min(arr.shape[:2]) * 0.02))
    sides = {
        "top": float(fg[:ring].mean()),
        "bottom": float(fg[-ring:].mean()),
        "left": float(fg[:, :ring].mean()),
        "right": float(fg[:, -ring:].mean()),
    }
    touching = [name for name, frac in sides.items() if frac > 0.35]

    # Subject margins (empty backdrop bands) and backdrop brightness.
    rows = fg.mean(axis=1) > 0.02
    cols = fg.mean(axis=0) > 0.02
    if rows.any() and cols.any():
        ys, xs = np.where(rows)[0], np.where(cols)[0]
        hh, ww = fg.shape
        margins = {
            "top": float(ys.min()) / hh,
            "bottom": float(hh - 1 - ys.max()) / hh,
            "left": float(xs.min()) / ww,
            "right": float(ww - 1 - xs.max()) / ww,
        }
    else:
        margins = {"top": 0.0, "bottom": 0.0, "left": 0.0, "right": 0.0}
    backdrop = ~fg
    backdrop_luma = (
        float(np.median(gray[backdrop])) if backdrop.sum() > 0.03 * backdrop.size else None
    )

    flags = []
    if sharp_p90 < 25.0:
        flags.append("low_sharpness")
    if plain_ratio > 0.65:
        flags.append("mostly_plain_surface")
    if fg_fraction < 0.40:
        flags.append("weak_macro_framing")
    if max(margins.values()) > 0.22:
        flags.append("large_empty_margin")
    if backdrop_luma is not None and backdrop_luma < 215.0:
        flags.append("backdrop_not_white")
    # A macro detail normally runs off at least one edge; a floating, fully
    # enclosed subject with empty margins usually means a whole-product portrait.
    if not touching and fg_fraction < 0.55:
        flags.append("full_product_view_suspected")

    return {
        "sharpness_p90": round(sharp_p90, 1),
        "plain_surface_ratio": round(plain_ratio, 3),
        "subject_fraction": round(fg_fraction, 3),
        "edges_touched": touching,
        "max_empty_margin": round(max(margins.values()), 3),
        "backdrop_luma": None if backdrop_luma is None else round(backdrop_luma, 1),
        "flags": flags,
    }


def crop_closeup(image: Image.Image) -> Image.Image:
    """
    Backward-compatible name. It NO LONGER CROPS. Kept so any stray import of the
    old helper keeps working and cannot cut off the feature.
    """
    return finalize_closeup(image)[0]
