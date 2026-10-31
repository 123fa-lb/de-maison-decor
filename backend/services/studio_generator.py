# V24 INFOGRAPHIC ONLY - Gemini prompt; no workflow changes

# DEMAISON_V22_THREE_GEMINI_PROMPTS

V22_THREE_GEMINI_PROMPTS = {

    "infographic": """Create ONE FINISHED premium editorial e-commerce INFOGRAPHIC IMAGE directly in this ONE paid Gemini image generation request. This is the FINAL deliverable, not a plain source photo for local composition. Follow this exact VISUAL DESIGN SYSTEM inspired by the seller's Tarini candle-holder infographic reference, while depicting ONLY the current uploaded SKU, never candle holders unless the SKU actually is a candle holder.

ART DIRECTION AND COMPOSITION (square 1:1): Photorealistic high-end product advertising, richly detailed and polished, warm natural lighting, elegant cream/beige/taupe or tasteful category-appropriate editorial interior, natural contact shadows, sophisticated premium photography. The actual product is the unmistakable hero, occupying about 60-70% of the main visual area, large on the LEFT/CENTER-LEFT, with correct geometry, true color, finish, count, shape and branding. Do not create duplicate products, extra accessories, fake packaging, or imaginary features. Make the whole hero product clearly identifiable and do not cut off essential parts.

TOP: a large elegant editorial serif-style product title, 1-2 lines, using the seller-provided product name ONLY if actually supplied. Otherwise use a truthful generic category title such as PRODUCT DETAILS; do NOT invent a brand or model name. Beneath it, one restrained short uppercase subtitle using only visible facts or seller-provided information. Maintain generous safe margins.

RIGHT: three VERTICALLY STACKED LARGE ROUND PHOTO MAGNIFIERS, each containing a DIFFERENT REAL, VISIBLE detail of this exact product, with thin white/cream circle borders and thin elegant connector lines/dots pointing to the matching location on the large hero product. Examples are a visible cap or handle, distinctive rim, authentic surface finish, actual carving or joint, or the real base. The round zooms must be large enough to see texture and detail, genuinely different, physically consistent with the hero, and not generic random crops. If the input photos support fewer than three unique features, show fewer honest callouts instead of inventing detail. Under or beside each magnifier put a short bold legible feature heading and a short legible factual explanation, with strong contrast against the background.

BOTTOM: a tasteful horizontal row of 3-4 minimalist line-style feature icons with brief captions ONLY for supported attributes or neutral product-use descriptions; avoid made-up certifications, claims such as 'durable', 'handcrafted', 'premium quality', 'safe', 'eco-friendly', or gifting suitability unless verified. A restrained botanical accent is optional only if it suits the product. Maintain the premium hierarchy of the reference: strong headline, dominant realistic hero, clear circular detail callouts, subtle fine connectors, clean bottom icon strip.

QUALITY RULES: Photorealistic professional campaign-quality image, crisp subject and zoom details, clean legible text with no garbling, proper visual hierarchy and whitespace, no awkward clipping, no overlapping labels, no unrelated decoration, no collage/grid of eight images, no blank white catalog shot. No false material/feature/size claims. Every circle must zoom an actual feature present in the supplied SKU photos. Adapt the setting, text and details intelligently to ANY product category while keeping this premium infographic layout. Render one complete infographic directly in Gemini; NEVER request or imply that a server or Pillow will add circles, arrows, text or layout afterward.""",

    # NOTE (V40): the "closeup" entry below is LEGACY and is no longer used.
    # The Close-up prompt is now built exclusively by
    # backend/services/closeup_prompt.py::build_closeup_prompt().
    "closeup": """Create ONE finished photorealistic premium macro CLOSE-UP directly with Gemini, like the supplied black/gold side-table reference: show the REAL most distinctive visible design feature, such as patterned tabletop/rim, engraved metalwork, texture, joinery, handle, cutwork or genuine lid. Focus feature fills 70-85 percent of image, razor sharp with natural microtexture, realistic premium studio lighting and shallow depth of field, some surrounding product context. NEVER show a generic smooth body crop, fabricated patterns, new components, labels, circles or collage. Retain exact actual SKU appearance.""",

    "dimension": """Create ONE COMPLETE dimension graphic directly with Gemini: entire faithful product visible on clean white, thin black double-headed width and height arrows placed outside the product, depth only when supplied, accurate alignment and readable clean black labels. Use ONLY the exact seller measurements given below, without estimation, rounding or conversion. Use ASCII PERIOD '.' for all decimal numbers: 7.5 is correct, 7,5 is wrong. No additional numbers, feature icons, panels, invented claims or clipped arrows. Output final image with measurement text already rendered.""",

}

# DEMAISON_V19_SIDE_MACRO

V19_TARGETED_INSTRUCTIONS = {

    "side": """MANDATORY SIDE PROFILE FOR IMAGE 2 ONLY. This is NOT a frontal product photo. Reposition the CAMERA by 90 degrees around the vertical axis relative to front view, at the same elevation and approximate distance. The resulting image must have a visibly different outline and reveal the true side thickness, edge, joints, or depth visible from the source, while hiding frontal elements that would not be visible from the side. For cylindrical or rotationally symmetric products (e.g. a bottle), the outer silhouette can legitimately remain similar: show a different actual physical face or the side of its distinctive lid/hinge/handle, if the source supports it. Never manufacture a seam, hinge, logo or back label that cannot be verified. Never mirror or simply rotate the original 2D picture. One fully framed standalone white-background commercial product photo. No text, no collage, no props, no cropped edges.""",

    # LEGACY (V40): not used any more. Close-up prompting lives in closeup_prompt.py.
    "macro": """MANDATORY PRODUCT-DETAIL MACRO FOR IMAGE 7/8 CLOSEUP CATEGORY. Before composing, examine the UPLOADED ORIGINAL PHOTO and identify the strongest real, distinctive, high-information detail. Choose a visible lid mechanism, cap edge, hinge, closure, carved or engraved pattern, ornamental texture, fabric weave, rim, joinery, or other recognizable construction feature. For a plain bottle with a distinctive flip-top cap, prioritize the real cap/closure assembly, the joining seam, and the actual finish, NOT the smooth featureless body. Compose a single intentional editorial macro of that feature: feature dominates 65-85 percent of frame; sharply resolved edges and micro-texture, believable depth of field, neutral seamless background, controlled studio highlights. Preserve actual colors, geometry, brand marks and texture. If the source does not reveal a special mechanism, do NOT invent one; instead use the most distinctive genuinely visible rim, finish or join. No generic smooth-body zoom, lifestyle room, furniture, hands, captions, callout circles, collage, fake details or decorative additions."""

}

# DEMAISON_V18_REVIEW_FIX

V18_REVIEW_QUALITY = {

 'white': "FINAL OUTPUT IS ONE STANDALONE PHOTOGRAPH, not a grid or collage. 1 FRONT: true frontal elevation, 2 SIDE: true lateral profile with obviously different visible surfaces and silhouette, 3 TOP: true overhead flat-lay showing the actual top, 4 THREE-QUARTER: unmistakable 45-degree diagonal showing front and side together. Keep complete object with generous safety margins. The camera itself must move; DO NOT fake angle change by rotating the existing photo in 2D. If hidden geometry is uncertain, do not invent markings, features or impossible structures. Premium seamless white catalog lighting, realistic grounding, accurate color and materials.",

 'dimension': "ONE FULL FINISHED STANDALONE dimension graphic, not collage. Show the whole product with ample white space; black horizontal width arrow and vertical height arrow near corresponding product extents. Depth only if user explicitly supplied it. Never invent dimensions or units. Put ALL arrowheads and every text label at least 12 percent inside canvas boundary. Use only seller-provided numeric values. If values are unclear do not fabricate. Clean typographic hierarchy; avoid duplicate contradictory measurements.",

 'infographic': "ONE FINISHED STANDALONE luxury e-commerce infographic. Product completely visible on left, clean right column with 2-3 round detailed crops of real visible product-specific textures and hardware, slim connecting lines, restrained cream/beige backdrop, high-end editorial typography. ALL text and circles inside safe margins. Never invent materials, features or product claims. No cropped circles, no split image collage, no generic body zooms.",

 # LEGACY (V40): not used for the Close-up request any more.
 'closeup': "ONE SINGLE STANDALONE EXTREME MACRO PHOTO, NOT a whole-product view, NOT a lifestyle scene. First visually identify the single most distinctive AUTHENTIC detail in the actual source photo: engraved pattern, embossed metal, carved grain, visible hinge, intricate cap, woven fibers, ornament or textured finish. Move the virtual camera very close to THAT specific feature. The special feature should fill at least 70 percent of image, tack-sharp with real micro-texture and raking studio lighting; include just a little adjacent edge for context. Clean minimal background, no distracting room, props, flat plain bottle body, generic smooth zoom, labels, collage, text, invented pattern, or product redesign.",

 'lifestyle': "ONE STANDALONE premium realistic interior/product-in-use photo, physically correct proportions, exact source product identity, natural contact shadow, tasteful environment, no collage, no titles or labels. Entire hero product clearly visible."

}

