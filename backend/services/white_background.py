from io import BytesIO
from threading import Lock
import numpy as np
import cv2

from PIL import Image, ImageOps, ImageFilter, ImageEnhance

_session = None
_lock = Lock()

CANVAS = 2000


def _get_session():
    global _session

    if _session is None:
        import colorama.win32
        colorama.win32.winapi_test = lambda: False

        from rembg import new_session

        print("[Maison] Loading quality AI model...", flush=True)

        _session = new_session(
            "isnet-general-use",
            providers=["CPUExecutionProvider"]
        )

    return _session


def _straighten(cutout):
    """
    Estimate tilt from the central body of a tall product.
    Avoid aggressive rotation when orientation is uncertain.
    """

    alpha = np.asarray(cutout.getchannel("A"))

    mask = (alpha > 170).astype(np.uint8) * 255

    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask, 8
    )

    if count <= 1:
        return cutout

    largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    body = np.uint8(labels == largest) * 255

    ys, xs = np.where(body > 0)

    if len(xs) < 500:
        return cutout

    # Use the central body to reduce influence from
    # handles, pens and small protruding objects.
    left, right = np.percentile(xs, [10, 90])
    top, bottom = np.percentile(ys, [15, 85])

    selected = (
        (xs >= left) & (xs <= right) &
        (ys >= top) & (ys <= bottom)
    )

    x = xs[selected].astype(np.float64)
    y = ys[selected].astype(np.float64)

    if len(x) < 500:
        return cutout

    points = np.column_stack((x, y))
    covariance = np.cov(points, rowvar=False)

    values, vectors = np.linalg.eigh(covariance)

    major = vectors[:, np.argmax(values)]
    minor_variance = max(float(np.min(values)), 1.0)
    ratio = float(np.max(values)) / minor_variance

    # Only auto-straighten clearly tall objects.
    # Bowls, plates and wide decor pieces are left unchanged.
    if ratio < 1.8:
        return cutout

    angle = np.degrees(np.arctan2(major[0], major[1]))

    # Keep correction conservative.
    if abs(angle) < 1.2 or abs(angle) > 15:
        return cutout

    print(
        f"[Maison] Auto straightening: {angle:.1f} degrees",
        flush=True
    )

    return cutout.rotate(
        float(angle),
        resample=Image.Resampling.BICUBIC,
        expand=True,
        fillcolor=(0, 0, 0, 0)
    )


def process_white(image):
    import colorama.win32
    colorama.win32.winapi_test = lambda: False

    from rembg import remove

    with _lock:
        source = ImageOps.exif_transpose(image).convert("RGB")

        # Preserve source detail for segmentation.
        source.thumbnail(
            (2000, 2000),
            Image.Resampling.LANCZOS
        )

        buffer = BytesIO()
        source.save(buffer, format="PNG")

        result = remove(
            buffer.getvalue(),
            session=_get_session(),
            alpha_matting=True,
            alpha_matting_foreground_threshold=220,
            alpha_matting_background_threshold=15,
            alpha_matting_erode_size=5
        )

    cutout = Image.open(BytesIO(result)).convert("RGBA")

    alpha = cutout.getchannel("A")

    # Suppress faint background noise without
    # destroying the main product outline.
    alpha = alpha.point(
        lambda value: 0 if value < 3 else value
    )

    alpha = alpha.filter(
        ImageFilter.GaussianBlur(0.15)
    )

    cutout.putalpha(alpha)

    # Automatic tilt correction
    cutout = _straighten(cutout)

    alpha = cutout.getchannel("A")

    bbox = alpha.point(
        lambda value: 255 if value > 18 else 0
    ).getbbox()

    if not bbox:
        raise ValueError("Product not detected")

    pad = 16

    bbox = (
        max(0, bbox[0] - pad),
        max(0, bbox[1] - pad),
        min(cutout.width, bbox[2] + pad),
        min(cutout.height, bbox[3] + pad)
    )

    cutout = cutout.crop(bbox)

    # Gentle detail enhancement, not aggressive sharpening
    rgb = cutout.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(1.03)
    rgb = rgb.filter(
        ImageFilter.UnsharpMask(
            radius=1.0,
            percent=65,
            threshold=3
        )
    )

    rgb.putalpha(cutout.getchannel("A"))
    cutout = rgb

    cutout.thumbnail(
        (1680, 1680),
        Image.Resampling.LANCZOS
    )

    canvas = Image.new(
        "RGBA",
        (CANVAS, CANVAS),
        (255, 255, 255, 255)
    )

    x = (CANVAS - cutout.width) // 2
    y = (CANVAS - cutout.height) // 2

    canvas.alpha_composite(cutout, (x, y))

    return canvas.convert("RGB")
