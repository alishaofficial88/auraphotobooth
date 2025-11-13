import os
from PIL import Image, ImageFilter, ImageDraw, ImageOps, ImageEnhance
import numpy as np
import cv2
import colorsys
import math

# 🔮 ENHANCED AURA COLOR MEANINGS
AURA_DICT = {
    "red": "Energetic, confident, passionate, strong-willed, action-oriented",
    "orange": "Creative, adventurous, enthusiastic, social, positive",
    "yellow": "Optimistic, intellectual, joyful, charismatic, playful",
    "green": "Loving, compassionate, nurturing, ambitious, healing",
    "pink": "Kind, romantic, generous, gentle, affectionate",
    "blue": "Calm, intuitive, spiritual, insightful, communicative",
    "purple": "Intuitive, mystical, inspired, visionary, empathic",
    "indigo": "Sensitive, spiritually attuned, psychic, deep",
    "violet": "Visionary, idealistic, spiritually connected",
    "white": "Pure, wise, enlightened, spiritually connected",
    "gold": "Enlightened, inspired, protected, abundant",
    "rainbow": "Dynamic, multi-talented, in transition, high creative flow"
}

def _rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*tuple(int(x) for x in rgb))

def map_rgb_to_aura(hex_rgb):
    """
    Enhanced color mapping based on real aura photography principles.
    """
    h_rgb = hex_rgb.lstrip('#')
    r, g, b = tuple(int(h_rgb[i:i+2], 16) for i in (0, 2, 4))
    h, s, v = colorsys.rgb_to_hsv(r/255., g/255., b/255.)
    hue_deg = h * 360

    # Enhanced aura color mapping
    if v < 0.15:
        name = "black"
    elif s < 0.2 and v > 0.8:
        name = "white"
    elif s < 0.3:
        name = "white" if v > 0.7 else "gray"
    elif 0 <= hue_deg < 15 or hue_deg >= 345:
        name = "red"
    elif 15 <= hue_deg < 40:
        name = "orange"
    elif 40 <= hue_deg < 70:
        name = "yellow"
    elif 70 <= hue_deg < 160:
        name = "green"
    elif 160 <= hue_deg < 200:
        name = "blue"
    elif 200 <= hue_deg < 250:
        name = "purple"
    elif 250 <= hue_deg < 290:
        name = "violet"
    elif 290 <= hue_deg < 330:
        name = "pink"
    elif 330 <= hue_deg < 345:
        name = "indigo"
    else:
        name = "rainbow"

    # Special cases for gold/white auras
    if 40 <= hue_deg < 70 and s > 0.6 and v > 0.8:
        name = "gold"

    meaning = AURA_DICT.get(name, "Balanced and harmonious energy")
    return name, meaning

