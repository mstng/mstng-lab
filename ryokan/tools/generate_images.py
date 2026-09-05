#!/usr/bin/env python3
"""湯宿「月待荘」サイトのイメージ素材（SVG）を生成する。

写真素材を使わず、浮世絵・水墨画の意匠をベクタのレイヤとして組み立てる。
稜線・霞・水面・灯りといった部品を関数にして、季節や時刻のパレットを
差し替えることで全カットの空気感を揃えている。

    python3 tools/generate_images.py

出力先: images/*.svg
"""

import math
import os
import random

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images")


# ---------------------------------------------------------------- 基本ユーティリティ

def catmull_rom(points, tension=1.0):
    """通過点列を滑らかな三次ベジエのパス文字列にする。"""
    if len(points) < 2:
        return ""
    pts = [points[0]] + list(points) + [points[-1]]
    d = "M {:.2f} {:.2f}".format(pts[1][0], pts[1][1])
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / (6 * tension), p1[1] + (p2[1] - p0[1]) / (6 * tension))
        c2 = (p2[0] - (p3[0] - p1[0]) / (6 * tension), p2[1] - (p3[1] - p1[1]) / (6 * tension))
        d += " C {:.2f} {:.2f}, {:.2f} {:.2f}, {:.2f} {:.2f}".format(
            c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    return d


def ridge_points(w, base, amp, seed, samples=16, skew=0.0):
    """稜線の通過点。低周波の正弦を三本重ね、乱数で崩す。"""
    rnd = random.Random(seed)
    f = [rnd.uniform(0.7, 1.3), rnd.uniform(1.8, 2.6), rnd.uniform(3.4, 4.6)]
    p = [rnd.uniform(0, math.tau) for _ in range(3)]
    pts = []
    for i in range(samples + 1):
        t = i / samples
        x = t * w
        y = (0.60 * math.sin(t * math.tau * f[0] / 2 + p[0])
             + 0.28 * math.sin(t * math.tau * f[1] / 2 + p[1])
             + 0.12 * math.sin(t * math.tau * f[2] / 2 + p[2]))
        y += rnd.uniform(-0.10, 0.10)
        pts.append((x, base - amp * (y * 0.5 + 0.5) - skew * amp * t))
    return pts


def ridge(w, h, base, amp, seed, fill, opacity=1.0, samples=16, skew=0.0):
    """山の稜線シルエットを一枚のパスとして返す。"""
    pts = ridge_points(w, base, amp, seed, samples, skew)
    d = catmull_rom(pts) + " L {:.2f} {:.2f} L 0 {:.2f} Z".format(w, h, h)
    return '<path d="{}" fill="{}" opacity="{:.3f}"/>'.format(d, fill, opacity)


def mist(w, y, height, seed, color="#ffffff", opacity=0.30, count=5):
    """横に流れる霞。ぼかした扁平楕円を重ねる。"""
    rnd = random.Random(seed)
    out = ['<g filter="url(#soft)" opacity="{:.3f}">'.format(opacity)]
    for _ in range(count):
        cx = rnd.uniform(-0.1, 1.1) * w
        cy = y + rnd.uniform(-0.5, 0.5) * height
        rx = rnd.uniform(0.22, 0.48) * w
        ry = rnd.uniform(0.18, 0.42) * height
        out.append('<ellipse cx="{:.1f}" cy="{:.1f}" rx="{:.1f}" ry="{:.1f}" fill="{}" opacity="{:.2f}"/>'
                   .format(cx, cy, rx, ry, color, rnd.uniform(0.35, 0.9)))
    out.append("</g>")
    return "".join(out)


def moon(cx, cy, r, color="#f6f0e2", glow=0.55):
    return (
        '<g><circle cx="{cx}" cy="{cy}" r="{gr:.1f}" fill="url(#moonGlow)" opacity="{g:.2f}"/>'
        '<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}"/></g>'
    ).format(cx=cx, cy=cy, r=r, gr=r * 4.6, g=glow, c=color)


def pine(x, y, s, color="#1b2a31", opacity=0.95, seed=0):
    """水墨画ふうの松。幹を曲げ、葉叢を層に置く。"""
    rnd = random.Random(seed)
    g = ['<g opacity="{:.2f}" fill="{}">'.format(opacity, color)]
    trunk = [(x, y), (x - 4 * s, y - 26 * s), (x + 3 * s, y - 52 * s), (x - 2 * s, y - 78 * s)]
    g.append('<path d="{}" fill="none" stroke="{}" stroke-width="{:.1f}" stroke-linecap="round"/>'
             .format(catmull_rom(trunk), color, 3.4 * s))
    for i in range(4):
        bx = x + (10 if i % 2 else -12) * s * rnd.uniform(0.8, 1.3)
        by = y - (34 + i * 15) * s
        rx, ry = (26 - i * 3.4) * s * rnd.uniform(0.85, 1.15), (7 - i * 0.9) * s
        g.append('<path d="M {:.1f} {:.1f} q {:.1f} {:.1f} {:.1f} 0 q {:.1f} {:.1f} {:.1f} 0 Z"/>'
                 .format(bx - rx, by, rx * 0.5, -ry * 2.4, rx * 2, rx * 0.5, ry * 1.5, -rx * 2))
        g.append('<path d="M {:.1f} {:.1f} L {:.1f} {:.1f}" stroke="{}" stroke-width="{:.1f}" '
                 'stroke-linecap="round" fill="none"/>'.format(x, by + 6 * s, bx, by, color, 1.8 * s))
    g.append("</g>")
    return "".join(g)


def bamboo(x, y, s, color="#3d5545", opacity=0.8, seed=0, joints=7):
    rnd = random.Random(seed)
    g = ['<g opacity="{:.2f}">'.format(opacity)]
    lean = rnd.uniform(-6, 6) * s
    g.append('<path d="M {:.1f} {:.1f} Q {:.1f} {:.1f} {:.1f} {:.1f}" stroke="{}" stroke-width="{:.1f}" '
             'fill="none" stroke-linecap="round"/>'
             .format(x, y, x + lean, y - 70 * s, x + lean * 2, y - 140 * s, color, 3.0 * s))
    for i in range(joints):
        t = (i + 1) / (joints + 1)
        jx = x + lean * 2 * t * t
        jy = y - 140 * s * t
        g.append('<path d="M {:.1f} {:.1f} q {:.1f} {:.1f} {:.1f} {:.1f}" stroke="{}" stroke-width="{:.1f}" '
                 'fill="none" stroke-linecap="round"/>'
                 .format(jx, jy, 14 * s * (1 if i % 2 else -1), -6 * s,
                         26 * s * (1 if i % 2 else -1), -2 * s, color, 1.6 * s))
    g.append("</g>")
    return "".join(g)


def water(w, y, h, seed, top="#1d3346", bottom="#0d1c29", ripples=14):
    """水面。反射のグラデーションに、細い波線を散らす。"""
    rnd = random.Random(seed)
    out = ['<rect x="0" y="{:.1f}" width="{}" height="{:.1f}" fill="url(#waterGrad)"/>'.format(y, w, h)]
    out.append('<g stroke="#ffffff" fill="none" stroke-linecap="round">')
    for _ in range(ripples):
        ry = y + rnd.uniform(0.03, 1.0) ** 1.5 * h
        rx = rnd.uniform(0, w)
        length = rnd.uniform(0.04, 0.20) * w
        op = 0.05 + 0.22 * (1 - (ry - y) / h)
        out.append('<path d="M {:.1f} {:.1f} q {:.1f} {:.1f} {:.1f} 0" stroke-width="{:.1f}" opacity="{:.2f}"/>'
                   .format(rx, ry, length / 2, rnd.uniform(-2.5, 2.5), length, rnd.uniform(0.8, 1.9), op))
    out.append("</g>")
    return "".join(out)


def petals(w, h, seed, color="#f2c9d4", count=26, size=5.0, opacity=0.75, shape="petal"):
    """舞う花びら・紅葉・雪。季節のカットに撒く。"""
    rnd = random.Random(seed)
    out = ['<g opacity="{:.2f}">'.format(opacity)]
    for _ in range(count):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        s = size * rnd.uniform(0.5, 1.5)
        rot = rnd.uniform(0, 360)
        if shape == "snow":
            out.append('<circle cx="{:.1f}" cy="{:.1f}" r="{:.1f}" fill="{}" opacity="{:.2f}"/>'
                       .format(x, y, s * 0.45, color, rnd.uniform(0.4, 1.0)))
        elif shape == "leaf":
            out.append('<g transform="translate({:.1f} {:.1f}) rotate({:.0f})" opacity="{:.2f}">'
                       '<path d="M 0 {:.1f} L {:.1f} 0 L 0 {:.1f} L {:.1f} 0 Z" fill="{}"/></g>'
                       .format(x, y, rot, rnd.uniform(0.5, 1.0), -s, s * 0.8, s, -s * 0.8, color))
        else:
            out.append('<g transform="translate({:.1f} {:.1f}) rotate({:.0f})" opacity="{:.2f}">'
                       '<path d="M 0 0 q {:.1f} {:.1f} 0 {:.1f} q {:.1f} {:.1f} 0 {:.1f} Z" fill="{}"/></g>'
                       .format(x, y, rot, rnd.uniform(0.5, 1.0), s * 0.75, s * 0.6, s * 1.5,
                               -s * 0.75, -s * 0.6, -s * 1.5, color))
    out.append("</g>")
    return "".join(out)


# ---------------------------------------------------------------- 建具・灯り

def roof(cx, y, w, s=1.0, color="#141a1f", opacity=1.0, ridge_cap=True):
    """入母屋の屋根。反りのある勾配と、跳ね上げた軒先。"""
    h = w * 0.24
    rw = w * 0.11          # 棟の半分の長さ
    d = ("M {le:.1f} {ey:.1f} "
         "Q {lc:.1f} {lcy:.1f} {rl:.1f} {ry:.1f} "
         "L {rr:.1f} {ry:.1f} "
         "Q {rc:.1f} {lcy:.1f} {re:.1f} {ey:.1f} "
         "Q {cx:.1f} {by:.1f} {le:.1f} {ey:.1f} Z").format(
        le=cx - w / 2, re=cx + w / 2, ey=y - h * 0.10,
        lc=cx - w * 0.31, rc=cx + w * 0.31, lcy=y - h * 0.58,
        rl=cx - rw, rr=cx + rw, ry=y - h,
        cx=cx, by=y + h * 0.16)
    out = ['<path d="{}" fill="{}" opacity="{:.2f}"/>'.format(d, color, opacity)]
    if ridge_cap:
        out.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" rx="{:.1f}" '
                   'fill="{}" opacity="{:.2f}"/>'
                   .format(cx - rw * 1.24, y - h - h * 0.11, rw * 2.48, h * 0.13, h * 0.05,
                           color, opacity))
    return "".join(out)


