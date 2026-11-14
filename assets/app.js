// Stepwise notes: renders notes/<path>.md into the page, driven by notes/nav.json.
// Routes are hash-based (#/information-retrieval/...), so the site works on any static host.

(function () {
  const NOTES_DIR = "notes/";
  const HOME = "home";

  const navEl = document.getElementById("nav");
  const noteEl = document.getElementById("note");
  const pagerEl = document.getElementById("pager");

  let leaves = []; // flat, in nav order: [{ title, path, num }]

  // ---------- Markdown + math ----------
  // $$...$$ for display math, $...$ for inline. Tokenized inside marked so code spans/blocks are left alone.

  function renderMath(tex, displayMode) {
    try {
      return katex.renderToString(tex, { displayMode, throwOnError: false });
    } catch (e) {
      return `<code>${tex}</code>`;
    }
  }

  marked.use({
    extensions: [
      {
        name: "blockMath",
        level: "block",
        start(src) {
          const i = src.indexOf("$$");
          return i < 0 ? undefined : i;
        },
        tokenizer(src) {
          const m = /^\$\$([\s\S]+?)\$\$[ \t]*(?:\n|$)/.exec(src);
          if (m) return { type: "blockMath", raw: m[0], text: m[1].trim() };
        },
        renderer(token) {
          return renderMath(token.text, true);
        },
      },
      {
        name: "inlineMath",
        level: "inline",
        start(src) {
          const i = src.indexOf("$");
          return i < 0 ? undefined : i;
        },
        tokenizer(src) {
          let m = /^\$\$([\s\S]+?)\$\$/.exec(src);
          if (m) return { type: "inlineMath", raw: m[0], text: m[1].trim(), display: true };
          m = /^\$((?:\\\$|[^$\n])+?)\$/.exec(src);
          if (m) return { type: "inlineMath", raw: m[0], text: m[1].trim(), display: false };
        },
        renderer(token) {
          return renderMath(token.text, token.display);
        },
      },
    ],
  });

  // ---------- Navigation ----------

  function buildNav(nodes) {
    const ul = document.createElement("ul");
    for (const node of nodes) {
      const li = document.createElement("li");
      if (node.children) {
        const details = document.createElement("details");
        const summary = document.createElement("summary");
        summary.textContent = node.title;
        details.appendChild(summary);
        details.appendChild(buildNav(node.children));
        li.appendChild(details);
      } else {
        li.className = "leaf";
        const a = document.createElement("a");
        a.href = "#/" + node.path;
        a.dataset.path = node.path;
        if (node.num != null) {
          const num = document.createElement("span");
          num.className = "num";
          num.textContent = node.num;
          a.appendChild(num);
        }
        const title = document.createElement("span");
        title.textContent = node.title;
        a.appendChild(title);
        li.appendChild(a);
        leaves.push(node);
      }
      ul.appendChild(li);
    }
    return ul;
  }

  function highlightActive(path) {
    for (const a of navEl.querySelectorAll("a.active")) a.classList.remove("active");
    const link = navEl.querySelector(`a[data-path="${CSS.escape(path)}"]`);
    if (!link) return;
    link.classList.add("active");
    // open every enclosing folder
    for (let el = link.parentElement; el && el !== navEl; el = el.parentElement) {
      if (el.tagName === "DETAILS") el.open = true;
    }
    link.scrollIntoView({ block: "nearest" });
  }

  function renderPager(path) {
    pagerEl.innerHTML = "";
    const i = leaves.findIndex((l) => l.path === path);
    if (i < 0) return;
    const link = (leaf, cls, label) => {
      const a = document.createElement("a");
      a.className = cls;
      a.href = "#/" + leaf.path;
      a.innerHTML = `<span class="label">${label}</span>`;
      a.appendChild(document.createTextNode((leaf.num != null ? leaf.num + ". " : "") + leaf.title));
      return a;
    };
    if (i > 0) pagerEl.appendChild(link(leaves[i - 1], "prev", "← Previous"));
    if (i < leaves.length - 1) pagerEl.appendChild(link(leaves[i + 1], "next", "Next →"));
  }

  // ---------- Notes ----------

  // Make relative image/link URLs in a note resolve against the note's own folder,
  // so `![](figures/fig1.png)` next to the .md file just works.
  function rebaseRelativeUrls(path) {
    const dir = NOTES_DIR + path.split("/").slice(0, -1).join("/") + "/";
    const isRelative = (u) => u && !/^([a-z]+:|\/|#)/i.test(u);
    for (const img of noteEl.querySelectorAll("img[src]")) {
      const src = img.getAttribute("src");
      if (isRelative(src)) img.setAttribute("src", dir + src);
    }
    for (const a of noteEl.querySelectorAll("a[href]")) {
      const href = a.getAttribute("href");
      if (!isRelative(href)) continue;
      // links to other notes (foo.md) become in-app routes; anything else is a file link
      if (/\.md$/.test(href)) {
        const parts = (dir.slice(NOTES_DIR.length) + href.replace(/\.md$/, "")).split("/");
        const out = [];
        for (const p of parts) {
          if (p === "..") out.pop();
          else if (p !== "." && p !== "") out.push(p);
        }
        a.setAttribute("href", "#/" + out.join("/"));
      } else {
        a.setAttribute("href", dir + href);
      }
    }
  }

  async function loadNote(path) {
    try {
      const res = await fetch(NOTES_DIR + path + ".md", { cache: "no-cache" });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const md = await res.text();
      noteEl.innerHTML = marked.parse(md);
      rebaseRelativeUrls(path);
      const h1 = noteEl.querySelector("h1");
      document.title = (h1 ? h1.textContent + " · " : "") + "Stepwise";
    } catch (err) {
      noteEl.innerHTML = `<h1>Note not found</h1><p class="error">Couldn't load <code>${NOTES_DIR}${path}.md</code> (${err.message}).</p>`;
      document.title = "Not found · Stepwise";
    }
    highlightActive(path);
    renderPager(path);
    window.scrollTo(0, 0);
  }

  function currentPath() {
    const p = decodeURIComponent(location.hash.replace(/^#\/?/, ""));
    return p || HOME;
  }

  // ---------- Mobile menu ----------

  const toggle = document.getElementById("menu-toggle");
  toggle.addEventListener("click", () => {
    const open = document.body.classList.toggle("nav-open");
    toggle.setAttribute("aria-expanded", String(open));
  });
  navEl.addEventListener("click", (e) => {
    if (e.target.closest("a")) {
      document.body.classList.remove("nav-open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });

  // ---------- Boot ----------

  async function init() {
    try {
      const res = await fetch(NOTES_DIR + "nav.json", { cache: "no-cache" });
      const nav = await res.json();
      navEl.appendChild(buildNav(nav));
      // top-level sections start expanded
      for (const d of navEl.querySelectorAll(":scope > ul > li > details")) d.open = true;
    } catch (err) {
      navEl.innerHTML = `<p class="error">Couldn't load nav.json. If you opened index.html directly, serve the folder instead: <code>python3 -m http.server</code></p>`;
    }
    window.addEventListener("hashchange", () => loadNote(currentPath()));
    loadNote(currentPath());
  }

  init();
})();
