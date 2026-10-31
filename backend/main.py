from io import BytesIO
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image, UnidentifiedImageError
from backend.services.white_background import process_white

app = FastAPI(title="Maison Studio API", version="1.1.0")
from backend.auth import router as auth_router, protect_api, allowed_origins
app.include_router(auth_router)
app.middleware("http")(protect_api)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allowed_origins(),
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/")
def home():
    return {"app": "Maison Studio", "status": "running"}

@app.get("/api/health")
def health():
    return {"success": True, "message": "Maison Studio backend connected"}

@app.post("/api/generate/white")
def generate_white(file: UploadFile = File(...)):
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(400, "Please upload an image file")
    try:
        content = file.file.read(20 * 1024 * 1024 + 1)
        if len(content) > 20 * 1024 * 1024:
            raise HTTPException(413, "Image exceeds 20 MB limit")
        with Image.open(BytesIO(content)) as source:
            if source.width * source.height > 50_000_000:
                raise HTTPException(413, "Image dimensions too large")
            result = process_white(source)
        output = BytesIO()
        result.save(output, format="JPEG", quality=95, subsampling=0)
        output.seek(0)
        return StreamingResponse(output, media_type="image/jpeg", headers={"Cache-Control": "no-store"})
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(400, f"Invalid or unreadable image: {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    except Exception as exc:
        print(f"[Maison] White background error: {exc}", flush=True)
        raise HTTPException(500, "Background removal failed. Check backend terminal for details.")


# Maison Studio: local CPU white-background generation
from io import BytesIO
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import Response
from PIL import Image, ImageOps
from starlette.concurrency import run_in_threadpool

def _generate_white_image(data: bytes) -> bytes:
    from backend.services.white_background import process_white

    with Image.open(BytesIO(data)) as source:
        source = ImageOps.exif_transpose(source)
        result = process_white(source)

    output = BytesIO()
    result.convert("RGB").save(
        output,
        format="JPEG",
        quality=95,
        subsampling=0
    )
    return output.getvalue()

@app.post("/api/white-test")
async def white_test(file: UploadFile = File(...)):
    try:
        data = await file.read()

        if not data:
            raise ValueError("Empty image uploaded")

        if len(data) > 25 * 1024 * 1024:
            raise ValueError("Image exceeds 25 MB limit")

        result = await run_in_threadpool(
            _generate_white_image, data
        )

        return Response(
            content=result,
            media_type="image/jpeg",
            headers={"Cache-Control": "no-store"}
        )

    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )
import os
import sqlite3
import threading
from io import BytesIO
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import File, Form, UploadFile, HTTPException
from fastapi.responses import Response
from PIL import Image, ImageOps, ImageDraw, ImageFont

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MAISON_ROOT = Path(__file__).resolve().parents[1]
MAISON_DB = MAISON_ROOT / "backend" / "maison_usage.db"
MAISON_LOCK = threading.Lock()

MAISON_CATEGORIES = {
    "white": "White Background",
    "closeup": "Close-up",
    "lifestyle": "Lifestyle",
    "infographic": "Infographic",
    "dimension": "Dimension",
}

def maison_db():
    with sqlite3.connect(MAISON_DB) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                sku TEXT NOT NULL,
                category TEXT NOT NULL,
                model TEXT NOT NULL,
                success INTEGER NOT NULL,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0
            )
        """)
        con.commit()

def maison_record(sku, category, model, success, input_tokens=0, output_tokens=0, variation=1):
    with MAISON_LOCK:
        maison_db()
        with sqlite3.connect(MAISON_DB) as con:
            cols = {r[1] for r in con.execute("PRAGMA table_info(usage)")}
            if "variation" not in cols:
                con.execute("ALTER TABLE usage ADD COLUMN variation INTEGER DEFAULT 1")
            con.execute(
                """INSERT INTO usage
                   (created_at,sku,category,model,success,input_tokens,output_tokens,variation)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (
                    datetime.now(timezone.utc).isoformat(),
                    sku, category, model, int(success),
                    input_tokens, output_tokens, variation
                )
            )
            con.commit()

@app.get("/api/maison/usage")
def maison_usage():
    maison_db()
    with sqlite3.connect(MAISON_DB) as con:
        row = con.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(success),0),
                COALESCE(SUM(input_tokens),0),
                COALESCE(SUM(output_tokens),0)
            FROM usage
        """).fetchone()

        categories = con.execute("""
            SELECT category, COUNT(*)
            FROM usage
            WHERE success=1
            GROUP BY category
        """).fetchall()

    return {
        "configured": bool(os.getenv("GEMINI_API_KEY")),
        "model": os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image"),
        "requests": row[0],
        "successful": row[1],
        "input_tokens": row[2],
        "output_tokens": row[3],
        "categories": dict(categories),
        "balance_inr": None,
        "balance_note": "Live prepaid balance is not available from this endpoint."
    }

def maison_prompt(category, sku, note, width, height, depth, unit, variation):
    preserve = """