def building(cx, y, w, seed=0, body="#171d22", warm="#f0b96a"):
    """宿の棟。屋根の下に、灯りの点いた障子窓を並べる。"""
    rnd = random.Random(seed)
    bh = w * 0.34
    g = ['<g>']
    g.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" fill="{}"/>'
             .format(cx - w * 0.42, y, w * 0.84, bh, body))
    win_w = w * 0.084
    n = 6
    for i in range(n):
        wx = cx - w * 0.35 + i * (w * 0.70 / (n - 1)) - win_w / 2
        lit = rnd.random() > 0.25
        g.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" rx="1" fill="{}" opacity="{:.2f}"/>'
                 .format(wx, y + bh * 0.22, win_w, bh * 0.40, warm if lit else "#2b3138",
                         0.92 if lit else 1.0))
        if lit:
            g.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" fill="{}" '
                     'filter="url(#soft)" opacity="0.42"/>'
                     .format(wx - win_w, y + bh * 0.22 - win_w, win_w * 3, bh * 0.40 + win_w * 2, warm))
    g.append(roof(cx, y + 4, w * 1.16, color=body))
    g.append("</g>")
    return "".join(g)


def lantern(x, y, s=1.0, warm="#f5b95c"):
    """提灯。灯芯のにじみをぼかしで足す。"""
    return (
        '<g><circle cx="{x}" cy="{cy:.1f}" r="{gr:.1f}" fill="{w}" opacity="0.20" filter="url(#soft)"/>'
        '<path d="M {x} {ty:.1f} L {x} {y}" stroke="#2a2320" stroke-width="{sw:.1f}"/>'
        '<ellipse cx="{x}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{w}" opacity="0.95"/>'
        '<ellipse cx="{x}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" stroke="#8a4a34" '
        'stroke-width="{sw2:.1f}" opacity="0.55"/></g>'
    ).format(x=x, y=y, ty=y - 30 * s, cy=y - 16 * s, rx=9 * s, ry=12 * s,
             gr=44 * s, sw=1.2 * s, sw2=1.0 * s, w=warm)