# DEMAISON_V17_REFERENCE_DELIVERABLE

V17_REFERENCE_GUIDE = {

 "white": "ONE INDIVIDUAL catalog photograph only, never a collage or numbered grid. Premium clean white background. Entire product visible, realistic contact shadow, generous safe margins. Match the actual product, color, finish, pattern, count and construction; no invented features. This is a camera angle, not a crop of the same front image. The required camera view is specified below.",

 "dimension": "ONE INDIVIDUAL premium dimension image. Pure white background, full product visible with ample outer space. Thin BLACK dimension arrows outside the silhouette, correct horizontal width and vertical height; depth only if explicitly provided. All labels and arrow tips safely inside the image, with at least 10 percent margins. Only the seller's actual supplied numbers and units, no guessed numbers. No decorative labels, collage or inset panels.",

 "infographic": "ONE INDIVIDUAL premium product infographic. Inspired by high-end furniture catalog styling, not a collage. Elegant ivory/warm beige background. Full uncropped hero product left, two or three circular TRUE product-detail magnifications right, delicate leader lines, readable concise labels grounded in actual photo. Clean balanced hierarchy, safe margins; no cut-off circles, text or product. Do not invent material or performance claims. Adapt styling and features to THIS product, never copy a different example item.",

 # LEGACY (V40): not used for the Close-up request any more.
 "closeup": "ONE INDIVIDUAL premium macro product photograph. Feature the MOST distinctive detail actually visible in the uploaded product photo: engraved texture, patterned top, fine rim, hardware, joint, stitching, weave or finish. Very sharp rich realistic micro-texture and flattering light; show enough contextual edge to recognize the product. No generic plain-body zoom, no text, no split panels, no invented details.",

 "lifestyle": "ONE INDIVIDUAL realistic premium lifestyle photo. Show THIS exact product prominently in an appropriate interior/use scene with believable size, physically plausible contact and natural shadows. Cohesive sophisticated lighting, not an artificial collage. No captions, logos, multiple panels or sidebars. Product fully in frame."

}

# DEMAISON_ALL_GEMINI_V15

V15_ALL_GEMINI_RULES = {

    "white": "DELIVERABLE: exactly ONE premium square catalog photo on pure white #FFFFFF, no captions or props. Camera variation 1: eye-level FRONT; variation 2: strict SIDE profile rotated 90 degrees, not the front view again; variation 3: OVERHEAD top-down at 90 degrees to the product; variation 4: THREE-QUARTER 45-degree perspective. Each view must differ in visible geometry, not merely zoom, background, or crop. Preserve product identity, material, component count, logos, pattern and color. Use available product source views; unseen surfaces from one source image are estimates, not guaranteed accurate. Remove loose dust, fingerprints and photographic artifacts but do not disguise structural defects or invent hidden branding. Entire object visible, no clipping, no multi-panel collage.",

    "lifestyle": "DELIVERABLE: one editorial premium square product-in-use photograph, real believable scale and setting chosen for THIS actual product. Product prominent, clean contact shadows, consistent natural lighting, attractive real interior or other suitable environment. No split layouts, blur sidebars, inset photos, duplicate products, or typography. Preserve exact product geometry and identity.",

    # LEGACY (V40): not used for the Close-up request any more.
    "closeup": "DELIVERABLE: one striking ultra-sharp product MACRO photo showing a meaningful distinguishing feature that is actually visible in source images: texture, carving, finish, joinery, rim, functional detail or branding. Feature fills 75-90 percent of square canvas; retain a small context cue. Do not crop a random smooth midsection or bottom, do not invent decoration. Clean incidental dust, keep genuine product characteristics. No text or collage.",

    "dimension": "DELIVERABLE: a COMPLETE FINAL 1:1 e-commerce DIMENSIONS IMAGE, not a blank source for local compositor. Show the ENTIRE real product large and centered on a pure white background, with thin BLACK double-ended measurement arrows placed just OUTSIDE and aligned to actual visible product edges: width arrow across product's horizontal span, height arrow along full vertical span, depth arrow only if given and meaningful. Use ONLY the EXACT numeric seller-supplied measurements below; never estimate, round, convert or add numbers. Labels in clean black readable type. Arrows must be tied to the actual product silhouette, not floating far away. No other text, extra diagrams, icons, collage, or made-up claims.",

    "infographic": "DELIVERABLE: a FINISHED premium 1:1 ecommerce product infographic, not a plain product image for local compositing. Visual direction: warm tasteful editorial background, very LARGE accurate hero product taking ~60 percent of frame, and a clean right-side vertical column of THREE CIRCULAR MAGNIFIED TRUE PRODUCT FEATURE DETAILS with fine connecting lines. Details must highlight actually visible different features, not random plain crops. Minimal tasteful headline using the verified product description only, concise short factual feature captions grounded in source image or seller notes, legible typography and elegant layout. No imaginary materials, durability, certifications, performance claims, or features. If product has no three distinctive visible details, use fewer honest callouts rather than inventing them. Do not reproduce the example product; adapt layout to the current SKU. ONE finished image, not an eight-panel collage."

}

# DEMAISON_REFERENCE_V14

V14_CATEGORY_RULES = {

'white': "WHITE BACKGROUND PRODUCT VIEW. Return one 1:1 single item on #FFFFFF, no typography, no collage, no extra product. The camera pose MUST correspond to the requested variation: 1 straight FRONT, 2 true 90-degree SIDE PROFILE, 3 directly OVERHEAD TOP DOWN, 4 diagonal 45-degree THREE-QUARTER. Camera orientation must be materially different from previous variations. Preserve identity, original color, label, exact component count and observed texture. If hidden geometry is unknown, approximate cautiously and do not fabricate branding. Clean only loose dust, fingerprints, lint, sensor artifacts; preserve genuine product defects.",

# LEGACY (V40): not used for the Close-up request any more.
'closeup': "MACRO PHOTOGRAPHY ONLY. Show a striking distinctive real detail, e.g. cap, spout, rim, weave, carved pattern, texture, joint, or control; NEVER a plain smooth middle-body or an arbitrary product bottom crop. Fill 85 percent of image with meaningful real detail, include a small recognition cue. 1:1 edge-to-edge, crisp high resolution, no text, no collage, no added parts, no invented decoration. Remove incidental dust and fingerprints, not actual product defects.",

'lifestyle': "ONE realistic, cohesive, full-bleed 1:1 lifestyle product photo. Choose product-appropriate environment, scale, lighting and usage, keep the authentic product as hero. No blur sidebars, white bars, grids, duplicate items, or text. Clean temporary dust and photography noise, not actual defects.",

}

# DEMAISON_REFERENCE_V13

V13_PHOTO_PROMPT = '\nDE MAISON V13 COMMERCIAL PRODUCT PHOTOGRAPHY QUALITY CONTRACT:\nThis product can be ANY retail product, not necessarily furniture, a candle holder or a globe.\nUse reference photographs as ground truth for identity. Preserve real shape, visible materials, silhouette, color, count of parts, labels and texture.\nRemove ONLY superficial dust, loose lint, fingerprints, temporary smudges and sensor noise; do not hide structural damage or alter sale-relevant defects.\nWHITE BACKGROUND: render one complete item on seamless white, no duplicate item, no collage, no text. Different white variations MUST use different camera poses: 1 eye-level FRONT; 2 strict profile SIDE at roughly 90 degrees; 3 OVERHEAD TOP looking down into any opening; 4 elevated THREE-QUARTER roughly 35-45 degrees. Variation 3 must not be an eye-level front shot. For all poses preserve consistent geometry and pattern; if unseen, make only a cautious plausible estimate, never claim it is exact. Keep entire object visible with safe margins.\nCLOSEUP: create ONE exceptional premium macro photograph, NOT a full-object view, NOT a plain featureless middle-body crop. Select the most visually interesting documented detail such as the actual rim, weave, carving, hinge, patterned finish, seam, embossed motif, cap, or joint. Macro subject fills 80-95% of square image, ultra-sharp focus, clean background, controlled reflections, genuine texture, no invented decoration, no collage, no writing. Keep one context cue to recognize the item.\nLIFESTYLE: use an appropriate environment based on actual product use. One square edge-to-edge commercial photograph, product dominant, no artificial blurred vertical strips or fake margins.\nDIMENSION AND INFOGRAPHIC are composited locally from actual product imagery. Gemini must never invent measurements or print marketing labels for those categories.\nOUTPUT: exactly one square professional product photo for this paid request, with no panel grid, labels, text, arrows or watermarks.\n'

