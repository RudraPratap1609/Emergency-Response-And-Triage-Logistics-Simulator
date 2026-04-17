import pygame
import sys
import random
import math
import json
import os

from items import SUPPLY_ITEMS, CATEGORY_COLORS, CAT_ABBREV
from knapsack import solve_01_knapsack, solve_greedy, evaluate

pygame.init()

SW, SH = 1280, 720
screen = pygame.display.set_mode((SW, SH), pygame.SCALED)
pygame.display.set_caption("Crisis Command | Space Optimizer")
clock = pygame.time.Clock()
FPS = 60

HISTORY_FILE = "player_history.json"

C = {
    "bg":        (  7,   9,  18),
    "panel":     ( 12,  17,  34),
    "card":      ( 15,  22,  44),
    "card_sel":  (  8,  42,  26),
    "card_hov":  ( 22,  34,  64),
    "card_dis":  ( 11,  14,  24),
    "border":    ( 32,  46,  76),
    "bdr_sel":   ( 28, 218,  95),
    "bdr_hov":   ( 38, 155, 255),
    "white":     (218, 228, 248),
    "muted":     ( 72,  95, 138),
    "dim":       ( 36,  52,  82),
    "cyan":      (  0, 215, 212),
    "green":     ( 28, 218,  95),
    "red":       (255,  60,  50),
    "blue":      ( 38, 148, 255),
    "orange":    (255, 162,  28),
    "yellow":    (255, 208,  40),
    "purple":    (148,  78, 248),
    "pink":      (255,  70, 155),
    "gold":      (255, 192,  38),
    "bar_bg":    ( 16,  24,  46),
    "teal_lo":   (  6,  36,  34),
    "teal_hi":   (  0, 212, 178),
}

STUDENT_C = {
    "bg":       (240, 245, 255),
    "panel":    (255, 255, 255),
    "card":     (230, 238, 255),
    "card_sel": (200, 245, 215),
    "card_hov": (210, 225, 255),
    "card_dis": (220, 220, 230),
    "border":   (180, 200, 230),
    "bdr_sel":  ( 30, 180,  80),
    "bdr_hov":  ( 50, 130, 230),
    "white":    ( 20,  30,  60),
    "muted":    ( 80, 100, 140),
    "dim":      (160, 180, 210),
    "cyan":     ( 10, 150, 160),
    "green":    ( 30, 160,  80),
    "red":      (200,  40,  40),
    "blue":     ( 30, 110, 210),
    "orange":   (210, 130,  20),
    "yellow":   (180, 140,  10),
    "purple":   (120,  60, 200),
    "pink":     (200,  50, 130),
    "gold":     (190, 140,  10),
    "bar_bg":   (200, 210, 230),
    "teal_lo":  (200, 235, 235),
    "teal_hi":  ( 10, 160, 140),
}

student_mode = False

def SC():
    return STUDENT_C if student_mode else C

def _font(names, size, bold=False):
    for name in names:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f:
                return f
        except Exception:
            pass
    return pygame.font.Font(None, size)

_MONO = ["consolas", "couriernew", "lucidaconsole", "courier", "monospace"]

F = {
    "hero":  _font(_MONO, 48, bold=True),
    "title": _font(_MONO, 32, bold=True),
    "large": _font(_MONO, 22, bold=True),
    "med":   _font(_MONO, 18),
    "small": _font(_MONO, 15),
    "tiny":  _font(_MONO, 13),
    "badge": _font(_MONO, 12, bold=True),
}

DIFFICULTIES = {
    "EASY":   {"n": 5,  "W": 25, "V": 50,  "color": None, "label": "5 items  W=25kg V=50L",  "tier": "Rescue Op",          "dots": "[ o o ]",  "time": 120},
    "MEDIUM": {"n": 8,  "W": 40, "V": 80,  "color": None, "label": "8 items  W=40kg V=80L",  "tier": "Tactical Response",  "dots": "[o o o]",  "time": 90},
    "HARD":   {"n": 10, "W": 55, "V": 100, "color": None, "label": "10 items W=55kg V=100L", "tier": "Critical Emergency", "dots": "[* * *]",  "time": 60},
    "CUSTOM": {"n": 8,  "W": 40, "V": 80,  "color": None, "label": "Custom",                 "tier": "Custom Op",          "dots": "[~ ~ ~]",  "time": 90},
}

def init_diff_colors():
    DIFFICULTIES["EASY"]["color"]   = SC()["green"]
    DIFFICULTIES["MEDIUM"]["color"] = SC()["yellow"]
    DIFFICULTIES["HARD"]["color"]   = SC()["red"]
    DIFFICULTIES["CUSTOM"]["color"] = SC()["purple"]

state = "MENU"
difficulty = "MEDIUM"
scenario = []
max_W = 0
max_V = 0
user_sel = set()
scroll_y = 0

dp_val = 0
dp_sel = []
dp_table = []
gr_val = 0
gr_sel = []
eval_data = {}

timer_start = 0
timer_duration = 0
timer_running = False
time_expired = False

custom_n = 8
custom_W = 40
custom_V = 80
custom_time = 90
custom_focus = None

history = []

LEFT_W = 460
CARD_W = 210
CARD_H = 110
CARD_PAD = 10
DEPOT_TOP = 80

LOADED_BASE_Y = 368

def load_history():
    global history
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except Exception:
            history = []
    else:
        history = []

def save_history(entry):
    history.append(entry)
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f)
    except Exception:
        pass

def txt(surf, text, fkey, color, x, y, align="left"):
    s = F[fkey].render(str(text), True, color)
    r = s.get_rect()
    if align == "center": r.centerx, r.top = x, y
    elif align == "right": r.right, r.top = x, y
    else: r.left, r.top = x, y
    surf.blit(s, r)
    return r