def stone_lantern(x, y, s=1.0, color="#3a3f42", warm="#f3c777"):
    """石灯籠。笠・火袋・竿の三段。"""
    return (
        '<g><circle cx="{x}" cy="{fy:.1f}" r="{gr:.1f}" fill="{w}" opacity="0.28" filter="url(#soft)"/>'
        '<rect x="{sx:.1f}" y="{sy:.1f}" width="{sw:.1f}" height="{sh:.1f}" fill="{c}"/>'
        '<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="{r:.1f}" fill="{c}"/>'
        '<rect x="{hx:.1f}" y="{hy:.1f}" width="{hw:.1f}" height="{hh:.1f}" fill="{w}" opacity="0.9"/>'
        '<path d="M {kx1:.1f} {ky:.1f} Q {x} {ky2:.1f} {kx2:.1f} {ky:.1f} Z" fill="{c}"/>'
        '<circle cx="{x}" cy="{tp:.1f}" r="{tr:.1f}" fill="{c}"/></g>'
    ).format(x=x, c=color, w=warm,
             sx=x - 3.5 * s, sy=y - 34 * s, sw=7 * s, sh=34 * s,
             bx=x - 11 * s, by=y - 52 * s, bw=22 * s, bh=18 * s, r=2 * s,
             hx=x - 6 * s, hy=y - 48 * s, hw=12 * s, hh=11 * s,
             kx1=x - 20 * s, kx2=x + 20 * s, ky=y - 52 * s, ky2=y - 70 * s,
             tp=y - 70 * s, tr=3.6 * s, fy=y - 43 * s, gr=40 * s)


def shoji(x, y, w, h, cols=4, rows=6, frame="#8b6f4e", paper="url(#shojiPaper)", sw=2.2):
    """障子。格子は等間隔に、紙は奥の灯りを透かす。"""
    g = ['<g>']
    g.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" fill="{}"/>'
             .format(x, y, w, h, paper))
    g.append('<g stroke="{}" stroke-width="{:.1f}" opacity="0.85">'.format(frame, sw))
    for i in range(1, cols):
        gx = x + w * i / cols
        g.append('<path d="M {:.1f} {:.1f} L {:.1f} {:.1f}"/>'.format(gx, y, gx, y + h))
    for j in range(1, rows):
        gy = y + h * j / rows
        g.append('<path d="M {:.1f} {:.1f} L {:.1f} {:.1f}"/>'.format(x, gy, x + w, gy))
    g.append("</g>")
    g.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" fill="none" stroke="{}" '
             'stroke-width="{:.1f}"/>'.format(x, y, w, h, frame, sw * 2.1))
    g.append("</g>")
    return "".join(g)


def tatami(x, y, w, h, rows=3, color="#b9ab7d", line="#8f8258"):
    """畳。目の線と縁で床の奥行きを出す。"""
    g = ['<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" fill="{}"/>'.format(x, y, w, h, color)]
    g.append('<g stroke="{}" stroke-width="1.6" opacity="0.5">'.format(line))
    for i in range(1, rows):
        gy = y + h * (i / rows) ** 0.78
        g.append('<path d="M {:.1f} {:.1f} L {:.1f} {:.1f}"/>'.format(x, gy, x + w, gy))
    g.append('<path d="M {:.1f} {:.1f} L {:.1f} {:.1f}"/>'.format(x + w * 0.5, y, x + w * 0.5, y + h))
    g.append("</g>")
    g.append('<g stroke="#4a4030" stroke-width="3" opacity="0.35" fill="none">')
    g.append('<path d="M {:.1f} {:.1f} L {:.1f} {:.1f}"/>'.format(x, y + h * 0.42, x + w, y + h * 0.42))
    g.append("</g>")
    return "".join(g)


def steam(w, y, height, seed, count=9, opacity=0.5):
    """湯気。細い帯を立ちのぼらせ、上ほど散らす。"""
    rnd = random.Random(seed)
    out = ['<g filter="url(#soft)" opacity="{:.2f}" fill="#ffffff">'.format(opacity)]
    for _ in range(count):
        cx = rnd.uniform(0.08, 0.92) * w
        top = y - height * rnd.uniform(0.55, 1.05)
        wdt = rnd.uniform(0.05, 0.13) * w
        d = ("M {:.1f} {:.1f} C {:.1f} {:.1f}, {:.1f} {:.1f}, {:.1f} {:.1f} "
             "C {:.1f} {:.1f}, {:.1f} {:.1f}, {:.1f} {:.1f} Z").format(
            cx - wdt / 2, y,
            cx - wdt * rnd.uniform(1.0, 1.8), (y + top) / 2, cx + wdt * 0.4, top + height * 0.18, cx, top,
            cx + wdt * rnd.uniform(1.0, 1.8), top + height * 0.3, cx + wdt * 1.1, (y + top) / 2,
            cx + wdt / 2, y)
        out.append('<path d="{}" opacity="{:.2f}"/>'.format(d, rnd.uniform(0.25, 0.7)))
    out.append("</g>")
    return "".join(out)


# ---------------------------------------------------------------- SVG 文書