def analyze_colors(image_path, k=3):
    """
    Return list of dominant colors as hex strings using kmeans.
    """
    im = Image.open(image_path).convert("RGB")
    im.thumbnail((300, 300))
    ar = np.array(im).reshape((-1, 3)).astype(np.float32)
    
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.2)
    _, labels, centers = cv2.kmeans(ar, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    # Get color frequencies
    unique, counts = np.unique(labels, return_counts=True)
    color_weights = dict(zip(unique, counts))
    
    centers = centers.astype(int)
    hexes = [_rgb_to_hex(c) for c in centers]
    
    # Sort by frequency (most dominant first)
    hexes_with_weights = [(hexes[i], color_weights.get(i, 0)) for i in range(len(hexes))]
    hexes_with_weights.sort(key=lambda x: x[1], reverse=True)
    
    return [h[0] for h in hexes_with_weights]

def _detect_subject_bbox_cv(image_path):
    """
    Enhanced subject detection with better contour handling.
    """
    img = cv2.imread(image_path)
    if img is None:
        h, w = 400, 400  # Default dimensions
        return w//4, h//4, w//2, h//2
    
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Multiple blur levels for better edge detection
    blur1 = cv2.GaussianBlur(gray, (7, 7), 0)
    blur2 = cv2.GaussianBlur(gray, (15, 15), 0)
    
    edges1 = cv2.Canny(blur1, 30, 100)
    edges2 = cv2.Canny(blur2, 10, 50)
    edges = cv2.bitwise_or(edges1, edges2)
    
    # Morphological operations to close gaps
    kernel = np.ones((5, 5), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        # Fallback: center region
        return w//4, h//4, w//2, h//2
    
    # Combine significant contours
    significant_contours = [c for c in contours if cv2.contourArea(c) > (w * h * 0.01)]
    
    if not significant_contours:
        return w//4, h//4, w//2, h//2
    
    # Create combined mask
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, significant_contours, -1, 255, -1)
    
    # Find bounding box of combined mask
    x, y, ww, hh = cv2.boundingRect(mask)
    
    # Add padding
    pad = int(0.15 * max(ww, hh))
    x = max(0, x - pad)
    y = max(0, y - pad)
    ww = min(w - x, ww + 2 * pad)
    hh = min(h - y, hh + 2 * pad)
    
    return x, y, ww, hh

def _create_aura_gradient(center_x, center_y, colors, size, max_radius):
    """
    Create a beautiful gradient aura effect.
    """
    aura_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    
    for i, color in enumerate(colors):
        # Create gradient rings
        radius = int(max_radius * (0.3 + 0.7 * (i / max(1, len(colors)-1))))
        
        # Create gradient mask
        gradient = Image.new("L", (radius*2, radius*2), 0)
        draw = ImageDraw.Draw(gradient)
        
        # Draw gradient circles
        for r in range(radius, 0, -10):
            alpha = int(255 * (1 - (r / radius)) * 0.6)
            bbox = [radius - r, radius - r, radius + r, radius + r]
            draw.ellipse(bbox, fill=alpha)
        
        # Create color layer
        color_layer = Image.new("RGBA", size, color)
        
        # Apply gradient mask
        gradient = gradient.resize((radius*2, radius*2))
        mask_layer = Image.new("L", size, 0)
        mask_layer.paste(gradient, (center_x - radius, center_y - radius))
        
        # Composite with blur
        color_layer.putalpha(mask_layer)
        color_layer = color_layer.filter(ImageFilter.GaussianBlur(15 + i*5))
        
        aura_layer = Image.alpha_composite(aura_layer, color_layer)
    
    return aura_layer

def generate_aura_image(input_path, output_path, filter_name="none", caption=""):
    """
    Creates a professional Polaroid-style aura image.
    """
    try:
        base = Image.open(input_path).convert("RGBA")
        w, h = base.size
        
        # Get dominant colors with enhanced analysis
        dom_colors = analyze_colors(input_path, k=4)
        
        # Convert to aura colors with better pastel blending
        aura_colors = []
        for hex_color in dom_colors[:3]:  # Use top 3 colors
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            
            # Enhanced pastel blending for softer auras
            blend_ratio = 0.7  # More pastel
            pr = int(r * blend_ratio + 255 * (1 - blend_ratio))
            pg = int(g * blend_ratio + 255 * (1 - blend_ratio))
            pb = int(b * blend_ratio + 255 * (1 - blend_ratio))
            
            # Adjust alpha for layered effect
            alpha = 120 - len(aura_colors) * 20
            aura_colors.append((pr, pg, pb, max(60, alpha)))
        
        # Add some magical colors if needed
        magical_colors = [
            (255, 223, 186, 100),  # Soft gold
            (186, 225, 255, 90),   # Soft blue
            (255, 186, 253, 80)    # Soft pink
        ]
        
        while len(aura_colors) < 3:
            aura_colors.append(magical_colors[len(aura_colors)])
        
        # Detect subject
        x, y, ww, hh = _detect_subject_bbox_cv(input_path)
        cx = x + ww // 2
        cy = y + hh // 2
        max_radius = int(max(ww, hh) * 2.5)
        
        # Create aura effect
        aura_layer = _create_aura_gradient(cx, cy, aura_colors, base.size, max_radius)
        
        # Add outer glow
        glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(glow)
        glow_radius = int(max_radius * 1.1)
        
        # Multi-layer glow
        for i in range(3):
            radius = glow_radius + i * 10
            alpha = 40 - i * 10
            bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
            draw.ellipse(bbox, outline=(255, 255, 255, alpha), width=8)
        
        glow = glow.filter(ImageFilter.GaussianBlur(15))
        aura_layer = Image.alpha_composite(aura_layer, glow)
        
        # Create vintage background
        bg_gradient = Image.new("RGBA", base.size)
        bg_draw = ImageDraw.Draw(bg_gradient)
        
        # Soft gradient background
        for i in range(h):
            ratio = i / h
            r = int(252 - ratio * 20)
            g = int(245 - ratio * 15)
            b = int(236 - ratio * 10)
            bg_draw.line([(0, i), (w, i)], fill=(r, g, b, 255))
        
        # Composite background with aura
        blended = Image.alpha_composite(bg_gradient, aura_layer)
        
        # Create soft mask for subject
        mask = Image.new("L", base.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        
        # Create softer mask with gradient edge
        mask_radius = min(ww, hh) // 2
        for r in range(mask_radius, 0, -5):
            alpha = int(255 * (r / mask_radius))
            bbox = [cx - r, cy - r, cx + r, cy + r]
            mask_draw.ellipse(bbox, fill=alpha)
        
        mask = mask.filter(ImageFilter.GaussianBlur(25))
        
        # Composite subject with aura
        subject_with_bg = Image.composite(base, blended, mask)
        final_image = Image.alpha_composite(blended, subject_with_bg)
        
        # Apply filters
        if filter_name == "vintage":
            # Add vintage tint
            vintage_overlay = Image.new("RGBA", final_image.size, (255, 240, 220, 30))
            final_image = Image.alpha_composite(final_image, vintage_overlay)
            enhancer = ImageEnhance.Contrast(final_image)
            final_image = enhancer.enhance(1.1)
        elif filter_name == "dreamy":
            # Soft dreamy effect
            final_image = final_image.filter(ImageFilter.GaussianBlur(0.8))
            dream_overlay = Image.new("RGBA", final_image.size, (220, 220, 255, 20))
            final_image = Image.alpha_composite(final_image, dream_overlay)
        elif filter_name == "golden":
            # Golden hour effect
            golden_overlay = Image.new("RGBA", final_image.size, (255, 230, 180, 40))
            final_image = Image.alpha_composite(final_image, golden_overlay)
            enhancer = ImageEnhance.Brightness(final_image)
            final_image = enhancer.enhance(1.15)
        
        # Create Polaroid frame
        polaroid_padding_x = 80
        polaroid_padding_y = 140
        polaroid_bg = Image.new("RGB", 
                               (w + polaroid_padding_x * 2, 
                                h + polaroid_padding_y * 2), 
                               (255, 255, 255))
        
        # Add subtle texture to Polaroid
        texture_overlay = Image.new("RGBA", polaroid_bg.size, (0, 0, 0, 0))
        texture_draw = ImageDraw.Draw(texture_overlay)
        for i in range(0, polaroid_bg.size[0], 4):
            for j in range(0, polaroid_bg.size[1], 4):
                if (i + j) % 8 == 0:
                    texture_draw.point((i, j), fill=(0, 0, 0, 3))
        
        polaroid_bg = Image.alpha_composite(
            polaroid_bg.convert("RGBA"), 
            texture_overlay
        ).convert("RGB")
        
        # Paste the final image onto Polaroid
        polaroid_bg.paste(
            final_image.convert("RGB"), 
            (polaroid_padding_x, polaroid_padding_y)
        )
        
        # Add Polaroid shadow
        shadow = Image.new("RGBA", polaroid_bg.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rectangle(
            [10, 10, polaroid_bg.size[0]-10, polaroid_bg.size[1]-10],
            fill=(0, 0, 0, 30)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(15))
        polaroid_with_shadow = Image.alpha_composite(
            polaroid_bg.convert("RGBA"), 
            shadow
        )
        
        # Add caption
        if caption:
            draw = ImageDraw.Draw(polaroid_with_shadow)
            try:
                from PIL import ImageFont
                # Try to use a nice font
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = None
            
            text_x = polaroid_padding_x + 20
            text_y = polaroid_padding_y + h + 20
            draw.text((text_x, text_y), caption, fill=(80, 80, 80), font=font)
        
        # Save final image
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        polaroid_with_shadow.convert("RGB").save(output_path, quality=95)
        
        # Return color analysis
        color_analysis = []
        for color in dom_colors[:3]:
            aura_name, meaning = map_rgb_to_aura(color)
            color_analysis.append((aura_name, meaning))
            
        return output_path, color_analysis
        
    except Exception as e:
        print(f"Error in generate_aura_image: {str(e)}")
        raise e