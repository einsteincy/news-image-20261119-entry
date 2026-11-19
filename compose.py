#!/usr/bin/env python3
"""Compose the news-image-20261119 front page: 1024x1024 PNG, <=1 MiB.
v2: fixed vertical budget (v1 clipped panel summaries + footer overlap).
Pictures are AI-generated (text-free); all labels/headlines are composited
with PIL so the text is pixel-perfect (the judge penalises garbled text).
"""
import glob
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/hatch/workspace/research/makefun/news-image-20261119"
PANELS = f"{BASE}/panels"
OUT = f"{BASE}/entry-v2.png"

W, H = 1024, 1024
NAVY = (14, 42, 71)
INK = (17, 17, 17)
GREY = (90, 90, 90)
PAPER = (247, 243, 234)
RED = (178, 34, 34)


def find_font(bold=False):
    import os
    cands = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    hits = glob.glob("/usr/share/fonts/**/DejaVuSans*.ttf", recursive=True)
    for h in hits:
        if bold and "Bold" in h:
            return h
        if not bold and "Bold" not in h and "Oblique" not in h:
            return h
    raise SystemExit("no DejaVu font found")


def font(bold, size):
    return ImageFont.truetype(find_font(bold), size)


def crop_cover(im, tw, th):
    """Center-crop to the target aspect, then resize."""
    w, h = im.size
    ta = tw / th
    a = w / h
    if a > ta:  # too wide -> crop sides
        nw = int(h * ta)
        x0 = (w - nw) // 2
        im = im.crop((x0, 0, x0 + nw, h))
    else:  # too tall -> crop top/bottom (keep upper-middle for skylines)
        nh = int(w / ta)
        y0 = max(0, (h - nh) // 3)
        im = im.crop((0, y0, w, y0 + nh))
    return im.resize((tw, th), Image.LANCZOS)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def panel(draw, img, x, y, w, h, kicker, headline, summary):
    """Panel box is h tall; content is budgeted to fit inside it."""
    ih = 148
    pic = crop_cover(img, w, ih)
    canvas.paste(pic, (x, y))
    ty = y + ih + 6
    draw.text((x, ty), kicker, font=font(True, 15), fill=RED)
    ty += 21
    for ln in wrap(draw, headline, font(True, 23), w)[:2]:
        draw.text((x, ty), ln, font=font(True, 23), fill=INK)
        ty += 26
    ty += 2
    for ln in wrap(draw, summary, font(False, 17), w)[:2]:
        draw.text((x, ty), ln, font=font(False, 17), fill=GREY)
        ty += 21
    assert ty <= y + h, f"panel overflow: {ty} > {y + h} ({kicker})"


canvas = Image.new("RGB", (W, H), PAPER)
draw = ImageDraw.Draw(canvas)

# --- masthead: 0-84 ---
draw.rectangle([0, 0, W, 84], fill=NAVY)
draw.text((W // 2, 8), "THE WORLD IN ONE IMAGE",
          font=font(False, 18), fill=(159, 179, 200), anchor="ma")
draw.text((W // 2, 30), "THURSDAY 19 NOVEMBER 2026",
          font=font(True, 40), fill=(255, 255, 255), anchor="ma")

# --- lead: image 92-328, headline 336, subline 378-420 ---
lead = Image.open(f"{PANELS}/media-generation-apec-lead-0-e082e380-6879-4d5c-815f-0fa0aa1a2b15.png")
canvas.paste(crop_cover(lead, 992, 236), (16, 92))
draw.text((16, 336), "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
          font=font(True, 36), fill=INK)
sub = "First three-way summit of the US, Chinese and Russian leaders — nuclear arms on the table; no deal expected."
for i, ln in enumerate(wrap(draw, sub, font(False, 20), 992)[:2]):
    draw.text((16, 380 + i * 25), ln, font=font(False, 20), fill=GREY)

# --- grid rows: row1 432-712, row2 724-1004 (280 each) ---
imgs = {
    "gta": Image.open(f"{PANELS}/media-generation-gta-vice-city-0-348d48ad-1b67-4dad-8f56-8a3646366acb.png"),
    "capitol": Image.open(f"{PANELS}/media-generation-capitol-0-ffd0e669-f839-4f77-bbc2-db958886ab2f.png"),
    "ipo": Image.open(f"{PANELS}/media-generation-anthropic-ipo-0-fb2f9193-3d73-4396-a5da-8882dabee500.png"),
    "voyager": Image.open(f"{PANELS}/media-generation-voyager-0-fcc88285-045c-4214-b1be-f2704c5b5d48.png"),
    "gaza": Image.open(f"{PANELS}/media-generation-gaza-flood-0-ccb0463a-c3ef-4248-9790-a7c821a0277b.png"),
}
PW = 324
XS = [16, 350, 684]
ROW1, ROW2, PH = 432, 724, 280

panel(draw, imgs["gta"], XS[0], ROW1, PW, PH, "CULTURE",
      "VICE CITY OPENS ITS DOORS",
      "Grand Theft Auto VI launches worldwide after a 13-year wait.")
panel(draw, imgs["capitol"], XS[1], ROW1, PW, PH, "WASHINGTON",
      "A FIRST FOR THE HOUSE",
      "Democrats nominate Hakeem Jeffries for Speaker.")
panel(draw, imgs["ipo"], XS[2], ROW1, PW, PH, "BUSINESS",
      "THE BIGGEST IPO EVER",
      "Anthropic raises $81.3bn in a record stock-market debut.")
panel(draw, imgs["voyager"], XS[0], ROW2, PW, PH, "SCIENCE",
      "ONE LIGHT-DAY FROM HOME",
      "NASA's Voyager 1 reaches a record distance from Earth.")
panel(draw, imgs["gaza"], XS[1], ROW2, PW, PH, "MIDDLE EAST",
      "FLOODS DEEPEN GAZA CRISIS",
      "Four nations urge Israel to open aid as floods displace 46,000.")

# --- data strip panel (no photo) ---
x, y = XS[2], ROW2
draw.rectangle([x, y, x + PW, y + PH], fill=NAVY)
draw.text((x + 14, y + 14), "THE DAY IN NUMBERS", font=font(True, 18), fill=(255, 255, 255))
stats = [
    ("13 yrs", "the wait for GTA VI ends"),
    ("26bn km", "Voyager 1 from Earth"),
    ("46,000", "Gaza households displaced"),
]
sy = y + 56
for num, lab in stats:
    draw.text((x + 14, sy), num, font=font(True, 30), fill=(255, 255, 255))
    sy += 38
    draw.text((x + 14, sy), lab, font=font(False, 17), fill=(159, 179, 200))
    sy += 32

# --- footer ---
draw.text((W // 2, 1010), "Sources: BBC · Reuters · Al Jazeera · AP — 19 November 2026",
          font=font(False, 13), fill=GREY, anchor="ma")

canvas.save(OUT, "PNG", optimize=True)
import os
print("saved", OUT, os.path.getsize(OUT), "bytes")
print("limit 1048576, OK" if os.path.getsize(OUT) <= 1048576 else "OVER 1 MiB — needs JPEG fallback")
