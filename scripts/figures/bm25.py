"""Figures for notes/information-retrieval/1-foundations/01-bm25.md"""
import math, os
from svgplot import *

OUT = os.path.join(os.path.dirname(__file__), "../../notes/information-retrieval/1-foundations/figures")

# ---------------------------------------------------------------- Fig 1: eliteness graphical model
def fig_eliteness():
    cy = 100
    b = []
    b.append('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
             '<path class="ahead" d="M0,0 L10,5 L0,10 z"/></marker></defs>')
    # plate around eliteness + tf
    b.append(f'<rect class="plate" x="298" y="28" width="430" height="150" rx="10"/>')
    b.append(text(716, 48, "for each query term i ∈ q", "muted small", "end"))
    # nodes
    b.append(f'<circle class="node" cx="90" cy="{cy}" r="30"/>')
    b.append(text(90, cy + 5, "Rel", "title", "middle"))
    b.append(f'<rect class="node hidden" x="320" y="{cy - 24}" width="80" height="48" rx="6"/>')
    b.append(text(360, cy + 5, "Eᵢ", "title", "middle"))
    b.append(f'<rect class="node" x="590" y="{cy - 24}" width="80" height="48" rx="6"/>')
    b.append(text(630, cy + 5, "tfᵢ", "title", "middle"))
    # sublabels
    b.append(text(90, cy + 52, "relevance (binary)", "muted small", "middle"))
    b.append(text(360, cy + 52, "eliteness (hidden)", "muted small", "middle"))
    b.append(text(630, cy + 52, "term frequency (observed)", "muted small", "middle"))
    # arrows + labels
    b.append(f'<line class="arrow" x1="122" y1="{cy}" x2="316" y2="{cy}" marker-end="url(#ah)"/>')
    b.append(text(219, cy - 10, "p₁ = P(Eᵢ = 1 | rel)", "small", "middle"))
    b.append(text(219, cy + 20, "p₀ = P(Eᵢ = 1 | non-rel)", "small", "middle"))
    b.append(f'<line class="arrow" x1="402" y1="{cy}" x2="586" y2="{cy}" marker-end="url(#ah)"/>')
    b.append(text(494, cy - 10, "Poisson(λ₁) if elite", "small", "middle"))
    b.append(text(494, cy + 20, "Poisson(λ₀) if not", "small", "middle"))
    return svg(740, 200, "\n".join(b), "Graphical model: relevance determines eliteness, eliteness determines term frequency")


# ---------------------------------------------------------------- Fig 2: 2-Poisson weight vs saturation approx
def logsumexp(a, b):
    m = max(a, b)
    return m + math.log(math.exp(a - m) + math.exp(b - m))


def w_elite(tf, p1, p0, l1, l0):
    pl = lambda t, l: t * math.log(l) - l  # log Poisson pmf without the tf! term (it cancels)
    A = logsumexp(math.log(p1) + pl(tf, l1), math.log(1 - p1) + pl(tf, l0))  # P(tf | rel)
    B = logsumexp(math.log(p0) + pl(tf, l1), math.log(1 - p0) + pl(tf, l0))  # P(tf | non-rel)
    C = logsumexp(math.log(p0) - l1, math.log(1 - p0) - l0)                  # P(0 | non-rel)
    D = logsumexp(math.log(p1) - l1, math.log(1 - p1) - l0)                  # P(0 | rel)
    return A + C - B - D


def fig_two_poisson():
    # (p1, p0, lambda1, lambda0): two typical concave settings and one with an initial S-shape (cf. paper Fig. 3.2 right)
    settings = [((0.6, 0.1, 2.0, 0.05), 1), ((0.9, 0.5, 3.0, 2.0), 3), ((0.7, 0.2, 8.0, 4.0), 4)]
    P = Plot(80, 20, 600, 220, (0, 15), (0, 1.05))
    b = [P.axes(range(0, 16, 3), [0, 0.25, 0.5, 0.75, 1.0], "term frequency tf", "wᵢ(tf) / asymptote", yfmt=lambda t: f"{t:g}")]
    b.append(P.hline(1.0))
    items = []
    for (p1, p0, l1, l0), c in settings:
        vals = [w_elite(t, p1, p0, l1, l0) for t in range(0, 60)]
        w_inf = vals[-1]
        pts = [(t, vals[t] / w_inf) for t in range(0, 16)]
        b.append(P.line(pts, f"s{c}").replace('stroke-width', 'stroke-width') )
        b.append(P.dots(pts, f"f{c}", r=3))
        items.append((f"2-Poisson: p₁={p1:g}, p₀={p0:g}, λ₁={l1:g}, λ₀={l0:g}", c, False))
    # fit tf/(k+tf) to the gradual concave curve
    p1, p0, l1, l0 = settings[1][0]
    vals = [w_elite(t, p1, p0, l1, l0) for t in range(0, 60)]
    target = [(t, vals[t] / vals[-1]) for t in range(0, 16)]
    k = min((sum((v - t / (k + t)) ** 2 for t, v in target), k) for k in [i / 100 for i in range(1, 2000)])[1]
    print(f"fitted k={k:.2f}")
    b.append(P.line([(x, x / (k + x)) for x in arange(0, 15)], "s2 dash"))
    items.append((f"tf / (k + tf),  k ≈ {k:.1f}", 2, True))
    b.append(P.legend(P.X(7), P.Y(0.5), items, 330))
    return svg(720, 300, "\n".join(b), "2-Poisson term weights for several parameter settings all start at zero and saturate; tf/(k+tf) has the same shape")