# DEMAISON_SINGLE_PHOTO_V11_2

# DEMAISON_IMAGE_SAFETY_V1

import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import Response
from PIL import Image, ImageOps, ImageDraw, ImageFont
from backend.services.infographic_layout import compose_infographic
from backend.services.maison_quality_v7 import prepare_neutral_source, full_bleed_square
from backend.services.maison_client_v8 import make_infographic, make_dimensions, marketplace_square, FINAL_UNIVERSAL_V8, FINAL_CATEGORY_V8
# DEMAISON_CLOSEUP_V40: close-up only (pure-Python helpers, no extra dependencies)
from backend.services.closeup_prompt import build_closeup_prompt
from backend.services.closeup_analysis import analyze_feature, feature_crop
from backend.services.closeup_crop import finalize_closeup, assess_closeup

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

router = APIRouter(prefix="/api/studio", tags=["Maison Studio"])

CATEGORIES = {

    "lifestyle": "Lifestyle",

    "infographic": "Infographic",

    "white": "White Background",

    "closeup": "Close-up",

    "dimension": "Dimension",

}

BASE_PROMPT = """

You are a senior luxury product photographer and commercial retoucher.

The uploaded images show ONE REAL PRODUCT from different angles.

Treat these reference photographs as the absolute source of truth.

NON-NEGOTIABLE PRODUCT ACCURACY:

- Preserve exact product identity, silhouette, proportions and structure.

- Preserve colors, materials, patterns, logos, labels and finishes.

- Preserve transparent, reflective, thin and delicate components.

- Never invent handles, legs, lids, decorations, text or attachments.

- Never replace the product with a visually similar product.

- Never alter the number of visible physical components.

- If a detail is unclear, do not fabricate it.

- The final result must be realistic premium commercial photography.

- Product should be sharp, clean and visually dominant.

- Avoid visual artifacts, distortions, duplicate products and watermarks.

Use all provided reference images to understand the product.

For white-background work, prioritize exact structural fidelity over beauty.

Do not silently correct or redesign real product characteristics.

Generate ONE finished image, not a collage.

"""

CATEGORY_PROMPTS = {

    "lifestyle": """

ROLE:

You are an expert commercial product photographer specializing

in premium home decor and e-commerce photography.

TASK:

Create ONE photorealistic lifestyle image featuring the exact

physical product shown in the supplied reference photographs.

STEP 1 — UNDERSTAND THE PRODUCT:

Identify the product category, intended use, visible materials,

finish, construction, silhouette, colors and distinguishing details.

Treat all reference photographs as evidence of ONE actual product.

Do not assume a specific product category in advance.

STEP 2 — PRESERVE PRODUCT IDENTITY:

The real product must remain the hero of the photograph.

Preserve:

- Exact visible shape and proportions.

- Original material, color and surface finish.

- Distinctive contours, patterns, textures and decorative details.

- All visible handles, openings, lids, supports and attachments.

- Genuine transparency, reflections and surface characteristics.

Never:

- Replace the product with a similar-looking item.

- Add or remove physical components.

- Smooth away distinctive product features.

- Change its color or finish to suit the room.

- Invent labels, patterns, decorations or branding.

- Distort the product to fit the composition.

If a product detail is unclear, avoid inventing it.

STEP 3 — CHOOSE THE ENVIRONMENT:

Automatically select a believable premium setting appropriate

to the actual product and its intended use.

For home decor, consider elegant contemporary interiors,

tasteful shelves, consoles, side tables, dining areas,

entryways or other contextually suitable placements.

For non-decor products, choose a setting consistent with their use.

Do not place every product in the same room.

Do not add unrelated props or visual clutter.

Keep background styling secondary to the product.

STEP 4 — MATERIAL-AWARE LIGHTING:

Use professional soft directional lighting plus restrained fill light.

For dark products:

Reveal contours, texture and construction without turning

black surfaces gray or washing out their original color.

For glass and transparent materials:

Maintain transparency, realistic refraction and visible edges.

For reflective metals:

Use controlled highlights while preserving the real finish.

For ceramics, stone, wood and textiles:

Reveal authentic glaze, grain, texture and surface characteristics.

Avoid:

- Crushed shadows hiding important product details.

- Overexposed highlights.

- Artificial plastic-looking surfaces.

- Dramatic lighting that obscures the product.

STEP 5 — PREMIUM COMPOSITION:

- Make the product immediately recognizable and visually dominant.

- Use believable scale, perspective and contact shadows.

- Keep important product features unobstructed.

- Allow enough separation between product and background.

- Maintain an editorial, refined, realistic photographic look.

- Choose an attractive angle without changing product geometry.

- Avoid unnecessary empty space and distracting foreground props.

- Do not create collages, text overlays or watermarks.

FINAL QUALITY CHECK:

Before finishing, prioritize:

1. Product identity and structural accuracy.

2. Product visibility and material fidelity.

3. Realistic placement and lighting.

4. Premium photographic presentation.

The result must look like the SAME actual product photographed

in a professionally styled environment, not a redesigned product.

""",

    "infographic": """

Generate one faithful, high-quality studio photograph of the

EXACT real product in the supplied reference images.

This image will be placed inside a separately controlled infographic.

Preserve original shape, materials, color, texture, proportions,

visible construction and distinctive design details.

Use a clean near-white neutral studio background.

Show the full product large, centered, sharp and unobstructed.

Keep fine details visible with soft professional lighting.

Absolutely NO typography, SKU, numbers, diagrams, circles,

pointers, arrows, icons, labels, captions, watermarks or props.

Do not invent features, specifications or product components.

Output one product photograph only.

""",

    "white": """

TASK: Faithfully retouch the photographed product into a clean

professional white-background e-commerce photograph.

THIS IS AN IMAGE EDITING TASK, NOT PRODUCT REDESIGN.

ABSOLUTE PRIORITY: PRODUCT IDENTITY.

- Preserve the exact physical product from the reference photographs.

- Preserve its original height-to-width ratio and body silhouette.

- Preserve the cap, nozzle, lid, hinge, handle and every visible attachment.

- Preserve the original cap angle and its construction.

- Do not replace the cap with a cleaner or more fashionable design.

- Preserve original surface finish, subtle texture and material appearance.

- Preserve genuine manufacturing characteristics.

- Do not make an imperfect product artificially perfect.

- Do not narrow, widen, shorten or lengthen the product.

- Do not invent or remove product components.

- Do not change branding, labels, colors or materials.

- Do not change the viewing angle unnecessarily.

BACKGROUND AND PRESENTATION:

- Replace the surrounding environment with pure white (#FFFFFF).

- Keep the product fully visible, centered and upright.

- Use restrained professional studio lighting.

- Add only a very soft realistic contact shadow beneath the product.

- Maintain accurate product edges and fine details.

- No props, decorations, typography, logos or watermarks.

IMPORTANT:

The final photograph should look like the SAME physical product

photographed in a professional studio, not an AI-generated replacement.

""",

    # LEGACY (V40): not used for the Close-up request any more.
    "closeup": """

Create ONE premium, photorealistic, tightly framed

commercial MACRO DETAIL photograph of the EXACT

product shown in the uploaded reference images.

PRIMARY GOAL:

Show one authentic, distinctive product feature in

beautiful, sharp detail. This is a DETAIL IMAGE,

not a full-product photograph.

COMPOSITION:

- Choose a real feature clearly visible in the references.

- For bottles, prioritize the original cap, lid,

  drinking opening, neck or closure mechanism.

- For other products, prioritize their actual craftsmanship,

  material finish, rim, edge, handle or decorative detail.

- Frame the chosen feature as the visual hero.

- The chosen feature and its immediate surrounding structure

  should occupy approximately 70-85% of the frame.

- Crop tightly and intentionally around that feature.

- Show only enough surrounding product to establish identity.

- Avoid showing long sections of the main product body.

- Keep the complete selected feature inside the image.

- Use a visually balanced, editorial macro composition.

- Avoid excessive empty space above or beside the product.

BACKGROUND:

- Seamless, neutral, softly blurred studio background.

- No tables, floors, platforms, fabrics or props.

- No scenery or decorative objects.

- Background must never compete with the product.

LIGHTING AND QUALITY:

- Luxury commercial product-detail photography.

- Sharp, realistic detail on the selected feature.

- Soft directional studio lighting.

- Controlled highlights and realistic shadows.

- Natural material texture without exaggeration.

- Clean, refined e-commerce presentation.

STRICT PRODUCT ACCURACY:

- Match the actual reference product.

- Preserve its real shape, color, material and construction.

- Never invent cap mechanisms, openings or other components.

- Never add or remove physical parts.

- Never invent textures, engravings, seams or markings.

- Do not change the product's proportions.

- Do not replace the original product with a similar design.

IMPORTANT:

A genuine, slightly wider detail is always better than

an invented extreme macro view.

OUTPUT:

One polished product-detail photograph.

No text, logos added by AI, labels, graphics,

collages, borders or watermarks.

""",

    "dimension": """

Create one accurate full-product studio photograph of the EXACT

reference product for a verified size-information listing image.

Preserve the real product silhouette, proportions, color, materials,

construction and all visible details.

Keep the complete product visible and centered against a clean

light-neutral background, with room around its edges.

Do not draw dimension arrows, lines, measurements, labels, text,

numbers, scales, diagrams or additional products.

The application will add ONLY actual user-provided measurements.

Never guess dimensions or physical specifications.

""",

}

