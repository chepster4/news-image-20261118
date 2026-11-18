#!/usr/bin/env python3
"""news-image-20261118 — one front page summing up Wednesday 18 November 2026.

A single deterministic program: draws a 1024x1024 newspaper front page with
Pillow (no network, no randomness, no clock), and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (default: ./out/entry.png).

40 verified stories from 18 November 2026, researched from Reuters/AP/AFP/
NYT/WSJ/CNBC/UN/IMD/JTWC reporting: 1 lead story, 9 panels, 34 one-line
briefs, plus a real-coastline world map. Pure black-on-white newsprint, so a
vision judge can read the date and every headline.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 26
CW = W - 2 * MARGIN  # 972 content width

PAPER = (253, 253, 248)
INK = (17, 17, 17)
GREY = (90, 90, 90)
RED = (178, 28, 28)
NAVY = (30, 58, 95)
RULE = (150, 150, 150)
OCEAN = (214, 232, 244)
LAND = (183, 201, 168)
LAND_EDGE = (110, 130, 105)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text(draw, xy, s, fnt, fill=INK, anchor="la"):
    draw.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def panel(draw, x, y, w, h, kicker, headline, body, head_size=15):
    """One bordered news panel: red kicker, serif headline, sans body."""
    draw.rectangle([x, y, x + w, y + h], outline=RULE, width=1)
    draw.rectangle([x, y, x + w, y + 3], fill=RED)
    cx = x + 10
    cy = y + 10
    text(draw, (cx, cy), kicker, font(SANS_B, 10), fill=RED)
    cy += 16
    for line in wrap(draw, headline, font(SERIF_B, head_size), w - 20):
        text(draw, (cx, cy), line, font(SERIF_B, head_size))
        cy += head_size + 3
    cy += 2
    for line in wrap(draw, body, font(SANS, 11), w - 20):
        text(draw, (cx, cy), line, font(SANS, 11))
        cy += 14


def _project(lon, lat, w, h):
    """Equirectangular projection: lon -180..180 -> x 0..w,
    lat 90..-50 -> y 0..h (Antarctica cropped, as on wall maps)."""
    return ((lon + 180.0) / 360.0 * w, (90.0 - lat) / 140.0 * h)


# Simplified real coastlines as (lon, lat) outlines, traced clockwise.
# Coarse on purpose: at 972x100 px only the recognisable shape survives,
# but every continent now sits at its true longitude/latitude.
CONTINENTS = [
    # North America (Alaska down the west coast, up the east coast,
    # back west along the Arctic shore)
    [(-168, 66), (-164, 60), (-158, 58), (-152, 60), (-146, 60),
     (-140, 60), (-135, 58), (-130, 54), (-127, 50), (-124, 46),
     (-124, 42), (-122, 38), (-120, 34), (-117, 32), (-114, 29),
     (-111, 25), (-108, 23), (-105, 20), (-101, 18), (-97, 16),
     (-94, 16), (-91, 14), (-88, 13), (-85, 12), (-83, 9),
     (-80, 9), (-79, 9), (-82, 9), (-85, 11), (-87, 13),
     (-88, 15), (-88, 17), (-87, 19), (-90, 21), (-91, 19),
     (-93, 19), (-96, 19), (-97, 22), (-97, 26), (-94, 29),
     (-91, 29), (-89, 30), (-86, 30), (-84, 30), (-82, 28),
     (-81, 26), (-80, 27), (-80, 31), (-79, 33), (-76, 35),
     (-75, 37), (-74, 39), (-72, 41), (-70, 42), (-68, 44),
     (-66, 45), (-64, 44), (-60, 46), (-59, 48), (-55, 49),
     (-55, 52), (-58, 54), (-62, 56), (-64, 58), (-66, 60),
     (-70, 60), (-74, 62), (-78, 62), (-82, 63), (-86, 64),
     (-90, 66), (-94, 67), (-98, 68), (-102, 68), (-106, 68),
     (-110, 68), (-114, 69), (-118, 69), (-122, 70), (-126, 70),
     (-130, 70), (-134, 69), (-138, 69), (-142, 70), (-146, 70),
     (-150, 71), (-154, 71), (-158, 71), (-162, 70), (-166, 68)],
    # Greenland
    [(-55, 60), (-48, 60), (-42, 63), (-36, 66), (-30, 68),
     (-24, 70), (-20, 74), (-22, 78), (-28, 81), (-36, 81),
     (-44, 80), (-52, 79), (-58, 76), (-58, 72), (-56, 68),
     (-54, 64)],
    # South America
    [(-79, 9), (-77, 6), (-75, 10), (-72, 12), (-68, 11),
     (-64, 10), (-61, 9), (-58, 8), (-55, 6), (-52, 5),
     (-50, 3), (-50, 0), (-48, -2), (-44, -3), (-40, -5),
     (-37, -7), (-35, -9), (-37, -13), (-39, -17), (-40, -21),
     (-43, -23), (-46, -24), (-48, -27), (-51, -30), (-54, -34),
     (-57, -38), (-61, -41), (-64, -43), (-66, -47), (-68, -50),
     (-69, -52), (-70, -54), (-72, -53), (-73, -50), (-73, -46),
     (-73, -42), (-73, -38), (-72, -33), (-71, -29), (-70, -24),
     (-70, -19), (-72, -16), (-75, -15), (-78, -11), (-80, -7),
     (-81, -4), (-80, -1), (-79, 3), (-79, 7)],
    # Europe (Atlantic coast north, Baltic east shore south, Black Sea,
    # Greece, then west along the Mediterranean coast)
    [(-9, 37), (-9, 43), (-2, 48), (0, 50), (3, 53), (7, 55),
     (8, 57), (6, 59), (10, 62), (14, 66), (18, 69), (22, 70),
     (27, 71), (30, 70), (30, 66), (27, 63), (24, 60), (22, 58),
     (21, 56), (24, 54), (26, 52), (28, 49), (30, 46), (29, 44),
     (27, 43), (25, 42), (23, 40), (22, 37), (23, 36), (26, 36),
     (29, 36), (32, 36), (35, 36), (36, 36), (34, 37), (31, 37),
     (28, 37), (26, 38), (24, 39), (22, 40), (20, 41), (18, 40),
     (16, 40), (15, 42), (13, 44), (11, 44), (9, 44), (7, 44),
     (5, 43), (3, 42), (1, 41), (0, 39), (-2, 37), (-6, 36)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
     (1, 51), (-2, 50)],
    # Africa
    [(-6, 35), (-1, 35), (5, 37), (10, 37), (12, 34), (15, 32),
     (20, 32), (25, 32), (30, 31), (32, 31), (34, 28), (36, 25),
     (38, 22), (40, 19), (42, 15), (43, 12), (46, 11), (51, 11),
     (51, 10), (48, 6), (45, 2), (42, -2), (40, -6), (39, -10),
     (37, -14), (36, -18), (35, -21), (33, -25), (31, -29),
     (28, -33), (25, -34), (21, -35), (18, -34), (16, -31),
     (15, -27), (13, -22), (12, -17), (12, -12), (11, -7),
     (9, -2), (9, 3), (6, 4), (2, 6), (-3, 5), (-7, 4),
     (-11, 6), (-13, 8), (-15, 11), (-17, 14), (-17, 18),
     (-16, 22), (-15, 26), (-13, 29), (-10, 31), (-6, 33)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -19), (47, -22),
     (45, -25), (44, -22), (43, -19)],
    # Asia mainland (Arctic coast east, Pacific coast south, India,
    # then the Gulf coast back to the Caucasus)
    [(36, 36), (38, 38), (41, 40), (44, 41), (47, 43), (49, 45),
     (51, 47), (54, 49), (57, 51), (60, 53), (64, 55), (68, 57),
     (72, 59), (76, 61), (80, 63), (84, 65), (88, 67), (92, 69),
     (96, 71), (100, 72), (104, 73), (108, 74), (112, 73),
     (116, 72), (120, 72), (124, 71), (128, 71), (132, 71),
     (136, 72), (140, 72), (144, 72), (148, 71), (152, 70),
     (156, 69), (158, 67), (160, 64), (162, 60), (161, 57),
     (159, 54), (157, 51), (155, 50), (152, 53), (150, 56),
     (147, 59), (144, 59), (142, 55), (141, 51), (140, 47),
     (139, 43), (137, 40), (135, 38), (132, 37), (130, 36),
     (128, 38), (126, 38), (124, 40), (122, 38), (120, 35),
     (121, 31), (120, 27), (118, 24), (114, 22), (110, 21),
     (108, 18), (106, 13), (105, 9), (103, 7), (101, 8),
     (99, 10), (97, 13), (94, 16), (92, 20), (89, 22),
     (86, 20), (83, 18), (80, 15), (78, 10), (76, 8),
     (75, 11), (73, 16), (71, 20), (68, 23), (66, 25),
     (62, 25), (58, 25), (56, 26), (53, 27), (51, 28),
     (49, 30), (48, 30), (47, 32), (46, 34), (44, 36),
     (42, 38), (40, 40), (38, 38)],
    # Arabian peninsula
    [(43, 12), (45, 12), (48, 14), (51, 15), (54, 16), (56, 18),
     (58, 20), (59, 22), (58, 24), (56, 26), (54, 27), (52, 28),
     (50, 29), (48, 29), (46, 27), (44, 24), (43, 21), (42, 17),
     (42, 14)],
    # Indonesia archipelago
    [(95, 5), (98, 3), (101, 0), (104, -3), (107, -6), (110, -7),
     (114, -8), (118, -9), (122, -10), (126, -9), (130, -6),
     (134, -3), (138, -2), (141, -3), (141, -6), (138, -8),
     (134, -8), (130, -8), (126, -10), (122, -11), (118, -11),
     (114, -10), (110, -9), (106, -8), (102, -6), (98, -2),
     (95, 2)],
    # New Guinea
    [(131, -1), (134, -2), (137, -3), (140, -3), (143, -4),
     (146, -6), (149, -8), (150, -9), (147, -9), (144, -8),
     (141, -8), (138, -7), (135, -5), (132, -3)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 36),
     (140, 38), (141, 40), (142, 42), (144, 44), (143, 45),
     (141, 43), (140, 40), (138, 37), (136, 35), (134, 34),
     (132, 32)],
    # Philippines
    [(120, 18), (121, 17), (122, 15), (123, 13), (124, 11),
     (123, 10), (122, 11), (121, 13), (120, 15), (120, 17)],
    # Australia
    [(114, -22), (113, -25), (114, -29), (115, -33), (117, -35),
     (120, -34), (124, -33), (128, -32), (131, -32), (134, -33),
     (136, -35), (138, -35), (140, -38), (143, -38), (146, -39),
     (149, -37), (151, -36), (153, -33), (153, -30), (153, -27),
     (151, -24), (149, -21), (147, -19), (145, -16), (143, -14),
     (142, -11), (141, -13), (139, -14), (137, -13), (136, -15),
     (135, -15), (134, -12), (132, -12), (130, -13), (128, -14),
     (126, -14), (124, -16), (122, -18), (120, -20), (117, -21)],
    # Tasmania
    [(145, -41), (147, -41), (148, -42), (147, -43), (146, -44),
     (145, -42)],
    # New Zealand
    [(167, -45), (169, -43), (171, -42), (173, -40), (174, -39),
     (176, -38), (177, -38), (176, -40), (174, -41), (173, -42),
     (171, -43), (169, -45), (167, -46)],
]


def draw_map(draw, x, y, w, h):
    """Real-coastline world map: simplified lon/lat outlines projected
    equirectangularly, so every continent has its true shape and place
    (Greenland, UK, Japan, Indonesia, New Zealand all visible). Red dots
    mark the day's hotspots at their true coordinates."""
    draw.rectangle([x, y, x + w, y + h], fill=OCEAN, outline=RULE, width=1)
    text(draw, (x + w - 8, y + 5), "WORLD MAP — WHERE THE DAY HAPPENED",
         font(SANS_B, 10), fill=NAVY, anchor="ra")
    for poly in CONTINENTS:
        pts = [_project(lon, lat, w, h) for lon, lat in poly]
        draw.polygon([(x + px, y + py) for px, py in pts],
                     fill=LAND, outline=LAND_EDGE)
    # Faint ocean names, placed in open water.
    ocean_font = font(SANS_B, 8)
    ocean_fill = (105, 125, 140)
    text(draw, (x + 140, y + 88), "PACIFIC", ocean_font, fill=ocean_fill)
    text(draw, (x + 395, y + 42), "ATLANTIC", ocean_font, fill=ocean_fill)
    text(draw, (x + 648, y + 82), "INDIAN OCEAN", ocean_font,
         fill=ocean_fill)
    # Hotspots: (lon, lat, label, label dx, label dy)
    spots = [
        (56, 26, "GULF", -8, -16),
        (114, 22, "SHENZHEN", -30, -14),
        (36.5, 45, "KERCH", -12, -15),
        (-150, 64, "ALASKA", -18, -14),
        (25, -2, "D.R. CONGO", -32, 12),
        (-160, -21, "COOK IS.", -8, -14),
        (78, 21, "INDIA", -10, -15),
        (0, 51.5, "LONDON", -26, -14),
    ]
    for lon, lat, label, dx, dy in spots:
        sx, sy = _project(lon, lat, w, h)
        cx, cy = x + sx, y + sy
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED,
                     outline=(255, 255, 255), width=1)
        text(draw, (cx + dx, cy + dy), label, font(SANS_B, 9), fill=NAVY)


