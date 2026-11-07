
"""Universal premium infographic compositor."""
from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageFont
from backend.services.infographic_matching import find_detail_regions, region_center


def _font(size, bold=False):
    paths = (
        [r"C:\Windows\Fonts\georgiab.ttf", r"C:\Windows\Fonts\arialbd.ttf"]
        if bold else
        [r"C:\Windows\Fonts\georgia.ttf", r"C:\Windows\Fonts\arial.ttf"]
    )
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def compose_infographic(hero):
    src = ImageOps.exif_transpose(hero).convert("RGB")
    size = 1600

    # Premium neutral editorial background, no duplicated hero.
    board = Image.new("RGB", (size, size), "#F4EFE7")
    draw = ImageDraw.Draw(board)

    draw.text(
        (90, 80), "PRODUCT DETAILS",
        font=_font(76, True), fill="#302820"
    )
    draw.text(
        (94, 177), "A CLOSER LOOK",
        font=_font(25), fill="#927A60"
    )

    # Place the Gemini image once, in the hero region.
    hero_rect = (70, 290, 1010, 1410)
    draw.rounded_rectangle(
        hero_rect, radius=28, fill="#FFFFFF"
    )

    fitted = ImageOps.contain(
        src,
        (hero_rect[2]-hero_rect[0]-40,
         hero_rect[3]-hero_rect[1]-40),
        Image.Resampling.LANCZOS
    )

    hx = hero_rect[0] + (hero_rect[2]-hero_rect[0]-fitted.width)//2
    hy = hero_rect[1] + (hero_rect[3]-hero_rect[1]-fitted.height)//2
    board.paste(fitted, (hx, hy))

    # Both crop and connector point use exactly the same hero image.
    regions = find_detail_regions(fitted, count=3)

    for i, box in enumerate(regions):
        diameter = 290
        x = 1190
        y = 310 + i * 365

        crop = fitted.crop(box)
        detail = ImageOps.fit(
            crop, (diameter, diameter),
            method=Image.Resampling.LANCZOS
        )

        mask = Image.new("L", (diameter, diameter), 0)
        md = ImageDraw.Draw(mask)
        md.ellipse((3, 3, diameter-4, diameter-4), fill=255)

        cx, cy = region_center(box)
        px, py = hx + cx, hy + cy

        draw = ImageDraw.Draw(board)
        draw.line(
            (px, py, x, y + diameter//2),
            fill="#B18B5B", width=3
        )
        draw.ellipse(
            (px-7, py-7, px+7, py+7),
            fill="#B18B5B"
        )

        board.paste(detail, (x, y), mask)
        draw = ImageDraw.Draw(board)
        draw.ellipse(
            (x+2, y+2, x+diameter-2, y+diameter-2),
            outline="#B18B5B", width=5
        )

    draw.line(
        (90, 1500, 1510, 1500),
        fill="#D6C9B7", width=2
    )
    draw.text(
        (90, 1525), "DETAILS FROM THE PRODUCT IMAGE",
        font=_font(23), fill="#756756"
    )
    return board
