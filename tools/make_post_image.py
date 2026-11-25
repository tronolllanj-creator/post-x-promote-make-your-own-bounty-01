import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NAVY = (20, 33, 61, 255)
NAVY_BAND = (10, 18, 38, 255)
GOLD = (217, 164, 65, 255)
GOLD_DARK = (176, 128, 40, 255)
GOLD_CONFETTI = (236, 196, 108, 255)
WHITE = (255, 255, 255, 255)
GREY = (178, 184, 196, 255)

BG_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BG_DIR)
OUT_PATH = os.path.join(REPO_ROOT, "post.png")

F_SIZE_HEAD1 = 84
F_SIZE_HEAD2 = 128
F_SIZE_BODY = 38
F_SIZE_BRAND = 56
F_SIZE_CODE = 34

SEG_HEAD1 = ["MAKE YOUR", "OWN BOUNTY"]
SEG_BODY = [
    "Describe any task. Set the reward.",
    "Agents compete.",
    "The best get paid.",
]
SEG_BRAND = ["make.fun", "makefun-dove-coast-bobsled"]


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def fit_font(draw, text, path, start, limit):
    size = int(start)
    while size > 12:
        font = load_font(path, size)
        if draw.textlength(text, font=font) <= limit:
            return font
        size -= 2
    return load_font(path, 12)


def star_points(cxp, cyp, r_out, r_in, n=5, rot=-math.pi / 2):
    pts = []
    i = 0
    while i < n * 2:
        ang = rot + i * math.pi / n
        r = r_out if i % 2 == 0 else r_in
        pts.append((cxp + r * math.cos(ang), cyp + r * math.sin(ang)))
        i += 1
    return pts


def draw_coin(draw, cx, cy, r):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD, outline=GOLD_DARK, width=4)
    draw.ellipse([cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10], fill=GOLD_CONFETTI)
    r_in = r * 0.42
    pts = star_points(cx, cy, r_in, r_in * 0.44)
    draw.polygon(pts, fill=WHITE)


def center_text(draw, text, font, cx, y):
    w = draw.textlength(text, font=font)
    draw.text((cx - w / 2, y), text, fill=WHITE, font=font)


def wrap_lines(draw, text, font, limit):
    words = text.split()
    lines = []
    cur = words[0]
    for w in words[1:]:
        trial = cur + " " + w
        if draw.textlength(trial, font=font) <= limit:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def render_background(base, img):
    base.rectangle([0, 0, SIZE, SIZE], fill=NAVY)
    base.polygon([(0, 300), (SIZE, 110), (SIZE, 320), (0, 440)], fill=NAVY_BAND)
    rng = random.Random(1337)
    for _ in range(70):
        x = rng.randint(0, SIZE - 1)
        y = rng.randint(0, SIZE - 1)
        radius = rng.randint(2, 5)
        base.ellipse([x, y, x + radius, y + radius], fill=GOLD_CONFETTI)
        if rng.random() < 0.25:
            base.ellipse([x, y, x + radius + 2, y + radius + 2], outline=GOLD_CONFETTI)


def layout(draw, img):
    cx = IMAGE_CX = SIZE // 2
    limit = int(SIZE * 0.84)

    block = []
    hfont1 = fit_font(draw, SEG_HEAD1[0], FONT_BOLD, F_SIZE_HEAD1, limit)
    hfont2 = fit_font(draw, SEG_HEAD1[1], FONT_BOLD, F_SIZE_HEAD2, limit)
    block.append((hfont1, SEG_HEAD1[0]))
    block.append((hfont2, SEG_HEAD1[1]))

    body_fonts = []
    bfont = fit_font(draw, SEG_BODY[0], FONT_REG, F_SIZE_BODY, limit)
    for line in SEG_BODY:
        body_fonts.append(line)

    def get_block_height(items, leading=14):
        total = 0
        for f, t in items:
            total += f.size + leading
        return total

    head_items = [(hfont1, SEG_HEAD1[0]), (hfont2, SEG_HEAD1[1])]
    head_h = get_block_height(head_items, 18)

    body_lines = []
    for line in SEG_BODY:
        body_lines.extend(wrap_lines(draw, line, bfont, limit))
    body_items = [(bfont, t) for t in body_lines]
    body_h = get_block_height(body_items, 12)

    bfont_brand = fit_font(draw, SEG_BRAND[0], FONT_BOLD, F_SIZE_BRAND, limit)
    bfont_code = fit_font(draw, SEG_BRAND[1], FONT_REG, F_SIZE_CODE, limit)

    coins_top = (910, 80, 55)
    coins_small1 = (150, SIZE - 150, 55)
    coins_small2 = (200, SIZE - 55, 38)

    y = 90
    for f, t in head_items:
        draw.text((cx - draw.textlength(t, font=f) / 2, y), t, fill=WHITE if f is hfont1 else GOLD, font=f)
        y += f.size + 18

    y += 12
    for t in body_lines:
        draw.text((cx - draw.textlength(t, font=bfont) / 2, y), t, fill=WHITE, font=bfont)
        y += bfont.size + 12

    rule_y = SIZE - 150
    draw.line([(120, rule_y), (SIZE - 120, rule_y)], fill=GOLD, width=3)
    brand_y = rule_y + 20
    draw.text((cx - draw.textlength(SEG_BRAND[0], font=bfont_brand) / 2, brand_y), SEG_BRAND[0], fill=WHITE, font=bfont_brand)
    code_y = brand_y + bfont_brand.size + 8
    draw.text((cx - draw.textlength(SEG_BRAND[1], font=bfont_code) / 2, code_y), SEG_BRAND[1], fill=GREY, font=bfont_code)
    return coins_top, coins_small1, coins_small2


def main():
    img = Image.new("RGB", (SIZE, SIZE), NAVY)
    base = ImageDraw.Draw(img)
    render_background(base, img)

    coins_top, coins_small1, coins_small2 = layout(base, img)
    draw_coin(base, coins_top[0], coins_top[1], coins_top[2])
    draw_coin(base, coins_small1[0], coins_small1[1], coins_small1[2])
    draw_coin(base, coins_small2[0], coins_small2[1], coins_small2[2])

    img.save(OUT_PATH, "PNG")
    print("saved", OUT_PATH, img.size[0], "x", img.size[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())