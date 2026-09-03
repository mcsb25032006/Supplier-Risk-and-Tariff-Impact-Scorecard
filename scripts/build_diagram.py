"""
PO Lifecycle Coupa Process Flow SVG Generator
=============================================
Generates diagrams/po_lifecycle_coupa.svg illustrating the 7-stage P2P workflow
and data fields captured at each stage.
"""

from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
diagrams_dir = project_root / "diagrams"
diagrams_dir.mkdir(parents=True, exist_ok=True)

stages = [
    ("1", "Purchase\nRequisition", ["Requestor", "Category", "Est. Cost"]),
    ("2", "PO Creation", ["PO ID", "Supplier", "Incoterm"]),
    ("3", "Supplier\nAcknowledgment", ["Promised Date", "HS Code"]),
    ("4", "Shipment", ["Freight Mode", "Customs Clearance"]),
    ("5", "Receipt", ["Actual Date", "Defect Flag"]),
    ("6", "Invoice", ["Unit Cost", "Duties / Tariff"]),
    ("7", "Payment", ["Payment Terms", "PO Closed"]),
]

BOX_W, BOX_H = 180, 130
GAP_X = 46
TOP = 90
LEFT = 40
N = len(stages)
TOTAL_W = LEFT * 2 + N * BOX_W + (N - 1) * GAP_X
TOTAL_H = TOP + BOX_H + 90


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_diagram():
    svg_parts = []
    svg_parts.append(f'<svg viewBox="0 0 {TOTAL_W} {TOTAL_H}" xmlns="http://www.w3.org/2000/svg" font-family="Arial, Helvetica, sans-serif">')
    svg_parts.append(f'<rect x="0" y="0" width="{TOTAL_W}" height="{TOTAL_H}" fill="#FAFAFA"/>')
    svg_parts.append(f'<text x="{TOTAL_W/2}" y="36" font-size="22" font-weight="700" fill="#1F3864" text-anchor="middle">Coupa Purchase-to-Pay (P2P) Lifecycle</text>')
    svg_parts.append(f'<text x="{TOTAL_W/2}" y="58" font-size="13" fill="#595959" text-anchor="middle">Simulated procurement flow for Supplier Risk &amp; Tariff-Impact Scorecard - data fields tracked at each stage</text>')

    arrow_y = TOP + BOX_H / 2

    for i, (num, title, fields) in enumerate(stages):
        x = LEFT + i * (BOX_W + GAP_X)
        y = TOP

        if i < N - 1:
            ax1 = x + BOX_W
            ax2 = x + BOX_W + GAP_X
            svg_parts.append(f'<line x1="{ax1}" y1="{arrow_y}" x2="{ax2 - 10}" y2="{arrow_y}" stroke="#8C8C8C" stroke-width="2.5"/>')
            svg_parts.append(f'<polygon points="{ax2-10},{arrow_y-6} {ax2},{arrow_y} {ax2-10},{arrow_y+6}" fill="#8C8C8C"/>')

        fill = "#1F3864" if i == 0 or i == N - 1 else "#2E5395"
        svg_parts.append(f'<rect x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="10" fill="#FFFFFF" stroke="{fill}" stroke-width="2"/>')
        svg_parts.append(f'<rect x="{x}" y="{y}" width="{BOX_W}" height="34" rx="10" fill="{fill}"/>')
        svg_parts.append(f'<rect x="{x}" y="{y+17}" width="{BOX_W}" height="17" fill="{fill}"/>')

        svg_parts.append(f'<circle cx="{x+20}" cy="{y+17}" r="12" fill="#FFFFFF"/>')
        svg_parts.append(f'<text x="{x+20}" y="{y+22}" font-size="13" font-weight="700" fill="{fill}" text-anchor="middle">{num}</text>')

        title_lines = title.split("\n")
        ty = y + 22 if len(title_lines) == 1 else y + 15
        for tl in title_lines:
            svg_parts.append(f'<text x="{x+42}" y="{ty}" font-size="13" font-weight="700" fill="#FFFFFF" text-anchor="start">{esc(tl)}</text>')
            ty += 14

        fy = y + 34 + 26
        svg_parts.append(f'<text x="{x+16}" y="{y+34+18}" font-size="10" font-weight="700" fill="#8C8C8C" text-anchor="start">DATA CAPTURED</text>')
        for field in fields:
            svg_parts.append(f'<text x="{x+16}" y="{fy}" font-size="11.5" fill="#404040" text-anchor="start">\u2022 {esc(field)}</text>')
            fy += 20

    foot_y = TOP + BOX_H + 40
    svg_parts.append(f'<text x="{LEFT}" y="{foot_y}" font-size="11" fill="#8C8C8C" text-anchor="start">Documented P2P process flow illustrating procurement data lifecycle tracking.</text>')
    svg_parts.append(f'<text x="{LEFT}" y="{foot_y+18}" font-size="11" fill="#8C8C8C" text-anchor="start">Fields map directly to columns in Raw_POs, SQL database tables, and Power BI data models.</text>')
    svg_parts.append('</svg>')

    out_file = diagrams_dir / "po_lifecycle_coupa.svg"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
    print(f"P2P Lifecycle SVG written to: {out_file}")


if __name__ == "__main__":
    build_diagram()
