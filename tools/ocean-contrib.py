#!/usr/bin/env python3
"""Buat grafik kontribusi GitHub bertema laut (SVG animasi).

Pakai:
  python3 tools/ocean-contrib.py valentaditya assets/ocean-contrib.svg
  python3 tools/ocean-contrib.py valentaditya out.svg --html contributions.html   # data dari file

Data diambil dari halaman publik https://github.com/users/<username>/contributions,
jadi tidak perlu token. Hanya pakai library bawaan Python.
"""
import argparse
import datetime as dt
import html
import re
import sys
import urllib.request

LEVELS = ["#13263a", "#1f4e74", "#2f7fae", "#5fb4d9", "#bfeefe"]
CELL, GAP = 12, 3
STEP = CELL + GAP
W, H = 900, 280
GX, GY = 64, 74  # posisi grid
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def fetch(user):
    req = urllib.request.Request(
        f"https://github.com/users/{user}/contributions",
        headers={"User-Agent": "ocean-contrib-readme"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse(page):
    cells = []
    for tag in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", page):
        d = re.search(r'data-date="([\d-]+)"', tag)
        lv = re.search(r'data-level="(\d)"', tag)
        pos = re.search(r'id="contribution-day-component-(\d+)-(\d+)"', tag)
        if d and lv and pos:
            cells.append({
                "date": dt.date.fromisoformat(d.group(1)),
                "level": int(lv.group(1)),
                "row": int(pos.group(1)),
                "col": int(pos.group(2)),
            })
    if not cells:
        sys.exit("Tidak menemukan data kontribusi (format halaman GitHub mungkin berubah).")
    m = re.search(r"([\d,]+)\s+contributions?\s+in the last year", page)
    total = m.group(1) if m else str(len([c for c in cells if c["level"]]))
    return cells, total


def build(cells, total):
    cols = max(c["col"] for c in cells) + 1
    grid_w = cols * STEP - GAP
    grid_h = 7 * STEP - GAP
    out = []
    a = out.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    a(f"""  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0f2033"/><stop offset="100%" stop-color="#0b1622"/>
    </linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#7ec8e3" stop-opacity="0.6"/><stop offset="100%" stop-color="#ffd9b3" stop-opacity="0.4"/>
    </linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0"/>
      <stop offset="50%" stop-color="#e6f8ff" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#22507a"/><stop offset="100%" stop-color="#0b1622"/>
    </linearGradient>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="16"/></clipPath>
    <clipPath id="cells">""")
    for c in cells:
        a(f'      <rect x="{GX + c["col"] * STEP}" y="{GY + c["row"] * STEP}" width="{CELL}" height="{CELL}" rx="3"/>')
    a(f"""    </clipPath>
    <path id="spark" d="M0 -5 L1.2 -1.2 L5 0 L1.2 1.2 L0 5 L-1.2 1.2 L-5 0 L-1.2 -1.2 Z"/>
    <style>
      .t {{ font-family: 'Segoe UI', 'Helvetica Neue', 'Noto Sans', 'Noto Sans JP', Arial, sans-serif; }}
      .c {{ animation: rise .6s ease-out both; transform-box: fill-box; transform-origin: center; }}
      @keyframes rise {{ from {{ opacity: 0; transform: translateY(6px) scale(.6) }} to {{ opacity: 1; transform: none }} }}
      .shine {{ animation: sweep 7s ease-in-out infinite; animation-delay: 1.6s; }}
      @keyframes sweep {{ 0% {{ transform: translateX(0) }} 55%, 100% {{ transform: translateX({grid_w + 260}px) }} }}
      .tw {{ animation: twinkle 2.6s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
      @keyframes twinkle {{ 0%,100% {{ opacity: 0; transform: scale(.3) }} 50% {{ opacity: 1; transform: scale(1) }} }}
      .w1 {{ animation: drift 12s linear infinite; }}
      .w2 {{ animation: drift 7s linear infinite reverse; }}
      @keyframes drift {{ from {{ transform: translateX(0) }} to {{ transform: translateX(-200px) }} }}
      .boat {{ animation: sail 26s linear infinite; }}
      @keyframes sail {{ from {{ transform: translateX(-60px) }} to {{ transform: translateX({W + 60}px) }} }}
      .bob {{ animation: bob 2.4s ease-in-out infinite; transform-origin: 0 0; }}
      @keyframes bob {{ 0%,100% {{ transform: translateY(0) rotate(-3deg) }} 50% {{ transform: translateY(-3px) rotate(3deg) }} }}
    </style>
  </defs>
  <g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>""")

    # header
    a(f'  <text class="t" x="24" y="38" font-size="17" font-weight="700" fill="#ffffff">{html.escape(total)} <tspan font-weight="400" fill="#d4ebf6">contributions in the last year</tspan></text>')
    a(f'  <text class="t" x="{W - 24}" y="38" text-anchor="end" font-size="13" fill="#7ec8e3" letter-spacing="2">朝凪 · TIDE CHART</text>')

    # month labels
    last = -10
    for col in range(cols):
        days = sorted((c for c in cells if c["col"] == col), key=lambda c: c["row"])
        first = next((c for c in days if c["date"].day <= 7), None)
        if first and col - last >= 3 and col < cols - 1:
            a(f'  <text class="t" x="{GX + col * STEP}" y="{GY - 10}" font-size="11" fill="#8aa9bf">{MONTHS[first["date"].month - 1]}</text>')
            last = col
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        a(f'  <text class="t" x="24" y="{GY + row * STEP + 10}" font-size="11" fill="#8aa9bf">{name}</text>')

    # cells (fade in column by column)
    for c in cells:
        delay = c["col"] * 0.018 + c["row"] * 0.01
        a(f'  <rect class="c" style="animation-delay:{delay:.3f}s" x="{GX + c["col"] * STEP}" y="{GY + c["row"] * STEP}" '
          f'width="{CELL}" height="{CELL}" rx="3" fill="{LEVELS[c["level"]]}"/>')

    # light sweeping across the grid like sun on water
    a(f'  <g clip-path="url(#cells)"><rect class="shine" x="{GX - 220}" y="{GY}" width="200" height="{grid_h}" fill="url(#shine)"/></g>')

    # sparkles on the busiest days
    top = [c for c in cells if c["level"] >= 3]
    for i, c in enumerate(top[:24]):
        x = GX + c["col"] * STEP + CELL / 2
        y = GY + c["row"] * STEP + CELL / 2
        a(f'  <use class="tw" href="#spark" x="{x}" y="{y}" fill="#ffffff" style="animation-delay:{(i * 0.37) % 2.6:.2f}s"/>')

    # legend + updated
    ly = GY + grid_h + 26
    lx = GX + grid_w - (5 * STEP) - 30
    a(f'  <text class="t" x="{lx - 8}" y="{ly + 10}" text-anchor="end" font-size="11" fill="#8aa9bf">Less</text>')
    for i, col in enumerate(LEVELS):
        a(f'  <rect x="{lx + i * STEP}" y="{ly}" width="{CELL}" height="{CELL}" rx="3" fill="{col}"/>')
    a(f'  <text class="t" x="{lx + 5 * STEP + 6}" y="{ly + 10}" font-size="11" fill="#8aa9bf">More</text>')
    a(f'  <text class="t" x="{GX}" y="{ly + 10}" font-size="11" fill="#8aa9bf" fill-opacity="0.75">updated {dt.date.today().isoformat()}</text>')

    # sea + sailing boat
    sy = H - 34
    wave = lambda y, amp: (f"M0 {y} Q50 {y - amp} 100 {y} " + " ".join(f"T{x} {y}" for x in range(200, W + 400, 100)) + f" V{H} H0 Z")
    a(f'  <g class="w1" opacity="0.5"><path fill="#7ec8e3" d="{wave(sy, 8)}"/></g>')
    a(f"""  <g class="boat"><g transform="translate(0 {sy - 2})"><g class="bob">
    <path d="M-16 0 L16 0 L11 7 L-11 7 Z" fill="#f4a68c"/>
    <path d="M0 -26 L0 0" stroke="#d4ebf6" stroke-width="1.6"/>
    <path d="M1.5 -24 L15 -3 L1.5 -3 Z" fill="#ffe6cf"/>
    <path d="M-1.5 -18 L-11 -3 L-1.5 -3 Z" fill="#7ec8e3"/>
  </g></g></g>""")
    a(f'  <g class="w2"><path fill="url(#sea)" d="{wave(sy + 12, 7)}"/></g>')

    a("  </g>")
    a(f'  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="15.5" fill="none" stroke="url(#edge)" stroke-width="1.5"/>')
    a("</svg>")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("user")
    ap.add_argument("out")
    ap.add_argument("--html", help="baca data dari file HTML, bukan dari internet")
    a = ap.parse_args()
    page = open(a.html, encoding="utf-8").read() if a.html else fetch(a.user)
    cells, total = parse(page)
    open(a.out, "w", encoding="utf-8").write(build(cells, total))
    print(f"OK: {a.out} ({len(cells)} hari, {total} kontribusi)")


if __name__ == "__main__":
    main()
