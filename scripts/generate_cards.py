"""Genera tarjetas Astro Reachy, 100 × 141 mm a 300 dpi, listas para imprimir."""
from __future__ import annotations
import json
from pathlib import Path
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT, BACKGROUND = ROOT / "assets" / "cards", ROOT / "assets" / "visuals" / "deep-space.png"
PLANETS = ROOT / "assets" / "planets"
OUT.mkdir(parents=True, exist_ok=True)
SIZE = (1200, 1700)  # 100 × 141,7 mm a 300 dpi
PALETTES = {"Sol":(255,184,60),"Mercurio":(174,162,152),"Venus":(237,178,101),"Tierra":(73,163,222),"Luna":(201,207,217),"Marte":(211,91,57),"Júpiter":(220,170,116),"Saturno":(226,201,125),"Urano":(111,211,219),"Neptuno":(64,104,218),"Más información":(120,106,255),"Otro planeta":(75,219,181)}

def font(size: int, bold: bool = False):
    return ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf", size)

def centered(draw, text, y, use_font, fill):
    box = draw.textbbox((0, 0), text, font=use_font)
    draw.text(((SIZE[0] - (box[2] - box[0])) / 2, y), text, font=use_font, fill=fill)

def planet_art(draw, name, color):
    cx, cy, radius = 600, 620, 230
    draw.ellipse((cx-radius-25,cy-radius-25,cx+radius+25,cy+radius+25), outline="#d2e0ff", width=3)
    draw.ellipse((cx-radius,cy-radius,cx+radius,cy+radius), fill=color, outline="#ffefbe", width=5)
    if name == "Tierra":
        draw.ellipse((455,480,600,620), fill="#47b263"); draw.ellipse((635,650,725,745), fill="#47b263")
    elif name == "Júpiter":
        for y in range(470,760,56): draw.rounded_rectangle((395,y,805,y+20), 10, fill="#a76d4e")
        draw.ellipse((635,590,740,660), fill="#b64c34")
    elif name == "Saturno": draw.ellipse((325,580,875,700), outline="#ef dca7".replace(" ",""), width=32)
    elif name == "Marte":
        draw.ellipse((475,490,550,555), fill="#9f3c28"); draw.ellipse((620,670,705,725), fill="#9f3c28")
    elif name == "Sol":
        for offset in range(20,110,30): draw.ellipse((cx-radius-offset,cy-radius-offset,cx+radius+offset,cy+radius+offset), outline="#ffc749", width=5)
    elif name in {"Más información", "Otro planeta"}: centered(draw, "✦", 485, font(250), "white")

def planet_photo(card, draw, image_key, name, color, index):
    """Inserta una fotografía NASA circular y cambia la decoración en cada tarjeta."""
    if name in {"Más información", "Otro planeta"}:
        planet_art(draw, name, color)
        return
    source = Image.open(PLANETS / f"{image_key}.jpg").convert("RGB")
    source = ImageEnhance.Contrast(source).enhance(1.12)
    source = ImageOps.fit(source, (460, 460), method=Image.Resampling.LANCZOS)
    mask = Image.new("L", (460, 460), 0)
    ImageDraw.Draw(mask).ellipse((5, 5, 455, 455), fill=255)
    # Halo y órbita: rotación y color únicos según planeta.
    cx, cy = 600, 620
    draw.ellipse((350, 370, 850, 870), fill="#050b24", outline="#dbe7ff", width=4)
    if index % 3 == 0:
        draw.ellipse((280, 535, 920, 705), outline="#91baff", width=8)
    elif index % 3 == 1:
        draw.arc((300, 390, 900, 850), 210, 335, fill="#ffcf7c", width=8)
        draw.arc((300, 390, 900, 850), 25, 145, fill="#7fcfff", width=4)
    else:
        for r in (255, 285): draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline="#9fa9ff", width=3)
    card.paste(source, (370, 390), mask)
    draw.ellipse((370, 390, 830, 850), outline=color, width=7)

items = json.loads((ROOT / "data" / "objects.json").read_text(encoding="utf-8"))
items.extend([{"name":"Más información","qr_id":"MAS_001"},{"name":"Otro planeta","qr_id":"OTRA_001"}])
for item in items:
    name, qr_id = item["name"], item["qr_id"]
    background = ImageOps.fit(Image.open(BACKGROUND).convert("RGB"), SIZE, method=Image.Resampling.LANCZOS).convert("RGBA")
    # Cada reverso incorpora una versión desenfocada de su propia fotografía,
    # así ninguna tarjeta comparte exactamente el mismo cielo.
    if qr_id not in {"MAS_001", "OTRA_001"}:
        photo_bg = ImageOps.fit(Image.open(PLANETS / f"{qr_id.split('_')[0]}.jpg").convert("RGB"), SIZE, method=Image.Resampling.LANCZOS)
        photo_bg = photo_bg.filter(ImageFilter.GaussianBlur(24)).convert("RGBA")
        photo_bg.putalpha(105)
        background = Image.alpha_composite(background, photo_bg)
    card = Image.alpha_composite(background, Image.new("RGBA", SIZE, (5,9,30,105)))
    # Tinte propio por astro: hace reconocible cada tarjeta incluso antes de leer el título.
    card = Image.alpha_composite(card, Image.new("RGBA", SIZE, (*PALETTES[name], 24)))
    draw = ImageDraw.Draw(card)
    centered(draw,"ASTRO REACHY",75,font(34,True),"#dbe8ff"); centered(draw,"TARJETA DE EXPLORACIÓN",125,font(18,True),"#8fb2e8")
    planet_photo(card, draw, qr_id.split("_")[0], name, PALETTES[name], items.index(item)); centered(draw,name.upper(),895,font(78,True),"white")
    centered(draw,"MUESTRA ESTA TARJETA A REACHY" if qr_id not in {"MAS_001","OTRA_001"} else "RESPUESTA PARA REACHY",997,font(24,True),"#bcd0ff")
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=4); qr.add_data(qr_id); qr.make(fit=True)
    qr_image = qr.make_image(fill_color="#071227",back_color="white").convert("RGBA"); qr_image.thumbnail((490,490),Image.Resampling.LANCZOS)
    draw.rounded_rectangle((300,1085,900,1595),34,fill="white",outline="#cadbff",width=7); card.alpha_composite(qr_image,((SIZE[0]-qr_image.width)//2,1100))
    centered(draw,qr_id,1615,font(27,True),"#d8e5ff"); card.convert("RGB").save(OUT/f"{qr_id}.png",dpi=(300,300))
print(f"{len(items)} tarjetas Astro Reachy creadas en {OUT}")