# DEMAISON_EXACT_V5: universal e-commerce image composition guidance.

QUALITY_GUIDANCE = {

    "white": """E-COMMERCE HERO IMAGE: Square 1:1 composition. True pure-white (#FFFFFF) seamless background, without borders, panels, frames or letterboxing. One full product, centered, upright and comfortably large (roughly 75-85% of image height for tall objects, or width for wide objects) with clear safety margin on every side. Do not crop edges, handles, feet, petals, thin elements or accessories that genuinely belong to the item. Preserve exact original geometry, finish, material, color, printed marks and authentic details. Do not create a new or idealized variant. Soft realistic contact shadow only.""",

    "lifestyle": """E-COMMERCE LIFESTYLE PHOTO: Deliver a cohesive square 1:1 photograph filling the entire frame edge-to-edge, with NO white sidebars, artificial margins, split panels or pasted-in product cutout. First identify the actual product and intended use from references. For home decor, choose a tasteful, believable room/shelf/console/dining or entryway context appropriate to THIS item; for other items choose their real use context. Product remains prominent, physically grounded at plausible scale with correct contact shadows and realistic lighting. Preserve all real colors, shape, patterns, construction, finish and components. No unrelated props hiding the item, no extra copies, no typography. Do not invent a different product.""",

    # LEGACY (V40): not used for the Close-up request any more.
    "closeup": """E-COMMERCE MACRO DETAIL: Compose a full-bleed square 1:1 real-looking close-up with NO white bars, picture borders or collage. Select ONE distinctive physical feature that is clearly visible in the supplied references (for home decor, an actual rim, texture, carving, joinery, weave, finish, base or ornament, as applicable). Feature should be large, sharp and easy to inspect, but fully inside the frame. Do not hallucinate hidden mechanisms, engravings, seams, materials or text. Natural optical depth of field, professional studio lighting, consistent original color and finish. If references do not resolve a tiny feature, choose a wider truthful crop instead of inventing detail.""",

    "infographic": """E-COMMERCE INFOGRAPHIC SOURCE ONLY: Produce a single square 1:1 clean studio photograph, NOT a designed infographic. Full exact product large and centered with generous safe margins, even neutral near-white background, visible real texture and details, no text/arrows/badges/panels. Do not change shape or components. The application will create the infographic layout deterministically from this image.""",

    "dimension": """E-COMMERCE DIMENSION SOURCE ONLY: Produce one square 1:1 clean studio product photograph. Entire real product must be clearly visible and centered, with safety space around every edge and no cropping, stretching or added parts. Neutral near-white background; preserve true proportions, materials and colors. NO dimension lines, text, numbers or diagrams: the application adds only user-entered measurements. Do not infer physical measurements from the photograph.""",

}

# DEMAISON_ADAPTIVE_V6: same-call reference-aware e-commerce photography.
# This is prompt guidance, not a separate classifier or additional paid request.

ADAPTIVE_PRODUCT_GUIDANCE = """

REFERENCE-FIRST COMMERCIAL IMAGE WORKFLOW (perform internally, no written analysis):

A. IDENTIFY THE REAL OBJECT FROM ALL REFERENCE PHOTOS BEFORE COMPOSING.

Determine its actual purpose, shape, orientation, scale cues, visible component count,

materials, finish, construction, openings, supports, decorations and any readable marks.

It may be ANY retail product. Home decor is common but NEVER assume it is a vase,

lamp, tray or bottle unless the actual reference establishes that identity.

If references disagree or a detail is obscured, keep the best-supported visible detail;

do not fabricate unseen surfaces or mechanically impossible structures.

B. PRESERVE PRODUCT IDENTITY ABOVE AESTHETICS.

The generated product must match the SAME physical item, not a similar catalogue item.

Keep exact silhouette, visible proportions, distinctive asymmetry, count of pieces,

colour, material, ornament, weave, carvings, grain, glazing, reflections, transparency,

logos and real imperfections. No extra handles, feet, flowers, lids, cables, motifs,

engraving, printed words or components. No changed cap or opening. No warped geometry.

Never transform one object into a different category or invent a complete set from one item.

C. ADAPT PHOTOGRAPHY TO THE ACTUAL MATERIAL AND USE.

Ceramic/stone: preserve glaze, pores and texture. Wood/rattan: preserve grain and weave.

Glass: true transparency, edge definition and realistic refraction. Metal: correct

specular highlights and finish. Fabric: authentic weave, folds and pattern.

Dark products: reveal contours without changing black to grey. Pale products: preserve

edge separation without tinting them. Reflective surfaces: controlled studio reflections.

For home decor, choose a physically plausible premium interior only for LIFESTYLE,

matching the object's function (wall art mounted on wall, tabletop decor on surface,

lighting in realistic placement, etc.). For other products, use their real usage context.

Never choose a generic setting that makes the object implausible or mis-scaled.

D. DELIVER MARKETPLACE-APPROPRIATE PHOTOGRAPHY.

One clear hero product, professional realistic light, sharp true details, natural shadows,

no watermark, duplicate, collage, extra text, stretched item or artificial borders.

A beautiful but inaccurate product is a FAILED result: prioritize fidelity instead.

Do not insert a fake measurement, claim, feature, logo, price, or label.

"""

ADAPTIVE_CATEGORY_RULES = {

    'white': 'Keep ONLY the actual product on pure #FFFFFF; full product and real accessories if truly attached, no room or props, no crop. Product should be visually large while retaining a clear safety margin.',

    'lifestyle': 'One natural full-frame photograph of the actual product in a context appropriate to its true function; background is supporting, never hiding or replacing the product. No white sidebars.',

    # LEGACY (V40): not used for the Close-up request any more.
    'closeup': 'Choose a real feature clearly visible in the reference photographs. Show its true finish and construction sharply; if insufficient detail, use a wider truthful detail view rather than inventing macro texture.',

    'infographic': 'Only one faithful neutral-background product source photo, large and completely visible. The app adds infographic graphics separately; AI must not add any graphics or text.',

    'dimension': 'Only one faithful neutral-background full-product source photo with space around all edges. The app adds the user-supplied measurements; AI must not guess or draw dimensions.',

}

# DEMAISON_FINAL_QUALITY_V7: category-specific reference-fidelity finishing rules.

FINAL_V7_GUIDANCE = {

    'white': "Commercial marketplace HERO, 1:1 SQUARE frame. Treat the first reference as the primary visual identity. Remove ONLY the environment. Exact object, same silhouette, color, surface wear, number of components, rim, handle, stitching, weave, carvings, lids, attachments and imperfections. One product fully visible and large, pure #FFFFFF background, no props, no lettering, no decorative shadows. Never replace the real item with an idealized version.",

    'lifestyle': "Generate a true full-bleed 1:1 SQUARE photograph, not a portrait photo later put into a square. Choose a natural, tasteful setting that fits the ACTUAL product's function: home decor in appropriate real interiors, other merchandise in its own credible setting. Keep product fully visible and clearly recognizable, not blocked by props. Correct scale, physical contact, natural soft light. Preserve every original identifying detail. No vertical panels, side strips, borders, typography or invented parts.",

    # LEGACY (V40): not used for the Close-up request any more.
    'closeup': "True 1:1 SQUARE macro detail of a feature visibly documented in the reference. Do not invent microscopic detail or mechanisms. For stitched or woven items, preserve real stitch direction and count where visible. For lids, closures and openings, reproduce actual geometry rather than a generic substitute. Use a slightly wider real feature view if a tighter crop would require inventing unseen detail. Full-bleed, sharp, faithful color and material, no side panels or captions.",

    'infographic': "Provide ONLY a large, exact product on uniform light neutral background for the deterministic infographic compositor. No text, claims, extra panels, arrows or synthetic feature closeups. Keep the complete object in frame. Distinctive details must match references.",

    'dimension': "Provide ONLY a complete large product on uniform neutral studio background, accurate real silhouette, no cropping and no guessed measurements. The app adds only actual user-entered dimensions. No arrows, text, rulers or size claims from AI.",

}

