"""Figures for notes/classical-ml/*.md"""
import math, os, random
from svgplot import *

OUT = os.path.join(os.path.dirname(__file__), "../../notes/classical-ml/figures")

EXTRA = """
  .region { fill: #2f6fdb; fill-opacity: 0.12; stroke: #2f6fdb; stroke-width: 1.5; }
  .contour { fill: none; stroke: #d9822b; stroke-width: 1.5; }
  .contour-touch { fill: none; stroke: #d9822b; stroke-width: 2.25; }
  .axis-strong { stroke: #6b7280; stroke-width: 1.25; }
  @media (prefers-color-scheme: dark) {
    .region { fill: #7aa7ff; stroke: #7aa7ff; fill-opacity: 0.15; }
    .contour, .contour-touch { stroke: #f0a35e; }
    .axis-strong { stroke: #9aa0a8; }
  }
"""


# ---------------------------------------------------------------- linear regression: residual plots
def fig_residuals():
    rnd = random.Random(7)
    xs = [rnd.uniform(0.3, 9.7) for _ in range(70)]
    panels = [
        ("Good: no structure", 3, [rnd.gauss(0, 0.9) for x in xs]),
        ("Nonlinear (assumption 3)", 2, [0.22 * (x - 5) ** 2 - 1.8 + rnd.gauss(0, 0.45) for x in xs]),
        ("Heteroskedastic (assumption 4)", 4, [rnd.gauss(0, 0.08 + 0.21 * x) for x in xs]),
    ]
    b = []
    for j, (title, c, rs) in enumerate(panels):
        P = Plot(60 + j * 235, 34, 190, 160, (0, 10), (-4.5, 4.5))
        b.append(text(P.x0, 18, title, "title"))
        b.append(P.axes([], [-4, 0, 4], "prediction ŷ", "residual" if j == 0 else "", yfmt=lambda t: f"{t:g}"))
        b.append(P.hline(0))
        b.append(P.dots([(x, max(-4.4, min(4.4, r))) for x, r in zip(xs, rs)], f"f{c}", r=2.6))
    return svg(760, 240, "\n".join(b), "Residuals vs predictions: random scatter, a U-shaped curve, and a widening funnel")


# ---------------------------------------------------------------- regularization: L1 vs L2 geometry
C0, Q = (0.6, 2.2), ((1.2, 0.6), (0.6, 1.0))


def quad(bx, by):
    dx, dy = bx - C0[0], by - C0[1]
    return Q[0][0] * dx * dx + 2 * Q[0][1] * dx * dy + Q[1][1] * dy * dy


def ellipse(level, n=240):
    pts = []
    for k in range(n + 1):
        t = 2 * math.pi * k / n
        ux, uy = math.cos(t), math.sin(t)
        r = math.sqrt(level / (Q[0][0] * ux * ux + 2 * Q[0][1] * ux * uy + Q[1][1] * uy * uy))
        pts.append((C0[0] + r * ux, C0[1] + r * uy))
    return pts


def fig_l1_l2():
    def boundary(kind, n=4000):
        pts = []
        for k in range(n):
            t = 2 * math.pi * k / n
            x, y = math.cos(t), math.sin(t)
            s = abs(x) + abs(y) if kind == "l1" else 1.0
            pts.append((x / s, y / s))
        return pts

    b = []
    for j, (kind, title, label) in enumerate([("l1", "L1 (lasso): ‖θ‖₁ ≤ t", "lasso: θ₁ = 0"),
                                               ("l2", "L2 (ridge): ‖θ‖₂² ≤ t", "ridge: both ≠ 0")]):
        P = Plot(40 + j * 370, 34, 300, 395, (-1.6, 2.8), (-1.4, 4.4))  # equal x/y scale
        b.append(text(P.x0, 18, title, "title"))
        # axes through the origin
        b.append(f'<line class="axis-strong" x1="{P.X(-1.6):.1f}" x2="{P.X(2.8):.1f}" y1="{P.Y(0):.1f}" y2="{P.Y(0):.1f}"/>')
        b.append(f'<line class="axis-strong" x1="{P.X(0):.1f}" x2="{P.X(0):.1f}" y1="{P.Y(-1.4):.1f}" y2="{P.Y(4.4):.1f}"/>')
        b.append(text(P.X(2.8) - 2, P.Y(0) + 16, "θ₁", "muted", "end"))
        b.append(text(P.X(0) + 8, P.Y(4.4) + 12, "θ₂", "muted"))
        region = boundary(kind, 400)
        b.append('<polygon class="region" points="' + " ".join(f"{P.X(x):.1f},{P.Y(y):.1f}" for x, y in region) + '"/>')
        best = min(boundary(kind), key=lambda p: quad(*p))
        level = quad(*best)
        for f in (0.15, 0.5):
            b.append(f'<polyline class="contour" points="' + " ".join(f"{P.X(x):.1f},{P.Y(y):.1f}" for x, y in ellipse(level * f)) + '"/>')
        b.append(f'<polyline class="contour-touch" points="' + " ".join(f"{P.X(x):.1f},{P.Y(y):.1f}" for x, y in ellipse(level)) + '"/>')
        b.append(f'<circle class="f2" cx="{P.X(C0[0]):.1f}" cy="{P.Y(C0[1]):.1f}" r="4"/>')
        b.append(text(P.X(C0[0]) + 8, P.Y(C0[1]) - 6, "OLS", "small"))
        b.append(f'<circle class="f1" cx="{P.X(best[0]):.1f}" cy="{P.Y(best[1]):.1f}" r="5"/>')
        b.append(text(P.X(best[0]) - 10, P.Y(best[1]) + 4, label, "small", "end"))
        print(kind, "solution", tuple(round(v, 3) for v in best))
    return svg(760, 445, "\n".join(b), "Loss contours first touch the L1 diamond at a corner (a zero weight) and the L2 disk off-axis", EXTRA)


