# -*- coding: utf-8 -*-
"""유형별 OG 이미지(1200x630) 생성 → web/public/og/{id}.png + default.png
실행: eda venv의 python으로 (PIL 필요: pip install pillow)
"""
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
OUT = os.path.join(os.path.dirname(__file__), "..", "public", "og")
os.makedirs(OUT, exist_ok=True)
W, H = 1200, 630

# 이름·비율·태그라인의 단일 소스: 앱과 동일한 quiz_model.json / taglines.json
with open(os.path.join(SRC, "quiz_model.json"), encoding="utf-8") as f:
    _model = json.load(f)
with open(os.path.join(SRC, "data", "taglines.json"), encoding="utf-8") as f:
    _taglines = json.load(f)

STYLE = {  # 시각 요소만 이 파일 소관
    0: {"emoji": "📱", "c1": (12, 20, 34), "c2": (8, 51, 68), "accent": (34, 211, 238)},
    1: {"emoji": "📺", "c1": (23, 20, 54), "c2": (30, 58, 138), "accent": (96, 165, 250)},
    2: {"emoji": "🔀", "c1": (10, 34, 30), "c2": (6, 78, 59), "accent": (52, 211, 153)},
    3: {"emoji": "🗣️", "c1": (42, 10, 48), "c2": (88, 28, 135), "accent": (232, 121, 249)},
    4: {"emoji": "🍽️", "c1": (46, 16, 10), "c2": (127, 29, 29), "accent": (251, 146, 60)},
    5: {"emoji": "🌿", "c1": (18, 20, 16), "c2": (6, 46, 30), "accent": (163, 230, 53)},
}
TYPES = {
    int(k): {
        "name": c["name"],
        # 웹(Math.round)과 동일한 반올림 — Python round()는 짝수 반올림이라 28.25→28.2가 됨
        "pct": f"{math.floor(c['pct'] * 10 + 0.5) / 10:.1f}",
        "tag": _taglines[k],
        **STYLE[int(k)],
    }
    for k, c in _model["classes"].items()
}

BOLD = "/System/Library/Fonts/Supplemental/AppleSDGothicNeo.ttc"
EMOJI = "/System/Library/Fonts/Apple Color Emoji.ttc"

def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)

def gradient(c1, c2):
    img = Image.new("RGB", (W, H))
    for y in range(H):
        t = y / H
        img.paste(tuple(int(a + (b - a) * t) for a, b in zip(c1, c2)), (0, y, W, y + 1))
    return img

def draw_emoji(img, ch, cx, cy, target=200):
    # Apple Color Emoji는 비트맵이라 160pt로 그린 뒤 리사이즈
    tmp = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    try:
        f = font(EMOJI, 160)
        d.text((110, 110), ch, font=f, anchor="mm", embedded_color=True)
    except Exception:
        f = font(BOLD, 160, 1)
        d.text((110, 110), ch, font=f, anchor="mm", fill=(255, 255, 255))
    tmp = tmp.resize((target, target), Image.LANCZOS)
    img.paste(tmp, (int(cx - target / 2), int(cy - target / 2)), tmp)

def card(tid, t):
    img = gradient(t["c1"], t["c2"]).convert("RGBA")
    d = ImageDraw.Draw(img)
    # 은은한 빛
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W - 500, -220, W + 220, 320], fill=t["accent"] + (46,))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img)

    d.text((90, 92), "나의 뉴스 DNA", font=font(BOLD, 34, 2), fill=(255, 255, 255, 150))
    draw_emoji(img, t["emoji"], 165, 265, 170)
    d.text((285, 265), t["name"], font=font(BOLD, 88, 1), fill=(255, 255, 255), anchor="lm")
    # 국민 % 배지 (반투명 배경은 별도 레이어로 합성해야 알파가 먹음)
    badge = f"대한민국 국민의 {t['pct']}%"
    bf = font(BOLD, 40, 1)
    bw = d.textlength(badge, font=bf)
    bx, by = 92, 380
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle([bx, by, bx + bw + 56, by + 74], radius=37, fill=(0, 0, 0, 90), outline=t["accent"] + (255,), width=3)
    img = Image.alpha_composite(img, layer)
    d = ImageDraw.Draw(img)
    d.text((bx + 28 + bw / 2, by + 37), badge, font=bf, fill=t["accent"], anchor="mm")
    d.text((92, 512), f"“{t['tag']}”", font=font(BOLD, 36, 2), fill=(255, 255, 255, 210))
    d.text((92, 572), "뉴스 DNA 테스트 · 국가 통계 6,000명 데이터 기반", font=font(BOLD, 24, 2), fill=(255, 255, 255, 120))
    img.convert("RGB").save(os.path.join(OUT, f"{tid}.png"), optimize=True)

def default_card():
    img = gradient((18, 14, 40), (76, 29, 149)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.text((W / 2, 150), "나의 뉴스 DNA는?", font=font(BOLD, 92, 1), fill=(255, 255, 255), anchor="mm")
    d.text((W / 2, 250), "국가 통계 6,000명 데이터로 만든 1분 테스트", font=font(BOLD, 36, 2), fill=(255, 255, 255, 190), anchor="mm")
    xs = W / 2 - 375
    for i, tid in enumerate([1, 2, 5, 0, 4, 3]):
        draw_emoji(img, TYPES[tid]["emoji"], xs + i * 150, 400, 110)
    d.text((W / 2, 545), "빠르면 2문항, 길어도 1분 · 6가지 유형", font=font(BOLD, 30, 2), fill=(255, 255, 255, 150), anchor="mm")
    img.convert("RGB").save(os.path.join(OUT, "default.png"), optimize=True)

for tid, t in TYPES.items():
    card(tid, t)
default_card()
print("saved:", sorted(os.listdir(OUT)))
