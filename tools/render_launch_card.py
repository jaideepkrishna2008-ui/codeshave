"""
Renders a modern, eye-catching launch card image for Twitter/X (1200x675).
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W = 1200
H = 675

img = Image.new("RGBA", (W, H), (9, 13, 22, 255))
draw = ImageDraw.Draw(img)

# Gradient background glow effect
for i in range(180, 0, -1):
    alpha = int((1.0 - (i / 180.0)) * 45)
    r = int(i * 3.5)
    draw.ellipse([W//2 - r, -50 - r//2, W//2 + r, 250 + r//2], fill=(56, 189, 248, alpha))

# Card border / backdrop
draw.rounded_rectangle([30, 30, W - 30, H - 30], radius=18, outline=(31, 41, 55, 255), width=2)

FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 46)
FONT_SUBTITLE = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)
FONT_STAT_BIG = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 38)
FONT_STAT_SUB = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
FONT_BADGE = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 16)
FONT_FOOTER = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 17)

# Brand header
draw.text((70, 65), "⚡ CodeShave", font=FONT_TITLE, fill=(56, 189, 248))
draw.text((360, 75), "v0.2.0 — Open Source", font=FONT_SUBTITLE, fill=(148, 163, 184))

# Big headline
headline = "Shave 80% of Tokens in Real Time"
draw.text((70, 135), headline, font=FONT_TITLE, fill=(243, 244, 246))

sub = "Universal AST & structural code compressor for Claude, Cursor, ChatGPT, & Antigravity"
draw.text((70, 195), sub, font=FONT_SUBTITLE, fill=(156, 163, 175))

# 3 Stat Cards in a row
cards_data = [
    ("-88.5%", "Token Reduction", "134k -> 15.3k tokens", (52, 211, 153)),
    ("42ms", "Deterministic Speed", "Zero dependencies (std lib)", (56, 189, 248)),
    ("100%", "Syntax Preserved", "Types, classes, & docstrings", (167, 139, 250)),
]

card_w = 330
card_h = 135
card_y = 260
start_x = 70
gap = 40

for idx, (val, title, subtitle, color) in enumerate(cards_data):
    cx = start_x + idx * (card_w + gap)
    draw.rounded_rectangle([cx, card_y, cx + card_w, card_y + card_h], radius=12, fill=(17, 24, 39), outline=(51, 65, 85), width=1)
    # Value
    draw.text((cx + 22, card_y + 16), val, font=FONT_STAT_BIG, fill=color)
    # Title
    draw.text((cx + 22, card_y + 68), title, font=FONT_SUBTITLE, fill=(241, 245, 249))
    # Sub
    draw.text((cx + 22, card_y + 98), subtitle, font=FONT_STAT_SUB, fill=(148, 163, 184))

# Language pill tags
langs = ["Python (AST)", "TypeScript", "JavaScript", "Go", "Rust", "Java", "C++", "C#"]
lx = 70
ly = 435
for l in langs:
    bbox = draw.textbbox((0, 0), l, font=FONT_BADGE)
    bw = bbox[2] - bbox[0] + 24
    bh = 32
    draw.rounded_rectangle([lx, ly, lx + bw, ly + bh], radius=8, fill=(30, 41, 59), outline=(71, 85, 105), width=1)
    draw.text((lx + 12, ly + 6), l, font=FONT_BADGE, fill=(226, 232, 240))
    lx += bw + 12

# Integrations row
ix = 70
iy = 485
draw.text((ix, iy + 6), "Built-in Turnkey MCP:", font=FONT_STAT_SUB, fill=(148, 163, 184))
ix += 175
tools = ["Claude Desktop", "Cursor IDE", "Windsurf", "Google Antigravity"]
for t in tools:
    bbox = draw.textbbox((0, 0), t, font=FONT_STAT_SUB)
    tw = bbox[2] - bbox[0] + 18
    draw.rounded_rectangle([ix, iy, ix + tw, iy + 28], radius=6, fill=(15, 23, 42), outline=(51, 65, 85), width=1)
    draw.text((ix + 9, iy + 5), t, font=FONT_STAT_SUB, fill=(56, 189, 248))
    ix += tw + 10

# Bottom Bar
draw.line([70, 550, W - 70, 550], fill=(31, 41, 55), width=1)

# Command block
cmd = "pip install codeshave"
draw.rounded_rectangle([70, 575, 340, 620], radius=8, fill=(15, 23, 42), outline=(56, 189, 248), width=1)
draw.text((88, 586), f"$ {cmd}", font=FONT_FOOTER, fill=(52, 211, 153))

# Links
repo = "github.com/jaideepkrishna2008-ui/codeshave"
draw.text((420, 586), repo, font=FONT_FOOTER, fill=(243, 244, 246))

play = "Live Playground: jaideepkrishna2008-ui.github.io/codeshave"
pbox = draw.textbbox((0, 0), play, font=FONT_FOOTER)
draw.text((W - 70 - (pbox[2] - pbox[0]), 586), play, font=FONT_FOOTER, fill=(56, 189, 248))

# Save outputs
desktop_path = Path("C:/Users/Jaideep krishna/OneDrive/Desktop/codeshave_launch_card.png")
asset_path = Path("c:/Users/Jaideep krishna/OneDrive/Desktop/codeshave/assets/codeshave_launch_card.png")

img.convert("RGB").save(desktop_path, "PNG", quality=95)
img.convert("RGB").save(asset_path, "PNG", quality=95)

print(f"✔ Saved: {desktop_path}")
print(f"✔ Saved: {asset_path}")
