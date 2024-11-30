from PIL import Image, ImageDraw, ImageFont
import os

# Create a new image with a white background
width = 1200  # recommended OG image width
height = 630  # recommended OG image height
background_color = "#ffffff"

img = Image.new('RGB', (width, height), background_color)
draw = ImageDraw.Draw(img)

# Try different system emoji fonts
font = None
font_size = 200

# List of common emoji font paths on different systems
font_paths = [
    'seguiemj.ttf',  # Windows
    '/System/Library/Fonts/Apple Color Emoji.ttf',  # macOS
    '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',  # Linux
    'NotoColorEmoji.ttf',  # Some Linux
]

for font_path in font_paths:
    try:
        font = ImageFont.truetype(font_path, font_size)
        break
    except (OSError, IOError):
        continue

if font is None:
    raise Exception("Could not find a suitable emoji font")

# Use trending up emoji
emoji = "📈"

# Get the size that the text will take
text_bbox = draw.textbbox((0, 0), emoji, font=font)
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]

# Calculate position for emoji with visual center offset
center_x = width / 2
center_y = height / 2
visual_center_offset = text_height * 0.4  # 40% from top
emoji_x = center_x - (text_width / 2)
emoji_y = center_y - visual_center_offset

# Draw the emoji
draw.text((emoji_x, emoji_y), emoji, font=font, fill="#000000")

# Ensure the static directory exists
os.makedirs('static', exist_ok=True)

# Save the image
img.save('static/og-image.png') 