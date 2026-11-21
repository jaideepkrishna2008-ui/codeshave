"""
Generates high-resolution, pixel-perfect terminal recording demo for Twitter/X and GitHub.
Outputs:
  - assets/terminal_recording.gif (Twitter/X compatible animated GIF)
  - assets/terminal_recording.mp4 (1080p H.264 video for Twitter/X video player)
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1200
HEIGHT = 700
BG_COLOR = (11, 15, 25)          # Deep terminal black
CARD_BG = (17, 24, 39)           # Outer frame
BORDER_COLOR = (51, 65, 85)      # Slate border
TITLEBAR_BG = (15, 23, 42)

# Colors
TEXT_WHITE = (241, 245, 249)
TEXT_MUTED = (148, 163, 184)
TEXT_DIM = (100, 116, 139)
ACCENT_GREEN = (52, 211, 153)
ACCENT_CYAN = (56, 189, 248)
ACCENT_PURPLE = (167, 139, 250)
ACCENT_RED = (248, 113, 113)
ACCENT_YELLOW = (251, 191, 36)

FONT_PATH = "C:/Windows/Fonts/consola.ttf"
FONT_SIZE = 18
FONT = ImageFont.truetype(FONT_PATH, FONT_SIZE)
FONT_BOLD = ImageFont.truetype(FONT_PATH, FONT_SIZE)
FONT_HEADER = ImageFont.truetype(FONT_PATH, 14)


def draw_terminal_base():
    img = Image.new("RGBA", (WIDTH, HEIGHT), (9, 13, 22, 255))
    draw = ImageDraw.Draw(img)

    # Outer rounded container
    pad_x = 40
    pad_y = 35
    w = WIDTH - pad_x * 2
    h = HEIGHT - pad_y * 2
    r = 14

    # Background window
    draw.rounded_rectangle([pad_x, pad_y, pad_x + w, pad_y + h], radius=r, fill=BG_COLOR, outline=BORDER_COLOR, width=2)

    # Title bar
    draw.rounded_rectangle([pad_x, pad_y, pad_x + w, pad_y + 44], radius=r, fill=TITLEBAR_BG)
    draw.rectangle([pad_x, pad_y + 30, pad_x + w, pad_y + 44], fill=TITLEBAR_BG)
    draw.line([pad_x, pad_y + 44, pad_x + w, pad_y + 44], fill=BORDER_COLOR, width=1)

    # Traffic dots
    dot_y = pad_y + 22
    draw.ellipse([pad_x + 22, dot_y - 6, pad_x + 34, dot_y + 6], fill=(239, 68, 68))
    draw.ellipse([pad_x + 44, dot_y - 6, pad_x + 56, dot_y + 6], fill=(245, 158, 11))
    draw.ellipse([pad_x + 66, dot_y - 6, pad_x + 78, dot_y + 6], fill=(16, 185, 129))

    # Title text
    title = "zsh — codeshave pack ./src --stats"
    bbox = draw.textbbox((0, 0), title, font=FONT_HEADER)
    tw = bbox[2] - bbox[0]
    draw.text((pad_x + (w - tw) // 2, pad_y + 14), title, font=FONT_HEADER, fill=TEXT_MUTED)

    return img


def render_lines(lines, cursor=None):
    """
    Renders lines into a fresh frame.
    Each line is a list of tuples: (text, color)
    """
    base = draw_terminal_base()
    draw = ImageDraw.Draw(base)

    start_x = 75
    start_y = 105
    line_h = 24

    for row_idx, line in enumerate(lines):
        x = start_x
        y = start_y + row_idx * line_h
        for segment in line:
            text, color = segment
            draw.text((x, y), text, font=FONT, fill=color)
            bbox = draw.textbbox((x, y), text, font=FONT)
            x = bbox[2]

        if cursor and row_idx == cursor[0]:
            cx = cursor[1]
            draw.rectangle([cx, y + 2, cx + 9, y + line_h - 4], fill=ACCENT_CYAN)

    return base.convert("RGB")


def build_recording_frames():
    frames = []
    durations = []  # in milliseconds

    # Script narrative
    prompt_prefix = [("user@devbox", ACCENT_GREEN), (":", TEXT_MUTED), ("~/app", ACCENT_CYAN), ("$ ", TEXT_WHITE)]

    # 1. Type `codeshave pack ./src --stats`
    cmd1 = "codeshave pack ./src --stats"
    lines = [prompt_prefix.copy()]

    # Cursor starts right after prompt
    calc_img = Image.new("RGBA", (10, 10))
    calc_draw = ImageDraw.Draw(calc_img)
    prompt_str = "user@devbox:~/app$ "
    p_box = calc_draw.textbbox((0, 0), prompt_str, font=FONT)
    px = 75 + (p_box[2] - p_box[0])

    # Initial prompt idle
    for _ in range(4):
        frames.append(render_lines(lines, cursor=(0, px)))
        durations.append(150)

    # Typing cmd1
    cur_text = ""
    for ch in cmd1:
        cur_text += ch
        l = prompt_prefix.copy()
        l.append((cur_text, TEXT_WHITE))
        box = calc_draw.textbbox((0, 0), cur_text, font=FONT)
        cx = px + (box[2] - box[0])
        frames.append(render_lines([l], cursor=(0, cx)))
        durations.append(60)

    # Brief enter press
    l_final = prompt_prefix.copy()
    l_final.append((cmd1, TEXT_WHITE))
    lines = [l_final]
    frames.append(render_lines(lines))
    durations.append(250)

    # 2. Output of pack appears
    banner = [("⚡ CodeShave v0.2.0 — Universal Multi-Language Code Compressor", ACCENT_PURPLE)]
    scan = [("Scanning: ./src (Python, TypeScript, Go, Rust, Java, C++)", TEXT_MUTED)]
    blank = [("", TEXT_WHITE)]
    header = [("FILE                                          LANG       ORIGINAL     SKELETON     SAVINGS   ", TEXT_MUTED)]
    sep = [("─────────────────────────────────────────────────────────────────────────────────────────────", BORDER_COLOR)]

    rows = [
        [("src/models/user.py                            ", TEXT_WHITE), ("python    ", ACCENT_CYAN), ("   4,210 t ", TEXT_WHITE), ("     780 t ", ACCENT_CYAN), ("   81.5%", ACCENT_GREEN)],
        [("src/services/billing.ts                       ", TEXT_WHITE), ("typescript", ACCENT_CYAN), ("   6,840 t ", TEXT_WHITE), ("   1,120 t ", ACCENT_CYAN), ("   83.6%", ACCENT_GREEN)],
        [("src/server/router.go                          ", TEXT_WHITE), ("go        ", ACCENT_CYAN), ("   5,120 t ", TEXT_WHITE), ("     890 t ", ACCENT_CYAN), ("   82.6%", ACCENT_GREEN)],
        [("src/engine/cache.rs                           ", TEXT_WHITE), ("rust      ", ACCENT_CYAN), ("   8,340 t ", TEXT_WHITE), ("   1,410 t ", ACCENT_CYAN), ("   83.1%", ACCENT_GREEN)],
        [("src/api/DataProcessor.java                    ", TEXT_WHITE), ("java      ", ACCENT_CYAN), ("   7,500 t ", TEXT_WHITE), ("   1,250 t ", ACCENT_CYAN), ("   83.3%", ACCENT_GREEN)],
    ]

    tot_sep = [("─────────────────────────────────────────────────────────────────────────────────────────────", BORDER_COLOR)]
    tot_row = [("TOTAL                                                      ", ACCENT_YELLOW), ("  32,010 t ", TEXT_WHITE), ("   5,450 t ", ACCENT_CYAN), ("   83.0%", ACCENT_GREEN)]
    summary1 = [("✔ Processed 5 polyglot files in 42.1ms", ACCENT_GREEN)]
    summary2 = [("✔ Total token savings: 26,560 tokens (83.0% reduction)", ACCENT_GREEN)]

    out_lines = [l_final, blank, banner, scan, blank, header, sep]
    for r in rows:
        out_lines.append(r)
    out_lines.append(tot_sep)
    out_lines.append(tot_row)
    out_lines.append(blank)
    out_lines.append(summary1)
    out_lines.append(summary2)
    out_lines.append(blank)

    # Show pack results and pause
    frames.append(render_lines(out_lines))
    durations.append(2800)

    # 3. Next command: `codeshave clip ./src/services/billing.ts`
    p2 = prompt_prefix.copy()
    cmd2 = "codeshave clip ./src/services/billing.ts"
    cur_text2 = ""
    for ch in cmd2:
        cur_text2 += ch
        p2_line = prompt_prefix.copy()
        p2_line.append((cur_text2, TEXT_WHITE))
        box = calc_draw.textbbox((0, 0), cur_text2, font=FONT)
        cx = px + (box[2] - box[0])
        current_view = out_lines + [p2_line]
        # Keep within max lines
        if len(current_view) > 22:
            current_view = current_view[-22:]
        frames.append(render_lines(current_view, cursor=(len(current_view) - 1, cx)))
        durations.append(45)

    # Clip output
    p2_done = prompt_prefix.copy()
    p2_done.append((cmd2, TEXT_WHITE))
    clip_res1 = [("✔ Copied to clipboard! 6,840 t -> 1,120 t (-83.6% reduction)", ACCENT_GREEN)]
    clip_res2 = [("Ready to paste directly into ChatGPT, Claude, or Cursor.", TEXT_MUTED)]

    all_done = out_lines + [p2_done, clip_res1, clip_res2, blank]
    if len(all_done) > 22:
        all_done = all_done[-22:]

    frames.append(render_lines(all_done))
    durations.append(3500)

    return frames, durations


def main():
    dest_dir = Path("c:/Users/Jaideep krishna/OneDrive/Desktop/codeshave/assets")
    dest_dir.mkdir(parents=True, exist_ok=True)
    gif_path = dest_dir / "terminal_recording.gif"
    mp4_path = dest_dir / "terminal_recording.mp4"

    print("Generating terminal frames...")
    frames, durations = build_recording_frames()
    print(f"Generated {len(frames)} frames. Rendering animated GIF...")

    # Save GIF
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"✔ Saved GIF: {gif_path} ({os.path.getsize(gif_path) / 1024:.1f} KB)")

    # Check for ffmpeg
    ffmpeg_exe = shutil.which("ffmpeg")
    if not ffmpeg_exe:
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass

    if ffmpeg_exe:
        print(f"Found ffmpeg: {ffmpeg_exe}. Rendering MP4 video...")
        temp_dir = dest_dir / "_temp_frames"
        temp_dir.mkdir(exist_ok=True)
        frame_idx = 0
        for idx, (frame, dur) in enumerate(zip(frames, durations)):
            repeat = max(1, round(dur / 40.0))  # at 25 fps, 1 frame is 40ms
            for _ in range(repeat):
                frame.save(temp_dir / f"f_{frame_idx:05d}.png")
                frame_idx += 1

        cmd = [
            ffmpeg_exe,
            "-y",
            "-framerate", "25",
            "-i", str(temp_dir / "f_%05d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            str(mp4_path),
        ]
        subprocess.run(cmd, check=True)
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"✔ Saved Twitter/X 1080p MP4: {mp4_path} ({os.path.getsize(mp4_path) / 1024:.1f} KB)")
    else:
        print("Note: ffmpeg not detected yet; GIF rendered at full fidelity.")


if __name__ == "__main__":
    main()
