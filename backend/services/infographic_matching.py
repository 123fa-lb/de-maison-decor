
"""Generic, coordinate-consistent infographic detail selection.

No product-specific labels, categories or feature names.
Crops and connector endpoints always originate from the same image.
"""
from PIL import Image, ImageFilter, ImageStat


def find_detail_regions(image, count=3):
    """Return distinct visually detailed source regions.

    This is image-detail detection, not semantic feature recognition.
    """
    src = image.convert("RGB")
    w, h = src.size
    if min(w, h) < 120:
        return []

    side = max(48, int(min(w, h) * 0.19))
    side = min(side, w, h)

    candidates = []

    for fy in (0.22, 0.38, 0.54, 0.70, 0.82):
        for fx in (0.20, 0.35, 0.50, 0.65, 0.80):
            cx = int(w * fx)
            cy = int(h * fy)

            x0 = max(0, min(w - side, cx - side // 2))
            y0 = max(0, min(h - side, cy - side // 2))
            box = (x0, y0, x0 + side, y0 + side)

            patch = src.crop(box).resize((128, 128))
            gray = patch.convert("L")

            contrast = ImageStat.Stat(gray).stddev[0]
            edges = ImageStat.Stat(
                gray.filter(ImageFilter.FIND_EDGES)
            ).mean[0]

            # Reject visually empty regions.
            if contrast < 12 or edges < 8:
                continue

            score = contrast + edges * 1.5
            candidates.append((score, box))

    candidates.sort(key=lambda item: item[0], reverse=True)

    selected = []

    for _, box in candidates:
        cx = (box[0] + box[2]) / 2
        cy = (box[1] + box[3]) / 2

        too_close = False
        for old in selected:
            ox = (old[0] + old[2]) / 2
            oy = (old[1] + old[3]) / 2

            if abs(cx - ox) < side * 0.85 and abs(cy - oy) < side * 0.85:
                too_close = True
                break

        if not too_close:
            selected.append(box)

        if len(selected) >= count:
            break

    return selected


def region_center(box):
    return (
        (box[0] + box[2]) // 2,
        (box[1] + box[3]) // 2,
    )
