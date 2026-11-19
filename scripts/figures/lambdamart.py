"""Figures for notes/information-retrieval/1-foundations/02-lambdamart.md"""
import math, os
from svgplot import *

OUT = os.path.join(os.path.dirname(__file__), "../../notes/information-retrieval/1-foundations/figures")

EXTRA = """
  .cell { fill: #ffffff; stroke: #9ca3af; stroke-width: 1.25; }
  .cell-rel { fill: #2f6fdb; stroke: #2f6fdb; stroke-width: 1.25; }
  .cell-rel-text { fill: #ffffff; font-weight: 600; }
  .move { stroke: #6b7280; stroke-width: 1.5; fill: none; stroke-dasharray: 5 4; }
  @media (prefers-color-scheme: dark) {
    .cell { fill: #1d2025; stroke: #6b7280; }
    .cell-rel { fill: #7aa7ff; stroke: #7aa7ff; }
    .cell-rel-text { fill: #16181c; }
    .move { stroke: #9aa0a8; }
  }
"""


def ndcg(labels):
    dcg = lambda ls: sum((2 ** l - 1) / math.log2(r + 2) for r, l in enumerate(ls))
    return dcg(labels) / dcg(sorted(labels, reverse=True))


def errors(labels):
    return sum(1 for i in range(len(labels)) for j in range(i + 1, len(labels)) if labels[j] > labels[i])


def push(labels, scores, sigma=1.0, metric=True):
    """-dC/ds_i for every doc: positive = push up (RankNet if metric=False, LambdaRank otherwise)."""
    n, out = len(labels), [0.0] * len(labels)
    base = ndcg(labels)
    for i in range(n):
        for j in range(n):
            if labels[i] > labels[j]:
                rho = 1 / (1 + math.exp(sigma * (scores[i] - scores[j])))
                w = 1.0
                if metric:
                    sw = labels[:]
                    sw[i], sw[j] = sw[j], sw[i]
                    w = abs(ndcg(sw) - base)
                out[i] += sigma * rho * w
                out[j] -= sigma * rho * w
    return out


def cells(x0, step, y, labels, size=28):
    b = []
    for r, l in enumerate(labels):
        x = x0 + r * step
        b.append(f'<rect class="{"cell-rel" if l else "cell"}" x="{x - size / 2:.1f}" y="{y - size / 2:.1f}" width="{size}" height="{size}" rx="5"/>')
        b.append(text(x, y + 4.5, str(r + 1), "small cell-rel-text" if l else "small muted", "middle"))
    return b


# ---------------------------------------------------------------- Fig 1: IR metrics are flat in the scores
def fig_flat_metric():
    # three fixed docs (label, score) + one moving doc with label 2 and score s
    fixed = [(0, 2.0), (1, 1.0), (0, 0.0)]
    mover = 2

    def state(s):
        docs = fixed + [(mover, s)]
        ranked = [l for l, _ in sorted(docs, key=lambda d: -d[1])]
        cost = 0.0
        for li, si in docs:
            for lj, sj in docs:
                if li > lj:
                    cost += math.log(1 + math.exp(-(si - sj)))
        return ndcg(ranked), cost

    xs = arange(-1.5, 3.5, 1000)
    T = Plot(90, 34, 560, 120, (-1.5, 3.5), (0.5, 1.0))
    B = Plot(90, 214, 560, 120, (-1.5, 3.5), (0, 8))
    b = [text(T.x0, 18, "NDCG: piecewise constant in s", "title")]
    b.append(T.axes([], [0.5, 0.75, 1.0], "", "NDCG", yfmt=lambda t: f"{t:g}"))
    b.append(text(B.x0, B.y0 - 16, "RankNet cost: smooth in s", "title"))
    b.append(B.axes([-1, 0, 1, 2, 3], [0, 4, 8], "score s of the most relevant doc", "cost", xfmt=lambda t: f"{t:g}"))
    for P in (T, B):
        for _, s in fixed:
            b.append(f'<line class="ref" x1="{P.X(s):.1f}" x2="{P.X(s):.1f}" y1="{P.y0}" y2="{P.y0 + P.h}"/>')
    # step function: draw each flat piece separately so jumps aren't drawn as slopes
    pieces, cur = [], []
    for x in xs:
        v = state(x)[0]
        if cur and abs(cur[-1][1] - v) > 1e-9:
            pieces.append(cur)
            cur = []
        cur.append((x, v))
    pieces.append(cur)
    for p in pieces:
        b.append(T.line(p, "s2"))
    b.append(B.line([(x, state(x)[1]) for x in xs], "s1"))
    b.append(text(T.X(-1.4), T.Y(0.97), "gradient = 0 almost everywhere", "muted small"))
    b.append(text(B.X(3.4), B.Y(6.6), "gradient everywhere", "muted small", "end"))
    return svg(700, 390, "\n".join(b), "As one document's score increases, NDCG jumps only when it passes another document; the RankNet cost decreases smoothly", EXTRA)


