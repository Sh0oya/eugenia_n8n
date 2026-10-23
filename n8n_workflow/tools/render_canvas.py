"""Draws the canvas of the workflow as an SVG (docs/img/canvas-plan.svg), from exports/can-my-pc-run-it.json.

    python tools/render_canvas.py

Same positions, sticky notes and connections as in n8n, so the README always shows the current workflow
(a screenshot of the canvas goes out of date as soon as a node moves).
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "exports" / "can-my-pc-run-it.json"
TARGET = ROOT / "docs" / "img" / "canvas-plan.svg"

STICKY = {1: "#fdf0a6", 3: "#f7c5c5", 4: "#c9ecc9", 5: "#c8defa", 6: "#e1d3f7", 7: "#e7e8ee"}
W, H = 200, 56   # node box


def kind(node):
    t = node["type"]
    if "Trigger" in t:
        return "#16a34a"
    if t.endswith(".code"):
        return "#d97706"
    if "langchain" in t:
        return "#7c3aed"
    return "#9ca3af"


def label(name):
    tool, _, action = name.partition(" - ")
    return (tool, action) if action else (name, "")


def main():
    wf = json.loads(SOURCE.read_text(encoding="utf-8"))
    stickies = [n for n in wf["nodes"] if n["type"].endswith("stickyNote")]
    nodes = {n["name"]: n for n in wf["nodes"] if not n["type"].endswith("stickyNote")}
    xs = [s["position"][0] for s in stickies] + [n["position"][0] for n in nodes.values()]
    ys = [s["position"][1] for s in stickies] + [n["position"][1] for n in nodes.values()]
    x0, y0 = min(xs) - 40, min(ys) - 40
    x1 = max([s["position"][0] + s["parameters"]["width"] for s in stickies] + [n["position"][0] + W for n in nodes.values()]) + 40
    y1 = max([s["position"][1] + s["parameters"]["height"] for s in stickies] + [n["position"][1] + H for n in nodes.values()]) + 40
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" font-family="Segoe UI, Roboto, Arial, sans-serif">',
           '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto"><path d="M0 0L10 5L0 10z" fill="#6b7280"/></marker></defs>',
           f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#ffffff"/>']
    for s in sorted(stickies, key=lambda s: -s["parameters"]["width"] * s["parameters"]["height"]):
        p, (x, y) = s["parameters"], s["position"]
        title = p["content"].strip().splitlines()[0].lstrip("# ").strip()
        out.append(f'<rect x="{x}" y="{y}" width="{p["width"]}" height="{p["height"]}" rx="14" fill="{STICKY.get(p.get("color"), "#e7e8ee")}" opacity="0.8"/>')
        out.append(f'<text x="{x + 24}" y="{y + 44}" font-size="34" font-weight="700" fill="#374151">{escape(title)}</text>')
    for source, kinds in wf["connections"].items():
        for kind_name, outputs in kinds.items():
            for targets in outputs:
                for t in targets or []:
                    a, b = nodes.get(source), nodes.get(t["node"])
                    if not a or not b:
                        continue
                    (ax, ay), (bx, by) = a["position"], b["position"]
                    if kind_name.startswith("ai_"):   # sub-nodes (models, parser) sit under their chain
                        sx, sy, ex, ey = ax + W / 2, ay, bx + W / 2, by + H
                    else:
                        sx, sy, ex, ey = ax + W, ay + H / 2, bx, by + H / 2
                    mid = (sx + ex) / 2
                    d = f"M{sx} {sy} C{mid} {sy} {mid} {ey} {ex} {ey}" if not kind_name.startswith("ai_") else f"M{sx} {sy} L{ex} {ey}"
                    out.append(f'<path d="{d}" fill="none" stroke="#6b7280" stroke-width="2" marker-end="url(#a)"/>')
    for n in nodes.values():
        x, y = n["position"]
        tool, action = label(n["name"])
        out.append(f'<rect x="{x}" y="{y}" width="{W}" height="{H}" rx="10" fill="#ffffff" stroke="{kind(n)}" stroke-width="3"/>')
        out.append(f'<text x="{x + W / 2}" y="{y + 23}" font-size="14" font-weight="700" text-anchor="middle" fill="#111827">{escape(tool)}</text>')
        if action:
            out.append(f'<text x="{x + W / 2}" y="{y + 42}" font-size="13" text-anchor="middle" fill="#4b5563">{escape(action)}</text>')
    out.append("</svg>")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text("\n".join(out), encoding="utf-8")
    print(f"{TARGET}: {len(nodes)} nodes, {len(stickies)} sticky notes")


if __name__ == "__main__":
    main()
