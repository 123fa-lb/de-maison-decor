"""Conservative e-commerce image finishing, no external models or API calls."""
from PIL import Image, ImageFilter, ImageOps


def _neutral_subject_box(image):
    """Find a clearly separated object on a near-uniform neutral studio background.
    Return None whenever segmentation is uncertain. Never crop based on guesswork.
    """
    im = image.convert('RGB')
    w, h = im.size
    if min(w, h) < 200:
        return None
    sample = im.resize((max(80, min(400, w)), max(80, min(400, h))))
    sw, sh = sample.size
    pix = sample.load()
    corners = [pix[x, y] for x in (2, sw-3) for y in (2, sh-3)]
    # Background must be light and nearly identical in all corners.
    if min(min(p) for p in corners) < 205:
        return None
    if max(max(abs(a-b) for a, b in zip(corners[0], p)) for p in corners) > 32:
        return None
    bg = tuple(sum(p[i] for p in corners) / len(corners) for i in range(3))
    coords = []
    for y in range(sh):
        for x in range(sw):
            p = pix[x, y]
            if max(abs(p[i]-bg[i]) for i in range(3)) > 43 and min(p) < 225:
                coords.append((x,y))
    if len(coords) < sw * sh * 0.025:
        return None
    x0 = min(p[0] for p in coords); x1 = max(p[0] for p in coords)
    y0 = min(p[1] for p in coords); y1 = max(p[1] for p in coords)
    # Refuse cropping if the subject or strong shadows touch the edges.
    if x0 < sw*.025 or x1 > sw*.975 or y0 < sh*.025 or y1 > sh*.975:
        return None
    if (x1-x0) < sw*.10 or (y1-y0) < sh*.10:
        return None
    pad_x = max(5, int((x1-x0)*.09)); pad_y = max(5, int((y1-y0)*.09))
    x0 = max(0, x0-pad_x); x1 = min(sw, x1+pad_x)
    y0 = max(0, y0-pad_y); y1 = min(sh, y1+pad_y)
    # Keep aspect ratio of source; no stretching of actual object.
    return (int(x0*w/sw), int(y0*h/sh), int((x1+1)*w/sw), int((y1+1)*h/sh))


def prepare_neutral_source(image):
    """Make a small, safely detected neutral-background product more prominent."""
    src = ImageOps.exif_transpose(image).convert('RGB')
    box = _neutral_subject_box(src)
    if box is None:
        return src
    # Do not crop if it would discard more than 80% of the photo; detection may be wrong.
    if (box[2]-box[0])*(box[3]-box[1]) < src.width*src.height*.20:
        return src
    return src.crop(box)


def full_bleed_square(image, category, size=2000):
    """Full-bleed square without opaque white side panels; retain all content if very tall."""
    src = ImageOps.exif_transpose(image).convert('RGB')
    w, h = src.size
    ratio = w / max(h, 1)
    if .94 <= ratio <= 1.06:
        # Crop at most 6% of one dimension to avoid conspicuous sidebars.
        return ImageOps.fit(src, (size, size), method=Image.Resampling.LANCZOS,
                            centering=(.5, .5))
    # For extreme aspect ratios, do not crop off a product; use edge-derived
    # background with a wide feather transition, never a white letterbox.
    backdrop = ImageOps.fit(src, (size, size), method=Image.Resampling.LANCZOS)
    backdrop = backdrop.filter(ImageFilter.GaussianBlur(radius=max(20, size//45)))
    fitted = ImageOps.contain(src, (size, size), Image.Resampling.LANCZOS)
    x = (size-fitted.width)//2; y = (size-fitted.height)//2
    # Feather only the background join; do not blur the product itself.
    mask = Image.new('L', (size, size), 0)
    from PIL import ImageDraw
    d = ImageDraw.Draw(mask)
    feather = max(10, size//80)
    d.rectangle((x+feather, y+feather, x+fitted.width-feather,
                 y+fitted.height-feather), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=feather))
    layer = Image.new('RGB', (size, size))
    layer.paste(fitted, (x,y))
    backdrop.paste(layer, (0,0), mask)
    return backdrop