def defs(sky=("#0b1420", "#2b3a4d", "#6b5566"), water_top="#1d3346", water_bottom="#0b1723",
         moon_color="#f6f0e2", extra=""):
    """全カット共通の定義。空・水面・ぼかし・和紙の地合い。"""
    return """<defs>
  <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{s0}"/><stop offset="52%" stop-color="{s1}"/>
    <stop offset="100%" stop-color="{s2}"/>
  </linearGradient>
  <linearGradient id="waterGrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{w0}"/><stop offset="100%" stop-color="{w1}"/>
  </linearGradient>
  <radialGradient id="moonGlow">
    <stop offset="0%" stop-color="{m}" stop-opacity="0.75"/>
    <stop offset="45%" stop-color="{m}" stop-opacity="0.18"/>
    <stop offset="100%" stop-color="{m}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="shojiPaper" cx="0.5" cy="0.55" r="0.75">
    <stop offset="0%" stop-color="#ffe9c0"/><stop offset="60%" stop-color="#f4d9a6"/>
    <stop offset="100%" stop-color="#dcbb85"/>
  </radialGradient>
  <radialGradient id="warmGlow">
    <stop offset="0%" stop-color="#ffd99a" stop-opacity="0.85"/>
    <stop offset="100%" stop-color="#ffd99a" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="vignette" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#000000" stop-opacity="0.30"/>
    <stop offset="40%" stop-color="#000000" stop-opacity="0"/>
    <stop offset="100%" stop-color="#000000" stop-opacity="0.38"/>
  </linearGradient>
  <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="18"/>
  </filter>
  <filter id="soft2" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="6"/>
  </filter>
  <filter id="washi" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" seed="11" result="n"/>
    <feColorMatrix in="n" type="saturate" values="0"/>
  </filter>
{extra}</defs>""".format(s0=sky[0], s1=sky[1], s2=sky[2], w0=water_top, w1=water_bottom,
                         m=moon_color, extra=extra)


def svg(w, h, body, defs_str, bg="url(#skyGrad)", grain=0.055, vignette=True):
    """レイヤを一枚の SVG に閉じる。最後に和紙の粒子と周辺減光を重ねる。"""
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {} {}" width="{}" height="{}" '
             'preserveAspectRatio="xMidYMid slice" role="img">'.format(w, h, w, h)]
    parts.append(defs_str)
    parts.append('<rect width="{}" height="{}" fill="{}"/>'.format(w, h, bg))
    parts.append(body)
    if vignette:
        parts.append('<rect width="{}" height="{}" fill="url(#vignette)"/>'.format(w, h))
    if grain:
        parts.append('<rect width="{}" height="{}" filter="url(#washi)" opacity="{:.3f}" '
                     'style="mix-blend-mode:overlay"/>'.format(w, h, grain))
    parts.append("</svg>")
    return "".join(parts)


def write(name, content):
    path = os.path.abspath(os.path.join(OUT_DIR, name))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print("  {:<26} {:>7,} bytes".format(name, len(content.encode("utf-8"))))


# ---------------------------------------------------------------- 風景のカット

def scene_hero():
    """表紙。宵の口、月の下に灯る宿。"""
    w, h = 1920, 1080
    hz = h * 0.58
    d = defs(sky=("#070e1a", "#22364f", "#7d6068"))
    b = []
    b.append(moon(1432, 226, 76, glow=0.62))
    b.append(mist(w, h * 0.30, 150, seed=3, color="#caa7b2", opacity=0.20, count=6))
    b.append(ridge(w, h, hz - 130, 260, seed=11, fill="#41506b", opacity=0.55, skew=0.12))
    b.append(mist(w, hz - 150, 110, seed=5, color="#e6dee6", opacity=0.34, count=5))
    b.append(ridge(w, h, hz - 40, 210, seed=23, fill="#2b3a52", opacity=0.85, skew=-0.08))
    b.append(mist(w, hz - 40, 96, seed=8, color="#dcd4e0", opacity=0.30, count=5))
    b.append(ridge(w, h, hz + 46, 150, seed=37, fill="#1b2634", opacity=1.0, skew=0.05))
    b.append(building(676, hz + 52, 560, seed=4))
    b.append(building(1188, hz + 92, 330, seed=9))
    b.append(water(w, hz + 268, h - (hz + 268), seed=17, ripples=20))
    for i, x in enumerate((250, 396, 1520, 1672)):
        b.append(lantern(x, hz + 262 + (i % 2) * 16, 1.6))
    b.append(pine(178, h - 44, 2.5, color="#0e161d", seed=2))
    b.append(pine(1836, h - 20, 3.1, color="#0e161d", seed=6))
    b.append(bamboo(96, h - 10, 2.2, color="#16242a", opacity=0.7, seed=1))
    return svg(w, h, "".join(b), d)


def scene_rotenburo():
    """露天風呂。岩に囲まれた湯が、月と稜線を映す。"""
    w, h = 1200, 900
    hz = h * 0.44
    d = defs(sky=("#060d18", "#1b2c42", "#3d4a55"), water_top="#2c4a55", water_bottom="#0f2028")
    b = [moon(946, 150, 44, glow=0.5)]
    b.append(ridge(w, h, hz - 60, 170, seed=31, fill="#33445c", opacity=0.6))
    b.append(mist(w, hz - 70, 80, seed=12, color="#dfe6ea", opacity=0.3, count=4))
    b.append(ridge(w, h, hz, 120, seed=44, fill="#1c2836", opacity=1.0))
    b.append(pine(120, hz + 24, 1.7, color="#101a20", seed=5))
    b.append(pine(1082, hz + 16, 1.4, color="#101a20", seed=8))
    b.append(stone_lantern(206, hz + 88, 1.5))
    # 湯船
    b.append('<path d="M 0 {y:.0f} Q {q1:.0f} {y2:.0f} {mx:.0f} {y3:.0f} Q {q2:.0f} {y2:.0f} {w} {y:.0f} '
             'L {w} {h} L 0 {h} Z" fill="#1b2730"/>'
             .format(y=hz + 58, y2=hz + 34, y3=hz + 70, q1=w * 0.24, mx=w * 0.5, q2=w * 0.76, w=w, h=h))
    b.append(water(w, hz + 104, h - (hz + 104), seed=21, ripples=22))
    # 月と灯りの映り込み
    grnd = random.Random(303)
    b.append('<g fill="#f4ecd8">')
    for i in range(16):
        gy = hz + 150 + (i / 15.0) ** 1.4 * (h - hz - 190)
        gw = grnd.uniform(10, 52) * (0.4 + i / 15.0)
        b.append('<ellipse cx="{:.0f}" cy="{:.0f}" rx="{:.0f}" ry="{:.1f}" opacity="{:.2f}"/>'
                 .format(946 + grnd.uniform(-46, 46), gy, gw, grnd.uniform(1.4, 3.2),
                         grnd.uniform(0.10, 0.34)))
    b.append('</g>')
    # 縁の岩
    rnd = random.Random(77)
    b.append('<g>')
    for i in range(15):
        rx = w * (i / 14.0) + rnd.uniform(-46, 46)
        ry = hz + 100 + rnd.uniform(-20, 16)
        rw, rh = rnd.uniform(44, 118), rnd.uniform(20, 44)
        b.append('<ellipse cx="{:.0f}" cy="{:.0f}" rx="{:.0f}" ry="{:.0f}" fill="#1e262b"/>'
                 .format(rx, ry, rw, rh))
        b.append('<path d="M {:.0f} {:.0f} q {:.0f} {:.0f} {:.0f} 0 Z" fill="#3a444b" opacity="{:.2f}"/>'
                 .format(rx - rw * 0.72, ry - rh * 0.18, rw * 0.72, -rh * 1.5, rw * 1.44,
                         rnd.uniform(0.30, 0.60)))
    b.append('</g>')
    b.append(steam(w, hz + 180, 210, seed=13, count=8, opacity=0.30))
    b.append('<g fill="#1a2024">'
             '<ellipse cx="150" cy="880" rx="210" ry="70"/>'
             '<ellipse cx="1070" cy="892" rx="230" ry="66"/></g>')
    return svg(w, h, "".join(b), d)


