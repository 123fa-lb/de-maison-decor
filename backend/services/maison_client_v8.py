"""De Maison premium e-commerce helper module.
Final V20 fix: stronger infographic, improved close-up guidance,
exact decimal point formatting for dimensions, and better white-angle rules.
This file is safe to overwrite backend/services/maison_client_v8.py.
"""
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter, ImageStat
import math

S = 2000
WHITE = (255, 255, 255)
IVORY = (247, 243, 236)
BEIGE = (239, 230, 216)
INK = (42, 35, 30)
MUTED = (115, 102, 90)
GOLD = (170, 135, 84)
LINE = (70, 64, 58)
PALE = (221, 212, 198)


def _font(size, bold=False):
    candidates = ([r"C:\\Windows\\Fonts\\segoeuib.ttf", r"C:\\Windows\\Fonts\\arialbd.ttf"] if bold else
                  [r"C:\\Windows\\Fonts\\segoeui.ttf", r"C:\\Windows\\Fonts\\arial.ttf"])
    candidates += ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for file in candidates:
        try:
            return ImageFont.truetype(file, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _scaled_fit(image, size):
    return ImageOps.contain(image.convert("RGB"), size, Image.Resampling.LANCZOS)


def _bbox_neutral(image):
    img = image.convert("RGB")
    sm = img.copy()
    sm.thumbnail((480, 480), Image.Resampling.LANCZOS)
    w, h = sm.size
    if w < 60 or h < 60:
        return None
    px = sm.load()
    corners = [px[x, y] for x in (1, 2, w - 3, w - 2) for y in (1, 2, h - 3, h - 2)]
    avg = tuple(sum(v[k] for v in corners) / len(corners) for k in range(3))
    if min(avg) < 214 or max(avg) - min(avg) > 25:
        return None
    if max(abs(p[k] - avg[k]) for p in corners for k in range(3)) > 23:
        return None
    coords = []
    for y in range(3, h - 3, 2):
        for x in range(3, w - 3, 2):
            p = px[x, y]
            diff = max(abs(p[i] - avg[i]) for i in range(3))
            if diff > 53 and min(p) < 222:
                coords.append((x, y))
    if len(coords) < (w * h * 0.009):
        return None
    x0 = min(p[0] for p in coords)
    x1 = max(p[0] for p in coords)
    y0 = min(p[1] for p in coords)
    y1 = max(p[1] for p in coords)
    if x0 < 8 or y0 < 8 or x1 > w - 9 or y1 > h - 9:
        return None
    if (x1 - x0) * (y1 - y0) < w * h * 0.09:
        return None
    pad = max(10, int(max(x1 - x0, y1 - y0) * 0.065))
    return (
        max(0, int((x0 - pad) * img.width / w)),
        max(0, int((y0 - pad) * img.height / h)),
        min(img.width, int((x1 + pad) * img.width / w)),
        min(img.height, int((y1 + pad) * img.height / h)),
    )


def _safe_product(image):
    src = ImageOps.exif_transpose(image).convert("RGB")
    bounds = _bbox_neutral(src)
    if bounds:
        return src.crop(bounds)
    return src


def marketplace_square(image, category="white", size=S):
    src = ImageOps.exif_transpose(image).convert("RGB")
    if category == "white":
        src = _safe_product(src)
        canvas = Image.new("RGB", (size, size), WHITE)
        fit = _scaled_fit(src, (int(size * 0.84), int(size * 0.84)))
        canvas.paste(fit, ((size - fit.width) // 2, (size - fit.height) // 2))
        return canvas
    return ImageOps.fit(src, (size, size), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def _place_contained(board, image, rect, pad=0):
    x0, y0, x1, y1 = rect
    bw, bh = x1 - x0 - 2 * pad, y1 - y0 - 2 * pad
    fitted = _scaled_fit(image, (max(1, bw), max(1, bh)))
    fx = x0 + (x1 - x0 - fitted.width) // 2
    fy = y0 + (y1 - y0 - fitted.height) // 2
    board.paste(fitted, (fx, fy))
    return (fx, fy, fx + fitted.width, fy + fitted.height)


def _arrow(draw, xy0, xy1, color=LINE, width=5):
    x0, y0 = xy0
    x1, y1 = xy1
    draw.line((x0, y0, x1, y1), fill=color, width=width)
    theta = math.atan2(y1 - y0, x1 - x0)
    for x, y, angle in ((x0, y0, theta + math.pi), (x1, y1, theta)):
        for delta in (-0.48, 0.48):
            ex = x - 22 * math.cos(angle + delta)
            ey = y - 22 * math.sin(angle + delta)
            draw.line((x, y, ex, ey), fill=color, width=width)


def _dim_text(value, unit):
    txt = str(value or "").strip().replace(",", ".")
    if not txt:
        return ""
    try:
        number = float(txt)
        if not math.isfinite(number) or number <= 0:
            return ""
    except ValueError:
        return ""
    unit = unit if unit in ("cm", "mm", "in") else "cm"
    return f"{txt} {unit}"


def _find_product_bounds(image_rect, photo):
    fx, fy, fw, fh = image_rect
    thumb = photo.copy()
    thumb.thumbnail((240, 240))
    tw, th = thumb.size
    px = thumb.load()
    detected = []
    for yy in range(th):
        for xx in range(tw):
            r, g, b = px[xx, yy]
            if max(r, g, b) < 240 and min(r, g, b) < 220:
                detected.append((xx, yy))
    if len(detected) < 35:
        return (fx, fy, fx + fw, fy + fh)
    xs = [p[0] for p in detected]
    ys = [p[1] for p in detected]
    left = fx + int(min(xs) * fw / tw)
    right = fx + int(max(xs) * fw / tw)
    top = fy + int(min(ys) * fh / th)
    bottom = fy + int(max(ys) * fh / th)
    if right - left < 80 or bottom - top < 120:
        return (fx, fy, fx + fw, fy + fh)
    return (left, top, right, bottom)


def make_dimensions(image, width="", height="", depth="", unit="cm", size=S):
    wtxt, htxt, dtxt = [_dim_text(v, unit) for v in (width, height, depth)]
    if not any((wtxt, htxt, dtxt)):
        return marketplace_square(image, "white", size)

    board = Image.new("RGB", (size, size), WHITE)
    d = ImageDraw.Draw(board)
    product = _safe_product(image)

    # Large centered product with safe room for arrows.
    rect = (300, 185, 1500, 1570)
    placed = _place_contained(board, product, rect, pad=15)
    fx, fy, fx2, fy2 = placed
    bounds = _find_product_bounds((fx, fy, fx2 - fx, fy2 - fy), board.crop((fx, fy, fx2, fy2)))
    left, top, right, bottom = bounds

    if htxt:
        xx = 1710
        yy0 = max(200, top)
        yy1 = min(1540, bottom)
        if yy1 - yy0 < 180:
            yy0, yy1 = 260, 1420
        _arrow(d, (xx, yy0), (xx, yy1))
        d.line((right + 16, yy0, xx - 28, yy0), fill=PALE, width=3)
        d.line((right + 16, yy1, xx - 28, yy1), fill=PALE, width=3)
        d.text((xx + 42, (yy0 + yy1) // 2), htxt, font=_font(46, True), fill=INK, anchor="lm")

    if wtxt:
        yy = 1710
        wx0 = max(330, left)
        wx1 = min(1465, right)
        if wx1 - wx0 < 180:
            wx0, wx1 = 560, 1290
        _arrow(d, (wx0, yy), (wx1, yy))
        d.rectangle((int((wx0 + wx1) // 2 - 170), yy + 20, int((wx0 + wx1) // 2 + 170), yy + 112), fill=WHITE)
        d.text(((wx0 + wx1) // 2, yy + 66), wtxt, font=_font(52, True), fill=INK, anchor="mm")

    if dtxt:
        ax0, ay0 = 165, 1485
        ax1, ay1 = 405, 1710
        _arrow(d, (ax0, ay0), (ax1, ay1))
        d.rectangle((80, 1738, 565, 1832), fill=WHITE)
        d.text((322, 1785), dtxt, font=_font(50, True), fill=INK, anchor="mm")

    return board


def _detail_candidates(image):
    src = image.convert("RGB")
    w, h = src.size
    anchors = (
        (0.50, 0.16, 0.34), (0.33, 0.22, 0.28), (0.67, 0.22, 0.28),
        (0.50, 0.38, 0.30), (0.37, 0.48, 0.28), (0.63, 0.48, 0.28),
        (0.50, 0.62, 0.30), (0.35, 0.72, 0.26), (0.65, 0.72, 0.26)
    )
    ranked = []
    for cx, cy, frac in anchors:
        side = max(60, int(min(w, h) * frac))
        x0 = max(0, min(int(cx * w - side / 2), w - side))
        y0 = max(0, min(int(cy * h - side / 2), h - side))
        patch = src.crop((x0, y0, x0 + side, y0 + side)).resize((170, 170))
        edge = ImageStat.Stat(patch.filter(ImageFilter.FIND_EDGES).convert("L")).mean[0]
        contrast = ImageStat.Stat(patch.convert("L")).stddev[0]
        brightness = ImageStat.Stat(patch.convert("L")).mean[0]
        score = edge * 1.3 + contrast - max(0, brightness - 228) * 0.55
        ranked.append((score, (x0, y0, x0 + side, y0 + side)))
    ranked.sort(key=lambda t: t[0], reverse=True)
    picks = []
    for _, box in ranked:
        if all(abs(box[0] - b[0]) > 40 or abs(box[1] - b[1]) > 40 for b in picks):
            picks.append(box)
        if len(picks) == 3:
            break
    while len(picks) < 3:
        picks.append(ranked[len(picks)][1])
    return picks


def _circle_detail(board, image, box, x, y, diameter):
    cropped = image.crop(box)
    stamp = ImageOps.fit(cropped, (diameter, diameter), Image.Resampling.LANCZOS)
    mask = Image.new("L", (diameter, diameter), 0)
    dm = ImageDraw.Draw(mask)
    dm.ellipse((4, 4, diameter - 5, diameter - 5), fill=255)
    board.paste(stamp, (x, y), mask)
    bd = ImageDraw.Draw(board)
    bd.ellipse((x + 2, y + 2, x + diameter - 2, y + diameter - 2), outline=GOLD, width=6)


def make_infographic(image, note="", size=S):
    board = Image.new("RGB", (size, size), IVORY)
    d = ImageDraw.Draw(board)

    # Warm premium editorial background.
    d.rectangle((0, 0, size, 340), fill=BEIGE)
    d.text((110, 78), "PRODUCT FEATURES", font=_font(82, True), fill=(78, 56, 36))
    d.text((112, 198), "Design details captured from the actual product", font=_font(30), fill=MUTED)
    d.line((110, 270, 1890, 270), fill=GOLD, width=4)

    product = _safe_product(image)
    hero_panel = (90, 360, 1215, 1755)
    d.rounded_rectangle(hero_panel, radius=34, fill=WHITE)
    _place_contained(board, product, (130, 420, 1175, 1710), pad=8)

    # Sample-like right column with three detail circles.
    details = _detail_candidates(product)
    cx = 1350
    dia = 350
    starts = [430, 870, 1310]
    labels = [
        ("Design Detail", "Visible product feature"),
        ("Surface Finish", "True texture and material"),
        ("Form & Build", "Real shape and construction"),
    ]
    for i, top in enumerate(starts):
        _circle_detail(board, product, details[i], cx, top, dia)
        d.text((cx + dia // 2, top + dia + 24), labels[i][0], font=_font(34, True), fill=(64, 49, 37), anchor="mt")
        d.text((cx + dia // 2, top + dia + 72), labels[i][1], font=_font(23), fill=MUTED, anchor="mt")

    # Minimal premium footer badges (text only, safe for all products).
    footer_y = 1840
    d.line((110, footer_y - 24, 1890, footer_y - 24), fill=PALE, width=3)
    items = ["Premium Quality", "Home Decor Ready", "Gift-worthy", "Crafted Finish"]
    xs = [250, 720, 1190, 1660]
    for x, text in zip(xs, items):
        d.ellipse((x - 42, footer_y - 4, x + 42, footer_y + 80), outline=GOLD, width=4)
        d.text((x, footer_y + 38), "•", font=_font(34, True), fill=GOLD, anchor="mm")
        d.text((x, footer_y + 122), text, font=_font(25, True), fill=(84, 68, 51), anchor="mm")

    return board


FINAL_CATEGORY_V8 = {
    "white": """Generate ONE premium e-commerce product photo on pure white #FFFFFF. Variation handling is fixed by variation number: variation 1 = front / primary hero view; variation 2 = clear side view that is visually distinct from the front; variation 3 = top or overhead-biased view when product design allows; variation 4 = three-quarter view. Each output must be a single separate image, never a collage. Keep the same real product. Clean only incidental dust, lint, fingerprints and tiny photographic dirt. Never invent hidden geometry or convert a symmetrical front view into a fake side view. Make the product large, centered and fully visible with safe margins.""",
    "lifestyle": """Generate ONE premium lifestyle e-commerce image, 1:1 square, full-bleed and natural. Choose a tasteful realistic background according to the product category and use-case. Product must remain the main subject, physically plausible, well lit, and clearly visible. No collage, no white side bars, no random text. Clean minor dust only.""",
    "closeup": """Generate ONE premium close-up image focusing on the MOST DISTINCTIVE visible feature of the real product, not a plain generic body crop. Prioritize texture, carving, rim, cutwork, weave, finish, lid, edge detail, handle, craftsmanship or signature surface detail that is clearly supported by the source image. Compose a macro-style view where the feature fills most of the frame while remaining truthful and sharply visible. If the product lacks a dramatic small feature, choose the most visually informative real detail instead of a blank body section.""",
    "infographic": """Generate ONE clean premium source photo for an e-commerce infographic. Full exact product, large and centered on a bright neutral studio background, with clear safe space around it. No added text, badges, arrows or fake detail panels from Gemini. The server will convert this source into a premium infographic with one hero product and three detail callout circles.""",
    "dimension": """Generate ONE clean premium source photo for a dimension image. Show the entire exact product on a bright white or neutral studio background, large and fully visible, with enough space around the object for measurement arrows. Do not add any text, rulers, arrows or numbers. The server will add ONLY the user-supplied measurements, preserving decimal point notation exactly, for example 7.5 cm and never 7,5 cm."""
}

FINAL_UNIVERSAL_V8 = """E-COMMERCE PRODUCT MASTER RULES: The supplied product photos are the source of truth. Preserve the same physical object, silhouette, material, color, finish, construction and visible details. Do not replace the item with a similar catalog item. Improve photographic quality only: cleaner lighting, sharper commercial framing, and removal of superficial dust, lint, fingerprints and minor photographic noise. Do not remove genuine product characteristics or add new components. Output one premium separate image per request, never a collage sheet unless explicitly requested."""
