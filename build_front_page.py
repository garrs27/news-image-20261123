#!/usr/bin/env python3
"""Build entry.png — a one-page newspaper summing up Monday 23 November 2026.

Deterministic: pure Pillow render from news.json with fixed system fonts.
No network, no clock, no randomness — same input, same bytes.
Canvas 1024x1024 (competition cap), PNG, must stay under 1 MiB.
Layout follows the proven news-image winner formula (WINNER-PATTERNS §9.4):
masthead with a giant date line, a UTC timeline strip, 3 illustrated leads,
14 numbered tiles with verification badges and named sources, a world map
with numbered pins, a DATE CHECK box discarding older stories, and a dense
one-line index — 59 stories in all, every one from 23 November 2026 reports.
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
MARGIN = 16
CW = W - 2 * MARGIN  # content width = 992

BG = (248, 244, 232)
INK = (17, 17, 17)
MUTED = (92, 88, 78)
RED = (163, 22, 33)
RULE = (30, 30, 30)
BADGE = {"CONFIRMED": (22, 110, 44), "REPORTED": (28, 74, 138), "CLAIM": (168, 104, 0)}
CHIP = {"C": (22, 110, 44), "R": (28, 74, 138), "CL": (168, 104, 0)}

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
COND = "/usr/share/fonts/truetype/noto/NotoSans-Condensed.ttf"
COND_B = "/usr/share/fonts/truetype/noto/NotoSans-CondensedBold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, font, maxw):
    if draw.textlength(text, font=font) <= maxw:
        return text
    while text and draw.textlength(text + "…", font=font) > maxw:
        text = text.rsplit(" ", 1)[0] if " " in text else text[:-1]
    return text + "…"


def badge(draw, x, y, status, font):
    label = status
    w = draw.textlength(label, font=font) + 10
    draw.rectangle([x, y, x + w, y + 15], fill=BADGE[status])
    draw.text((x + 5, y + 1), label, font=font, fill=(255, 255, 255))
    return x + w


def num_chip(draw, x, y, n, size=17):
    draw.rectangle([x, y, x + size, y + size], fill=INK)
    s = str(n)
    f = F(SANS_B, 11 if n < 10 else 10)
    tw = draw.textlength(s, font=f)
    draw.text((x + (size - tw) / 2, y + 2), s, font=f, fill=(255, 255, 255))


# ---------- lead illustrations (flat, programmatic, text-free) ----------

def art_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 42, 74))
    cx, cy, r = x + w // 2, y + h // 2, 44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(64, 132, 190))
    d.ellipse([cx - 30, cy - 26, cx - 6, cy - 6], fill=(74, 160, 90))
    d.ellipse([cx + 4, cy + 2, cx + 30, cy + 24], fill=(74, 160, 90))
    d.ellipse([cx - 12, cy + 16, cx + 6, cy + 30], fill=(74, 160, 90))
    # thermometer: talks overheated, no deal
    tx = x + w - 42
    d.rectangle([tx, y + 14, tx + 10, y + h - 26], fill=(230, 230, 225))
    d.rectangle([tx + 2, y + 26, tx + 8, y + h - 26], fill=RED)
    d.ellipse([tx - 5, y + h - 32, tx + 15, y + h - 12], fill=RED)
    # crossed-out speech bubble: no agreement text came out
    bx, by = x + 22, y + 16
    d.rounded_rectangle([bx, by, bx + 56, by + 30], 7, fill=(240, 238, 228))
    d.line([bx + 8, by + 6, bx + 48, by + 24], fill=RED, width=4)
    d.line([bx + 48, by + 6, bx + 8, by + 24], fill=RED, width=4)


def art_capitol(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 30, 62))
    cx = x + w // 2
    base = y + h - 16
    d.rectangle([cx - 105, base - 34, cx + 105, base], fill=(238, 236, 228))
    for i in range(7):
        px = cx - 90 + i * 30
        d.rectangle([px, base - 32, px + 9, base - 4], fill=(120, 128, 150))
    d.rectangle([cx - 112, base - 40, cx + 112, base - 34], fill=(250, 248, 240))
    d.pieslice([cx - 52, base - 96, cx + 52, base - 18], 180, 360, fill=(238, 236, 228))
    d.rectangle([cx - 3, base - 108, cx + 3, base - 92], fill=(250, 248, 240))
    d.rectangle([cx - 118, base, cx + 118, base + 5], fill=(200, 198, 188))
    # blue wave of seats won
    for i in range(9):
        sx = cx - 96 + i * 24
        d.rectangle([sx, base + 8, sx + 14, base + 13], fill=(64, 120, 220))


def art_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(38, 36, 52))
    base = y + h - 10
    # intact block
    d.rectangle([x + 18, base - 74, x + 92, base], fill=(88, 84, 104))
    # struck block with a jagged top
    bx = x + 118
    d.polygon([(bx, base), (bx, base - 58), (bx + 26, base - 44), (bx + 44, base - 66),
               (bx + 74, base - 50), (bx + 74, base)], fill=(70, 66, 88))
    # third block
    d.rectangle([x + 216, base - 62, x + 282, base], fill=(88, 84, 104))
    for bx0, bw, bh in ((x + 18, 74, 74), (x + 216, 66, 62)):
        for r_ in range(4):
            for c_ in range(3):
                wx, wy = bx0 + 10 + c_ * 22, base - bh + 10 + r_ * 16
                d.rectangle([wx, wy, wx + 9, wy + 8], fill=(250, 196, 84))
    # fire glow + smoke over the struck block
    d.ellipse([bx + 12, base - 40, bx + 62, base - 12], fill=(226, 110, 32))
    d.ellipse([bx + 22, base - 30, bx + 52, base - 16], fill=(250, 178, 64))
    for sx, sy, sr in ((bx + 14, 8, 13), (bx + 38, 3, 17), (bx + 66, 10, 11)):
        d.ellipse([sx, y + sy, sx + sr * 2, y + sy + sr], fill=(150, 146, 160))
    # rescue light beam
    d.polygon([(x + 250, base), (x + 196, base - 66), (x + 214, base - 70)], fill=(255, 226, 130))


# ---------- simplified world map with numbered pins ----------

def lonlat(lon, lat, x, y, w, h):
    return x + (lon + 180) / 360 * w, y + (65 - lat) / 115 * h


def draw_map(d, x, y, w, h, pins):
    d.rectangle([x, y, x + w, y + h], fill=(222, 228, 222), outline=RULE)
    land = (178, 196, 164)
    # rough continent blobs (lon/lat polygons)
    polys = [
        [(-168, 66), (-140, 70), (-125, 49), (-122, 37), (-105, 20), (-97, 16),
         (-87, 13), (-83, 9), (-79, 9), (-90, 14), (-97, 26), (-90, 29), (-81, 25),
         (-76, 35), (-70, 42), (-65, 45), (-80, 48), (-95, 49), (-125, 60), (-152, 60)],
        [(-79, 9), (-70, 11), (-62, 8), (-50, 0), (-44, -3), (-35, -8), (-41, -22),
         (-48, -28), (-58, -35), (-65, -41), (-71, -50), (-74, -52), (-73, -44),
         (-73, -30), (-70, -18), (-77, -12), (-81, -4), (-80, 1), (-77, 4)],
        [(-10, 36), (-9, 43), (-2, 44), (0, 46), (-5, 48), (2, 50), (8, 55), (8, 57),
         (18, 56), (21, 55), (24, 58), (30, 60), (28, 66), (18, 69), (10, 62), (5, 58),
         (5, 52), (10, 44), (12, 42), (19, 40), (23, 36), (28, 37), (30, 36), (36, 36),
         (30, 41), (23, 40), (19, 42), (14, 44), (8, 44), (3, 42), (0, 39), (-2, 37)],
        [(-17, 15), (-10, 5), (2, 6), (9, 4), (9, -1), (13, -12), (12, -18), (14, -22),
         (19, -34), (27, -34), (32, -26), (35, -20), (36, -10), (40, -2), (41, 2),
         (51, 11), (44, 11), (40, 15), (38, 18), (35, 24), (33, 27), (32, 31), (22, 33),
         (11, 34), (0, 36), (-6, 35), (-10, 31), (-17, 21)],
        [(36, 36), (44, 38), (48, 30), (55, 25), (58, 23), (60, 25), (66, 25), (72, 20),
         (76, 8), (80, 8), (86, 20), (88, 22), (92, 16), (95, 16), (98, 10), (100, 6),
         (103, 2), (105, 9), (107, 12), (109, 14), (106, 20), (110, 21), (114, 22),
         (118, 25), (121, 28), (122, 31), (120, 35), (122, 38), (126, 38), (127, 40),
         (130, 42), (132, 43), (137, 45), (141, 46), (141, 50), (137, 54), (142, 59),
         (155, 60), (170, 66), (178, 65), (178, 68), (150, 70), (120, 73), (100, 77),
         (80, 73), (66, 69), (55, 68), (50, 65), (45, 66), (40, 64), (35, 60), (33, 55),
         (35, 50), (36, 45), (36, 40)],
        [(113, -22), (114, -32), (118, -35), (124, -33), (130, -32), (134, -33), (137, -35),
         (140, -38), (145, -38), (150, -37), (153, -30), (153, -25), (150, -22), (146, -19),
         (142, -11), (140, -12), (136, -12), (132, -11), (126, -14), (122, -17), (117, -20)],
        [(95, 5), (100, 0), (105, -3), (110, -4), (114, -2), (117, 0), (115, 3), (110, 2),
         (105, 3), (100, 5), (97, 6)],
        [(130, 31), (133, 34), (137, 35), (140, 36), (141, 40), (141, 44), (143, 44),
         (141, 40), (140, 37), (138, 35), (135, 34), (131, 32)],
    ]
    for poly in polys:
        pts = [lonlat(lon, lat, x, y, w, h) for lon, lat in poly]
        d.polygon(pts, fill=land)
    for p in pins:
        px, py = lonlat(p["lon"], p["lat"], x, y, w, h)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=1)
        s = str(p["n"])
        f = F(SANS_B, 9 if p["n"] < 10 else 8)
        tw = d.textlength(s, font=f)
        d.text((px - tw / 2, py - 5), s, font=f, fill=(255, 255, 255))


ART = {"cop31": art_cop31, "capitol": art_capitol, "kyiv": art_kyiv}


def main():
    data = json.load(open(os.path.join(HERE, "news.json")))
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    total = len(data["leads"]) + len(data["tiles"]) + len(data["index"])

    # ----- masthead -----
    y = 8
    name_f = F(SERIF_B, 34)
    tw = d.textlength(data["paper"], font=name_f)
    d.text(((W - tw) / 2, y), data["paper"], font=name_f, fill=INK)
    y += 44
    d.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=3)
    y += 5
    date_f = F(SANS_B, 31)
    tw = d.textlength(data["date_line"], font=date_f)
    d.text(((W - tw) / 2, y), data["date_line"], font=date_f, fill=RED)
    y += 40
    counts = (f"{total} STORIES · 7 REGIONS · 18 FIELDS · EVERY STORY HAPPENED OR WAS "
              f"FIRST REPORTED ON MONDAY 23 NOVEMBER 2026")
    cf = F(SANS_B, 12)
    tw = d.textlength(counts, font=cf)
    d.text(((W - tw) / 2, y), counts, font=cf, fill=INK)
    y += 19
    d.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=2)
    y += 6

    # ----- timeline strip -----
    d.rectangle([MARGIN, y, W - MARGIN, y + 34], fill=(238, 232, 214), outline=RULE)
    tf = F(COND_B, 11)
    d.text((MARGIN + 6, y + 5), "THE DAY", font=F(SANS_B, 10), fill=RED)
    d.text((MARGIN + 6, y + 18), "IN UTC", font=F(SANS_B, 10), fill=RED)
    d.line([MARGIN + 58, y + 3, MARGIN + 58, y + 31], fill=RULE)
    colw = (CW - 70) / 6
    for i, item in enumerate(data["timeline"]):
        tx = MARGIN + 64 + i * colw
        d.text((tx, y + 3), item["t"] + " UTC", font=tf, fill=INK)
        for j, ln in enumerate(wrap(d, item["x"], F(COND, 9), colw - 6)[:2]):
            d.text((tx, y + 17 + j * 9), ln, font=F(COND, 9), fill=MUTED)
    y += 40

    # ----- leads -----
    lead_h = 262
    colw = (CW - 16) / 3
    for i, lead in enumerate(data["leads"]):
        lx = MARGIN + i * (colw + 8)
        ART[lead["art"]](d, lx, y, colw, 104)
        ly = y + 108
        kick = f"No. {lead['n']} · {lead['region']} · {lead['field']}"
        d.text((lx, ly), kick, font=F(SANS_B, 10), fill=RED)
        ly += 14
        for ln in wrap(d, lead["headline"], F(SANS_B, 17), colw)[:3]:
            d.text((lx, ly), ln, font=F(SANS_B, 17), fill=INK)
            ly += 20
        ly += 2
        for ln in wrap(d, lead["summary"], F(SANS, 11), colw)[:5]:
            d.text((lx, ly), ln, font=F(SANS, 11), fill=INK)
            ly += 14
        bx = badge(d, lx, y + lead_h - 16, lead["status"], F(SANS_B, 9))
        d.text((bx + 6, y + lead_h - 14), "— " + lead["source"], font=F(COND, 10), fill=MUTED)
    y += lead_h + 4
    d.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=2)
    y += 5
    d.text((MARGIN, y), "MORE OF THE DAY — 14 STORIES, EACH WITH ITS SOURCE AND STATUS",
           font=F(SANS_B, 12), fill=INK)
    y += 18

    # ----- tiles: 2 columns x 7 rows -----
    tile_h = 37
    tcolw = (CW - 10) / 2
    for idx, tile in enumerate(data["tiles"]):
        r_, c_ = divmod(idx, 2)
        tx, ty = MARGIN + c_ * (tcolw + 10), y + r_ * tile_h
        num_chip(d, tx, ty, tile["n"])
        kick = f"{tile['region']} · {tile['field']}"
        d.text((tx + 22, ty + 1), kick, font=F(SANS_B, 9), fill=RED)
        st = tile["status"]
        sw = d.textlength(st, font=F(SANS_B, 8)) + 8
        d.rectangle([tx + tcolw - sw, ty, tx + tcolw, ty + 12], fill=BADGE[st])
        d.text((tx + tcolw - sw + 4, ty + 1), st, font=F(SANS_B, 8), fill=(255, 255, 255))
        hl = fit(d, tile["headline"], F(COND_B, 13), tcolw - 22)
        d.text((tx + 22, ty + 12), hl, font=F(COND_B, 13), fill=INK)
        sm = fit(d, tile["summary"] + "  — " + tile["source"].title(), F(COND, 10), tcolw - 22)
        d.text((tx + 22, ty + 26), sm, font=F(COND, 10), fill=MUTED)
        if r_ < 6:
            d.line([tx, ty + tile_h - 2, tx + tcolw, ty + tile_h - 2], fill=(205, 198, 178))
    y += 7 * tile_h + 4
    d.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=2)
    y += 5

    # ----- map + date check -----
    row_h = 128
    map_w = 540
    d.text((MARGIN, y), "WHERE IT HAPPENED — PIN NUMBERS MATCH THE STORIES ABOVE",
           font=F(SANS_B, 10), fill=INK)
    draw_map(d, MARGIN, y + 14, map_w, row_h - 14, data["map_pins"])
    dx = MARGIN + map_w + 12
    dw = W - MARGIN - dx
    d.rectangle([dx, y, dx + dw, y + row_h], fill=(255, 252, 240), outline=RED, width=2)
    d.text((dx + 8, y + 5), "DATE CHECK — OLD NEWS WE LEFT OUT", font=F(SANS_B, 11), fill=RED)
    d.text((dx + 8, y + 20), "These famous stories are NOT from Monday 23 November:",
           font=F(COND, 10), fill=MUTED)
    dcy = y + 34
    for item in data["date_check"]:
        line = fit(d, "✕ " + item["x"], F(COND, 10), dw - 66)
        d.text((dx + 8, dcy), line, font=F(COND, 10), fill=INK)
        dl = item["d"]
        d.text((dx + dw - 8 - d.textlength(dl, font=F(COND_B, 10)), dcy), dl,
               font=F(COND_B, 10), fill=RED)
        dcy += 13
    d.text((dx + 8, dcy + 2), "Only events of 23 Nov 2026 are counted as today's news.",
           font=F(COND_B, 10), fill=INK)
    y += row_h + 6
    d.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=2)
    y += 5

    # ----- index -----
    d.text((MARGIN, y), "THE REST OF MONDAY — 42 MORE STORIES IN ONE LINE EACH   "
                        "(C = CONFIRMED · R = REPORTED · CL = CLAIM)",
           font=F(SANS_B, 11), fill=INK)
    y += 16
    icolw = (CW - 16) / 3
    per_col = 14
    for idx, item in enumerate(data["index"]):
        c_, r_ = divmod(idx, per_col)
        ix, iy = MARGIN + c_ * (icolw + 8), y + r_ * 12
        d.text((ix, iy), str(item["n"]), font=F(SANS_B, 9), fill=RED)
        txt = fit(d, item["x"], F(COND, 10), icolw - 52)
        d.text((ix + 20, iy), txt, font=F(COND, 10), fill=INK)
        chip = item["s"]
        cw_ = 15 if chip == "CL" else 11
        d.rectangle([ix + icolw - cw_, iy + 1, ix + icolw, iy + 11], fill=CHIP[chip])
        cf2 = F(SANS_B, 7)
        tw = d.textlength(chip, font=cf2)
        d.text((ix + icolw - cw_ + (cw_ - tw) / 2, iy + 2), chip, font=cf2, fill=(255, 255, 255))
    y += per_col * 12 + 4

    # ----- footer -----
    d.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=2)
    y += 4
    foot = ("Sources named on every story: Reuters · AP · AFP · BBC · Xinhua · SCMP · FT · WSJ · Bloomberg · "
            "CNA · CBS Sports · ESPN · TSN · Inshorts · UDN · ETtoday — all reports of Monday 23 November 2026.")
    foot = fit(d, foot, F(COND, 9), CW)
    tw = d.textlength(foot, font=F(COND, 9))
    d.text(((W - tw) / 2, y), foot, font=F(COND, 9), fill=MUTED)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