def scene_kashikiri():
    """貸切の檜風呂。湯気と障子越しの灯り。"""
    w, h = 1200, 900
    d = defs(sky=("#20160f", "#3a2718", "#241a12"), water_top="#4a6b63", water_bottom="#22403c")
    b = ['<rect width="{}" height="{}" fill="#2a1d14"/>'.format(w, h)]
    # 板壁
    b.append('<g stroke="#4a3423" stroke-width="2" opacity="0.6">')
    for i in range(14):
        b.append('<path d="M {x:.0f} 0 L {x:.0f} 520"/>'.format(x=i * (w / 13.0)))
    b.append("</g>")
    b.append(shoji(660, 96, 470, 330, cols=4, rows=5))
    b.append('<ellipse cx="895" cy="260" rx="420" ry="300" fill="url(#warmGlow)" opacity="0.5"/>')
    b.append(bamboo(126, 520, 1.9, color="#3f5a44", opacity=0.9, seed=4))
    b.append(bamboo(196, 520, 1.6, color="#334f3c", opacity=0.7, seed=9))
    # 檜の湯船
    b.append('<path d="M 60 520 L 1140 520 L 1088 872 L 112 872 Z" fill="#8a6a44"/>')
    b.append('<g clip-path="url(#tubClip)">')
    b.append('<path d="M 92 556 L 1108 556 L 1062 856 L 138 856 Z" fill="url(#waterGrad)"/>')
    b.append(water(w, 560, 292, seed=31, ripples=16, top="#5a7d73", bottom="#274a44"))
    b.append('</g>')
    b.append('<g stroke="#6f5334" stroke-width="3" opacity="0.55" fill="none">'
             '<path d="M 60 520 L 1140 520"/><path d="M 92 556 L 1108 556"/></g>')
    b.append(steam(w, 620, 260, seed=27, count=8, opacity=0.28))
    b.append('<g><rect x="150" y="486" width="120" height="34" rx="4" fill="#6d4f31"/>'
             '<rect x="168" y="452" width="26" height="36" rx="3" fill="#d9c9a8"/>'
             '<rect x="212" y="462" width="40" height="26" rx="3" fill="#cbb894"/></g>')
    d = d.replace("</defs>", '<clipPath id="tubClip">'
                  '<path d="M 92 556 L 1108 556 L 1062 856 L 138 856 Z"/></clipPath></defs>')
    return svg(w, h, "".join(b), d, bg="#2a1d14", grain=0.07)


