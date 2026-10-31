# DEMAISON_IMAGE_SAFETY_V1

from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageChops

W = H = 2000

def font(size, bold=False, serif=False):
    names = (
        ["georgiab.ttf", "georgia.ttf"] if serif else
        ["segoeuib.ttf", "arialbd.ttf"] if bold else
        ["segoeui.ttf", "arial.ttf"]
    )
    for name in names:
        try:
            return ImageFont.truetype("C:/Windows/Fonts/" + name, size)
        except OSError:
            pass
    return ImageFont.load_default()

def foreground_crop(image):
    """Conservative crop: preserve the complete image whenever segmentation is uncertain.

    No artificial background removal. Transparent, white, reflective or low-contrast
    products stay intact rather than risking removal of genuine product components.
    """
    im = image.convert("RGB")
    small = im.copy()
    small.thumbnail((450, 450), Image.Resampling.LANCZOS)
    if small.width < 30 or small.height < 30:
        return im

    # Only crop photographs with a uniform, light neutral background.
    w, h = small.size
    p = small.load()
    corners = [p[0, 0], p[w-1, 0], p[0, h-1], p[w-1, h-1]]
    avg = tuple(sum(c[k] for c in corners) / 4 for k in range(3))
    spread = max(max(abs(c[k]-avg[k]) for k in range(3)) for c in corners)
    if spread > 14 or min(avg) < 225 or max(avg)-min(avg) > 24:
        return im

    # Only use pixels that differ significantly from the known light background.
    # Pale, glass and highly reflective products are ambiguous: preserve full image.
    from PIL import ImageStat
    pix = small.load()
    mask = Image.new('L', small.size, 0)
    mp = mask.load()
    for y in range(h):
        for x in range(w):
            rgb = pix[x, y]
            if max(abs(rgb[k]-avg[k]) for k in range(3)) >= 58:
                mp[x, y] = 255

    bbox = mask.getbbox()
    if bbox is None:
        return im
    x1, y1, x2, y2 = bbox
    cover = (x2-x1)*(y2-y1)/(w*h)
    # Edge-touching silhouettes, tiny detected regions or huge foregrounds are unsafe.
    if cover < 0.08 or cover > 0.82 or x1 < 8 or y1 < 8 or x2 > w-8 or y2 > h-8:
        return im

    # Generous margin protects pale edges, shadows and transparent components.
    padx = max(16, int((x2-x1)*0.16))
    pady = max(16, int((y2-y1)*0.16))
    sx, sy = im.width/w, im.height/h
    crop = (max(0, int((x1-padx)*sx)), max(0, int((y1-pady)*sy)),
            min(im.width, int((x2+padx)*sx)), min(im.height, int((y2+pady)*sy)))
    if crop[2] <= crop[0] or crop[3] <= crop[1]:
        return im
    return im.crop(crop)

def contain(canvas, image, rect, margin=20):
    x1, y1, x2, y2 = rect
    available = (max(1, x2-x1-2*margin),
                 max(1, y2-y1-2*margin))
    pic = ImageOps.contain(
        image.convert("RGB"),
        available,
        Image.Resampling.LANCZOS
    )
    x = x1 + (x2-x1-pic.width)//2
    y = y1 + (y2-y1-pic.height)//2
    canvas.paste(pic, (x, y))

def compose_infographic(source):
    """Deterministic premium infographic; no extra API requests."""
    source = ImageOps.exif_transpose(source).convert("RGB")
    product = foreground_crop(source)

    bg = "#F6F4F0"
    ink = "#242320"
    muted = "#79736C"
    accent = "#A77D52"
    border = "#E7E1D8"

    canvas = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(canvas)

    d.text((105, 70), "PRODUCT HIGHLIGHTS",
           font=font(26, bold=True), fill=accent)
    d.text((100, 119), "Details that matter.",
           font=font(88, serif=True), fill=ink)
    d.line((105, 253, 1895, 253), fill=border, width=3)

    hero = (100, 300, 1250, 1790)
    upper = (1280, 300, 1900, 1030)
    lower = (1280, 1055, 1900, 1790)

    for box in (hero, upper, lower):
        d.rounded_rectangle(box, radius=25, fill="white",
                            outline=border, width=2)

    # Hero: use product crop, preserve aspect ratio.
    contain(canvas, product, (130, 330, 1220, 1570), 20)

    pw, ph = product.size

    # Detail regions from the actual product photo.
    top_crop = product.crop((
        int(pw*0.05), 0,
        max(int(pw*0.95), 1),
        max(int(ph*0.56), 1)
    ))

    middle_crop = product.crop((
        int(pw*0.05), int(ph*0.23),
        max(int(pw*0.95), 1),
        max(int(ph*0.78), int(ph*0.23)+1)
    ))

    contain(canvas, top_crop, (1310, 325, 1870, 865), 10)
    contain(canvas, middle_crop, (1310, 1080, 1870, 1620), 10)

    d = ImageDraw.Draw(canvas)

    def caption(box, number, heading, subheading):
        left, top, right, bottom = box
        d.line((left+35, bottom-160, right-35, bottom-160),
               fill=border, width=2)
        d.text((left+40, bottom-139), number,
               font=font(23, bold=True), fill=accent)
        d.text((left+40, bottom-98), heading,
               font=font(34, bold=True), fill=ink)
        d.text((left+40, bottom-48), subheading,
               font=font(23), fill=muted)

    caption(hero, "01 / OVERVIEW", "Original design",
            "Form, proportions and appearance")
    caption(upper, "02 / DETAIL", "Closer perspective",
            "Visible design elements")
    caption(lower, "03 / DETAIL", "Surface study",
            "Texture and visual finish")

    d.line((105, 1840, 1895, 1840), fill=border, width=3)
    d.text((105, 1880), "PRODUCT DETAIL COLLECTION",
           font=font(26, bold=True), fill=muted)

    return canvas