def verified_dimension_image(image, width, height, depth, unit):

    from PIL import Image, ImageDraw, ImageFont, ImageOps
    import math

    SIZE = 2000
    BG = "#F8F7F4"
    INK = "#242424"
    MUTED = "#77736D"
    LINE = "#494741"
    ACCENT = "#B7A58A"

    def font(size, bold=False):

        candidates = (

            [r"C:\Windows\Fonts\arialbd.ttf",
             r"C:\Windows\Fonts\segoeuib.ttf"]

            if bold else

            [r"C:\Windows\Fonts\arial.ttf",
             r"C:\Windows\Fonts\segoeui.ttf"]

        )

        for candidate in candidates:

            try:

                return ImageFont.truetype(candidate, size)

            except OSError:

                pass

        return ImageFont.load_default()

    def measurement(value):

        return str(value).strip() if value is not None else ""

    width = measurement(width)
    height = measurement(height)
    depth = measurement(depth)
    unit = measurement(unit) or "cm"

    if not any((width, height, depth)):

        return image

    board = Image.new("RGB", (SIZE, SIZE), BG)
    d = ImageDraw.Draw(board)

    title_font = font(73, True)
    small_font = font(27)
    value_font = font(55, True)
    label_font = font(28, True)
    footer_font = font(23)

    # Premium editorial heading

    d.text((125, 100), "PRODUCT DIMENSIONS",
           font=title_font, fill=INK)

    d.text((128, 200), "SIZE & PROPORTIONS",
           font=small_font, fill=MUTED)

    d.line((125, 257, 1875, 257), fill="#D9D5CD", width=3)

    # Clean, large product presentation.
    # Fill the entire photo panel with the original image.
    # No artificial white side strips or decorative outer frame.

    photo = image.convert("RGB")

    panel = (405, 355, 1510, 1530)
    px1, py1, px2, py2 = panel
    pw, ph = px2-px1, py2-py1

    # Keep the entire photo visible: never crop product edges.

    fitted = ImageOps.contain(photo, (pw, ph), Image.Resampling.LANCZOS)
    fw, fh = fitted.size
    fx = px1 + (pw - fw) // 2
    fy = py1 + (ph - fh) // 2

    board.paste(fitted, (fx, fy))

    # Detect dark product bounds for better arrow alignment.
    # Fall back to the photo bounds for light-colored products.

    thumb = fitted.copy()
    thumb.thumbnail((220, 220))
    tw, th = thumb.size
    pixels = thumb.load()
    detected = []

    for yy in range(th):

        for xx in range(tw):

            r, g, b = pixels[xx, yy]

            if max(r, g, b) < 110:

                detected.append((xx, yy))

    if len(detected) >= 35:

        xs = [p[0] for p in detected]
        ys = [p[1] for p in detected]
        left = fx + int(min(xs) * fw / tw)
        right = fx + int(max(xs) * fw / tw)
        top = fy + int(min(ys) * fh / th)
        bottom = fy + int(max(ys) * fh / th)

        if right-left < 100 or bottom-top < 150:

            left, right, top, bottom = fx, fx+fw, fy, fy+fh

    else:

        left, right, top, bottom = fx, fx+fw, fy, fy+fh

    def arrowhead(x, y, angle, size=17):

        spread = 0.46

        pts = [

            (x, y),

            (x-size*math.cos(angle-spread),
             y-size*math.sin(angle-spread)),

            (x-size*math.cos(angle+spread),
             y-size*math.sin(angle+spread))

        ]

        d.polygon(pts, fill=LINE)

    # Height measurement on the left

    if height:

        ax = 310
        ay1 = max(355, top)
        ay2 = min(1530, bottom)

        d.line((ax, ay1, ax, ay2), fill=LINE, width=4)
        arrowhead(ax, ay1, -math.pi/2)
        arrowhead(ax, ay2, math.pi/2)

        d.line((ax+24, ay1, max(ax+38, left-15), ay1),
               fill="#B8B3AA", width=3)

        d.line((ax+24, ay2, max(ax+38, left-15), ay2),
               fill="#B8B3AA", width=3)

        htext = f"{height} {unit}"
        bbox = d.textbbox((0, 0), htext, font=value_font)
        text_h = bbox[3]-bbox[1]
        mid_y = (ay1+ay2)//2

        d.rounded_rectangle(

            (70, mid_y-55, 285, mid_y+55),

            radius=15, fill=BG

        )

        d.text((178, mid_y-8), htext,
               font=value_font, fill=INK, anchor="mm")

        d.text((178, mid_y+35), "HEIGHT",
               font=small_font, fill=MUTED, anchor="mm")

    # Width measurement below the photo

    if width:

        wy = 1620
        wx1 = max(415, left)
        wx2 = min(1500, right)

        if wx2-wx1 < 120:

            wx1, wx2 = 640, 1270

        d.line((wx1, wy, wx2, wy), fill=LINE, width=4)
        arrowhead(wx1, wy, math.pi)
        arrowhead(wx2, wy, 0)

        d.line((wx1, min(bottom+12, 1580), wx1, wy-18),
               fill="#B8B3AA", width=3)

        d.line((wx2, min(bottom+12, 1580), wx2, wy-18),
               fill="#B8B3AA", width=3)

        d.text(((wx1+wx2)//2, 1680), f"{width} {unit}",
               font=value_font, fill=INK, anchor="mm")

        d.text(((wx1+wx2)//2, 1734), "WIDTH",
               font=small_font, fill=MUTED, anchor="mm")

    # Depth as an independent specification, not a fake perspective arrow

    if depth:

        d.rounded_rectangle(

            (1550, 580, 1875, 805),

            radius=22, fill="#EEECE6",

            outline="#D9D3C8", width=2

        )

        d.text((1590, 624), "DEPTH",
               font=label_font, fill=MUTED)

        d.text((1590, 690), f"{depth} {unit}",
               font=value_font, fill=INK)

        d.line((1590, 773, 1835, 773),
               fill=ACCENT, width=4)

    # Footer

    d.line((125, 1835, 1875, 1835),
           fill="#D9D5CD", width=3)

    d.text((125, 1870), "DIMENSIONS PROVIDED BY USER",
           font=footer_font, fill=MUTED)

    d.text((1875, 1870), "PRODUCT SPECIFICATIONS",
           font=footer_font, fill=MUTED, anchor="ra")

    return board

@router.post("/generate")
async def generate(

    files: list[UploadFile] = File(...),
    category: str = Form(...),
    sku: str = Form("Product"),
    note: str = Form(""),
    width: str = Form(""),
    height: str = Form(""),
    depth: str = Form(""),
    unit: str = Form("cm"),
    variation: int = Form(1),

):

    from google import genai
    from google.genai import types
    from backend.main import maison_record

    # V11.2: one product photo accepted; camera angles synthesized as needed.

    if category == "white" and variation not in (1, 2, 3, 4):

        raise HTTPException(422, "White variation must be between 1 and 4")

    if category not in CATEGORIES:

        raise HTTPException(400, "Invalid category")

    if not files or len(files) > 6:

        raise HTTPException(400, "Provide 1 to 6 reference images")

    if category == "dimension" and not any(

        str(v).strip() for v in (width, height, depth)

    ):

        raise HTTPException(422, "Dimension images require real measurements")

    key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image").strip()

    if not key:

        raise HTTPException(503, "Gemini API key not configured")

    try:

        parts = []
        closeup_refs = []  # V41: full-resolution copies, Close-up only

        for file in files:

            data = await file.read(20 * 1024 * 1024 + 1)

            if not data or len(data) > 20 * 1024 * 1024:

                raise ValueError("Invalid reference image or image exceeds 20 MB")

            with Image.open(BytesIO(data)) as source:

                if source.width * source.height > 50_000_000:

                    raise ValueError("Reference image dimensions too large")

                image = ImageOps.exif_transpose(source).convert("RGB")
                if category == "closeup":
                    hi_res = image.copy()
                    hi_res.thumbnail((3000, 3000))
                    closeup_refs.append(hi_res)
                image.thumbnail((1600, 1600))

                buffer = BytesIO()
                image.save(buffer, "JPEG", quality=92)

                parts.append(

                    types.Part.from_bytes(

                        data=buffer.getvalue(),

                        mime_type="image/jpeg",

                    )

                )

        prompt = (

            BASE_PROMPT

            + "\n" + CATEGORY_PROMPTS[category] + "\n" + QUALITY_GUIDANCE[category]

            + f"\nAdditional user instructions: {note or 'None'}"

        )

        if category == "dimension":

            prompt += (

                "\nActual user-provided measurements exist. "

                "Do not draw measurement numbers yourself."

            )

        # DEMAISON_ADAPTIVE_V6: adapt to any actual product without extra API calls.

        prompt += "\n" + ADAPTIVE_PRODUCT_GUIDANCE
        prompt += "\nCATEGORY-SPECIFIC CHECK: " + ADAPTIVE_CATEGORY_RULES[category]

        # Variation changes framing/lighting only, NEVER the physical product.

        prompt += (f"\nImage variation {max(1, min(int(variation), 30))}: "

                   "if a different image is requested, vary only camera composition "

                   "and lighting within this category. Keep the identical real item. "

                   "Do not force a new view that is unsupported by the references.")

        # DEMAISON_FINAL_QUALITY_V7

        prompt += "\nFINAL CATEGORY PHOTO REQUIREMENT: " + FINAL_V7_GUIDANCE[category]
        prompt += "\nOutput must be a SQUARE 1:1 photo with the SAME physical product. Product accuracy is more important than creative styling."

        # DEMAISON_CLIENT_REQUIREMENTS_V8
        # One compact, authoritative prompt per image, without extra AI calls.

        prompt = (FINAL_UNIVERSAL_V8 + "\n\nCATEGORY: " + category

                  + "\n" + FINAL_CATEGORY_V8[category]

                  + f"\nVariation number: {max(1, min(int(variation), 30))}. "

                    "Follow the category-specific variation rule only when references support it.")

        if note and note.strip():

            prompt += "\nVerified seller notes (avoid unverified marketing claims): " + note.strip()[:600]

        # V11.2: generate a distinct view even if only a front photo exists.

        if category == "white":

            angles = {1: "FRONT", 2: "SIDE", 3: "TOP", 4: "THREE-QUARTER"}

            prompt += ("\nREQUIRED WHITE BACKGROUND CAMERA VIEW: " + angles[variation]

                       + ". Make this angle visibly distinct from other requested angles. "

                       + "The source image establishes product identity, color, visible details and material. "

                       + "Unseen geometry is an approximation: never invent unsupported logos, "

                       + "decorations, mechanisms, attachments or printed text. "

                       + "Keep the whole product in a clean pure-white 1:1 studio photograph.")

        # DEMAISON_REFERENCE_V13: paid image prompt, no extra calls.

        prompt += V13_PHOTO_PROMPT
        prompt += "\n" + V14_CATEGORY_RULES.get(category, "")

        # DEMAISON_ALL_GEMINI_V15: image-specific final creative direction.

        prompt += "\nFINAL V15 DELIVERABLE INSTRUCTIONS: " + V15_ALL_GEMINI_RULES.get(category, "")

        if category == "dimension":

            actual = [("width", width), ("height", height), ("depth", depth)]
            provided = [f"{name}: {str(value).strip()} {unit}" for name, value in actual if str(value or "").strip()]

            if not provided:

                raise HTTPException(422, "Enter actual dimensions before a paid dimension image request.")

            prompt += "\nSELLER VERIFIED MEASUREMENTS (use exactly, no others): " + "; ".join(provided)

        if category == "infographic":

            prompt += "\nProduct name / verified features ONLY from uploaded source photos and seller note. If no product name provided, use neutral title PRODUCT DETAILS."

        # V17 final image-specific instructions (one paid request -> one individual image).

        prompt += "\n\nV17 FINAL DELIVERABLE: " + V17_REFERENCE_GUIDE.get(category, "")

        if category == "white":

            views = {1:"FRONT: eye-level, product facing camera", 2:"SIDE: true 90-degree profile, distinct visible silhouette", 3:"TOP: direct overhead 90-degree downward camera", 4:"THREE QUARTER: diagonal 45-degree perspective"}
            prompt += "\nMANDATORY DISTINCT CAMERA POSE: " + views.get(variation, "FRONT")

        prompt += "\nNEVER output an 8-panel reference sheet. ONE final image for this request. Do not crop or truncate the product, arrows, captions or circular details."

        # V18: final category-specific, reference-style quality direction.

        prompt += "\n\nV18 FINAL IMAGE QUALITY REQUIREMENTS: " + V18_REVIEW_QUALITY.get(category, "")
        prompt += "\nOutput ONE standalone final image for this request. Never output multi-panel contact sheet or numbered collage. Ensure all graphic elements are safely inside the canvas."

        # V19: focused correction only. Keep other categories and dimension logic untouched.
        # V40: the former `elif category == "closeup"` macro directive was removed;
        # the Close-up prompt is now built once, at the end, by build_closeup_prompt().

        if category == "white" and variation == 2:

            prompt += "\n\nV19 FINAL SIDE VIEW DIRECTIVE: " + V19_TARGETED_INSTRUCTIONS["side"]

        # DEMAISON_V22_THREE_GEMINI_PROMPTS: infographic and dimension only (V40: closeup excluded).

        if category in V22_THREE_GEMINI_PROMPTS and category != "closeup":

            prompt += "\n\nFINAL CATEGORY-SPECIFIC GEMINI IMAGE DIRECTION: " + V22_THREE_GEMINI_PROMPTS[category]

        if category == "dimension":

            exact_values = []

            for field_name, field_value in (("width", width), ("height", height), ("depth", depth)):

                raw_value = str(field_value or "").strip()

                if raw_value:

                    exact_values.append(f"{field_name}: {raw_value.replace(',', '.')} {unit}")

            if not exact_values:

                raise HTTPException(422, "Enter seller dimensions before generating the paid Gemini dimensions image.")

            prompt += "\nEXACT SELLER MEASUREMENTS (ASCII DOT DECIMALS): " + "; ".join(exact_values)
            prompt += "\nUse only these numbers and exact decimal punctuation in the final image."

        # DEMAISON_V25_INFOGRAPHIC_FINAL_ONLY: overrides conflicting older infographic directions.

        if category == "infographic":

            prompt += """

FINAL HIGHEST-PRIORITY INSTRUCTION FOR THIS ONE INFOGRAPHIC IMAGE:

Produce ONE fully designed, premium, photorealistic E-COMMERCE INFOGRAPHIC in a single paid Gemini image-generation request. The final image itself MUST contain the finished layout, typography, circular detail insets, and icons. Do NOT produce a plain product photo for later server composition. Do NOT output a collage of separate images.

VISUAL REFERENCE TO MATCH IN DESIGN QUALITY AND COMPOSITION (adapt to the uploaded product, do not copy candle holders): luxury home-decor editorial advertising; rich warm photographic environment, realistic surfaces, tasteful depth of field and beautiful directional lighting; a large hero product occupying approximately the left 60-70% of the image, naturally grounded on a surface; premium spacious headline at top; a column of THREE distinct circular macro-detail insets down the right, each with a thin high-contrast ring, precise white connector line to the correct physical part of the hero product, a short bold heading and a readable concise supporting phrase; elegant bottom row of three or four small line-art feature icons with short captions, visually integrated into the photograph, NOT inside a flat rectangular banner. Beautiful typography and carefully aligned margins, readable on a phone. The target is an upscale, art-directed product advertisement, NOT a generic beige catalog infographic.

ADAPT TO ANY PRODUCT CATEGORY: choose a believable tasteful setting that suits the actual uploaded product (for example kitchen counter, desk, bedroom, dining table, bathroom shelf, or appropriate neutral luxury environment). Never force candles, a wooden table, gold, warm flames, or home-decor wording onto an unrelated product. Preserve the exact number of items shown in the uploaded SKU, their identity, silhouette, materials, color, finish, proportions, logos and physical design. Do not add or remove accessories, lids, handles or parts. Avoid covering the product with text or circles.

THREE CALLOUTS: pick THREE DIFFERENT, visually evident features of THIS product from the uploaded photos (e.g. real cap/handle, visible texture, real base). Each circle must actually show a crisp zoom of its own real feature, not three similar blank dark patches. Keep circles large enough to understand and do not repeat the same area. Never invent cutwork, fasteners, insulation, waterproofing, leakproofing, temperature retention, food safety, material grade, manufacturing method, or other unverifiable specifications. If only two distinct details are visible, use a third honest alternative view of a visible real detail, without invented claims.

TEXT RULES: use a short elegant product/category title based only on known seller-provided information; never invent a brand or model name. Use concise legible labels describing visible physical traits only. Do not claim 'leak-proof', 'powder-coated', 'cold and hot liquids', 'premium quality', 'handcrafted', 'durable', or other performance claims unless the seller explicitly provided that information. Bottom icons must be relevant and truthful, and may use neutral visible attributes instead of claims. No garbled, misspelled, tiny, clipped or overlapping text. Keep all circles, labels, lines, icons and product fully inside the frame.

FINAL ART DIRECTION: prioritize photorealistic rich lighting, realistic shadows, high-end composition, clean hierarchy, three bright distinct macro circles, premium typography, and readable detail descriptions. Make it visually comparable to a professionally art-directed luxury product infographic, rather than a template pasted over a plain studio photo. One complete final infographic image only.

"""

        # DEMAISON_V28_INFOGRAPHIC_FINAL_LAYOUT_ONLY

        if category == "infographic":

            prompt += "\n\nFINAL INFOGRAPHIC INSTRUCTION V28 — highest priority for infographic only; replace conflicting earlier infographic art directions. Produce ONE finished premium e-commerce infographic image with the PAID GEMINI IMAGE GENERATION request already being made. Use uploaded product photos as the only source of product identity and visual facts. Use the supplied candle-holder design reference for visual sophistication and composition, not its actual products or text.\n\nCOMPOSITION: A realistic softly blurred premium home/lifestyle scene suitable for the actual product, tasteful rich lighting, warm but natural tones, real contact shadows. Large faithfully reproduced hero product on LEFT (about 55% width); three vertically aligned circular genuine detail close-ups on RIGHT, with thin clean white connector lines pointing to the correct visible source location. Refined editorial serif headline and short sans-serif subheading at top. Small elegant feature-icon row at bottom. NO OUTER BORDER OR FRAME. NO WHITE STRIP OR BOX behind footer. No panels, collage, watermark or fake brand. Keep every element within comfortable safe margins.\n\nSTRICT NON-OVERLAPPING GRID: Divide the right-hand annotation column into three separate vertical bands with reserved space for a circle and its own caption. Each band: circle first, bold short heading DIRECTLY BELOW, then ONE short readable description BELOW heading. Leave clear vertical gap before next circle. NEVER place a circle, connector, caption, or background decoration over ANY text. No captions crossing circle boundaries. If space is tight, reduce circle diameter or shorten captions rather than overlap. All three circle captions must be complete and visible. Keep connectors behind the callouts and away from letters.\n\nTHREE GENUINELY DIFFERENT FEATURES: First show the most distinctive upper feature (such as cap/hinge/handle/rim). Second show another genuinely interesting visible structural detail (neck joint, seam, handle attachment, textured cutwork, engraving or edge) — NEVER a featureless black patch. Third show a DIFFERENT visible lower feature such as the real base/underside. Each circle must depict the same real product and show meaningful magnified detail, not a generic repeated body crop. Do not invent parts or hidden mechanisms. If fewer than three meaningful features are visible, repeat no fake features: use fewer well-supported callouts rather than fabricating.\n\nTEXT AND TYPOGRAPHY: Large refined editorial SERIF headline with clean spelling; a restrained smaller sans-serif subtitle; callout titles bold and readable; descriptions medium-size sans-serif, 3–6 ordinary words, high contrast. Use precise simple phrases to minimize spelling mistakes. No microscopic labels, truncated words, strange line breaks, duplicate letters or spelling errors. Every callout has its own complete title and description.\n\nTRUTHFUL CONTENT ONLY: Do not infer or state stainless steel, BPA-free, leak-proof, non-slip, sustainable, insulated, anti-tip, durable, temperature retention, medical/safety or performance claims from a photo. Such claims are permitted ONLY if explicitly supplied in the seller's instructions. If the actual material is not confirmed, describe visible shape, color or design instead. For a matte black bottle with a visible lid and base, safe examples include 'Carry Loop', 'Matte Black Surface', 'Rounded Base' — use only what is truly visible. Avoid invented product names. Footer icons and labels must also be visibly supported, not generic promises.\n\nFINAL SELF-CHECK BEFORE RENDERING: no outer white border; no caption overlap; no empty or featureless detail circles; three distinct real details when supported; complete readable captions; no unsupported material or performance claims; no product distortion; no text clipped by image edge. This is ONE paid Gemini image request, no extra calls or retries.\n"

        # DEMAISON_V30_INFOGRAPHIC_ONLY_START

        if category == "infographic":

            prompt += """

FINAL INFOGRAPHIC ART DIRECTION ? OVERRIDES EARLIER

INFOGRAPHIC STYLING INSTRUCTIONS.

Generate ONE complete premium product infographic

using the paid Gemini image model.

REFERENCE STYLE:

A luxurious editorial product advertisement with the

visual sophistication of a premium home-decor catalogue.

COMPOSITION:

- A beautiful realistic lifestyle environment appropriate

  to the actual product.

- The product is physically placed within the scene,

  not pasted into a rectangular photo box.

- Large hero product occupying the left and center.

- Three circular photographic detail callouts on the right.

- Thin elegant connector lines.

- Beautiful natural lighting, rich colors and realistic shadows.

- No outer border, no rectangular photo panels.

- No empty placeholder boxes or generic template appearance.

PRODUCT ACCURACY:

- Preserve the exact product identity, appearance, color,

  proportions, visible components and quantity.

- Adapt the scene to the product category.

- Do not copy candle holders into another product's image.

- Every circular close-up must show a real, distinct,

  visually meaningful part of the uploaded product.

- Avoid three similar crops of a plain surface.

- For simple objects, prioritize distinctive components,

  edges, joins, openings, handles, closures and bases.

- Never fabricate hidden mechanisms or unseen details.

PREMIUM TYPOGRAPHY:

- Large elegant editorial serif product headline.

- Refined, clearly readable sans-serif feature headings.

- Professional hierarchy, balanced spacing and contrast.

- Product-specific title based only on known information.

- No generic PRODUCT DETAILS heading when a reliable

  product name is available.

- No text overlap, cropped letters or broken words.

TEXT ACCURACY:

- Use the fewest words necessary.

- Prefer three short feature headings and no long descriptions.

- Use only straightforward, correctly spelled words.

- Each heading must correspond to its actual circular detail.

- Do not invent product materials, performance, safety,

  certifications, dimensions or durability claims.

- Never claim BPA-free, insulated, leak-proof, non-slip,

  stainless steel or sustainable without verified seller data.

- Proofread all visible text before finalizing the image.

- If a description is uncertain, omit it rather than invent it.

BOTTOM DESIGN:

- Use three small elegant feature icons only when meaningful.

- Avoid generic marketing claims.

- Integrate icons naturally with the scene and typography.

- No white rectangular icon strip.

QUALITY:

- Premium commercial photography and sophisticated layout.

- Natural photorealistic materials and lighting.

- Beautiful, polished, uncluttered and ready for client review.

- ONE complete infographic image, not a collage.

- Gemini must generate the entire image.

- Do not use local composition or text overlays.

"""

        # DEMAISON_V30_INFOGRAPHIC_ONLY_END

        # DEMAISON_DIMENSION_ONLY_START

        if category == "dimension":

            prompt += """

FINAL DIMENSION IMAGE INSTRUCTIONS:

Generate ONE premium e-commerce dimension image entirely

using the paid Gemini image API.

REFERENCE STYLE:

- Pure white background.

- Preserve the real uploaded product exactly.

- Clean, professional product photography.

- Thin BLACK measurement arrows with arrowheads at both ends.

- Clear labels next to each arrow.

- No decorative icons, marketing claims or infographic panels.

MEASUREMENT LAYOUT:

- LENGTH: bottom horizontal double-headed arrow.

- BREADTH: diagonal/depth-direction double-headed arrow.

- HEIGHT: right-side vertical double-headed arrow.

- Adapt arrow positions to actual product orientation.

- Do not obscure the product.

- Use only the exact seller-entered measurements.

- Never estimate dimensions from the photo.

- Preserve decimal points exactly, for example 7.5 cm.

- NEVER replace decimal dots with commas.

- Do not add extra measurements.

- If a dimension is not supplied, do not invent a value.

OUTPUT:

- ONE complete dimension image generated by Gemini.

- No local image composition.

"""

        # DEMAISON_DIMENSION_ONLY_END

        # DEMAISON_DIMENSION_ARROWS_V2_START

        if category == "dimension":

            prompt += """

FINAL DIMENSION ARROW RULES:

Generate ONE clean dimension image using Gemini.

- Pure white background.

- Preserve the exact uploaded product.

- Use thin BLACK double-headed measurement arrows.

- Every arrow must have a clear arrowhead at BOTH ends.

- Length: horizontal arrow below the product.

- Height: vertical arrow to the right.

- Breadth: diagonal depth-direction arrow ONLY when

  a valid breadth measurement is provided AND a distinct

  depth dimension is meaningful for this product.

- For round or cylindrical products where breadth is

  the same as length, do not duplicate the diameter arrow.

- Never invent a missing breadth value.

- Position arrows outside the product silhouette.

- Keep labels close to their corresponding arrows.

- Use exact seller-provided measurements and units.

- Preserve decimal dots, e.g. 7.5 cm, never 7,5 cm.

- No extra text, icons, infographic design or decorations.

- Gemini generates the entire image.

"""

        # DEMAISON_DIMENSION_ARROWS_V2_END

        # DEMAISON_CLOSEUP_V40_PROMPT_START
        # Single authoritative Close-up prompt. This REPLACES (does not append to)
        # everything assembled above for this category, and supersedes the former
        # V31 / V34 / V36 / V37 close-up blocks, which contradicted each other.
        # Still exactly ONE paid Gemini image request; no retries.
        if category == "closeup":
            prompt = build_closeup_prompt(note)
        # DEMAISON_CLOSEUP_V40_PROMPT_END

        parts.append(types.Part.from_text(text=prompt))

        client = genai.Client(api_key=key)

        # DEMAISON_CLOSEUP_V41_ANALYSIS_START
        # Close-up only. ONE small text-only request picks the feature; its box becomes
        # a reference crop for the single paid image request. Any failure falls back to
        # the single-request prompt. Disable with DEMAISON_CLOSEUP_ANALYSIS=0.
        closeup_mode = "single"
        if category == "closeup":
            # Optional: use a different (e.g. higher-resolution) image model for Close-up ONLY.
            closeup_model_override = os.getenv("GEMINI_CLOSEUP_IMAGE_MODEL", "").strip()
            if closeup_model_override:
                model = closeup_model_override
        if category == "closeup" and os.getenv("DEMAISON_CLOSEUP_ANALYSIS", "1").strip() != "0":
            try:
                analysis = analyze_feature(
                    client, types, list(parts[:-1]),
                    os.getenv("GEMINI_ANALYSIS_MODEL", "gemini-2.5-flash").strip(), note,
                )
                if analysis:
                    crop_img, crop_info = feature_crop(closeup_refs, analysis)
                    if crop_img is not None:
                        crop_buf = BytesIO()
                        crop_img.save(crop_buf, "JPEG", quality=95)
                        crop_part = types.Part.from_bytes(data=crop_buf.getvalue(), mime_type="image/jpeg")
                        if os.getenv("DEMAISON_CLOSEUP_INCLUDE_FULL_REFS", "0").strip() == "1":
                            parts.insert(0, crop_part)
                            closeup_mode = "analysis+crop"
                        else:
                            # DEFAULT: send ONLY the feature crop. Full-product photos pull the
                            # model toward a whole-product portrait, so they are left out.
                            parts[:] = [crop_part, parts[-1]]
                            closeup_mode = "crop-only"
                    else:
                        closeup_mode = "analysis"
                    print(f"[MAISON STUDIO] {sku}/closeup feature={analysis['feature_name']!r} mode={closeup_mode} crop={crop_info}", flush=True)
                    parts[-1] = types.Part.from_text(
                        text=build_closeup_prompt(
                            note, analysis,
                            has_crop=crop_img is not None,
                            crop_only=(closeup_mode == "crop-only"),
                        )
                    )
            except Exception as ana_exc:
                print(f"[MAISON STUDIO] {sku}/closeup analysis skipped: {ana_exc}", flush=True)
        # DEMAISON_CLOSEUP_V41_ANALYSIS_END

        # DEMAISON_CLOSEUP_V40_CONFIG_START
        # Close-up only: ask the model for a native 1:1 canvas so no local crop or
        # padding is needed. Building the config is a local operation (no API call);
        # if the installed google-genai SDK lacks ImageConfig, the original config is used.
        config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )
        if category == "closeup":
            try:
                image_config_cls = getattr(types, "ImageConfig", None)
                if image_config_cls is not None:
                    # Optional higher resolution (e.g. "2K"). OFF unless the env var is set,
                    # because not every image model accepts it.
                    size_opt = os.getenv("DEMAISON_CLOSEUP_IMAGE_SIZE", "").strip()
                    img_kwargs = {"aspect_ratio": "1:1"}
                    if size_opt:
                        img_kwargs["image_size"] = size_opt
                    config = types.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"],
                        image_config=image_config_cls(**img_kwargs),
                    )
            except Exception as cfg_exc:
                print(f"[MAISON STUDIO] {sku}/closeup: aspect_ratio config unavailable ({cfg_exc}); using default", flush=True)
                config = types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                )
        # DEMAISON_CLOSEUP_V40_CONFIG_END

        response = client.models.generate_content(

            model=model,

            contents=[

                types.Content(

                    role="user",

                    parts=parts,

                )

            ],

            config=config,

        )

        result_bytes = None

        for candidate in response.candidates or []:

            if not candidate.content:

                continue

            for part in candidate.content.parts or []:

                inline = getattr(part, "inline_data", None)

                if inline and inline.data:

                    result_bytes = inline.data
                    break

            if result_bytes:

                break

        if not result_bytes:

            raise ValueError("Gemini returned no image")

        closeup_qa_header = None

        with Image.open(BytesIO(result_bytes)) as generated:

            generated = ImageOps.exif_transpose(generated).convert("RGB")

            # DEMAISON_EXACT_V5: preserve the full product in every category.
            # Generated pixels are not assumed to be native 2000x2000.

            generated = ImageOps.exif_transpose(generated).convert("RGB")
            source = generated.copy()

            # V15: Gemini supplies the finished composition for ALL five categories.
            # Never overlay another infographic or measurement arrows on the model result.
            # Non-white images should fill square without blurred sidebars.

            canvas = source  # V17: preserve native Gemini framing

            # DEMAISON_CLOSEUP_V40_POST_START
            # No cropping. Framing is decided by Gemini only. We pad to square only if
            # the model returned a non-square image, and run advisory (log/header only)
            # quality checks. Any failure here falls back to the untouched Gemini image.
            if category == "closeup":
                try:
                    canvas, closeup_finalize = finalize_closeup(source)
                    closeup_report = assess_closeup(canvas)
                    closeup_flags = closeup_report.get("flags") or []
                    closeup_qa_header = ",".join(closeup_flags) if closeup_flags else "ok"
                    print(
                        f"[MAISON STUDIO] {sku}/closeup QA: {closeup_report} finalize={closeup_finalize}",
                        flush=True,
                    )
                except Exception as qa_exc:
                    canvas = source
                    closeup_qa_header = "qa_unavailable"
                    print(f"[MAISON STUDIO] {sku}/closeup post-process skipped: {qa_exc}", flush=True)
            # DEMAISON_CLOSEUP_V40_POST_END

            output = BytesIO()
            canvas.save(output, "JPEG", quality=95, subsampling=0)

        usage = getattr(response, "usage_metadata", None)

        maison_record(

            sku,

            category,

            model,

            True,

            int(getattr(usage, "prompt_token_count", 0) or 0),

            int(getattr(usage, "candidates_token_count", 0) or 0),

            variation=variation,

        )

        response_headers = {"Cache-Control": "no-store"}
        response_headers["X-DeMaison-SKU"] = str(sku)[:180]
        response_headers["X-DeMaison-Category"] = str(category)[:60]
        if closeup_qa_header:
            response_headers["X-Closeup-QA"] = closeup_qa_header
            response_headers["X-Closeup-Mode"] = closeup_mode

        return Response(

            content=output.getvalue(),

            media_type="image/jpeg",

            headers=response_headers,

        )

    except Exception as exc:

        maison_record(sku, category, model, False, variation=variation)
        print(f"[MAISON STUDIO] {sku}/{category}: {exc}", flush=True)

        raise HTTPException(

            502,

            f"Generation failed: {str(exc)[:350]}",

        )