def scene_room(name, seed, view_sky, view_ridge, accent, flower="#c4566a", layout=1):
    """客室。間取りを三通り持たせ、部屋ごとに構図を変える。

    layout 1: 中央に大きく開いた障子。両脇も障子の角部屋。
    layout 2: 床の間と掛軸を左に置いた離れ。眺めは右寄りの縦長。
    layout 3: 右手の障子壁と、左に低い窓を取った小間。
    """
    w, h = 1200, 900
    d = defs(sky=view_sky, water_top="#2a3f4a", water_bottom="#16252e")
    b = ['<rect width="{}" height="{}" fill="#221913"/>'.format(w, h)]

    # 天井（竿縁）
    b.append('<path d="M 0 0 L {w} 0 L {w} 118 L 0 118 Z" fill="#2b2018"/>'.format(w=w))
    b.append('<g stroke="#3d2e21" stroke-width="3" opacity="0.7">')
    for i in range(1, 7):
        b.append('<path d="M {x:.0f} 0 L {x:.0f} 118"/>'.format(x=i * w / 7.0))
    b.append('<path d="M 0 118 L {} 118"/></g>'.format(w))

    if layout == 1:
        vx, vy, vw, vh = 300, 150, 600, 420
    elif layout == 2:
        vx, vy, vw, vh = 560, 146, 470, 430
    else:
        vx, vy, vw, vh = 140, 214, 430, 320

    # 障子ごしの眺め
    b.append('<g clip-path="url(#viewClip)">')
    b.append('<rect x="{}" y="{}" width="{}" height="{}" fill="url(#skyGrad)"/>'.format(vx, vy, vw, vh))
    b.append(ridge(w, vy + vh, vy + vh - 150, 150, seed=seed, fill=view_ridge, opacity=0.6))
    b.append(ridge(w, vy + vh, vy + vh - 80, 110, seed=seed + 5, fill="#1f2c38", opacity=0.95))
    b.append(mist(w, vy + vh - 120, 70, seed=seed + 2, color="#ffffff", opacity=0.3, count=4))
    b.append(pine(vx + 62, vy + vh - 8, 1.05, color="#131c22", seed=seed))
    if layout == 2:
        # 離れは、眺めの手前に専用露天の湯気を覗かせる
        b.append(steam(vx + vw, vy + vh - 6, 120, seed=seed + 9, count=4, opacity=0.34))
    b.append("</g>")
    b.append('<rect x="{}" y="{}" width="{}" height="{}" fill="none" stroke="#6f5334" stroke-width="10"/>'
             .format(vx, vy, vw, vh))

    floor_y = 570 if layout != 3 else 546

    if layout == 1:
        b.append(shoji(70, 150, 228, 420, cols=3, rows=6))
        b.append(shoji(902, 150, 228, 420, cols=3, rows=6))
    elif layout == 2:
        # 床の間：地板・落し掛け・掛軸・香炉
        b.append('<rect x="86" y="146" width="360" height="424" fill="#1d1610"/>')
        b.append('<rect x="86" y="146" width="360" height="26" fill="#4a3423"/>')
        b.append('<rect x="86" y="524" width="360" height="46" fill="#5c4229"/>')
        b.append('<g><rect x="222" y="196" width="94" height="272" fill="#e8dcc2"/>'
                 '<rect x="222" y="196" width="94" height="272" fill="none" stroke="#8a6f4a" stroke-width="3"/>'
                 '<rect x="214" y="188" width="110" height="12" rx="3" fill="#4a3423"/>'
                 '<rect x="214" y="464" width="110" height="12" rx="3" fill="#4a3423"/>'
                 '<path d="M 254 238 q 14 34 0 68 q -14 34 0 66" stroke="#2b241d" stroke-width="4" '
                 'fill="none" stroke-linecap="round"/>'
                 '<path d="M 284 250 q -12 40 2 84" stroke="#2b241d" stroke-width="3.4" fill="none" '
                 'stroke-linecap="round"/>'
                 '<rect x="266" y="404" width="16" height="16" fill="#a1442f"/></g>')
        b.append('<g><ellipse cx="366" cy="516" rx="26" ry="10" fill="#3a4a4a"/>'
                 '<path d="M 344 516 q 22 -26 44 0 Z" fill="#4a5c5c"/></g>')
        b.append(shoji(1058, 146, 72, 430, cols=1, rows=6))
    else:
        b.append(shoji(640, 150, 490, 420, cols=5, rows=6))
        b.append('<rect x="0" y="150" width="120" height="420" fill="#241a13"/>')

    b.append(tatami(0, floor_y, w, h - floor_y, rows=3))

    # 座卓まわり
    if layout == 2:
        # 一枚板の長卓
        b.append('<g><rect x="576" y="712" width="500" height="86" rx="8" fill="#4a3626"/>'
                 '<rect x="576" y="694" width="500" height="86" rx="8" fill="#6b4d33"/>'
                 '<rect x="596" y="706" width="460" height="58" rx="6" fill="#7d5c3d" opacity="0.5"/></g>')
        tx, ty = 700, 726
    else:
        cx = 600 if layout == 1 else 760
        b.append('<g><ellipse cx="{}" cy="{}" rx="238" ry="70" fill="#4a3626"/>'
                 '<ellipse cx="{}" cy="{}" rx="238" ry="70" fill="#6b4d33"/>'
                 '<ellipse cx="{}" cy="{}" rx="216" ry="58" fill="#7d5c3d" opacity="0.55"/></g>'
                 .format(cx, 766, cx, 750, cx, 750))
        tx, ty = cx - 44, 736

    # 急須と湯呑
    b.append('<g><ellipse cx="{}" cy="{}" rx="34" ry="17" fill="#2f3a36"/>'
             '<path d="M {} {} q 34 -34 68 0 Z" fill="#3d4a45"/>'
             '<path d="M {} {} q 22 4 20 18" stroke="#2f3a36" stroke-width="4" fill="none"/>'
             '<circle cx="{}" cy="{}" r="5" fill="#2f3a36"/></g>'
             .format(tx, ty, tx - 34, ty, tx + 34, ty - 12, tx, ty - 28))
    for i, dx in enumerate((86, 130)):
        b.append('<g><ellipse cx="{}" cy="{}" rx="17" ry="9" fill="#e8e0d0"/>'
                 '<path d="M {} {} q 17 20 34 0 Z" fill="#f2ece0"/></g>'
                 .format(tx + dx, ty + 6 + i * 6, tx + dx - 17, ty + 6 + i * 6))

    # 一輪挿し
    vase_x = 1010 if layout != 2 else 156
    b.append('<g transform="translate({} 660)">'
             '<path d="M -14 78 q -10 -46 8 -58 q -12 -14 6 -20 q 18 6 6 20 q 18 12 8 58 Z" fill="#2c3a44"/>'
             '<path d="M 0 0 q -16 -34 -6 -56" stroke="#3f5a44" stroke-width="3" fill="none"/>'
             '<circle cx="-8" cy="-58" r="9" fill="{f}"/><circle cx="2" cy="-70" r="6.5" fill="{f}" '
             'opacity="0.85"/><circle cx="-16" cy="-44" r="5" fill="{f}" opacity="0.7"/></g>'
             .format(vase_x, f=flower))

    # 行灯
    ax = 160 if layout == 1 else (1040 if layout == 2 else 210)
    b.append('<g><ellipse cx="{}" cy="690" rx="180" ry="150" fill="url(#warmGlow)" opacity="0.45"/>'
             '<rect x="{}" y="612" width="84" height="104" rx="4" fill="url(#shojiPaper)"/>'
             '<rect x="{}" y="612" width="84" height="104" rx="4" fill="none" stroke="#5a4128" '
             'stroke-width="5"/><rect x="{}" y="716" width="108" height="12" rx="3" fill="#4a3423"/>'
             '<rect x="{}" y="600" width="108" height="12" rx="3" fill="#4a3423"/></g>'
             .format(ax, ax - 42, ax - 42, ax - 54, ax - 54))

    # 座布団
    if layout == 2:
        seats = (676, 976)
    elif layout == 1:
        seats = (352, 852)
    else:
        seats = (520, 1000)
    b.append('<g fill="{a}"><ellipse cx="{p}" cy="822" rx="86" ry="34"/>'
             '<ellipse cx="{q}" cy="822" rx="86" ry="34"/></g>'.format(a=accent, p=seats[0], q=seats[1]))
    b.append('<g fill="#000" opacity="0.15"><ellipse cx="{}" cy="836" rx="250" ry="30"/></g>'
             .format(600 if layout != 2 else 820))

    d = d.replace("</defs>", '<clipPath id="viewClip"><rect x="{}" y="{}" width="{}" height="{}"/>'
                             '</clipPath></defs>'.format(vx, vy, vw, vh))
    return svg(w, h, "".join(b), d, bg="#221913", grain=0.06)


