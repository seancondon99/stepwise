"""Figures for notes/information-retrieval/1-foundations/03-clickthrough.md"""
import os
from svgplot import *

OUT = os.path.join(os.path.dirname(__file__), "../../notes/information-retrieval/1-foundations/figures")

EXTRA = """
  .cell { fill: #ffffff; stroke: #9ca3af; stroke-width: 1.25; }
  .cell-click { fill: #2f6fdb; stroke: #2f6fdb; stroke-width: 1.25; }
  .cell-click-text { fill: #ffffff; font-weight: 600; }
  .hm { fill: #2f6fdb; }
  .hm-diag { fill: none; stroke: #1f2328; stroke-width: 1.5; }
  .hm-strong { fill: #ffffff; }
  .arc { fill: none; stroke-width: 1.75; }
  @media (prefers-color-scheme: dark) {
    .cell { fill: #1d2025; stroke: #6b7280; }
    .cell-click { fill: #7aa7ff; stroke: #7aa7ff; }
    .cell-click-text { fill: #16181c; }
    .hm { fill: #7aa7ff; }
    .hm-diag { stroke: #e6e6e3; }
    .hm-strong { fill: #16181c; }
  }
"""

# Table 2 of the paper: % of times the abstract at rank r (rows) was viewed before a click at rank c (cols)
TABLE2 = [
    [90.6, 76.2, 73.9, 60.0, 54.5, 45.5],
    [56.8, 90.5, 82.6, 53.3, 63.6, 54.5],
    [30.2, 47.6, 95.7, 80.0, 81.8, 45.5],
    [17.3, 19.0, 47.8, 93.3, 63.6, 45.5],
    [8.6, 14.3, 21.7, 53.3, 100.0, 72.7],
    [4.3, 4.8, 8.7, 33.3, 18.2, 81.8],
]


def fig_viewed_before_click():
    x0, y0, s = 150, 50, 62
    b = [text(x0 + 3 * s, 20, "rank of the clicked link", "muted", "middle")]
    cx, cy = 92, y0 + 3 * s
    b.append(text(cx, cy, "rank of the viewed abstract", "muted", "middle", f' transform="rotate(-90 {cx} {cy})"'))
    for c in range(6):
        b.append(text(x0 + c * s + s / 2, y0 - 10, str(c + 1), "muted small", "middle"))
    for r in range(6):
        b.append(text(x0 - 10, y0 + r * s + s / 2 + 4, str(r + 1), "muted small", "end"))
        for c in range(6):
            v = TABLE2[r][c]
            x, y = x0 + c * s, y0 + r * s
            b.append(f'<rect class="hm" x="{x + 1}" y="{y + 1}" width="{s - 2}" height="{s - 2}" rx="4" fill-opacity="{0.06 + 0.84 * v / 100:.2f}"/>')
            b.append(text(x + s / 2, y + s / 2 + 4, f"{v:.0f}%", "small" + (" hm-strong" if v > 55 else ""), "middle"))
        # outline the diagonal (the clicked abstract itself)
        b.append(f'<rect class="hm-diag" x="{x0 + r * s + 1}" y="{y0 + r * s + 1}" width="{s - 2}" height="{s - 2}" rx="4"/>')
    lx = x0 + 6 * s + 24
    b.append(text(lx, y0 + 20, "above the diagonal:", "small title"))
    b.append(text(lx, y0 + 38, "abstracts above a click", "small"))
    b.append(text(lx, y0 + 56, "are mostly read", "small"))
    b.append(text(lx, y0 + 96, "just below the diagonal:", "small title"))
    b.append(text(lx, y0 + 114, "the next abstract is read", "small"))
    b.append(text(lx, y0 + 132, "about half the time", "small"))
    b.append(text(lx, y0 + 172, "further below: rarely", "small title"))
    return svg(760, y0 + 6 * s + 12, "\n".join(b),
               "Heatmap of how often each abstract was viewed before a click at each rank: high above the diagonal, about half just below it, low further below", EXTRA)


