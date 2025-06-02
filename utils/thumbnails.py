from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import colorsys
import math

def generate_thumbnail_with_dalle(client, concept, video_title,
                                 platform="YouTube"):
    """Generate a thumbnail image using DALL-E based on the
    concept and video title."""
    try:
        # Define aspect ratio based on platform
        if platform == "YouTube":
            aspect_ratio = "16:9"
            size = "1792x1024" # DALL-E supports 1792x1024 whic
                                
        elif platform == "Instagram":
            aspect_ratio = "1:1"
            size = "1024x1024" # Square format for Instagram
        elif platform=="LinkedIn":
            aspect_ratio="1.91:1"
            size="1792x1024"
        else:
            aspect_ratio = "16:9"  # Default to YouTube
            size = "1792x1024"

        # Extract key elements from the concept
        text_overlay = concept.get('text_overlay', '')
        focal_point = concept.get('focal_point', '')
        tone = concept.get('tone', '')
        concept_desc = concept.get('concept', '')
        
        colors = concept.get('colors', ['#FFFFFF', '#000000'])
        main_color = colors[0] if len(colors) > 0 else '#FFFFFF'

        prompt = f"""
        Create a professional {platform} thumbnail with these
        specifications:
        - Clear {aspect_ratio} format for {platform}
        - Main focus: {focal_point}
        - Emotional tone: {tone}
        - Bold, clear text overlay reading "{text_overlay}"
        prominently displayed
        - Text should be highly legible, possibly in color
        {main_color} with contrasting outline
        - Concept: {concept_desc}
        - Related to: {video_title}
        - Professional eye-catching design with high contrast
        - Make sure the text stands out and is easily readable
        - Thumbnail should look professional and high-quality for
        {platform}
        - Text should be integrated with the visual elements in a
        visually appealing way
        """
        response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="standard",
        n=1,
        )
        image_url = response.data[0].url
        return image_url

    except Exception as e:
        print(f"Error generating thumbnail with DALL-E: {e}")
        return None 

def create_gradient_background(concept, width=1280, height=720):
    """Create a gradient background using the colors from the
    concept."""
    # Get colors from concept, or use defaults
    colors = concept.get('colors', ['#3366CC', '#FFFFFF',
                                    '#FF5555'])
    if len(colors) < 2:
        colors.append('#FFFFFF')
    try:
        color1=hex_to_rgb(colors[0])
        color2=hex_to_rgb(colors[1]) if len(colors)>1 else '#FFFFFF'
    except:
        color1=(51,102,204)
        color2=(255,255,255)
    img = Image.new('RGB', (width, height), color=color1)
    draw = ImageDraw.Draw(img)

    # Create gradient
    for y in range(height):
        # Calculate ratio of current position
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        # Draw a line with the interpolated color
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    tone = concept.get('tone', '').lower()
    if 'professional' in tone or 'educational' in tone:
        add_professional_pattern(img, draw)
    elif 'energetic' in tone or 'exciting' in tone:
        add_energetic_pattern(img, draw)
    elif 'emotional' in tone or 'dramatic' in tone:
        add_dramatic_pattern(img, draw)
    return img
def hex_to_rgb(hex_color):
    """Convert hex color code to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def add_watermark(img,draw):
    """Add a subtle watermark to the image."""
    watermark_text="Video seo optimizer"
    try:
            font = ImageFont.truetype('arial.ttf', 20)
    except:
        font = ImageFont.load_default()

    # Draw watermark in bottom right corner
    draw.text(
        (img.width - 220, img.height - 30),
        watermark_text,
        fill=(255, 255, 255, 128),
        font=font
    )
    




def add_professional_pattern(img, draw):
    """Add a subtle professional pattern to the background."""
    width, height = img.size

    # Draw subtle lines
    for i in range(0, width, 40):
        draw.line([(i, 0), (i, height)], fill=(255, 255, 255, 10))

    for i in range(0, height, 40):
        draw.line([(0, i), (width, i)], fill=(255, 255, 255, 10))



def add_energetic_pattern(img, draw):
    """Add an energetic pattern to the background."""
    width, height = img.size

    # Draw diagonal lines
    for i in range(-height, width + height, 60):
        draw.line([(i, 0), (i + height, height)], fill=(255, 255,
                                                      255, 15))
        draw.line([(i, height), (i + height, 0)], fill=(255, 255,
                                                      255, 15))


                                                    
def add_dramatic_pattern(img, draw):
    """Add a dramatic pattern to the background."""
    width, height = img.size
    center_x, center_y = width // 2, height // 2

    # Draw concentric circles
    for radius in range(50, max(width, height), 100):
        draw.arc(
            [(center_x - radius, center_y - radius),
             (center_x + radius, center_y + radius)],
            0, 360, fill=(255, 255, 255, 20)
        )

def create_thumbnail_preview(concept, video_title,
    base_image_url=None):
    """
    Create a thumbnail preview based on concept description.
    This generates a basic visualization when DALL-E is not
    avail
    """
    if base_image_url:
        try:
            response = requests.get(base_image_url)
            img = Image.open(BytesIO(response.content))
            # Resize to standard thumbnail size if needed
            img = img.resize((1280, 720))
        except Exception:
            # Fallback to creating a blank image
            img = create_gradient_background(concept)
    else:
        img = create_gradient_background(concept)
    draw = ImageDraw.Draw(img)

    # Add text overlay if specified
    if concept.get('text_overlay'):
        add_text_with_outline(img, draw, concept)
    add_watermark(img, draw)
    return img

    