def scene_kaiseki(seed=101, cloth="#1a1a1e", title="dinner"):
    """会席。黒塗りの折敷を真上から見た構図。"""
    w, h = 1200, 900
    d = defs()
    rnd = random.Random(seed)
    b = ['<rect width="{}" height="{}" fill="{}"/>'.format(w, h, cloth)]
    b.append('<ellipse cx="600" cy="430" rx="640" ry="470" fill="#2a2a30" opacity="0.55" '
             'filter="url(#soft)"/>')
    # 折敷
    b.append('<rect x="150" y="170" width="900" height="600" rx="14" fill="#14141a"/>')
    b.append('<rect x="164" y="184" width="872" height="572" rx="10" fill="#1e1e26"/>')
    b.append('<rect x="164" y="184" width="872" height="572" rx="10" fill="none" stroke="#9a7b45" '
             'stroke-width="2.5" opacity="0.7"/>')

    def dish(cx, cy, r, rim, inner, items):
        g = ['<g><ellipse cx="{}" cy="{}" rx="{:.0f}" ry="{:.0f}" fill="#000" opacity="0.35" '
             'filter="url(#soft2)"/>'.format(cx, cy + r * 0.10, r * 1.03, r * 0.80)]
        g.append('<ellipse cx="{}" cy="{}" rx="{}" ry="{:.0f}" fill="{}"/>'.format(cx, cy, r, r * 0.76, rim))
        g.append('<ellipse cx="{}" cy="{}" rx="{:.0f}" ry="{:.0f}" fill="{}"/>'
                 .format(cx, cy, r * 0.82, r * 0.60, inner))
        for (dx, dy, dr, col, op) in items:
            g.append('<ellipse cx="{:.0f}" cy="{:.0f}" rx="{:.0f}" ry="{:.0f}" fill="{}" opacity="{:.2f}"/>'
                     .format(cx + dx, cy + dy, dr, dr * 0.72, col, op))
        g.append('<ellipse cx="{}" cy="{}" rx="{}" ry="{:.0f}" fill="none" stroke="#ffffff" '
                 'stroke-width="1.2" opacity="0.16"/>'.format(cx, cy, r, r * 0.76))
        g.append("</g>")
        return "".join(g)

    def scatter(n, spread, palette, size):
        return [(rnd.uniform(-spread, spread), rnd.uniform(-spread * 0.62, spread * 0.62),
                 rnd.uniform(size * 0.6, size), rnd.choice(palette), rnd.uniform(0.8, 1.0))
                for _ in range(n)]

    if title == "dinner":
        # 造り
        b.append(dish(390, 320, 118, "#20343a", "#2c454c",
                      scatter(7, 62, ["#d9737a", "#e89aa0", "#f0e2d4", "#9fb6a6"], 26)))
        # 椀
        b.append(dish(760, 310, 92, "#3a1f18", "#5c2d20",
                      scatter(5, 42, ["#e5d7b8", "#c9a86a", "#7f9a72"], 20)))
        # 焼物
        b.append(dish(360, 590, 104, "#2b2b33", "#3a3a44",
                      scatter(4, 48, ["#b9743d", "#d99a58", "#6f8a63"], 28)))
        # 小鉢三種
        for i, cx in enumerate((640, 770, 900)):
            b.append(dish(cx, 585 + (i % 2) * 18, 56, "#2f2a33", "#40384a",
                          scatter(4, 24, ["#8fae7f", "#e0cf9c", "#c46a72"], 14)))
        # 飯椀・汁椀
        b.append(dish(940, 320, 74, "#3a1f18", "#f2ece0", []))
        b.append('<ellipse cx="940" cy="316" rx="46" ry="32" fill="#faf6ee"/>')
    else:
        b.append(dish(370, 320, 96, "#3a1f18", "#f4efe4", []))
        b.append('<ellipse cx="370" cy="316" rx="60" ry="40" fill="#fbf8f1"/>')
        b.append(dish(640, 306, 82, "#3a1f18", "#6d3524",
                      scatter(5, 34, ["#d9c48c", "#8fae7f", "#e8dcc2"], 16)))
        b.append(dish(900, 330, 92, "#26343a", "#33474e",
                      scatter(3, 40, ["#e6dcc8", "#b8814a", "#7f9a72"], 24)))
        for i, cx in enumerate((360, 520, 690, 870)):
            b.append(dish(cx, 590 + (i % 2) * 16, 54, "#2f2a33", "#3e3746",
                          scatter(3, 22, ["#9ab188", "#e2cf9e", "#c9705f"], 13)))
    # 箸と箸置き
    b.append('<g><rect x="330" y="716" width="360" height="7" rx="3.5" fill="#7a4a2c" '
             'transform="rotate(-1.2 510 720)"/>'
             '<rect x="330" y="730" width="360" height="7" rx="3.5" fill="#7a4a2c" '
             'transform="rotate(-1.2 510 734)"/>'
             '<ellipse cx="356" cy="726" rx="26" ry="13" fill="#2f4a44"/></g>')
    # 徳利と盃
    b.append('<g><path d="M 1000 660 q -26 -12 -22 -46 q 2 -22 12 -30 q -8 -14 10 -16 q 18 2 10 16 '
             'q 10 8 12 30 q 4 34 -22 46 Z" fill="#e6e0d2"/>'
             '<ellipse cx="1000" cy="662" rx="24" ry="9" fill="#cdc5b4"/>'
             '<ellipse cx="946" cy="690" rx="24" ry="12" fill="#f0ebdd"/>'
             '<ellipse cx="946" cy="688" rx="18" ry="8" fill="#d9c99c"/></g>')
    b.append('<rect width="{}" height="{}" fill="url(#vignette)" opacity="0.9"/>'.format(w, h))
    return svg(w, h, "".join(b), d, bg=cloth, grain=0.05, vignette=False)


SEASONS = {
    "spring": dict(sky=("#3d4f74", "#8e7f96", "#e6c3c6"), far="#6a7593", near="#3f4a58",
                   accent="#f2c9d4", shape="petal", count=40, label="春"),
    "summer": dict(sky=("#123252", "#2f6a86", "#a8cbc4"), far="#3f7a7a", near="#1f4a46",
                   accent="#ffffff", shape="snow", count=16, label="夏"),
    "autumn": dict(sky=("#3a2438", "#8a4f3c", "#e0a05e"), far="#7a4a3a", near="#3a2620",
                   accent="#d96a3c", shape="leaf", count=34, label="秋"),
    "winter": dict(sky=("#1b2740", "#48597a", "#cdd6e2"), far="#8592a8", near="#2c3648",
                   accent="#ffffff", shape="snow", count=60, label="冬"),
}


