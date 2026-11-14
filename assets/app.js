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

  // Shorthands usable in any note's math.
  const MACROS = {
    "\\rel": "\\mathrm{rel}",
    "\\nrel": "\\overline{\\mathrm{rel}}",
  };

  function renderMath(tex, displayMode) {
    try {
      return katex.renderToString(tex, { displayMode, throwOnError: false, macros: { ...MACROS } });
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

  // ---------- Derivation blocks ----------
  // A ```derivation fenced block renders an aligned equation chain, one step per line:
  //   LHS & RHS || tag || note
  // `&` marks the alignment point; tag and note are optional. A note is short text shown to the
  // right, or `[!ASSUMPTION] short title :: longer body` to render a chip that expands on click.

  let derivId = 0;

  // First `&` not written as `\&` (avoids regex lookbehind, which older Safari lacks).
  function indexOfUnescapedAmp(s) {
    for (let i = 0; i < s.length; i++) {
      if (s[i] === "\\") i++;
      else if (s[i] === "&") return i;
    }
    return -1;
  }

  function renderDerivation(src) {
    const rows = [];
    for (const line of src.split("\n")) {
      if (!line.trim()) continue;
      const [eq, tag = "", ...rest] = line.split(/\s*\|\|\s*/);
      const note = rest.join(" || ").trim();
      const amp = indexOfUnescapedAmp(eq);
      const lhs = amp < 0 ? "" : eq.slice(0, amp);
      const rhs = amp < 0 ? eq : eq.slice(amp + 1);

      let noteHtml = "";
      let more = "";
      const m = /^\[!(\w+)\]\s*/.exec(note);
      if (m && CALLOUTS[m[1].toLowerCase()]) {
        const kind = m[1].toLowerCase();
        const [title, body = ""] = note.slice(m[0].length).split(" :: ");
        const id = "deriv-more-" + ++derivId;
        noteHtml =
          `<button type="button" class="d-chip callout-${kind}" aria-expanded="false" aria-controls="${id}">` +
          `<span class="d-chip-kind">${CALLOUTS[kind]}</span>` +
          (title.trim() ? `<span class="d-chip-title">${marked.parseInline(title.trim())}</span>` : "") +
          `<span class="d-chip-caret" aria-hidden="true">▸</span></button>`;
        more = `<div class="d-more callout-${kind}" id="${id}" hidden>${marked.parseInline(body.trim())}</div>`;
      } else if (note) {
        noteHtml = marked.parseInline(note);
      }

      rows.push(
        `<div class="d-lhs">${lhs.trim() ? renderMath("\\displaystyle " + lhs, false) : ""}</div>` +
          `<div class="d-rhs">${renderMath("\\displaystyle {}" + rhs, false)}</div>` +
          `<div class="d-note">${noteHtml}</div>` +
          `<div class="d-tag">${tag.trim() ? "(" + tag.trim() + ")" : ""}</div>` +
          more
      );
    }
    return `<div class="deriv">${rows.join("")}</div>`;
  }

  marked.use({
    renderer: {
      code(code, lang) {
        // marked v12 passes (text, lang); newer versions pass a token object
        if (code && typeof code === "object") ({ text: code, lang } = code);
        if ((lang || "").trim() !== "derivation") return false;
        return renderDerivation(code);
      },
    },
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

  // Callouts: a blockquote starting with [!ASSUMPTION], [!PROBLEM], [!INTUITION] or [!NOTE]
  // becomes a colored box with a title.
  const CALLOUTS = { assumption: "Assumption", problem: "Problem", intuition: "Intuition", note: "Note" };

  function renderCallouts() {
    for (const bq of noteEl.querySelectorAll("blockquote")) {
      const p = bq.querySelector("p");
      const m = p && /^\s*\[!(\w+)\]\s*/.exec(p.innerHTML);
      if (!m || !CALLOUTS[m[1].toLowerCase()]) continue;
      const kind = m[1].toLowerCase();
      p.innerHTML = p.innerHTML.slice(m[0].length);
      if (!p.innerHTML.trim()) p.remove();
      bq.classList.add("callout", "callout-" + kind);
      const title = document.createElement("div");
      title.className = "callout-title";
      title.textContent = CALLOUTS[kind];
      bq.prepend(title);
    }
  }

  async function loadNote(path) {
    try {
      const res = await fetch(NOTES_DIR + path + ".md", { cache: "no-cache" });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const md = await res.text();
      noteEl.innerHTML = marked.parse(md);
      rebaseRelativeUrls(path);
      renderCallouts();
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
  noteEl.addEventListener("click", (e) => {
    const chip = e.target.closest(".d-chip");
    if (!chip) return;
    const more = document.getElementById(chip.getAttribute("aria-controls"));
    const open = chip.getAttribute("aria-expanded") !== "true";
    chip.setAttribute("aria-expanded", String(open));
    if (more) more.hidden = !open;
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