# ---------------------------------------------------------------- Fig 2: fewer pairwise errors, worse NDCG
def fig_misaligned():
    A = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
    B = [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0]
    x0, step, yA, yB = 100, 40, 40, 150
    b = []
    for y, lab, name in [(yA, A, "A"), (yB, B, "B")]:
        b.append(text(40, y + 5, name, "title", "middle"))
        b += cells(x0, step, y, lab)
        b.append(text(x0 + 12 * step + 6, y - 2, f"pairwise errors = {errors(lab)}", "small"))
        b.append(text(x0 + 12 * step + 6, y + 16, f"NDCG = {ndcg(lab):.2f}", "small"))
    b.append('<defs><marker id="mv" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
             '<path class="ahead" d="M0,0 L10,5 L0,10 z"/></marker></defs>')
    for ra, rb, lab in [(2, 5, "down 3"), (11, 6, "up 5")]:
        xa, xb = x0 + (ra - 1) * step, x0 + (rb - 1) * step
        b.append(f'<line class="move" x1="{xa:.1f}" y1="{yA + 18}" x2="{xb:.1f}" y2="{yB - 20}" marker-end="url(#mv)"/>')
        # label offset perpendicular to the line, on its upper side
        dx, dy = xb - xa, (yB - 20) - (yA + 18)
        n = math.hypot(dx, dy)
        nx, ny = (dy / n, -dx / n) if dx > 0 else (-dy / n, dx / n)
        mx, my = (xa + xb) / 2 + 16 * nx, (yA + 18 + yB - 20) / 2 + 16 * ny
        b.append(text(mx, my + 4, lab, "muted small", "start" if nx > 0 else "end"))
    return svg(760, 180, "\n".join(b), "Moving the top relevant doc down 3 and the bottom one up 5 removes two pairwise errors but lowers NDCG", EXTRA)


# ---------------------------------------------------------------- Fig 3: RankNet vs LambdaRank arrows
def fig_arrows():
    labels = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
    scores = [-0.5 * r for r in range(len(labels))]
    x0, step, maxlen = 140, 46, 62
    b = ['<defs>'
         '<marker id="up" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path class="f1" d="M0,0 L10,5 L0,10 z"/></marker>'
         '<marker id="dn" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path class="f4" d="M0,0 L10,5 L0,10 z"/></marker>'
         '</defs>']
    rows = [("RankNet", push(labels, scores, metric=False), 100), ("LambdaRank", push(labels, scores), 270)]
    for name, lam, y in rows:
        top = max(abs(v) for v in lam)
        b.append(text(20, y - 4, name, "title"))
        b.append(text(20, y + 14, "−∂C/∂sᵢ", "muted small"))
        b += cells(x0, step, y, labels)
        for r, v in enumerate(lam):
            L = maxlen * abs(v) / top
            if L < 3:
                continue
            x = x0 + r * step
            if v > 0:
                b.append(f'<line class="line s1" x1="{x}" x2="{x}" y1="{y - 17}" y2="{y - 17 - L:.1f}" marker-end="url(#up)"/>')
            else:
                b.append(f'<line class="line s4" x1="{x}" x2="{x}" y1="{y + 17}" y2="{y + 17 + L:.1f}" marker-end="url(#dn)"/>')
        print(name, [round(v / top, 2) for v in lam])
    return svg(700, 360, "\n".join(b), "Per-document forces for the same ranking: RankNet spreads the push evenly over all pairs; LambdaRank concentrates it at the top", EXTRA)


if __name__ == "__main__":
    write_all(OUT, [
        ("lambda-flat-metric.svg", fig_flat_metric),
        ("lambda-misaligned.svg", fig_misaligned),
        ("lambda-arrows.svg", fig_arrows),
    ])