def scene_season(key):
    """四季のカット。同じ稜線の骨格に、季節の色と舞うものを載せる。"""
    cfg = SEASONS[key]
    w, h = 900, 700
    hz = h * 0.62
    seed = sum(ord(c) for c in key)
    d = defs(sky=cfg["sky"], water_top=cfg["near"], water_bottom="#101820")
    b = []
    if key in ("autumn", "winter"):
        b.append(moon(700, 130, 40, glow=0.45))
    b.append(mist(w, h * 0.34, 90, seed=seed, color="#ffffff", opacity=0.18, count=4))
    b.append(ridge(w, h, hz - 90, 170, seed=seed, fill=cfg["far"], opacity=0.55, skew=0.10))
    b.append(mist(w, hz - 100, 62, seed=seed + 1, color="#ffffff", opacity=0.30, count=4))
    b.append(ridge(w, h, hz - 10, 130, seed=seed + 3, fill=cfg["near"], opacity=0.95))
    if key == "winter":
        b.append('<path d="{}" fill="#e8eef5" opacity="0.85"/>'
                 .format(catmull_rom(ridge_points(w, hz - 10, 130, seed + 3, 16))
                         + " L {} {:.0f} L 0 {:.0f} Z".format(w, hz + 40, hz + 40)))
    b.append(water(w, hz + 40, h - (hz + 40), seed=seed + 7, ripples=12,
                   top=cfg["near"], bottom="#0d151d"))
    b.append(building(300, hz + 44, 210, seed=seed))
    b.append(pine(96, hz + 96, 1.5, color="#141c22", seed=seed))
    b.append(pine(824, hz + 74, 1.2, color="#141c22", seed=seed + 4))
    b.append(stone_lantern(662, hz + 92, 1.0))
    b.append(petals(w, h, seed + 11, color=cfg["accent"], count=cfg["count"],
                    size=7.0, opacity=0.7, shape=cfg["shape"]))
    return svg(w, h, "".join(b), d)


def scene_approach():
    """夕暮れの門前。石畳と杉並木、提灯の列。"""
    w, h = 1400, 700
    d = defs(sky=("#2a1c2e", "#7a4a48", "#e5a86c"), water_top="#3a3038", water_bottom="#1a1620")
    b = []
    b.append(mist(w, h * 0.30, 110, seed=61, color="#f0c9a8", opacity=0.26, count=5))
    b.append(ridge(w, h, h * 0.44, 200, seed=71, fill="#5a4152", opacity=0.5))
    b.append(ridge(w, h, h * 0.50, 150, seed=83, fill="#2e2434", opacity=0.9))
    # 石畳
    b.append('<path d="M 520 380 L 880 380 L 1180 700 L 220 700 Z" fill="#4a4048"/>')
    rnd = random.Random(91)
    b.append('<g stroke="#2e2830" stroke-width="2" fill="none" opacity="0.6">')
    for i in range(9):
        t = (i + 1) / 10.0
        y = 380 + t * 320
        half = 180 + t * 300
        b.append('<path d="M {:.0f} {:.0f} L {:.0f} {:.0f}"/>'.format(700 - half, y, 700 + half, y))
    b.append("</g>")
    # 杉並木
    for i in range(6):
        t = i / 5.0
        s = 0.9 + t * 2.2
        b.append(pine(int(470 - t * 430), int(400 + t * 300), s, color="#1b2028", seed=i))
        b.append(pine(int(930 + t * 430), int(400 + t * 300), s, color="#1b2028", seed=i + 20))
    # 提灯の列
    for i in range(5):
        t = i / 4.0
        s = 1.0 + t * 1.5
        b.append(lantern(int(520 - t * 320), int(392 + t * 250), s))
        b.append(lantern(int(880 + t * 320), int(392 + t * 250), s))
    b.append(building(700, 300, 330, seed=3))
    b.append(roof(700, 302, 330, color="#12161c"))
    b.append(steam(w, 700, 120, seed=44, count=5, opacity=0.22))
    return svg(w, h, "".join(b), d)


def crest():
    """家紋ふうの印。三日月と山を円に納める。currentColor で色を継ぐ。"""
    s = 200
    b = ['<mask id="cres"><rect width="200" height="200" fill="#fff"/>'
         '<circle cx="136" cy="60" r="20" fill="#000"/></mask>',
         '<circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" stroke-width="4"/>',
         '<circle cx="100" cy="100" r="80" fill="none" stroke="currentColor" stroke-width="1.5" '
         'opacity="0.45"/>',
         '<circle cx="126" cy="66" r="21" fill="currentColor" mask="url(#cres)"/>',
         '<path d="M 40 130 L 74 74 L 96 106 L 122 64 L 160 130 Z" fill="currentColor"/>',
         '<path d="M 38 144 q 31 -11 62 0 q 31 11 62 0" stroke="currentColor" stroke-width="4" '
         'fill="none" stroke-linecap="round"/>']
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s} {s}" width="{s}" height="{s}" '
            'fill="none">{b}</svg>'.format(s=s, b="".join(b)))

# ---------------------------------------------------------------- 出力

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("月待荘 イメージ素材を生成します")
    write("hero.svg", scene_hero())
    write("approach.svg", scene_approach())
    write("onsen-rotenburo.svg", scene_rotenburo())
    write("onsen-kashikiri.svg", scene_kashikiri())
    write("room-tsukimi.svg", scene_room(
        "tsukimi", 13, ("#0a1524", "#25405e", "#6d7f96"), "#44567a", "#5c3f52",
        flower="#c4566a", layout=1))
    write("room-hanare.svg", scene_room(
        "hanare", 29, ("#1c2436", "#4a5a6e", "#9aa89c"), "#5a6a76", "#3e5348",
        flower="#e0b45a", layout=2))
    write("room-kaze.svg", scene_room(
        "kaze", 47, ("#2a1e2c", "#7a4c4a", "#d9a06c"), "#7a5a58", "#4a3a3c",
        flower="#e08a5a", layout=3))
    write("cuisine-dinner.svg", scene_kaiseki(101, "#15151a", "dinner"))
    write("cuisine-breakfast.svg", scene_kaiseki(202, "#1d1a16", "breakfast"))
    for key in SEASONS:
        write("season-{}.svg".format(key), scene_season(key))
    write("crest.svg", crest())
    print("完了: {} に出力しました".format(os.path.normpath(OUT_DIR)))


if __name__ == "__main__":
    main()