# DEMAISON_CLIENT_FINAL_V10: No Gemini calls for dimension/infographic composition.

@router.post("/compose-local")
async def compose_local(

    file: UploadFile = File(...),
    category: str = Form(...),
    sku: str = Form("Unassigned"),
    width: str = Form(""),
    height: str = Form(""),
    depth: str = Form(""),
    unit: str = Form("cm"),

):

    if category not in ("dimension", "infographic"):

        raise HTTPException(400, "Only dimension and infographic supported")

    data = await file.read(20 * 1024 * 1024 + 1)

    if not data or len(data) > 20 * 1024 * 1024:

        raise HTTPException(400, "Invalid image size")

    try:

        with Image.open(BytesIO(data)) as im:

            if im.width * im.height > 50_000_000:

                raise ValueError("Image dimensions too large")

            src = ImageOps.exif_transpose(im).convert("RGB")

        if category == "dimension":

            values = (width, height, depth)

            if not all(str(v).strip() and 0 < float(v) < 100000 for v in values):

                raise ValueError("Provide real positive width, height and depth")

            if unit not in ("cm", "mm", "in"):

                raise ValueError("Unsupported measurement unit")

            canvas = make_dimensions(src, width, height, depth, unit)

        else:

            canvas = make_infographic(src)

        if canvas.size != (2000, 2000):

            raise ValueError("Invalid output dimensions")

        buf = BytesIO()
        canvas.save(buf, format="JPEG", quality=95, subsampling=0)

        return Response(content=buf.getvalue(), media_type="image/jpeg", headers={"Cache-Control":"no-store", "X-DeMaison-SKU": str(sku)[:180], "X-DeMaison-Category": str(category)[:60]})

    except (ValueError, OSError) as exc:

        raise HTTPException(422, str(exc))