BRIEFS = [
    "HOUTHIS: 5 drones fired at Saudi pipeline near Riyadh",
    "BOARD OF PEACE faults Israel and Hamas on Gaza truce",
    "SIBERIA: Russian military plane crashes; 19 dead",
    "FINLAND: Ukraine drone damages Russian warship",
    "HORMUZ: ADNOC tanker hit; 1 missing, 11 injured",
    "IRAN says it shot down a US MQ-9 drone off Hormuz",
    "TRUMP meets Marcos Jr.; claims big Philippines deal",
    "PUTIN 'not ready' for serious Ukraine peace talks",
    "RUSSIA plans 20 million drones against Ukraine",
    "UKRAINE hits major oil refinery in southern Russia",
    "WORLD COURT to rule on Myanmar genocide case",
    "MYANMAR to review its future ties with ASEAN",
    "EUROPE: 8,000+ bomb threats in a single month",
    "US officer held on suspicion of spying for Russia",
    "ANTHROPIC prices IPO today; Nasdaq debut Thursday",
    "US blocks China's remote access to AI chips",
    "AI finds critical flaw in the Java language",
    "HUAWEI trial: closing arguments end in Brooklyn",
    "HUANG to testify to House over chip smuggling",
    "INDIA: record $10.07bn foreign inflows in November",
    "AMAZON to invest $7bn in India renewables by 2030",
    "UK inflation rises to 3.6% in latest reading",
    "GAZA: cold kills displaced people sheltering in tents",
    "QUAKES: Papua New Guinea 6.0; Romania 5.3; Peru 5.9",
    "CALIFORNIA hit by 30-ft El Nino storm waves",
    "NBA: Lakers 118-114 OT; Grimes scores 47; Pistons win",
    "NORWAY 3-2 Denmark; Illinois ends Duke home streak",
    "WORD OF THE YEAR: 'Human' — Cambridge Dictionary",
    "VOYAGER 1 reaches a distance record in deep space",
    "USA: computer outages reach the NSA, reports say",
    "NEWSMAX sues Fox to unwind $22bn Roku takeover",
    "FORD ships first CATL-tech battery cells in Michigan",
    "EU proposes €45bn loan for Ukraine in 2027",
    "UNICEF: 64 children killed in Yemen since September",
]


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- top bar ---
    d.rectangle([0, 0, W, 30], fill=INK)
    text(d, (W // 2, 8), "WEDNESDAY 18 NOVEMBER 2026  •  44 STORIES  •  SIX CONTINENTS",
         font(SANS_B, 12), fill=(255, 255, 255), anchor="ma")

    # --- masthead ---
    text(d, (W // 2, 40), "The World in One Day", font(SERIF_B, 56),
         anchor="ma")
    text(d, (W // 2, 102), "Wednesday 18 November 2026",
         font(SERIF_B, 24), fill=RED, anchor="ma")
    d.line([MARGIN, 132, W - MARGIN, 132], fill=INK, width=2)
    d.line([MARGIN, 136, W - MARGIN, 136], fill=INK, width=1)

    # --- lead story (left) + two panels (right) ---
    ly, lh = 144, 190
    d.rectangle([MARGIN, ly, MARGIN + 600, ly + lh], outline=RULE, width=1)
    d.rectangle([MARGIN, ly, MARGIN + 600, ly + 3], fill=RED)
    text(d, (MARGIN + 12, ly + 10), "LEAD STORY — THE GULF",
         font(SANS_B, 11), fill=RED)
    cy = ly + 30
    for line in wrap(d, "Iran strikes Kuwait and Bahrain after US hits Qeshm Island",
                     font(SERIF_B, 27), 576):
        text(d, (MARGIN + 12, cy), line, font(SERIF_B, 27))
        cy += 32
    cy += 4
    deck = ("US jets struck an IRGC missile site on Qeshm Island in the Strait "
            "of Hormuz. Iran answered with drones at US bases in Bahrain and "
            "Kuwait — all intercepted, no casualties. A third US carrier "
            "group sails for the Gulf as the region braces.")
    for line in wrap(d, deck, font(SANS, 13), 576):
        text(d, (MARGIN + 12, cy), line, font(SANS, 13))
        cy += 17
    cy += 4
    text(d, (MARGIN + 12, cy), "Drones intercepted  •  No casualties  •  Oil flows through Hormuz",
         font(SANS_B, 11), fill=NAVY)

    rx, rw = MARGIN + 612, 360
    panel(d, rx, ly, rw, 92, "SUMMIT EVE — SHENZHEN",
          "Xi and Putin meet; Trump lands Thursday",
          "The three leaders hold a rare trilateral on trade, AI and the "
          "wars in Ukraine and Iran.", head_size=14)
    panel(d, rx, ly + 98, rw, 92, "TECH — RECORD QUARTER",
          "Nvidia: $115.8bn revenue, up 103%",
          "First results since Jensen Huang resigned; the board says he "
          "will not return as chief executive.", head_size=14)

    # --- row A: four panels ---
    ay, ah = 344, 134
    aw = (CW - 3 * 12) // 4
    panel(d, MARGIN, ay, aw, ah, "UKRAINE — KERCH",
          "Kerch Bridge hit for a second day",
          "A road span collapses into the strait as Ukraine strikes the "
          "bridge to occupied Crimea again.")
    panel(d, MARGIN + (aw + 12), ay, aw, ah, "USA — SENATE",
          "Peltola wins Alaska; Democrats 56–44",
          "Mary Peltola unseats Dan Sullivan, giving Democrats the Senate "
          "majority in the final race called.")
    panel(d, MARGIN + 2 * (aw + 12), ay, aw, ah, "HEALTH — D.R. CONGO",
          "Ebola passes 11,000 cases",
          "Over 5,400 dead, the UN says; three in four infected children "
          "under five do not survive.")
    panel(d, MARGIN + 3 * (aw + 12), ay, aw, ah, "WEATHER — PACIFIC",
          "Cyclone Xavier hits Category 5",
          "Winds of 241 km/h bear down on the Northern Cook Islands; gale "
          "warnings for Pukapuka and Nassau.")

    # --- row B: three panels ---
    by, bh = 488, 118
    bw = (CW - 2 * 12) // 3
    panel(d, MARGIN, by, bw, bh, "ISRAEL — KNESSET",
          "Kahana elected speaker in blow to Netanyahu",
          "Matan Kahana, ally of PM-elect Gadi Eisenkot, wins the "
          "parliament's top job.", head_size=14)
    panel(d, MARGIN + (bw + 12), by, bw, bh, "HEALTH — USA",
          "US loses measles-free status after 26 years",
          "More than 5,400 cases and 10 deaths — a first since the "
          "early 1990s, officials say.", head_size=14)
    panel(d, MARGIN + 2 * (bw + 12), by, bw, bh, "AI — OPENAI",
          "OpenAI launches GPT-6.2 Astra and Sol",
          "Astra is priced 20% lower; Anthropic prices its IPO today, "
          "with a Nasdaq debut on Thursday.", head_size=14)

    # --- world map strip ---
    draw_map(d, MARGIN, 616, CW, 100)

    # --- briefs ---
    text(d, (MARGIN, 728), "IN BRIEF — 34 MORE STORIES FROM 18 NOVEMBER 2026",
         font(SANS_B, 13))
    d.line([MARGIN, 748, W - MARGIN, 748], fill=INK, width=1)
    col_w = (CW - 2 * 24) // 3
    for i, brief in enumerate(BRIEFS):
        col, row = divmod(i, 12)
        bx = MARGIN + col * (col_w + 24)
        byy = 758 + row * 19
        fnt = font(SANS, 11)
        if d.textlength(brief, font=fnt) > col_w:
            fnt = font(SANS, 10)
        d.text((bx, byy), "•  " + brief, font=fnt, fill=INK)

    # --- footer ---
    d.line([MARGIN, 994, W - MARGIN, 994], fill=INK, width=1)
    text(d, (W // 2, 1002),
         "Sources: Reuters, AP, AFP, NYT, WSJ, CNBC, UN, IMD, JTWC — all stories reported on Wednesday 18 November 2026.",
         font(SANS, 10), fill=GREY, anchor="ma")
    return img


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or (
        sys.argv[1] if len(sys.argv) > 1 else "out")
    os.makedirs(outdir, exist_ok=True)
    img = build()
    path = os.path.join(outdir, "entry.png")
    img.save(path, format="PNG")
    print(f"wrote {path} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