# ---------------------------------------------------------------- Fig 3: k1 and length normalization
def fig_bm25_knobs():
    b = []
    xmax = 15
    # left: k1
    L = Plot(70, 36, 270, 200, (0, xmax), (0, 1.05))
    b.append(text(L.x0, 18, "Saturation: varying k₁", "title"))
    b.append(L.axes([0, 5, 10, 15], [0, 0.25, 0.5, 0.75, 1.0], "term frequency tf", "weight / wᵢ(RSJ)", yfmt=lambda t: f"{t:g}"))
    b.append(L.line([(0, 0), (1, 1), (xmax, 1)], "s4 dash"))
    for c, k in [(1, 1.2), (2, 3), (3, 10)]:
        b.append(L.line([(x, x / (k + x)) for x in arange(0, xmax)], f"s{c}"))
    b.append(L.legend_grid([
        ("k₁ → 0 (binary, BIM)", 4, True),
        ("k₁ = 1.2", 1, False),
        ("k₁ = 3", 2, False),
        ("k₁ = 10", 3, False),
    ], colw=165))
    # right: document length
    R = Plot(450, 36, 270, 200, (0, xmax), (0, 1.05))
    b.append(text(R.x0, 18, "Length normalization: k₁ = 1.2, b = 0.75", "title"))
    b.append(R.axes([0, 5, 10, 15], [0, 0.25, 0.5, 0.75, 1.0], "term frequency tf", "weight / wᵢ(RSJ)", yfmt=lambda t: f"{t:g}"))
    items = []
    for c, r in [(3, 0.5), (1, 1.0), (2, 2.0), (4, 4.0)]:
        K = 1.2 * ((1 - 0.75) + 0.75 * r)
        b.append(R.line([(x, x / (K + x)) for x in arange(0, xmax)], f"s{c}"))
        items.append((f"dl / avdl = {r:g}", c, False))
    b.append(R.legend_grid(items))
    return svg(740, 330, "\n".join(b), "BM25 term weight versus tf for several k1 values and several document lengths")


# ---------------------------------------------------------------- Fig 4: IDF
def fig_idf():
    N = 1_000_000
    P = Plot(80, 20, 600, 220, (1, N), (-15, 15), xlog=True)
    b = []
    b.append(f'<rect class="shade" x="{P.X(N / 2):.1f}" y="{P.y0}" width="{P.X(N) - P.X(N / 2):.1f}" height="{P.h}"/>')
    sup = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶"}
    b.append(P.axes([10 ** e for e in range(0, 7)], [-15, -10, -5, 0, 5, 10, 15],
                    "document frequency nᵢ  (N = 10⁶, log scale)", "wᵢ(IDF)",
                    xfmt=lambda t: "1" if t == 1 else "10" + "".join(sup[ch] for ch in str(int(round(math.log10(t)))))))
    b.append(P.hline(0))
    xs = [10 ** (6 * i / 600) for i in range(601)]
    xs = [x for x in xs if x <= N]
    b.append(P.line([(x, math.log(1 + (N - x + 0.5) / (x + 0.5))) for x in xs], "s2 dash"))
    b.append(P.line([(x, math.log((N - x + 0.5) / (x + 0.5))) for x in xs], "s1"))
    b.append(text(P.X(N / 2) - 6, P.Y(-11.5), "nᵢ > N/2: weight goes negative", "small", "end"))
    b.append(P.legend(P.X(1.6), P.Y(-6), [
        ("log (N − nᵢ + 0.5) / (nᵢ + 0.5)", 1, False),
        ("Lucene: log(1 + (N − nᵢ + 0.5) / (nᵢ + 0.5))", 2, True),
    ], 310))
    return svg(720, 300, "\n".join(b), "IDF weight falls with document frequency and goes negative for terms in over half the documents")


if __name__ == "__main__":
    write_all(OUT, [("bm25-eliteness.svg", fig_eliteness), ("bm25-two-poisson.svg", fig_two_poisson),
                    ("bm25-k1-b.svg", fig_bm25_knobs), ("bm25-idf.svg", fig_idf)])