You are an expert luxury e-commerce product photographer.
Edit the PROVIDED PRODUCT PHOTO. The photo is the source of truth.
Keep the product's exact shape, proportions, material, stitching,
surface texture, pattern, branding, and original colors.
Do not replace the product with a similar-looking item.
Do not invent product features or accessories.
Create one polished commercial product image.
Square composition, professional lighting, natural shadows,
clean edges, no watermark, no unrelated text.
"""

    instructions = {
        "white": """
Create a professional marketplace packshot.
Pure white (#FFFFFF) background.
Entire product visible and centered.
Soft realistic contact shadow.
Do not remove genuine product components.
""",
        "closeup": """
Create a premium close-up detail photograph of the actual product.
Show a meaningful material, stitching, finish, texture or craftsmanship
detail visible in the reference. Do not invent microscopic detail.
Professional studio macro photography.
""",
        "lifestyle": """
Place this exact product naturally into a premium,
realistic interior appropriate for its use.
Tasteful modern decor, beautiful natural lighting,
photorealistic commercial photography.
Keep the product clearly visible and recognizable.
""",
        "infographic": """
Create a refined luxury e-commerce product infographic.
Use an elegant minimal layout, restrained typography,
clear visual hierarchy, and the actual product photo.
Only use verified product details from the user instructions.
Do not invent features, materials, benefits or measurements.
""",
        "dimension": """
Create a premium e-commerce dimension image.
Keep the complete product visible against a clean neutral background.
Leave clear negative space for dimension labels.
Do not invent numerical measurements.
"""
    }

    prompt = (
        preserve
        + "\nTASK:\n" + instructions[category]
        + f"\nSKU: {sku}\nVariation: {variation}\n"
        + f"\nAdditional customer instructions: {note or 'None'}\n"
    )

    if category == "dimension":
        prompt += (
            f"\nActual dimensions provided by customer: "
            f"width={width or 'not provided'}, "
            f"height={height or 'not provided'}, "
            f"depth={depth or 'not provided'}, unit={unit}.\n"
            "Do not render numerical measurement text. "
            "The application will overlay verified measurements."
        )

    return prompt

def maison_dimension_overlay(image, width, height, depth, unit):
    """Add verified measurements, never AI-guessed numbers."""
    entries = [
        ("W", width),
        ("H", height),
        ("D", depth),
    ]
    entries = [(label, value) for label, value in entries if str(value).strip()]
    if not entries:
        return image

    image = image.convert("RGB")
    draw = ImageDraw.Draw(image)
    w, h = image.size

    try:
        font_path = r"C:\Windows\Fonts\arialbd.ttf"
        font = ImageFont.truetype(font_path, max(25, w // 34))
    except Exception:
        font = ImageFont.load_default()

    labels = "    ".join(f"{label}: {value} {unit}" for label, value in entries)

    box_h = max(95, h // 11)
    draw.rounded_rectangle(
        (w * .06, h - box_h - 25, w * .94, h - 25),
        radius=18,
        fill=(245, 243, 239),
        outline=(210, 204, 195),
        width=2
    )
    draw.text(
        (w // 2, h - box_h // 2 - 25),
        labels,
        font=font,
        fill=(35, 34, 32),
        anchor="mm"
    )
    return image

@app.post("/api/maison/generate")
def maison_generate(
    file: UploadFile = File(...),
    category: str = Form(...),
    sku: str = Form("Product"),
    note: str = Form(""),
    width: str = Form(""),
    height: str = Form(""),
    depth: str = Form(""),
    unit: str = Form("cm"),
    variation: int = Form(1)
):
    from google import genai
    from google.genai import types

    if category not in MAISON_CATEGORIES:
        raise HTTPException(400, "Unsupported image category")

    key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image").strip()

    if not key:
        raise HTTPException(
            503,
            "GEMINI_API_KEY missing from D:\\DE-MAISON\\.env"
        )

    data = file.file.read(20 * 1024 * 1024 + 1)

    if not data or len(data) > 20 * 1024 * 1024:
        raise HTTPException(413, "Image missing or exceeds 20 MB")

    try:
        with Image.open(BytesIO(data)) as source:
            if source.width * source.height > 50_000_000:
                raise HTTPException(413, "Image dimensions too large")
            reference = ImageOps.exif_transpose(source).convert("RGB")
            reference.thumbnail((2048, 2048))

        source_buffer = BytesIO()
        reference.save(source_buffer, "JPEG", quality=94)

        client = genai.Client(api_key=key)

        prompt = maison_prompt(
            category, sku, note,
            width, height, depth, unit, variation
        )

        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(
                    data=source_buffer.getvalue(),
                    mime_type="image/jpeg"
                ),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            )
        )

        image_bytes = None

        for candidate in response.candidates or []:
            for part in candidate.content.parts or []:
                if getattr(part, "inline_data", None):
                    image_bytes = part.inline_data.data
                    break
            if image_bytes:
                break

        if not image_bytes:
            raise ValueError(
                "Gemini returned no image. Check model access, safety response and billing."
            )

        with Image.open(BytesIO(image_bytes)) as generated:
            generated = ImageOps.exif_transpose(generated).convert("RGB")

            # 2000x2000 delivery canvas; not a claim of native 2K detail.
            canvas = Image.new("RGB", (2000, 2000), "white")
            fitted = ImageOps.contain(
                generated, (2000, 2000), Image.Resampling.LANCZOS
            )
            canvas.paste(
                fitted,
                ((2000 - fitted.width) // 2,
                 (2000 - fitted.height) // 2)
            )

            if category == "dimension":
                canvas = maison_dimension_overlay(
                    canvas, width, height, depth, unit
                )

            output = BytesIO()
            canvas.save(
                output,
                "JPEG",
                quality=95,
                subsampling=0
            )

        usage = getattr(response, "usage_metadata", None)
        input_tokens = int(
            getattr(usage, "prompt_token_count", 0) or 0
        )
        output_tokens = int(
            getattr(usage, "candidates_token_count", 0) or 0
        )

        maison_record(
            sku, category, model, True,
            input_tokens, output_tokens
        )

        return Response(
            content=output.getvalue(),
            media_type="image/jpeg",
            headers={"Cache-Control": "no-store"}
        )

    except HTTPException:
        raise
    except Exception as exc:
        maison_record(sku, category, model, False)
        print(f"[MAISON GEMINI] {category}/{sku}: {exc}", flush=True)
        raise HTTPException(
            502,
            f"Gemini generation failed: {str(exc)[:350]}"
        )

from backend.services.studio_generator import router as studio_router
app.include_router(studio_router)



# DE MAISON DECOR: date-wise per-image usage report (no provider credentials exposed).
from fastapi import Query
from datetime import timezone, timedelta


# DEMAISON_SAFE_COSTS_V1: advisory model pricing, never a wallet deduction.
# Published paid-tier standard pricing; may differ from actual billed amounts,
# taxes, FX conversion, discounts, retries, output text and billing adjustments.
# Only estimate the explicitly supported model. Unknown models remain unpriced.
def maison_estimate_cost_usd(model, input_tokens, success):
    if not success or model != "gemini-2.5-flash-image":
        return None
    if input_tokens is None or int(input_tokens) <= 0:
        return None
    return round(0.039 + int(input_tokens) * 0.30 / 1_000_000, 6)

@app.get("/api/maison/report")
def maison_report_v2(date: str = Query(default=""), days: int = Query(default=7, ge=1, le=365)):
    from datetime import datetime, timedelta
    import sqlite3
    tz = timezone(timedelta(hours=5, minutes=30))
    today = datetime.now(tz).date()
    if date:
        try:
            end = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(400, "Use YYYY-MM-DD date format")
    else:
        end = today
    start = end - timedelta(days=days - 1)
    maison_db()
    with sqlite3.connect(MAISON_DB) as con:
        con.row_factory = sqlite3.Row
        cols = {row[1] for row in con.execute("PRAGMA table_info(usage)")}
        if "variation" not in cols:
            con.execute("ALTER TABLE usage ADD COLUMN variation INTEGER DEFAULT 1")
            con.commit()
        rows = [dict(r) for r in con.execute(
            "SELECT id,created_at,sku,category,model,success,input_tokens,output_tokens,variation FROM usage ORDER BY id DESC"
        )]
    records = []
    for row in rows:
        try:
            dt = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
            local = dt.astimezone(tz)
        except (ValueError, TypeError):
            continue
        if start <= local.date() <= end:
            records.append({
                "id": row["id"], "date": local.date().isoformat(),
                "time": local.strftime("%I:%M %p"), "sku": row["sku"],
                "category": row["category"], "success": bool(row["success"]),
                "input_tokens": row["input_tokens"], "output_tokens": row["output_tokens"],
                "variation": row["variation"] or 1,
                "cost_inr": None,
                "estimated_cost_usd": maison_estimate_cost_usd(row["model"], row["input_tokens"], row["success"]),
                "cost_status": "Estimated using published standard rate; not billed amount" if maison_estimate_cost_usd(row["model"], row["input_tokens"], row["success"]) is not None else "Estimate unavailable for this model or request"
            })
    total = len(records)
    retries = sum(r["variation"] > 1 for r in records)
    return {
        "start_date": start.isoformat(), "end_date": end.isoformat(),
        "requests": total, "successful": sum(r["success"] for r in records),
        "regenerations": retries,
        "regeneration_rate": round(retries / total * 100, 1) if total else 0,
        "input_tokens": sum(r["input_tokens"] or 0 for r in records),
        "output_tokens": sum(r["output_tokens"] or 0 for r in records),
        "verified_balance_inr": None,
        "balance_status": "Provider does not expose prepaid wallet balance through generation API",
        "records": records,
    }


# De Maison Decor generated-image archive (30-day retention)
from backend.image_history import router as image_history_router, archive_generated_image, start_history_cleanup
app.include_router(image_history_router)
app.middleware("http")(archive_generated_image)
start_history_cleanup()
