import os
from PIL import Image, ImageFilter, ImageDraw, ImageOps, ImageEnhance
import numpy as np
import cv2
import colorsys
import math

# 🔮 REAL AURA PHOTOBOTH COLOR MEANINGS (from industry standards)
AURA_DICT = {
    "red": "Energetic, fiery, passionate, confident, action-oriented",
    "orange": "Creative, enthusiastic, social, adventurous, positive",
    "yellow": "Optimistic, intellectual, joyful, charismatic, playful",
    "green": "Loving, compassionate, nurturing, ambitious, holistic thinker",
    "pink": "Kind, caring, romantic, generous, gentle",
    "blue": "Calm, intuitive, spiritual, insightful, protective",
    "purple": "Intuitive, mystical, inspired, visionary, empathic",
    "indigo": "Sensitive, spiritually attuned, psychic",
    "white": "Pure, wise, spiritually connected, healer",
    "black": "Protective, introspective, grounded, sometimes tired",
    "rainbow": "Energized, dynamic, in transition, high creative flow",
    "gray": "Neutral, reserved, reflective energy"
}

def _rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*tuple(int(x) for x in rgb))

def map_rgb_to_aura(hex_rgb):
    """
    Map hex color to nearest aura color using HSV distance.
    Returns (name, meaning)
    """
    h_rgb = hex_rgb.lstrip('#')
    r, g, b = tuple(int(h_rgb[i:i+2], 16) for i in (0, 2, 4))
    h, s, v = colorsys.rgb_to_hsv(r/255., g/255., b/255.)
    hue_deg = h * 360

    # Enhanced mapping based on real aura booths
    if v < 0.1:
        name = "black"
    elif 0 <= hue_deg < 15 or hue_deg >= 345:
        name = "red"
    elif 15 <= hue_deg < 45:
        name = "orange"
    elif 45 <= hue_deg < 80:
        name = "yellow"
    elif 80 <= hue_deg < 160:
        name = "green"
    elif 160 <= hue_deg < 200:
        name = "blue"
    elif 200 <= hue_deg < 270:
        name = "purple"
    elif 270 <= hue_deg < 320:
        name = "pink"
    elif 320 <= hue_deg < 345:
        name = "indigo"
    else:
        name = "gray"

    # If saturation is very low, consider it gray/black
    if s < 0.1 and v > 0.1:
        name = "gray"

    # Rainbow if multiple colors are present? (for future)
    # For now, we use dominant color

    meaning = AURA_DICT.get(name, "Balanced energy")
    return name, meaning

def analyze_colors(image_path, k=3):
    """
    Return list of dominant colors as hex strings using kmeans.
    """
    im = Image.open(image_path).convert("RGB")
    im.thumbnail((250, 250))
    ar = np.array(im).reshape((-1, 3)).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.2)
    _, labels, centers = cv2.kmeans(ar, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = centers.astype(int)
    hexes = [_rgb_to_hex(c) for c in centers]
    return hexes

def _detect_subject_bbox_cv(image_path):
    """
    Detect subject bbox using contour method.
    Returns (x, y, w, h)
    """
    img = cv2.imread(image_path)
    if img is None:
        return 0,0,img.shape[1], img.shape[0]
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9,9), 0)
    edges = cv2.Canny(blur, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 0,0,w,h
    largest = max(contours, key=cv2.contourArea)
    x,y,ww,hh = cv2.boundingRect(largest)
    pad = int(0.2 * max(ww, hh))
    x = max(0, x-pad); y = max(0, y-pad)
    ww = min(w-x, ww+2*pad); hh = min(h-y, hh+2*pad)
    return x,y,ww,hh

def generate_aura_image(input_path, output_path, filter_name="none", caption=""):
    """
    Creates a true Polaroid-style aura image.
    """
    base = Image.open(input_path).convert("RGBA")
    w, h = base.size

    # Get dominant colors
    dom = analyze_colors(input_path, k=3)
    tints = []
    for hx in dom:
        r = int(hx[1:3], 16); g = int(hx[3:5], 16); b = int(hx[5:7], 16)
        # Make pastel by blending with white
        pr = int((r + 255) / 2); pg = int((g + 255) / 2); pb = int((b + 255) / 2)
        tints.append((pr, pg, pb, 130))
    extras = [(255,182,193,110), (173,216,230,110), (255,250,205,110)]
    while len(tints) < 3:
        tints.append(extras[len(tints) % len(extras)])

    # Detect subject center
    x,y,ww,hh = _detect_subject_bbox_cv(input_path)
    cx = x + ww//2
    cy = y + hh//2
    max_radius = int(max(ww, hh) * 2.2)

    # Create aura layer
    aura_layer = Image.new("RGBA", base.size, (0,0,0,0))
    for i, color in enumerate(tints):
        radius = int(max_radius * (0.4 + 0.6 * (i / max(1, len(tints)-1))))
        ellipse = Image.new("RGBA", base.size, (0,0,0,0))
        dd = ImageDraw.Draw(ellipse)
        bbox = [cx-radius, cy-radius, cx+radius, cy+radius]
        dd.ellipse(bbox, fill=color)
        blur_amount = 18 + i*8
        ellipse = ellipse.filter(ImageFilter.GaussianBlur(blur_amount))
        aura_layer = Image.alpha_composite(aura_layer, ellipse)

    # Add outer glow ring
    ring = Image.new("RGBA", base.size, (0,0,0,0))
    rd = ImageDraw.Draw(ring)
    ring_radius = int(max_radius * 1.05)
    rd.ellipse([cx-ring_radius, cy-ring_radius, cx+ring_radius, cy+ring_radius], outline=(255,255,255,80), width=6)
    ring = ring.filter(ImageFilter.GaussianBlur(10))
    aura_layer = Image.alpha_composite(aura_layer, ring)

    # Vintage background
    background = Image.new("RGBA", base.size, (252,245,236,255))
    blended = Image.alpha_composite(background, aura_layer)

    # Composite subject with feathered mask
    mask = Image.new("L", base.size, 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([x, y, x+ww, y+hh], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(30))
    combined = Image.composite(base, blended, mask=ImageOps.invert(mask.convert("L")))

    # Apply filter
    if filter_name == "bw":
        combined = combined.convert("L").convert("RGBA")
    elif filter_name == "warm":
        enhancer = ImageEnhance.Color(combined)
        combined = enhancer.enhance(1.15)
    elif filter_name == "retro":
        combined = combined.filter(ImageFilter.GaussianBlur(0)).convert("RGBA")
        combined = Image.blend(combined, Image.new("RGBA", combined.size, (255, 230, 200, 40)), 0.12)

    # Add Polaroid frame
    pad_x = 60; pad_y = 120
    frame = Image.new("RGBA", (w + pad_x*2, h + pad_y*2), (255,255,255,255))
    frame.paste(combined, (pad_x, pad_y), combined)
    frame = frame.filter(ImageFilter.GaussianBlur(0.6))

    # Add caption
    if caption:
        draw = ImageDraw.Draw(frame)
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = None
        text_x = pad_x + 16
        text_y = pad_y + h + 10
        draw.text((text_x, text_y), caption, fill=(60,60,60), font=font)

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    frame.convert("RGB").save(output_path, quality=92)
    return output_path