def rrect(surf, color, rect, radius=8, bw=0, bc=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if bw and bc:
        pygame.draw.rect(surf, bc, rect, bw, border_radius=radius)

def draw_glow(surf, rect, color, radius=10, alpha=55, layers=2):
    for i in range(layers, 0, -1):
        ex = i * 4
        s = pygame.Surface((rect.w + ex * 2, rect.h + ex * 2), pygame.SRCALPHA)
        a = min(255, (alpha * 2) // i)
        pygame.draw.rect(s, (*color[:3], a), s.get_rect(), border_radius=radius + ex)
        surf.blit(s, (rect.x - ex, rect.y - ex))

def gradient_bar(surf, x, y, w, h, val, max_val, c1, c2):
    ratio = min((val / max_val) if max_val else 0, 1.0)
    fill = int(ratio * w)
    pygame.draw.rect(surf, SC()["bar_bg"], (x, y, w, h), border_radius=h // 2)
    if fill > 0:
        for px in range(fill):
            t = px / max(fill - 1, 1)
            c = tuple(int(c1[j] + (c2[j] - c1[j]) * t) for j in range(3))
            pygame.draw.line(surf, c, (x + px, y + 2), (x + px, y + h - 2))
    border_c = SC()["red"] if ratio > 0.9 else SC()["border"]
    pygame.draw.rect(surf, border_c, (x, y, w, h), 1, border_radius=h // 2)

def draw_bg_grid():
    screen.fill(SC()["bg"])
    grid_c = (20, 28, 55) if not student_mode else (210, 220, 240)
    for gx in range(0, SW, 52):
        pygame.draw.line(screen, grid_c, (gx, 0), (gx, SH))
    for gy in range(0, SH, 52):
        pygame.draw.line(screen, grid_c, (0, gy), (SW, gy))

def draw_corner_accents(color=None):
    col = color or SC()["dim"]
    arm = 48
    for (cx, cy, dx, dy) in [(0, 0, 1, 1), (SW, 0, -1, 1), (0, SH, 1, -1), (SW, SH, -1, -1)]:
        for k in range(3):
            off = k * 8
            pygame.draw.line(screen, col, (cx + dx * off, cy + dy * off), (cx + dx * off, cy + dy * (arm - off)), 1)
            pygame.draw.line(screen, col, (cx + dx * off, cy + dy * off), (cx + dx * (arm - off), cy + dy * off), 1)

def category_badge(surf, cx, cy, abbrev, cat_color, r=11):
    bs = pygame.Surface((r * 2 + 6, r * 2 + 6), pygame.SRCALPHA)
    pygame.draw.circle(bs, (*cat_color, 210), (r + 3, r + 3), r)
    pygame.draw.circle(bs, (*cat_color, 70), (r + 3, r + 3), r + 2, 2)
    surf.blit(bs, (cx - r - 3, cy - r - 3))
    txt(surf, abbrev, "badge", (8, 8, 16), cx, cy - 6, "center")

def draw_timer_bar(surf, x, y, w, h):
    if not timer_running:
        return
    elapsed = (pygame.time.get_ticks() - timer_start) / 1000.0
    remaining = max(0, timer_duration - elapsed)
    ratio = remaining / timer_duration if timer_duration > 0 else 0
    c1 = SC()["green"] if ratio > 0.5 else (SC()["orange"] if ratio > 0.25 else SC()["red"])
    c2 = SC()["cyan"] if ratio > 0.5 else (SC()["yellow"] if ratio > 0.25 else SC()["pink"])
    pygame.draw.rect(surf, SC()["bar_bg"], (x, y, w, h), border_radius=h // 2)
    fill = int(ratio * w)
    if fill > 0:
        for px in range(fill):
            t = px / max(fill - 1, 1)
            c = tuple(int(c1[j] + (c2[j] - c1[j]) * t) for j in range(3))
            pygame.draw.line(surf, c, (x + px, y + 2), (x + px, y + h - 2))
    pygame.draw.rect(surf, SC()["border"], (x, y, w, h), 1, border_radius=h // 2)
    secs = int(remaining)
    tc = SC()["red"] if secs <= 10 else SC()["white"]
    txt(surf, f"{secs}s", "small", tc, x + w + 10, y - 2)

def get_timer_remaining():
    if not timer_running:
        return timer_duration
    elapsed = (pygame.time.get_ticks() - timer_start) / 1000.0
    return max(0, timer_duration - elapsed)

def user_stats():
    tw  = sum(scenario[i]["weight"] for i in user_sel)
    tv  = sum(scenario[i]["volume"] for i in user_sel)
    tval = sum(scenario[i]["value"]  for i in user_sel)
    return tw, tv, tval

def can_add(idx):
    tw, tv, _ = user_stats()
    return (tw + scenario[idx]["weight"] <= max_W and
            tv + scenario[idx]["volume"]  <= max_V)

def new_scenario(diff):
    global scenario, max_W, max_V, user_sel, scroll_y
    global timer_start, timer_duration, timer_running, time_expired
    cfg = DIFFICULTIES[diff]
    scenario = random.sample(SUPPLY_ITEMS, min(cfg["n"], len(SUPPLY_ITEMS)))
    max_W = cfg["W"]
    max_V = cfg["V"]
    user_sel = set()
    scroll_y = 0
    timer_duration = cfg["time"]
    timer_start = pygame.time.get_ticks()
    timer_running = True
    time_expired = False

def card_rects():
    rects = []
    for i in range(len(scenario)):
        col = i % 2
        row = i // 2
        x = CARD_PAD + col * (CARD_W + CARD_PAD)
        y = DEPOT_TOP + row * (CARD_H + CARD_PAD) - scroll_y
        rects.append(pygame.Rect(x, y, CARD_W, CARD_H))
    return rects

def remove_rects():
    rects = {}
    for j, idx in enumerate(sorted(user_sel)):
        ly = LOADED_BASE_Y + j * 36
        if ly > SH - 100:
            break
        rects[idx] = pygame.Rect(SW - 100, ly + 4, 80, 26)
    return rects

def draw_student_mode_btn(surf, mp):
    bw, bh = 140, 32
    bx = SW - bw - 14
    by = SH - bh - 10
    brect = pygame.Rect(bx, by, bw, bh)
    hov = brect.collidepoint(mp)
    col = SC()["purple"]
    if hov:
        draw_glow(surf, brect, col, radius=8, alpha=40, layers=1)
    rrect(surf, SC()["panel"], brect, 8, 2, col)
    label = "STUDENT MODE" if not student_mode else "EXPERT MODE"
    txt(surf, label, "tiny", SC()["white"], brect.centerx, by + 8, "center")
    return brect

def draw_history_btn(surf, mp):
    bw, bh = 120, 32
    bx = SW - bw - 164
    by = SH - bh - 10
    brect = pygame.Rect(bx, by, bw, bh)
    hov = brect.collidepoint(mp)
    col = SC()["cyan"]
    if hov:
        draw_glow(surf, brect, col, radius=8, alpha=40, layers=1)
    rrect(surf, SC()["panel"], brect, 8, 2, col)
    txt(surf, "HISTORY", "tiny", SC()["white"], brect.centerx, by + 8, "center")
    return brect

def draw_close_btn(surf, mp):
    bw, bh = 32, 32
    bx = SW - bw - 20
    by = 20
    brect = pygame.Rect(bx, by, bw, bh)
    hov = brect.collidepoint(mp)
    col = SC()["red"] if hov else SC()["panel"]
    rrect(surf, col, brect, 8, 2, SC()["red"])
    txt(surf, "X", "large", SC()["white"], brect.centerx, brect.centery - 10, "center")
    return brect

def draw_menu(mp):
    cbtn = draw_close_btn(screen, mp)
    init_diff_colors()
    draw_bg_grid()
    draw_corner_accents(SC()["dim"])
    t = pygame.time.get_ticks() / 1000.0

    if student_mode:
        pulse = 80 + int(30 * math.sin(t * 1.6))
        title_c = (pulse // 4, pulse // 2, pulse)
    else:
        pulse = 160 + int(75 * math.sin(t * 1.6))
        title_c = (0, pulse, min(255, pulse + 45))

    txt(screen, "CRISIS COMMAND SYSTEM", "hero", title_c, SW // 2, 20, "center")

    if student_mode:
        txt(screen, "Pick a difficulty, choose your supplies, beat the timer!",
            "small", SC()["muted"], SW // 2, 80, "center")
    else:
        txt(screen, "Emergency Resource Allocation Engine | 2D Knapsack DP: Weight + Volume",
            "small", SC()["muted"], SW // 2, 80, "center")

    pygame.draw.line(screen, SC()["cyan"], (SW // 2 - 240, 104), (SW // 2 + 240, 104), 1)
    pygame.draw.circle(screen, SC()["cyan"], (SW // 2, 104), 4)

    txt(screen, "SELECT OPERATION TIER", "large", SC()["white"], SW // 2, 115, "center")

    diff_btns = {}
    bw, bh = 270, 155
    gap = 15
    total = 4 * bw + 3 * gap
    bx0 = (SW - total) // 2

    for k, diff in enumerate(["EASY", "MEDIUM", "HARD", "CUSTOM"]):
        cfg = DIFFICULTIES[diff]
        col = cfg["color"]
        bx = bx0 + k * (bw + gap)
        rect = pygame.Rect(bx, 145, bw, bh)
        hov = rect.collidepoint(mp)

        if hov:
            draw_glow(screen, rect, col, radius=10, alpha=70)

        bg = SC()["card_hov"] if hov else SC()["panel"]
        rrect(screen, bg, rect, 10, 2, col if hov else SC()["border"])
        pygame.draw.rect(screen, col, pygame.Rect(bx + 2, 145, bw - 4, 5), border_radius=3)

        txt(screen, diff, "title", col, bx + bw // 2, 155, "center")
        txt(screen, cfg["tier"], "small", SC()["muted"], bx + bw // 2, 192, "center")
        txt(screen, cfg["dots"], "large", col, bx + bw // 2, 210, "center")

        sx = bx + 14
        if diff == "CUSTOM":
            txt(screen, "Items  : custom", "tiny", SC()["white"], sx, 238)
            txt(screen, "W / V  : custom", "tiny", SC()["white"], sx, 254)
            txt(screen, "Timer  : custom s", "tiny", SC()["orange"], sx, 270)
        else:
            txt(screen, f"Items  : {cfg['n']}", "tiny", SC()["white"], sx, 238)
            txt(screen, f"W:{cfg['W']}kg  V:{cfg['V']}L", "tiny", SC()["white"], sx, 254)
            txt(screen, f"Timer  : {cfg['time']}s", "tiny", SC()["orange"], sx, 270)

        diff_btns[diff] = rect

    if not student_mode:
        abox = pygame.Rect(50, 320, SW - 100, 185)
        rrect(screen, SC()["panel"], abox, 8, 1, SC()["border"])
        pygame.draw.rect(screen, SC()["cyan"], (50, 320, 3, 185), border_radius=2)

        txt(screen, "ALGORITHM  —  2D 0/1 KNAPSACK  (WEIGHT  x  VOLUME)",
            "large", SC()["cyan"], SW // 2, 330, "center")

        left_lines = [
            ("Problem:", SC()["muted"]),
            ("  n items, each with weight w_i, volume v_i, value val_i.", SC()["white"]),
            ("  Find subset that MAXIMISES total value", SC()["white"]),
            ("  within capacity W (kg) AND V (litres).", SC()["white"]),
            ("  Rule: each item taken 0 OR 1 times only.", SC()["orange"]),
        ]
        right_lines = [
            ("2D DP Recurrence:", SC()["cyan"]),
            ("  K[w][v] = max(", SC()["yellow"]),
            ("    K[w][v],               <- skip item i", SC()["muted"]),
            ("    val_i + K[w-wi][v-vi]  <- take item i", SC()["muted"]),
            ("  )", SC()["yellow"]),
            ("  Time O(n*W*V) | Space O(W*V)", SC()["green"]),
        ]
        for j, (line, col) in enumerate(left_lines):
            txt(screen, line, "small", col, 70, 365 + j * 20)
        for j, (line, col) in enumerate(right_lines):
            txt(screen, line, "small", col, SW // 2 + 10, 365 + j * 20)

        pygame.draw.line(screen, SC()["border"], (50, 525), (SW - 50, 525), 1)
        txt(screen, "HOW TO PLAY", "large", SC()["white"], SW // 2, 535, "center")
        steps = [
            ("1. Choose a difficulty — scenario randomized from 48 items.",  "4. Hit SUBMIT — 2D DP engine solves it instantly."),
            ("2. Click items to load: respect both WEIGHT and VOLUME limits.", "5. Compare: Your pick vs Greedy vs DP Optimal."),
            ("3. Beat the timer!",                                             "6. Study the K[w][V_max] slice to trace the DP."),
        ]
        for j, (ls, rs) in enumerate(steps):
            txt(screen, ls, "small", SC()["muted"], 90, 563 + j * 22)
            txt(screen, rs, "small", SC()["muted"], SW // 2 + 40, 563 + j * 22)
    else:
        hbox = pygame.Rect(80, 325, SW - 160, 265)
        rrect(screen, SC()["panel"], hbox, 10, 1, SC()["border"])
        txt(screen, "HOW TO PLAY", "title", SC()["blue"], SW // 2, 340, "center")
        steps = [
            ("1. Pick EASY, MEDIUM, HARD or set your own CUSTOM difficulty."),
            ("2. You have limited TIME to pack a rescue vehicle."),
            ("3. Click items to add — watch BOTH the weight AND volume bars!"),
            ("4. Hit SUBMIT. See if you beat the computer's optimal solution."),
            ("5. Check HISTORY to see how you've improved over time."),
        ]
        for j, step in enumerate(steps):
            txt(screen, step, "med", SC()["white"], SW // 2, 390 + j * 32, "center")

    txt(screen,
        "VIT Vellore | Design & Analysis of Algorithms | 2D Space Optimized DP",
        "tiny", SC()["dim"], SW // 2, SH - 30, "center")

    sm_btn = draw_student_mode_btn(screen, mp)
    his_btn = draw_history_btn(screen, mp)

    return diff_btns, sm_btn, his_btn, cbtn

def draw_custom_setup(mp):
    global custom_n, custom_W, custom_V, custom_time, custom_focus
    draw_bg_grid()
    draw_corner_accents(SC()["dim"])
    cbtn = draw_close_btn(screen, mp)

    txt(screen, "CUSTOM DIFFICULTY SETUP", "hero", SC()["purple"], SW // 2, 20, "center")
    txt(screen, "Configure your own scenario", "small", SC()["muted"], SW // 2, 80, "center")

    fields = [
        ("Number of Items",   "custom_n",    custom_n,    3,  len(SUPPLY_ITEMS)),
        ("Weight Limit (kg)", "custom_W",    custom_W,   10, 100),
        ("Volume Limit (L)",  "custom_V",    custom_V,   20, 200),
        ("Timer (seconds)",   "custom_time", custom_time, 20, 300),
    ]

    box_w, box_h = 560, 68
    bx = SW // 2 - box_w // 2
    start_y = 138
    gap = 84

    field_rects = {}
    minus_rects = {}
    plus_rects = {}

    for j, (label, key, val, vmin, vmax) in enumerate(fields):
        by = start_y + j * gap
        brect = pygame.Rect(bx, by, box_w, box_h)
        focused = (custom_focus == key)
        col = SC()["purple"] if focused else SC()["border"]
        rrect(screen, SC()["panel"], brect, 8, 2, col)

        txt(screen, label, "med", SC()["white"], bx + 16, by + 10)
        txt(screen, str(val), "title", SC()["yellow"], bx + box_w // 2, by + 12, "center")

        mr = pygame.Rect(bx + 440, by + 14, 40, 40)
        pr = pygame.Rect(bx + 500, by + 14, 40, 40)
        minus_rects[key] = mr
        plus_rects[key] = pr
        field_rects[key] = brect

        mhov = mr.collidepoint(mp)
        phov = pr.collidepoint(mp)
        rrect(screen, SC()["red"] if mhov else SC()["panel"], mr, 6, 2, SC()["red"])
        rrect(screen, SC()["green"] if phov else SC()["panel"], pr, 6, 2, SC()["green"])
        txt(screen, "-", "title", SC()["white"], mr.centerx, mr.y + 2, "center")
        txt(screen, "+", "title", SC()["white"], pr.centerx, pr.y + 2, "center")

    start_btn = pygame.Rect(SW // 2 - 140, start_y + len(fields) * gap + 26, 280, 52)
    back_btn  = pygame.Rect(SW // 2 - 140, start_y + len(fields) * gap + 90, 280, 38)

    hov_s = start_btn.collidepoint(mp)
    if hov_s:
        draw_glow(screen, start_btn, SC()["green"], radius=10, alpha=70)
    rrect(screen, SC()["green"] if hov_s else SC()["panel"], start_btn, 8, 2, SC()["green"])
    txt(screen, "START CUSTOM", "large", SC()["white"], start_btn.centerx, start_btn.y + 14, "center")

    rrect(screen, SC()["panel"], back_btn, 6, 2, SC()["border"])
    txt(screen, "< BACK TO MENU", "small", SC()["muted"], back_btn.centerx, back_btn.y + 10, "center")

    return field_rects, minus_rects, plus_rects, start_btn, back_btn, cbtn

def draw_packing(mp):
    draw_bg_grid()
    cbtn = draw_close_btn(screen, mp)
    tw, tv, tval = user_stats()

    panel_s = pygame.Surface((LEFT_W, SH), pygame.SRCALPHA)
    if student_mode:
        panel_s.fill((230, 238, 255, 230))
    else:
        panel_s.fill((12, 17, 34, 225))
    screen.blit(panel_s, (0, 0))
    pygame.draw.line(screen, SC()["border"], (LEFT_W, 0), (LEFT_W, SH), 1)

    txt(screen, "SUPPLY DEPOT", "title", SC()["cyan"], LEFT_W // 2, 10, "center")
    if student_mode:
        txt(screen, "Click items to add. Watch weight AND volume!",
            "small", SC()["muted"], LEFT_W // 2, 45, "center")
    else:
        txt(screen, "Click to load | Scroll | Click loaded item to remove",
            "tiny", SC()["muted"], LEFT_W // 2, 45, "center")

    screen.set_clip(pygame.Rect(0, DEPOT_TOP - 2, LEFT_W, SH - DEPOT_TOP + 2))

    rects = card_rects()
    for i, r in enumerate(rects):
        if r.bottom < DEPOT_TOP or r.top > SH:
            continue

        item = scenario[i]
        sel = i in user_sel
        aff = can_add(i) or sel
        hov = (r.collidepoint(mp) and mp[0] < LEFT_W and mp[1] > DEPOT_TOP)

        if sel:
            bg, bdr = SC()["card_sel"], SC()["bdr_sel"]
        elif not aff:
            bg, bdr = SC()["card_dis"], SC()["border"]
        elif hov:
            bg, bdr = SC()["card_hov"], SC()["bdr_hov"]
        else:
            bg, bdr = SC()["card"], SC()["border"]

        if (sel or hov) and aff:
            draw_glow(screen, r, bdr, radius=8, alpha=40)

        rrect(screen, bg, r, 8, 2, bdr)

        cat_c = CATEGORY_COLORS.get(item.get("category", ""), SC()["muted"])
        abbrev = CAT_ABBREV.get(item.get("category", ""), "?")
        pygame.draw.rect(screen, cat_c, (r.x, r.y + 2, 4, CARD_H - 4), border_radius=2)
        category_badge(screen, r.right - 20, r.y + 14, abbrev, cat_c)

        nc = SC()["white"] if aff else SC()["muted"]
        txt(screen, item["name"], "med", nc, r.x + 12, r.y + 8)
        txt(screen, item.get("category", ""), "tiny", cat_c, r.x + 12, r.y + 28)
        txt(screen, f"Wt {item['weight']}kg  Vol {item['volume']}L", "tiny", SC()["muted"], r.x + 12, r.y + 44)
        txt(screen, f"Value  {item['value']} pts", "small", SC()["yellow"], r.x + 12, r.y + 59)

        if sel:
            txt(screen, "[LOADED]", "tiny", SC()["green"], r.right - 72, r.y + 88)
        elif not aff:
            tw_tmp = sum(scenario[k]["weight"] for k in user_sel)
            tv_tmp = sum(scenario[k]["volume"] for k in user_sel)
            w_over = tw_tmp + item["weight"] > max_W
            v_over = tv_tmp + item["volume"] > max_V
            if w_over and v_over:
                msg = "[NO ROOM]"
            elif w_over:
                msg = "[HEAVY]"
            else:
                msg = "[FULL]"
            txt(screen, msg, "tiny", SC()["red"], r.right - 72, r.y + 88)

    screen.set_clip(None)

    rows_total = (len(scenario) + 1) // 2
    content_h = rows_total * (CARD_H + CARD_PAD)
    if content_h > SH - DEPOT_TOP:
        txt(screen, "v  scroll  v", "tiny", SC()["muted"], LEFT_W // 2, SH - 14, "center")

    rx = LEFT_W + 16
    rw = SW - rx - 16

    txt(screen, "RESCUE VEHICLE", "title", SC()["white"], rx + rw // 2, 10, "center")
    txt(screen, f"Op: {difficulty}   {DIFFICULTIES[difficulty]['label']}",
        "tiny", SC()["muted"], rx + rw // 2, 45, "center")

    pygame.draw.line(screen, SC()["border"], (rx, 65), (rx + rw, 65), 1)

    txt(screen, "TIME REMAINING", "small", SC()["orange"], rx, 75)
    draw_timer_bar(screen, rx, 95, rw - 50, 16)

    if time_expired:
        txt(screen, "TIME'S UP!", "large", SC()["red"], rx + rw // 2, 118, "center")

    wr = tw / max_W if max_W else 0
    wc1 = SC()["red"] if wr > 0.9 else (SC()["orange"] if wr > 0.75 else SC()["blue"])
    wc2 = SC()["red"] if wr > 0.9 else (SC()["yellow"] if wr > 0.75 else SC()["cyan"])
    txt(screen, f"WEIGHT   {tw} / {max_W} kg", "med", SC()["white"], rx, 136)
    gradient_bar(screen, rx, 156, rw, 14, tw, max_W, wc1, wc2)

    vr = tv / max_V if max_V else 0
    vc1 = SC()["red"] if vr > 0.9 else (SC()["orange"] if vr > 0.75 else SC()["purple"])
    vc2 = SC()["red"] if vr > 0.9 else (SC()["yellow"] if vr > 0.75 else SC()["pink"])
    txt(screen, f"VOLUME   {tv} / {max_V} L", "med", SC()["white"], rx, 176)
    gradient_bar(screen, rx, 196, rw, 14, tv, max_V, vc1, vc2)

    vbox = pygame.Rect(rx, 218, rw, 38)
    rrect(screen, SC()["panel"], vbox, 6, 1, SC()["border"])
    txt(screen, f"SURVIVAL VALUE :  {tval} pts", "large", SC()["yellow"], rx + rw // 2, 228, "center")

    if not student_mode:
        ab = pygame.Rect(rx, 264, rw, 58)
        rrect(screen, SC()["panel"], ab, 6, 1, SC()["border"])
        pygame.draw.rect(screen, SC()["cyan"], (rx, 264, 3, 58), border_radius=2)
        txt(screen, "2D DP Recurrence:", "tiny", SC()["cyan"], rx + 10, 270)
        txt(screen, "K[w][v] = max( K[w][v], val_i + K[w-wi][v-vi] )", "small", SC()["yellow"], rx + 10, 286)
        txt(screen, f"2D table ({max_W+1} x {max_V+1}) built across {len(scenario)} items", "tiny", SC()["green"], rx + 10, 305)

    pygame.draw.line(screen, SC()["border"], (rx, 332), (rx + rw, 332), 1)
    txt(screen, "LOADED ITEMS", "med", SC()["cyan"], rx, 340)

    rm_rects = remove_rects()

    if not user_sel:
        txt(screen, "(none — click items on the left to add them)", "small", SC()["muted"], rx, LOADED_BASE_Y)
    else:
        for j, idx in enumerate(sorted(user_sel)):
            ly = LOADED_BASE_Y + j * 36
            if ly > SH - 100:
                txt(screen, "... more items loaded", "tiny", SC()["muted"], rx, ly)
                break
            item = scenario[idx]
            cat_c = CATEGORY_COLORS.get(item.get("category", ""), SC()["muted"])
            row_r = pygame.Rect(rx, ly, rw - 90, 30)
            rrect(screen, SC()["panel"], row_r, 4, 1, SC()["border"])
            pygame.draw.rect(screen, cat_c, (rx, ly + 1, 3, 28), border_radius=2)
            txt(screen, item["name"], "small", SC()["white"], rx + 12, ly + 8)
            txt(screen, f"{item['weight']}kg {item['volume']}L / {item['value']}pts", "tiny", SC()["muted"], rx + 160, ly + 10)
            rb = pygame.Rect(SW - 100, ly + 4, 80, 24)
            hov = rb.collidepoint(mp)
            if hov:
                draw_glow(screen, rb, SC()["red"], radius=4, alpha=40, layers=1)
            rrect(screen, SC()["red"] if hov else (45, 10, 10), rb, 4, 1, SC()["red"])
            txt(screen, "REMOVE", "tiny", SC()["white"], rb.centerx, ly + 6, "center")

    has_sel = bool(user_sel)
    sbtn = pygame.Rect(rx + rw // 2 - 140, SH - 70, 280, 50)
    hov = sbtn.collidepoint(mp) and has_sel

    if hov:
        draw_glow(screen, sbtn, SC()["green"], radius=10, alpha=70)

    rrect(screen, SC()["green"] if hov else ((20, 60, 35) if has_sel else SC()["panel"]), sbtn, 8, 2, SC()["green"] if has_sel else SC()["border"])
    txt(screen, "SUBMIT LOADOUT", "large", SC()["white"] if has_sel else SC()["muted"], sbtn.centerx, SH - 56, "center")

    if not has_sel:
        txt(screen, "select at least one item to continue", "tiny", SC()["red"], sbtn.centerx, SH - 14, "center")

    return rects, sbtn, cbtn

def draw_results(mp):
    draw_bg_grid()
    draw_corner_accents(SC()["dim"])
    cbtn = draw_close_btn(screen, mp)

    ed = eval_data
    eff = ed["efficiency"]
    ec = SC()["green"] if eff >= 90 else (SC()["orange"] if eff >= 70 else SC()["red"])

    RANK = {
        "OPTIMAL":      "S RANK  —  OPTIMAL",
        "NEAR OPTIMAL": "A RANK  —  NEAR OPTIMAL",
        "SUBOPTIMAL":   "B RANK  —  SUBOPTIMAL",
        "POOR":         "C RANK  —  POOR",
    }
    rank_txt = RANK.get(ed["status"], ed["status"])
    if time_expired:
        rank_txt = "TIMED OUT  —  " + rank_txt

    txt(screen, "MISSION DEBRIEF", "title", SC()["yellow"], SW // 2, 6, "center")
    txt(screen, f"{rank_txt} | Score: {ed['user_value']} pts | DP Optimal: {ed['dp_value']} pts | Efficiency: {eff:.1f}%", "small", ec, SW // 2, 45, "center")

    pygame.draw.line(screen, SC()["border"], (40, 65), (SW - 40, 65), 1)

    col_w = 380
    gap = 12
    total = 3 * col_w + 2 * gap
    cx0 = (SW - total) // 2
    cy, ch = 80, 260

    headers    = ["YOUR LOADOUT", "GREEDY HEURISTIC", "DP OPTIMAL"]
    subtitles  = ["manual selection", "val/(wt+vol) sort", "2D K[w][v] DP"]
    values_arr = [ed["user_value"], ed["greedy_value"], ed["dp_value"]]
    sels_list  = [sorted(user_sel), gr_sel, dp_sel]
    col_colors = [SC()["blue"], SC()["orange"], SC()["green"]]
    dp_set = set(dp_sel)

    for c in range(3):
        cx = cx0 + c * (col_w + gap)
        cr = pygame.Rect(cx, cy, col_w, ch)
        col = col_colors[c]

        if c == 2:
            draw_glow(screen, cr, col, radius=10, alpha=45)

        rrect(screen, SC()["panel"], cr, 10, 2, col)
        pygame.draw.rect(screen, col, (cx + 2, cy, col_w - 4, 5), border_radius=3)

        txt(screen, headers[c],   "large", col,          cx + col_w // 2, cy + 10, "center")
        txt(screen, subtitles[c], "tiny",  SC()["muted"], cx + col_w // 2, cy + 35, "center")

        sc = SC()["gold"] if c == 2 else col
        txt(screen, f"{values_arr[c]} pts", "title", sc, cx + col_w // 2, cy + 50, "center")

        sel = sels_list[c]
        sw = sum(scenario[i]["weight"] for i in sel)
        sv = sum(scenario[i]["volume"] for i in sel)
        txt(screen, f"W:{sw}/{max_W}kg  V:{sv}/{max_V}L  ({len(sel)} items)", "tiny", SC()["muted"], cx + 10, cy + 90)

        pygame.draw.line(screen, SC()["border"], (cx + 8, cy + 105), (cx + col_w - 8, cy + 105), 1)

        for j, idx in enumerate(sel):
            iy = cy + 110 + j * 22
            if iy > cy + ch - 30:
                txt(screen, f"  ... +{len(sel)-j} more", "tiny", SC()["muted"], cx + 10, iy)
                break
            item = scenario[idx]
            in_dp = idx in dp_set
            star = "*" if in_dp else "."
            sc2 = SC()["yellow"] if in_dp else SC()["muted"]
            txt(screen, star,              "small", sc2,          cx + 8,          iy)
            txt(screen, item["name"][:20], "small", SC()["white"], cx + 22,         iy)
            txt(screen, f"{item['value']}", "small", SC()["yellow"], cx + col_w - 10, iy, "right")

        gap_v = ed["dp_value"] - values_arr[c]
        if gap_v == 0:
            txt(screen, "[ OPTIMAL ]", "small", SC()["green"], cx + col_w // 2, cy + ch - 22, "center")
        else:
            txt(screen, f"[ Gap: -{gap_v} pts ]", "small", SC()["red"], cx + col_w // 2, cy + ch - 22, "center")

    txt(screen, "* = item in DP optimal  |  Greedy ranks by val/(weight+volume)", "tiny", SC()["yellow"], SW // 2, cy + ch + 5, "center")

    if not student_mode:
        tbl_hdr_y = cy + ch + 24
        txt(screen, "2D DP SLICE VISUALIZATION   K[w][V_max]", "large", SC()["cyan"], SW // 2, tbl_hdr_y, "center")
        txt(screen, "K[w] at v=V_max for each item step | YELLOW=optimal cell | Bright teal=value increased by taking item", "tiny", SC()["muted"], SW // 2, tbl_hdr_y + 22, "center")

        tbl_y = tbl_hdr_y + 40
        n = len(scenario)
        W_cap = max_W
        lbl_w = 100
        avail_w = SW - 16 - lbl_w
        avail_h = SH - tbl_y - 45
        cell_w = max(8, min(26, avail_w // (W_cap + 1)))
        cell_h = max(8, min(22, avail_h // (n + 2)))

        max_v_tbl = max((dp_table[i][w] for i in range(n + 1) for w in range(W_cap + 1)), default=1)
        max_v_tbl = max(max_v_tbl, 1)

        txt(screen, "i \\ w", "tiny", SC()["muted"], 4, tbl_y)
        for w in range(W_cap + 1):
            cx_t = lbl_w + w * cell_w
            if cx_t + cell_w > SW - 8:
                break
            txt(screen, str(w), "tiny", SC()["muted"], cx_t + cell_w // 2, tbl_y, "center")

        for i in range(n + 1):
            ry = tbl_y + 14 + i * cell_h
            if ry + cell_h > SH - 45:
                break
            lbl = "0 (base)" if i == 0 else f"{i} {scenario[i-1]['name'][:8]}"
            txt(screen, lbl, "tiny", SC()["muted"], 4, ry + 2)

            for w in range(W_cap + 1):
                cx_t = lbl_w + w * cell_w
                if cx_t + cell_w > SW - 8:
                    break
                v = dp_table[i][w]
                inten = v / max_v_tbl
                tl, th = SC()["teal_lo"], SC()["teal_hi"]
                r_ch = int(tl[0] + inten * (th[0] - tl[0]))
                g_ch = int(tl[1] + inten * (th[1] - tl[1]))
                b_ch = int(tl[2] + inten * (th[2] - tl[2]))
                cell_c = (r_ch, g_ch, b_ch)

                is_answer = (i == n and w == W_cap)
                changed = (i > 0 and v > dp_table[i - 1][w])

                if is_answer:
                    cell_c = SC()["yellow"]
                elif changed:
                    cell_c = (min(255, r_ch + 22), min(255, g_ch + 38), min(255, b_ch + 64))

                pygame.draw.rect(screen, cell_c, (cx_t, ry, cell_w - 1, cell_h - 1))

                if cell_w >= 14:
                    tc = (SC()["bg"] if is_answer else SC()["white"] if inten > 0.5 else SC()["muted"])
                    txt(screen, str(v), "tiny", tc, cx_t + cell_w // 2, ry + 2, "center")

    rbtn = pygame.Rect(SW // 2 - 280, SH - 36, 240, 30)
    mbtn = pygame.Rect(SW // 2 +  40, SH - 36, 240, 30)

    for btn, col, label in [(rbtn, SC()["green"], "PLAY AGAIN (same)"), (mbtn, SC()["blue"], "MAIN MENU")]:
        hov = btn.collidepoint(mp)
        if hov:
            draw_glow(screen, btn, col, radius=6, alpha=50, layers=1)
        rrect(screen, col if hov else SC()["panel"], btn, 6, 2, col)
        txt(screen, label, "small", SC()["white"], btn.centerx, SH - 28, "center")

    return rbtn, mbtn, cbtn

def draw_history(mp):
    draw_bg_grid()
    draw_corner_accents(SC()["dim"])
    cbtn = draw_close_btn(screen, mp)

    txt(screen, "PLAYER HISTORY", "hero", SC()["cyan"], SW // 2, 20, "center")
    txt(screen, f"{len(history)} games played", "small", SC()["muted"], SW // 2, 75, "center")

    pygame.draw.line(screen, SC()["border"], (40, 95), (SW - 40, 95), 1)

    if not history:
        txt(screen, "No games played yet!", "title", SC()["muted"], SW // 2, SH // 2, "center")
        txt(screen, "Play a round and come back here.", "med", SC()["muted"], SW // 2, SH // 2 + 50, "center")
    else:
        cols = [("#", 40), ("Difficulty", 140), ("Your Score", 140), ("DP Optimal", 140),
                ("Efficiency", 140), ("Status", 160), ("Timed Out", 110), ("Items", 80)]
        table_x = (SW - sum([c[1] for c in cols])) // 2
        table_y = 110
        row_h = 36
        headers = [c[0] for c in cols]
        widths  = [c[1] for c in cols]

        cx = table_x
        for h, w in zip(headers, widths):
            txt(screen, h, "small", SC()["cyan"], cx + w // 2, table_y, "center")
            cx += w

        pygame.draw.line(screen, SC()["border"], (table_x, table_y + 20), (table_x + sum(widths), table_y + 20), 1)

        max_rows = min(len(history), (SH - table_y - 180) // row_h)
        recent = history[-(max_rows):][::-1]

        for j, entry in enumerate(recent):
            ry = table_y + 24 + j * row_h
            eff = entry.get("efficiency", 0)
            ec = (SC()["green"] if eff >= 90 else SC()["orange"] if eff >= 70 else SC()["red"])

            row_bg = SC()["panel"] if j % 2 == 0 else SC()["card"]
            pygame.draw.rect(screen, row_bg, pygame.Rect(table_x, ry - 3, sum(widths), row_h - 2), border_radius=4)

            values = [
                str(len(history) - j),
                entry.get("difficulty", "?"),
                f"{entry.get('user_value', 0)} pts",
                f"{entry.get('dp_value', 0)} pts",
                f"{eff:.1f}%",
                entry.get("status", "?"),
                "YES" if entry.get("timed_out", False) else "no",
                str(entry.get("n_items", "?")),
            ]
            colors = [SC()["muted"], SC()["white"], SC()["yellow"], SC()["gold"], ec, ec,
                      SC()["red"] if entry.get("timed_out", False) else SC()["muted"], SC()["white"]]

            cx = table_x
            for val, col, w in zip(values, colors, widths):
                txt(screen, val, "small", col, cx + w // 2, ry + 4, "center")
                cx += w

        pygame.draw.line(screen, SC()["border"],
                         (table_x, table_y + 24 + max_rows * row_h),
                         (table_x + sum(widths), table_y + 24 + max_rows * row_h), 1)

        hist_y = table_y + 24 + max_rows * row_h + 15

        if len(history) >= 2 and hist_y + 160 < SH - 50:
            txt(screen, "EFFICIENCY OVER TIME", "large", SC()["cyan"], SW // 2, hist_y, "center")

            chart_x = 200
            chart_y = hist_y + 30
            chart_w = SW - 400
            chart_h = 100
            max_bars = min(len(history), 40)
            recent_h = history[-max_bars:]

            pygame.draw.rect(screen, SC()["panel"],
                             pygame.Rect(chart_x - 10, chart_y - 10, chart_w + 20, chart_h + 30), border_radius=6)

            bar_w = max(6, (chart_w - 10) // max_bars - 2)
            spacing = (chart_w - 10) // max_bars

            for k, entry in enumerate(recent_h):
                eff = entry.get("efficiency", 0)
                bh = int((eff / 100) * chart_h)
                bx = chart_x + k * spacing
                by = chart_y + chart_h - bh
                col = (SC()["green"] if eff >= 90 else SC()["orange"] if eff >= 70 else SC()["red"])
                pygame.draw.rect(screen, col, pygame.Rect(bx, by, bar_w, bh), border_radius=2)
                if bar_w >= 12 and k % max(1, max_bars // 10) == 0:
                    txt(screen, f"{int(eff)}%", "tiny", SC()["muted"], bx + bar_w // 2, by - 12, "center")

            for perc in [25, 50, 75, 100]:
                gy = chart_y + chart_h - int((perc / 100) * chart_h)
                pygame.draw.line(screen, SC()["dim"], (chart_x - 10, gy), (chart_x + chart_w + 10, gy), 1)
                txt(screen, f"{perc}%", "tiny", SC()["muted"], chart_x - 12, gy - 6, "right")

    back_btn = pygame.Rect(SW // 2 - 110, SH - 45, 200, 36)
    clr_btn  = pygame.Rect(SW // 2 + 110, SH - 45, 180, 36)
    hov_b = back_btn.collidepoint(mp)
    hov_c = clr_btn.collidepoint(mp)

    rrect(screen, SC()["blue"] if hov_b else SC()["panel"], back_btn, 6, 2, SC()["blue"])
    txt(screen, "< BACK TO MENU", "small", SC()["white"], back_btn.centerx, SH - 33, "center")

    rrect(screen, SC()["red"] if hov_c else SC()["panel"], clr_btn, 6, 2, SC()["red"])
    txt(screen, "CLEAR HISTORY", "small", SC()["white"], clr_btn.centerx, SH - 33, "center")

    return back_btn, clr_btn, cbtn

def main():
    global state, difficulty, student_mode
    global dp_val, dp_sel, dp_table, gr_val, gr_sel, eval_data
    global user_sel, scroll_y
    global timer_start, timer_duration, timer_running, time_expired
    global custom_n, custom_W, custom_V, custom_time, custom_focus
    global history

    load_history()

    diff_btns  = {}
    sbtn       = pygame.Rect(0, 0, 1, 1)
    rbtn       = pygame.Rect(0, 0, 1, 1)
    mbtn       = pygame.Rect(0, 0, 1, 1)
    sm_btn     = pygame.Rect(0, 0, 1, 1)
    his_btn    = pygame.Rect(0, 0, 1, 1)
    back_btn   = pygame.Rect(0, 0, 1, 1)
    clr_btn    = pygame.Rect(0, 0, 1, 1)
    field_rects  = {}
    minus_rects  = {}
    plus_rects   = {}
    cstart_btn = pygame.Rect(0, 0, 1, 1)
    cback_btn  = pygame.Rect(0, 0, 1, 1)
    cbtn       = pygame.Rect(0, 0, 1, 1)

    FIELD_LIMITS = {
        "custom_n":    (3, len(SUPPLY_ITEMS)),
        "custom_W":    (10, 100),
        "custom_V":    (20, 200),
        "custom_time": (20, 300),
    }

    while True:
        mp = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and state != "MENU":
                    state = "MENU"
                    timer_running = False

                if state == "CUSTOM":
                    if custom_focus == "custom_n":
                        if event.key == pygame.K_UP:   custom_n = min(FIELD_LIMITS["custom_n"][1], custom_n + 1)
                        elif event.key == pygame.K_DOWN: custom_n = max(FIELD_LIMITS["custom_n"][0], custom_n - 1)
                    elif custom_focus == "custom_W":
                        if event.key == pygame.K_UP:   custom_W = min(FIELD_LIMITS["custom_W"][1], custom_W + 5)
                        elif event.key == pygame.K_DOWN: custom_W = max(FIELD_LIMITS["custom_W"][0], custom_W - 5)
                    elif custom_focus == "custom_V":
                        if event.key == pygame.K_UP:   custom_V = min(FIELD_LIMITS["custom_V"][1], custom_V + 10)
                        elif event.key == pygame.K_DOWN: custom_V = max(FIELD_LIMITS["custom_V"][0], custom_V - 10)
                    elif custom_focus == "custom_time":
                        if event.key == pygame.K_UP:   custom_time = min(FIELD_LIMITS["custom_time"][1], custom_time + 10)
                        elif event.key == pygame.K_DOWN: custom_time = max(FIELD_LIMITS["custom_time"][0], custom_time - 10)

            if event.type == pygame.MOUSEWHEEL and state == "PACKING":
                scroll_y = max(0, scroll_y - event.y * 30)
                rows_total = (len(scenario) + 1) // 2
                max_scroll = max(0, rows_total * (CARD_H + CARD_PAD) - (SH - DEPOT_TOP) + 30)
                scroll_y = min(scroll_y, max_scroll)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if cbtn.collidepoint(mp):
                    pygame.quit()
                    sys.exit()

                if state == "MENU" and sm_btn.collidepoint(mp):
                    student_mode = not student_mode
                    continue

                if state == "MENU":
                    if his_btn.collidepoint(mp):
                        state = "HISTORY"
                        continue
                    for diff, rect in diff_btns.items():
                        if rect.collidepoint(mp):
                            if diff == "CUSTOM":
                                state = "CUSTOM"
                            else:
                                difficulty = diff
                                new_scenario(diff)
                                state = "PACKING"

                elif state == "CUSTOM":
                    for key, rect in field_rects.items():
                        if rect.collidepoint(mp):
                            custom_focus = key
                    for key, rect in minus_rects.items():
                        if rect.collidepoint(mp):
                            lo, hi = FIELD_LIMITS[key]
                            step = 5 if key == "custom_W" else (10 if key in ("custom_time", "custom_V") else 1)
                            if key == "custom_n":    custom_n    = max(lo, custom_n - step)
                            elif key == "custom_W":  custom_W    = max(lo, custom_W - step)
                            elif key == "custom_V":  custom_V    = max(lo, custom_V - step)
                            elif key == "custom_time": custom_time = max(lo, custom_time - step)
                    for key, rect in plus_rects.items():
                        if rect.collidepoint(mp):
                            lo, hi = FIELD_LIMITS[key]
                            step = 5 if key == "custom_W" else (10 if key in ("custom_time", "custom_V") else 1)
                            if key == "custom_n":    custom_n    = min(hi, custom_n + step)
                            elif key == "custom_W":  custom_W    = min(hi, custom_W + step)
                            elif key == "custom_V":  custom_V    = min(hi, custom_V + step)
                            elif key == "custom_time": custom_time = min(hi, custom_time + step)
                    if cstart_btn.collidepoint(mp):
                        DIFFICULTIES["CUSTOM"]["n"]     = custom_n
                        DIFFICULTIES["CUSTOM"]["W"]     = custom_W
                        DIFFICULTIES["CUSTOM"]["V"]     = custom_V
                        DIFFICULTIES["CUSTOM"]["time"]  = custom_time
                        DIFFICULTIES["CUSTOM"]["label"] = f"{custom_n} items  W={custom_W}kg V={custom_V}L"
                        difficulty = "CUSTOM"
                        new_scenario("CUSTOM")
                        state = "PACKING"
                    if cback_btn.collidepoint(mp):
                        state = "MENU"

                elif state == "PACKING":
                    handled = False
                    for idx, r in remove_rects().items():
                        if r.collidepoint(mp):
                            user_sel.discard(idx)
                            handled = True
                            break

                    if not handled:
                        if sbtn.collidepoint(mp) and user_sel:
                            timer_running = False
                            dp_val, dp_sel, dp_table = solve_01_knapsack(scenario, max_W, max_V)
                            gr_val, gr_sel = solve_greedy(scenario, max_W, max_V)
                            eval_data = evaluate(list(user_sel), dp_sel, gr_sel, scenario, dp_val, gr_val)
                            save_history({
                                "difficulty": difficulty,
                                "user_value": eval_data["user_value"],
                                "dp_value":   eval_data["dp_value"],
                                "efficiency": eval_data["efficiency"],
                                "status":     eval_data["status"],
                                "timed_out":  time_expired,
                                "n_items":    len(scenario),
                            })
                            state = "RESULTS"
                        elif time_expired and not user_sel:
                            pass
                        else:
                            for i, r in enumerate(card_rects()):
                                if (r.collidepoint(mp) and mp[0] < LEFT_W and mp[1] > DEPOT_TOP):
                                    if i in user_sel: user_sel.discard(i)
                                    elif can_add(i): user_sel.add(i)
                                    break

                elif state == "RESULTS":
                    if rbtn.collidepoint(mp):
                        new_scenario(difficulty)
                        state = "PACKING"
                    elif mbtn.collidepoint(mp):
                        state = "MENU"
                        timer_running = False

                elif state == "HISTORY":
                    if back_btn.collidepoint(mp):
                        state = "MENU"
                    elif clr_btn.collidepoint(mp):
                        history = []
                        try:
                            if os.path.exists(HISTORY_FILE):
                                os.remove(HISTORY_FILE)
                        except Exception:
                            pass

        if state == "PACKING" and timer_running:
            remaining = get_timer_remaining()
            if remaining <= 0 and not time_expired:
                time_expired = True
                timer_running = False

        if state == "MENU":
            diff_btns, sm_btn, his_btn, cbtn = draw_menu(mp)
        elif state == "CUSTOM":
            field_rects, minus_rects, plus_rects, cstart_btn, cback_btn, cbtn = draw_custom_setup(mp)
        elif state == "PACKING":
            _, sbtn, cbtn = draw_packing(mp)
        elif state == "RESULTS":
            rbtn, mbtn, cbtn = draw_results(mp)
        elif state == "HISTORY":
            back_btn, clr_btn, cbtn = draw_history(mp)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()