# ---------------------------------------------------------------- logistic regression: sigmoid + BCE
def fig_logistic():
    b = []
    L = Plot(70, 34, 260, 180, (-6, 6), (0, 1))
    b.append(text(L.x0, 18, "σ(z) = 1 / (1 + e⁻ᶻ)", "title"))
    b.append(L.axes([-6, -3, 0, 3, 6], [0, 0.5, 1], "z = xᵀθ", "ŷ", yfmt=lambda t: f"{t:g}"))
    b.append(L.hline(0.5))
    b.append(L.line([(z, 1 / (1 + math.exp(-z))) for z in arange(-6, 6)], "s1"))
    R = Plot(450, 34, 260, 180, (0, 1), (0, 5))
    b.append(text(R.x0, 18, "Per-example loss", "title"))
    b.append(R.axes([0, 0.5, 1], [0, 1, 2, 3, 4, 5], "prediction ŷ", "loss", xfmt=lambda t: f"{t:g}"))
    b.append(R.line([(p, -math.log(p)) for p in arange(0.0068, 1)], "s1"))
    b.append(R.line([(p, -math.log(1 - p)) for p in arange(0, 0.9932)], "s2"))
    b.append(R.legend_grid([("y = 1:  −log ŷ", 1, False), ("y = 0:  −log(1 − ŷ)", 2, False)], colw=150))
    return svg(760, 290, "\n".join(b), "Sigmoid curve, and binary cross-entropy for each label: confident wrong predictions cost a lot")


# ---------------------------------------------------------------- SVM: losses vs margin
def fig_svm_losses():
    P = Plot(80, 20, 600, 220, (-2.5, 3), (0, 4))
    b = [P.axes([-2, -1, 0, 1, 2, 3], [0, 1, 2, 3, 4], "margin  m = y · xᵀθ", "loss")]
    b.append(f'<line class="ref" x1="{P.X(1):.1f}" x2="{P.X(1):.1f}" y1="{P.y0}" y2="{P.y0 + P.h}"/>')
    b.append(text(P.X(1) + 6, P.y0 + 14, "m = 1", "muted small"))
    b.append(P.line([(m, (1 - m) ** 2) for m in arange(-1.0, 3) if (1 - m) ** 2 <= 4], "s3"))
    b.append(P.line([(-2.5, 1), (0, 1), (0, 0), (3, 0)], "s4 dash"))
    b.append(P.line([(m, math.log2(1 + math.exp(-m))) for m in arange(-2.5, 3)], "s2"))
    b.append(P.line([(m, max(0.0, 1 - m)) for m in arange(-2.5, 3)], "s1"))
    b.append(P.legend_grid([("hinge  max(0, 1 − m)", 1, False), ("logistic  log₂(1 + e⁻ᵐ)", 2, False),
                            ("squared  (1 − m)²", 3, False), ("0–1", 4, True)], cols=4, colw=158))
    return svg(720, 310, "\n".join(b), "Classification losses against the margin: hinge, logistic, squared and 0-1")


# ---------------------------------------------------------------- decision trees: impurity
def fig_impurity():
    P = Plot(80, 20, 520, 210, (0, 1), (0, 0.55))
    b = [P.axes([0, 0.25, 0.5, 0.75, 1], [0, 0.25, 0.5], "p  (share of class 1 in the node)", "impurity",
                xfmt=lambda t: f"{t:g}", yfmt=lambda t: f"{t:g}")]
    ent = lambda p: 0.0 if p in (0, 1) else -(p * math.log2(p) + (1 - p) * math.log2(1 - p))
    b.append(P.line([(p, min(p, 1 - p)) for p in arange(0, 1)], "s3 dash"))
    b.append(P.line([(p, ent(p) / 2) for p in arange(0, 1)], "s2"))
    b.append(P.line([(p, 2 * p * (1 - p)) for p in arange(0, 1)], "s1"))
    b.append(P.legend_grid([("Gini  2p(1 − p)", 1, False), ("entropy / 2", 2, False),
                            ("misclassification  min(p, 1 − p)", 3, True)], cols=3, colw=165))
    return svg(640, 300, "\n".join(b), "Gini, half-entropy and misclassification error for a two-class node")


# ---------------------------------------------------------------- bagging: variance of the average
def fig_bagging_variance():
    P = Plot(80, 20, 520, 210, (1, 50), (0, 1.0))
    b = [P.axes([1, 10, 20, 30, 40, 50], [0, 0.25, 0.5, 0.75, 1], "number of trees B", "Var(average) / σ²",
                yfmt=lambda t: f"{t:g}")]
    items = []
    for c, rho in [(3, 0.0), (1, 0.2), (2, 0.5)]:
        if rho > 0:
            b.append(P.hline(rho))
        b.append(P.line([(B, rho + (1 - rho) / B) for B in arange(1, 50, 300)], f"s{c}"))
        items.append((f"ρ = {rho:g}", c, False))
    b.append(text(P.X(50), P.Y(0.5) - 6, "floor = ρσ²", "muted small", "end"))
    b.append(P.legend_grid(items, cols=3, colw=110))
    return svg(640, 300, "\n".join(b), "Variance of a bagged average falls with more trees but levels off at rho times sigma squared")


if __name__ == "__main__":
    write_all(OUT, [
        ("linreg-residuals.svg", fig_residuals),
        ("reg-l1-l2.svg", fig_l1_l2),
        ("logreg.svg", fig_logistic),
        ("svm-losses.svg", fig_svm_losses),
        ("tree-impurity.svg", fig_impurity),
        ("bagging-variance.svg", fig_bagging_variance),
    ])
