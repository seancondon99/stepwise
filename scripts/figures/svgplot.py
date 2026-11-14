"""Tiny SVG plotting helpers shared by the figure scripts (no dependencies)."""
import math, os, sys


STYLE = """<style>
  text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 13px; fill: #1f2328; }
  .muted { fill: #6b7280; }
  .small { font-size: 12px; }
  .title { font-weight: 600; }
  .axis { stroke: #9ca3af; stroke-width: 1; fill: none; }
  .grid { stroke: #ececea; stroke-width: 1; fill: none; }
  .s1 { stroke: #2f6fdb; } .f1 { fill: #2f6fdb; }
  .s2 { stroke: #d9822b; } .f2 { fill: #d9822b; }
  .s3 { stroke: #2e9e6a; } .f3 { fill: #2e9e6a; }
  .s4 { stroke: #b0398f; } .f4 { fill: #b0398f; }
  .line { fill: none; stroke-width: 2.25; stroke-linejoin: round; stroke-linecap: round; }
  .dash { stroke-dasharray: 6 5; }
  .ref { stroke: #6b7280; stroke-width: 1.25; stroke-dasharray: 4 4; fill: none; }
  .shade { fill: #d0453a; opacity: 0.08; }
  .node { fill: #ffffff; stroke: #1f2328; stroke-width: 1.5; }
  .hidden { fill: #e9effb; }
  .arrow { stroke: #1f2328; stroke-width: 1.5; fill: none; }
  .ahead { fill: #1f2328; }
  .plate { fill: none; stroke: #9ca3af; stroke-width: 1.25; stroke-dasharray: 6 4; }
  .legend-bg { fill: #fdfdfc; opacity: 0.9; }
  @media (prefers-color-scheme: dark) {
    text { fill: #e6e6e3; }
    .muted { fill: #9aa0a8; }
    .axis { stroke: #6b7280; }
    .grid { stroke: #2a2e34; }
    .s1 { stroke: #7aa7ff; } .f1 { fill: #7aa7ff; }
    .s2 { stroke: #f0a35e; } .f2 { fill: #f0a35e; }
    .s3 { stroke: #5cc495; } .f3 { fill: #5cc495; }
    .s4 { stroke: #e07cc4; } .f4 { fill: #e07cc4; }
    .ref { stroke: #9aa0a8; }
    .shade { fill: #ff6b5e; opacity: 0.1; }
    .node { fill: #1d2025; stroke: #e6e6e3; }
    .hidden { fill: #263450; }
    .arrow { stroke: #e6e6e3; }
    .ahead { fill: #e6e6e3; }
    .legend-bg { fill: #16181c; }
  }
</style>"""


def svg(w, h, body, label, extra_style=""):
    style = STYLE.replace("</style>", extra_style + "</style>") if extra_style else STYLE
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{label}">\n{style}\n{body}\n</svg>\n')


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, cls="", anchor="start", extra=""):
    c = f' class="{cls}"' if cls else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}"{c}{extra}>{esc(s)}</text>'


class Plot:
    def __init__(self, x0, y0, w, h, xlim, ylim, xlog=False):
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.xlim, self.ylim, self.xlog = xlim, ylim, xlog

    def X(self, x):
        a, b = self.xlim
        if self.xlog:
            x, a, b = math.log10(x), math.log10(a), math.log10(b)
        return self.x0 + (x - a) / (b - a) * self.w

    def Y(self, y):
        a, b = self.ylim
        return self.y0 + self.h - (y - a) / (b - a) * self.h

    def axes(self, xticks, yticks, xlabel, ylabel, xfmt=str, yfmt=str):
        out = []
        for t in yticks:
            out.append(f'<line class="grid" x1="{self.x0}" x2="{self.x0 + self.w}" y1="{self.Y(t):.1f}" y2="{self.Y(t):.1f}"/>')
            out.append(text(self.x0 - 8, self.Y(t) + 4, yfmt(t), "muted small", "end"))
        for t in xticks:
            out.append(text(self.X(t), self.y0 + self.h + 18, xfmt(t), "muted small", "middle"))
        out.append(f'<line class="axis" x1="{self.x0}" x2="{self.x0 + self.w}" y1="{self.y0 + self.h}" y2="{self.y0 + self.h}"/>')
        out.append(f'<line class="axis" x1="{self.x0}" x2="{self.x0}" y1="{self.y0}" y2="{self.y0 + self.h}"/>')
        out.append(text(self.x0 + self.w / 2, self.y0 + self.h + 40, xlabel, "muted", "middle"))
        cx, cy = self.x0 - 44, self.y0 + self.h / 2
        out.append(text(cx, cy, ylabel, "muted", "middle", f' transform="rotate(-90 {cx:.1f} {cy:.1f})"'))
        return "\n".join(out)

    def line(self, pts, cls):
        d = " ".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in pts)
        return f'<polyline class="line {cls}" points="{d}"/>'

    def dots(self, pts, cls, r=3.5):
        return "\n".join(f'<circle class="{cls}" cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}"/>' for x, y in pts)

    def hline(self, y, cls="ref"):
        return f'<line class="{cls}" x1="{self.x0}" x2="{self.x0 + self.w}" y1="{self.Y(y):.1f}" y2="{self.Y(y):.1f}"/>'

    def legend_grid(self, items, cols=2, colw=135, dy=19):
        out = []
        y0 = self.y0 + self.h + 64
        for j, (label, c, dashed) in enumerate(items):
            x = self.x0 + (j % cols) * colw
            yy = y0 + (j // cols) * dy
            out.append(f'<line class="line s{c}{" dash" if dashed else ""}" x1="{x}" x2="{x + 22}" y1="{yy - 4}" y2="{yy - 4}"/>')
            out.append(text(x + 30, yy, label, "small"))
        return "\n".join(out)

    def legend(self, x, y, items, width):
        # items: [(label, color_idx, dashed)]
        out = [f'<rect class="legend-bg" x="{x - 8}" y="{y - 14}" width="{width}" height="{len(items) * 19 + 8}" rx="4"/>']
        for j, (label, c, dashed) in enumerate(items):
            yy = y + j * 19
            if dashed == "dot":
                out.append(f'<circle class="f{c}" cx="{x + 11}" cy="{yy - 4}" r="3.5"/>')
            else:
                out.append(f'<line class="line s{c}{" dash" if dashed else ""}" x1="{x}" x2="{x + 22}" y1="{yy - 4}" y2="{yy - 4}"/>')
            out.append(text(x + 30, yy, label, "small"))
        return "\n".join(out)


def arange(a, b, n=200):
    return [a + (b - a) * i / n for i in range(n + 1)]




def write_all(out_dir, figures):
    """figures: [(filename, fn)]"""
    os.makedirs(out_dir, exist_ok=True)
    for name, fn in figures:
        with open(os.path.join(out_dir, name), "w") as f:
            f.write(fn())
        print("wrote", os.path.join(out_dir, name))