# ---------------------------------------------------------------- the five strategies on l1* l2 l3* l4 l5* l6 l7
CLICKS = {1, 3, 5}
SUB = "₀₁₂₃₄₅₆₇₈₉"
# (name, plain-English rule, preferences as (winner, loser), idea lines, idea kind)
STRATEGIES = [
    ("1  Click > Skip Above", "click beats skipped links above it", [(3, 2), (5, 2), (5, 4)],
     ["skipping a higher link =", "overriding the ranking"], "k-int"),
    ("2  Last Click > Skip Above", "same, but only the last click", [(5, 2), (5, 4)],
     ["earlier clicks were", "less informed"], "k-int"),
    ("3  Click > Earlier Click", "later click beats earlier click", [(3, 1), (5, 1), (5, 3)],
     ["assumes later clicks", "are more relevant"], "k-ass"),
    ("4  Click > Skip Previous", "click beats the skipped link just above", [(3, 2), (5, 4)],
     ["the abstract right above", "a click is almost always read"], "k-int"),
    ("5  Click > No-Click Next", "click beats the unclicked link just below", [(1, 2), (3, 4), (5, 6)],
     ["always agrees with the", "existing ranking"], "k-prob"),
]

STRAT_STYLE = EXTRA + """
  .k-int { fill: #23845a; } .k-ass { fill: #c02a8c; } .k-prob { fill: #c8372d; }
  @media (prefers-color-scheme: dark) {
    .k-int { fill: #5cc495; } .k-ass { fill: #ec7cc6; } .k-prob { fill: #ff7f74; }
  }
"""

MARKER = ('<defs><marker id="pref" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
          '<path class="f2" d="M0,0 L10,5 L0,10 z"/></marker></defs>')


def ranking_row(x0, step, y, pairs, size=26):
    b = []
    for r in range(1, 8):
        x = x0 + (r - 1) * step
        cls = "cell-click" if r in CLICKS else "cell"
        b.append(f'<rect class="{cls}" x="{x - size / 2}" y="{y - size / 2}" width="{size}" height="{size}" rx="5"/>')
        b.append(text(x, y + 4.5, f"l{SUB[r]}", "small cell-click-text" if r in CLICKS else "small muted", "middle"))
    for win, lose in pairs:
        xa, xb = x0 + (win - 1) * step, x0 + (lose - 1) * step
        h = 7 + 6 * abs(win - lose)
        xa2 = xa + (-4 if xb < xa else 4)
        xb2 = xb + (4 if xb < xa else -4)
        b.append(f'<path class="arc s2" d="M{xa2},{y - size / 2 - 1} Q{(xa + xb) / 2},{y - size / 2 - 2 * h} {xb2},{y - size / 2 - 1}" marker-end="url(#pref)"/>')
    return b


def fig_strategies():
    x0, step, rowh, top = 300, 40, 80, 80
    ix = x0 + 6 * step + 34
    b = [MARKER]
    b.append(text(x0 + 3 * step, 18, "clicks on l₁, l₃, l₅  (in that order)", "muted small", "middle"))
    b.append(text(ix, 18, "why", "muted small"))
    for k, (name, rule, pairs, idea, kind) in enumerate(STRATEGIES):
        y = top + k * rowh
        b.append(text(10, y - 4, name, "small title"))
        b.append(text(10, y + 13, rule, "small muted"))
        b += ranking_row(x0, step, y, pairs)
        b.append(text(ix, y - 4, idea[0], f"small {kind}"))
        b.append(text(ix, y + 13, idea[1], f"small {kind}"))
    return svg(760, top + 4 * rowh + 30, "\n".join(b),
               "Preferences each of the five strategies extracts from clicks on l1, l3 and l5: arcs go from the preferred doc to the doc it beats", STRAT_STYLE)


def fig_main():
    x0, step = 60, 44
    b = [MARKER] + ranking_row(x0, step, 64, STRATEGIES[0][2])
    tx = x0 + 6 * step + 40
    b.append(text(tx, 52, "a click beats every link the user", "title"))
    b.append(text(tx, 72, "skipped over above it", "title"))
    b.append(text(tx, 96, "l₃ > l₂,  l₅ > l₂,  l₅ > l₄", "muted small"))
    return svg(600, 104, "\n".join(b), "Click beats skip above: clicks on l1, l3, l5 give l3 over l2, l5 over l2, l5 over l4", STRAT_STYLE)


if __name__ == "__main__":
    write_all(OUT, [
        ("click-viewed-before.svg", fig_viewed_before_click),
        ("click-strategies.svg", fig_strategies),
        ("click-main.svg", fig_main),
    ])
