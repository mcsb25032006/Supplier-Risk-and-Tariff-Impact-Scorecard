"""
Scorecard Hero Preview SVG Generator
====================================
Generates diagrams/scorecard_preview.svg displaying executive supplier risk scorecards.
"""

from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
diagrams_dir = project_root / "diagrams"
diagrams_dir.mkdir(parents=True, exist_ok=True)

suppliers = [
    {
        "name": "TitanForge Components",
        "country": "United States \u2022 Domestic",
        "on_time": "84.2%",
        "lead_time": "12.5 days (\u00b15.8)",
        "tariff": "0.0%",
        "risk": "11.9",
        "rag": "Green",
        "color": "#2E7D32",
        "bg": "#EAF6EC",
    },
    {
        "name": "Bajio Precision Systems",
        "country": "Mexico \u2022 Nearshore (USMCA)",
        "on_time": "86.8%",
        "lead_time": "18.1 days (\u00b16.5)",
        "tariff": "0.0%",
        "risk": "11.7",
        "rag": "Green",
        "color": "#2E7D32",
        "bg": "#EAF6EC",
    },
    {
        "name": "Zhongxin Compute Mfg.",
        "country": "China \u2022 Offshore",
        "on_time": "73.0%",
        "lead_time": "39.0 days (\u00b115.4)",
        "tariff": "35.0%",
        "risk": "33.5",
        "rag": "Red",
        "color": "#C62828",
        "bg": "#FDECEA",
    },
]

CARD_W, CARD_H = 360, 300
GAP = 36
LEFT = 40
TOP = 110
N = len(suppliers)
TOTAL_W = LEFT * 2 + N * CARD_W + (N - 1) * GAP
TOTAL_H = TOP + CARD_H + 70


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_hero_preview():
    p = []
    p.append(f'<svg viewBox="0 0 {TOTAL_W} {TOTAL_H}" xmlns="http://www.w3.org/2000/svg" font-family="Arial, Helvetica, sans-serif">')
    p.append(f'<rect x="0" y="0" width="{TOTAL_W}" height="{TOTAL_H}" fill="#0F1F3D"/>')
    p.append(f'<text x="{TOTAL_W/2}" y="46" font-size="26" font-weight="800" fill="#FFFFFF" text-anchor="middle">Supplier Risk &amp; Tariff-Impact Scorecard</text>')
    p.append(f'<text x="{TOTAL_W/2}" y="72" font-size="14" fill="#AEB9D4" text-anchor="middle">3 suppliers &#8226; 340 purchase orders &#8226; July 2026 tariff conditions</text>')
    p.append(f'<line x1="{LEFT}" y1="88" x2="{TOTAL_W-LEFT}" y2="88" stroke="#2A3A5C" stroke-width="1"/>')

    for i, s in enumerate(suppliers):
        x = LEFT + i * (CARD_W + GAP)
        y = TOP

        p.append(f'<rect x="{x}" y="{y}" width="{CARD_W}" height="{CARD_H}" rx="14" fill="#FFFFFF"/>')
        p.append(f'<rect x="{x}" y="{y}" width="{CARD_W}" height="8" rx="4" fill="{s["color"]}"/>')
        p.append(f'<rect x="{x}" y="{y+4}" width="{CARD_W}" height="4" fill="{s["color"]}"/>')
        p.append(f'<text x="{x+28}" y="{y+40}" font-size="17" font-weight="700" fill="#0F1F3D" text-anchor="start">{esc(s["name"])}</text>')
        p.append(f'<text x="{x+28}" y="{y+60}" font-size="12.5" fill="#6B7280" text-anchor="start">{esc(s["country"])}</text>')

        badge_w = 74
        bx = x + 28
        by = y + 76
        p.append(f'<rect x="{bx}" y="{by}" width="{badge_w}" height="26" rx="13" fill="{s["bg"]}" stroke="{s["color"]}" stroke-width="1.5"/>')
        p.append(f'<text x="{bx+badge_w/2}" y="{by+17.5}" font-size="12" font-weight="700" fill="{s["color"]}" text-anchor="middle">{esc(s["rag"])}</text>')
        p.append(f'<line x1="{x+28}" y1="{y+120}" x2="{x+CARD_W-28}" y2="{y+120}" stroke="#EEF0F4" stroke-width="1"/>')

        p.append(f'<text x="{x+28}" y="{y+170}" font-size="46" font-weight="800" fill="{s["color"]}" text-anchor="start">{esc(s["risk"])}</text>')
        p.append(f'<text x="{x+28}" y="{y+190}" font-size="11.5" fill="#6B7280" text-anchor="start">COMPOSITE RISK SCORE (0=best, 100=worst)</text>')

        metrics = [
            ("On-Time Delivery", s["on_time"]),
            ("Avg. Lead Time", s["lead_time"]),
            ("Tariff Exposure", s["tariff"]),
        ]
        my = y + 224
        for label, value in metrics:
            p.append(f'<text x="{x+28}" y="{my}" font-size="12.5" fill="#374151" text-anchor="start">{esc(label)}</text>')
            p.append(f'<text x="{x+CARD_W-28}" y="{my}" font-size="13" font-weight="700" fill="#0F1F3D" text-anchor="end">{esc(value)}</text>')
            my += 26

    foot_y = TOP + CARD_H + 44
    p.append(f'<text x="{LEFT}" y="{foot_y}" font-size="11.5" fill="#7C89A8" text-anchor="start">Built with SQL &#8226; Excel (live tariff-scenario toggle) &#8226; Power BI &#8226; Python automation &#8226; simulated dataset, real July 2026 tariff rates</text>')
    p.append('</svg>')

    out_file = diagrams_dir / "scorecard_preview.svg"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(p))
    print(f"Hero preview SVG written to: {out_file}")


if __name__ == "__main__":
    build_hero_preview()
