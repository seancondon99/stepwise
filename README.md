# Stepwise

**Live site: https://seancondon99.github.io/stepwise/**

A static site of my paper notes. No build step: notes are Markdown files rendered in the browser.

## Run locally

```sh
python3 -m http.server 8000
# open http://localhost:8000
```

(The notes are loaded with `fetch`, so opening `index.html` straight from disk won't work. Serve the folder instead.)

## Layout

```
index.html            page shell
assets/app.js         nav + Markdown rendering (marked + KaTeX from CDN)
assets/style.css
notes/nav.json        sidebar tree: sections → subsections → notes
notes/home.md         landing page
notes/<section>/<subsection>/<NN-slug>.md
```

## Adding a note

1. Create a `.md` file anywhere under `notes/`.
2. Add it to `notes/nav.json`. A node with `children` is a folder; a node with `path` is a note (path relative to `notes/`, without `.md`). `num` is optional.

```json
{ "num": 30, "title": "My New Paper", "path": "information-retrieval/5-rag-and-agents/30-my-new-paper" }
```

## Writing notes

- Standard Markdown, including tables and fenced code.
- Math: `$inline$` and `$$display$$` (KaTeX). Number an equation with `\tag{2.1}`. Shorthands: `\rel` → rel, `\nrel` → rel with an overbar (add more in `MACROS` in `assets/app.js`).
- Callouts: start a blockquote with `[!ASSUMPTION]` (pink), `[!PROBLEM]` (red), `[!INTUITION]` (green) or `[!NOTE]` (blue):

  ```md
  > [!ASSUMPTION]
  > Terms are conditionally independent given relevance.
  ```
- Figures: `<figure><img src="figures/x.svg" alt="..."><figcaption>...</figcaption></figure>`. SVGs can carry their own `prefers-color-scheme` styles for dark mode.
- Images: put them next to the note (e.g. `figures/fig1.png`) and reference them relatively: `![](figures/fig1.png)`.
- Link to another note with its relative `.md` path, e.g. `[BEIR](../2-neural-ranking/12-beir.md)`.

## Hosting

Built for GitHub Pages: push to GitHub, then go to **Settings → Pages**, choose **Deploy from a branch**, and select `main` / `(root)`. The site will be at `https://<user>.github.io/<repo>/`.

The empty `.nojekyll` file tells GitHub Pages to serve the files as-is, without running them through Jekyll.
