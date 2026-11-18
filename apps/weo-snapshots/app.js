/* app.js — the WEO Snapshots page: controls, the latest-values table, the 12 charts, the code boxes and the URL.
   Generated into macro102-site/apps/weo-snapshots/ by /write-weo-snapshots (do not edit there).
   The logic (charts, table, Python code, URL) is in weocore.js; this file only wires it to the page.
   Charts are always drawn with Plotly.newPlot: the book's plotly-theme.html wraps it to keep the light
   figure and recolor it in dark mode (Plotly.react would bypass that). */
(function () {
  "use strict";
  var COLAB = "https://colab.research.google.com/notebooks/empty.ipynb";
  var root = document.getElementById("snap-app");
  if (!root) return;
  var panels = JSON.parse(document.getElementById("snap-panels").textContent);
  var weo, state, db;

  function $(id) { return document.getElementById(id); }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  // ---- Python highlighting with Quarto's classes (the book's code colors, light and dark) ---------
  var KEYWORDS = /^(import|as|from|def|return|for|in|if|else|and|or|not|with|lambda)$/;
  function highlight(code) {
    var re = /(#[^\n]*)|("""[\s\S]*?"""|f?"(?:[^"\\\n]|\\.)*")|(\b\d+(?:\.\d+)?\b)|(\b[A-Za-z_][A-Za-z_0-9]*\b)|([\s\S])/g, m, out = "";
    while ((m = re.exec(code))) {
      if (m[1]) out += '<span class="co">' + esc(m[1]) + "</span>";
      else if (m[2]) out += '<span class="st">' + esc(m[2]) + "</span>";
      else if (m[3]) out += '<span class="dv">' + m[3] + "</span>";
      else if (m[4]) {
        var w = m[4], next = code.charAt(re.lastIndex);
        if (w === "import" || w === "as") out += '<span class="im">' + w + "</span>";
        else if (KEYWORDS.test(w)) out += '<span class="kw">' + w + "</span>";
        else if (w === "None" || w === "True" || w === "False") out += '<span class="va">' + w + "</span>";
        else if (next === "(") out += '<span class="fu">' + w + "</span>";
        else out += w;
      } else out += esc(m[5]);
    }
    return out;
  }

  // ---- clipboard and files ------------------------------------------------------------------------
  function copyText(text, button) {
    function done(ok) {
      var old = button.dataset.label || button.textContent;
      button.dataset.label = old;
      button.textContent = ok ? "Copied!" : "Press Ctrl+C";
      button.classList.toggle("snap-done", ok);
      setTimeout(function () { button.textContent = old; button.classList.remove("snap-done"); }, 1600);
    }
    function fallback() {
      var t = el("textarea");
      t.value = text;
      t.setAttribute("readonly", "");
      t.style.position = "fixed";
      t.style.opacity = "0";
      document.body.appendChild(t);
      t.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      document.body.removeChild(t);
      done(ok);
    }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(function () { done(true); }, fallback);
    else fallback();
  }
  function download(name, href) {
    var a = el("a");
    a.href = href;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  // ---- a code box: "Copy code" (upper right), the code, "Open Colab" (lower right) ------------------
  function codeBox(summary, getCode) {
    var det = el("details", "snap-code");
    det.appendChild(el("summary", null, summary));
    var box = el("div", "snap-codebox");
    var copy = el("button", "snap-copy", "Copy code");
    copy.type = "button";
    var wrap = el("div", "sourceCode");                // Quarto's code block: the book's code colors
    var pre = el("pre", "sourceCode python");
    var code = el("code", "sourceCode python");
    pre.appendChild(code);
    wrap.appendChild(pre);
    var foot = el("div", "snap-codefoot");
    foot.appendChild(el("span", "snap-codetip", "Copy the code, open an empty Colab notebook, paste it into a cell and run it (Shift+Enter)."));
    var colab = el("a", "snap-colab", "Open Colab ↗");
    colab.href = COLAB;
    colab.target = "_blank";
    colab.rel = "noopener";
    foot.appendChild(colab);
    box.appendChild(copy);
    box.appendChild(wrap);
    box.appendChild(foot);
    det.appendChild(box);
    function render() { if (det.open) code.innerHTML = highlight(getCode()); }
    det.addEventListener("toggle", render);
    copy.addEventListener("click", function () { copyText(getCode(), copy); });
    det.render = render;
    return det;
  }

  // ---- the panels -----------------------------------------------------------------------------------
  var cards = {};
  function buildPanels() {
    var grid = $("snap-grid");
    panels.forEach(function (p, k) {
      var card = el("section", "snap-card");
      card.id = "panel-" + p.id;
      var head = el("div", "snap-cardhead");
      var title = el("h3", "snap-title anchored");
      var unit = el("div", "snap-unit");
      head.appendChild(el("span", "snap-num", String(k + 1)));
      var words = el("div", "snap-words");
      words.appendChild(title);
      words.appendChild(unit);
      head.appendChild(words);
      var tools = el("div", "snap-tools");
      var seg = null;
      if (p.series.length > 1) {                       // compare mode: which series to draw
        seg = el("div", "snap-seg");
        seg.setAttribute("role", "group");
        seg.setAttribute("aria-label", "Series to compare");
        p.series.forEach(function (s, i) {
          var b = el("button", null, s.label);
          b.type = "button";
          b.addEventListener("click", function () { state.show[p.id] = i; update(p.id); });
          seg.appendChild(b);
        });
        tools.appendChild(seg);
      }
      head.appendChild(tools);
      card.appendChild(head);
      var chart = el("div", "snap-chart");
      chart.id = "chart-" + p.id;
      card.appendChild(chart);
      card.appendChild(el("p", "snap-hint", p.hint));
      var code = codeBox("Show the Python code", function () { return weo.panelCode(p, state); });
      card.appendChild(code);
      grid.appendChild(card);
      var note = el("p", "snap-note");
      note.hidden = true;
      chart.insertAdjacentElement("afterend", note);
      cards[p.id] = { card: card, title: title, unit: unit, chart: chart, seg: seg, code: code, note: note };
    });
  }

  function drawPanel(p) {
    var c = cards[p.id], fig = weo.figure(p, state);
    c.title.textContent = fig.title;
    c.unit.textContent = fig.unit;
    if (c.seg) {
      c.seg.hidden = state.countries.length === 1;
      Array.prototype.forEach.call(c.seg.children, function (b, i) {
        b.setAttribute("aria-pressed", String((state.show[p.id] || 0) === i));
      });
    }
    c.card.classList.toggle("snap-empty", fig.empty);
    c.note.textContent = fig.note;                     // where a line is not the IMF's (e.g. a book estimate)
    c.note.hidden = !fig.note;
    // Plotly's own camera icon saves the chart as shown (the site hides the toolbar on touch screens)
    window.Plotly.newPlot(c.chart, fig.data, fig.layout, {
      responsive: true, displaylogo: false,
      modeBarButtonsToRemove: ["select2d", "lasso2d", "autoScale2d"],
      toImageButtonOptions: { format: "png", scale: 2,
                              filename: "weo-snapshots_" + state.countries.join("-") + "_" + p.id }
    });
    c.code.render();
  }

  // ---- the latest values and the IMF's forecasts ----------------------------------------------------
  function table() {
    var t = weo.table(state), box = $("snap-table");
    box.innerHTML = "";
    var tab = el("table", "snap-latest");
    var head = el("thead"), r1 = el("tr"), r2 = el("tr");
    var several = state.countries.length > 1, span = 1 + t.years.length;
    r1.appendChild(el("th", "snap-tcol", ""));
    if (several) state.countries.forEach(function (iso, k) {
      var th = el("th", "snap-tgroup snap-c" + k);
      th.colSpan = span;
      th.appendChild(el("span", "snap-dot"));
      th.appendChild(document.createTextNode(" " + weo.name(iso)));
      r1.appendChild(th);
    });
    r2.appendChild(el("th", "snap-tcol", "Indicator"));
    state.countries.forEach(function () {
      r2.appendChild(el("th", "snap-tnum", "Latest actual"));
      t.years.forEach(function (y) { r2.appendChild(el("th", "snap-tnum", String(y))); });
    });
    if (several) head.appendChild(r1);
    head.appendChild(r2);
    tab.appendChild(head);
    var body = el("tbody");
    t.rows.forEach(function (row) {
      var tr = el("tr");
      var th = el("th", "snap-tcol");
      var a = el("a", null, row.label);
      a.href = "#panel-" + row.id;
      a.addEventListener("click", function (e) {      // scroll to the chart, keep the view's URL
        e.preventDefault();
        cards[row.id].card.scrollIntoView({ behavior: "smooth", block: "start" });
      });
      th.appendChild(a);
      th.appendChild(el("span", "snap-tunit", " " + row.unit));
      tr.appendChild(th);
      row.cells.forEach(function (cells) {
        cells.forEach(function (c, k) {
          var td = el("td", "snap-tnum" + (c.proj ? " snap-proj" : ""), c.text);
          if (k === 0 && c.year) td.appendChild(el("span", "snap-tyear", " (" + c.year + ")"));
          if (c.proj) td.title = "IMF projection";
          tr.appendChild(td);
        });
      });
      body.appendChild(tr);
    });
    tab.appendChild(body);
    var wrap = el("div", "snap-tablewrap");
    wrap.appendChild(tab);
    box.appendChild(wrap);
    box.appendChild(el("p", "snap-small", t.years.length
      ? "Italic numbers are IMF projections (" + db.vintage.name + " WEO). \"Latest actual\" is the last year of actual data."
      : "\"Latest actual\" is the last year of actual data. Turn the IMF projections on to see the forecasts."));
  }

  // ---- the controls ---------------------------------------------------------------------------------
  function heading() {
    var h = $("snap-heading");
    h.innerHTML = "";
    if (state.countries.length === 1) {
      var c = db.countries.filter(function (x) { return x.iso3 === state.countries[0]; })[0];
      h.appendChild(document.createTextNode(c.name));
      if (c.group) h.appendChild(el("span", "snap-pop", " (a WEO country group)"));
      else if (c.pop) h.appendChild(el("span", "snap-pop", " (Population = " + weo.fmt(c.pop, c.pop < 1 ? 2 : 1) + "m in " + db.vintage.year + ")"));
    } else {
      h.appendChild(document.createTextNode(state.countries.map(function (c) { return weo.name(c); }).join(" · ")));
    }
    var ref = weo.reference(state);
    $("snap-benchnote").textContent = (ref ? "Gray line: " + weo.name(ref) + " (the benchmark)."
      : state.bench === "NONE" ? "No reference line." : weo.name(state.bench) + " is shown, so there is no reference line.") +
      " Gray bands: recessions of " + weo.name(state.countries[0]) + " (real GDP fell)" +
      (state.proj ? " and the years of IMF projections (dotted lines)." : ".");
  }
  function chips() {
    var box = $("snap-chips");
    box.innerHTML = "";
    state.countries.forEach(function (iso, k) {
      var chip = el("span", "snap-chip snap-c" + k);         // the line color of the country (app.css)
      chip.appendChild(el("span", "snap-dot"));
      chip.appendChild(document.createTextNode(weo.name(iso)));
      if (state.countries.length > 1) {
        var x = el("button", "snap-x", "×");
        x.type = "button";
        x.setAttribute("aria-label", "Remove " + weo.name(iso));
        x.addEventListener("click", function () {
          state.countries = state.countries.filter(function (c) { return c !== iso; });
          update();
        });
        chip.appendChild(x);
      }
      box.appendChild(chip);
    });
    var left = WeoCore.MAX_COUNTRIES - state.countries.length;
    $("snap-limit").textContent = left > 0 ? "Compare up to " + WeoCore.MAX_COUNTRIES + " countries or groups (" + left + " more)."
                                           : "Five shown: remove one to add another.";
  }
  function years() {
    var a = $("snap-y0"), b = $("snap-y1");
    a.value = state.start;
    b.value = state.end;
    $("snap-ylabel").textContent = state.start + "–" + state.end;
    var span = db.last - db.first;
    $("snap-yfill").style.left = (100 * (state.start - db.first) / span) + "%";
    $("snap-yfill").style.right = (100 * (db.last - state.end) / span) + "%";
  }

  var pending = null, scrollWhenDrawn = false;
  function update(only) {
    if (window.history && history.replaceState) history.replaceState(null, "", "#" + weo.format(state));
    heading();
    chips();
    years();
    table();
    $("snap-bench").value = state.bench;
    $("snap-proj").checked = state.proj;
    $("snap-whole").render();
    if (only) { drawPanel(weo.byId[only]); return; }
    // draw the charts one per frame (the page stays responsive)
    if (pending) cancelAnimationFrame(pending);
    var todo = panels.slice();
    (function next() {
      var p = todo.shift();
      if (!p) {
        pending = null;
        if (scrollWhenDrawn) { scrollWhenDrawn = false; afterLoad(); }
        return;
      }
      drawPanel(p);
      pending = requestAnimationFrame(next);
    })();
  }

  function show(iso) { state.countries = [iso]; state.focus = null; update(); }
  function add(iso) {
    if (state.countries.indexOf(iso) >= 0) return;
    if (state.countries.length >= WeoCore.MAX_COUNTRIES) { flash($("snap-limit")); return; }
    state.countries = state.countries.concat([iso]);
    update();
  }
  function flash(e) { e.classList.remove("snap-flash"); void e.offsetWidth; e.classList.add("snap-flash"); }

  // the type-ahead search: Enter or a click shows the country, "+ Compare" (or Shift+Enter) adds it
  function search() {
    var input = $("snap-search"), list = $("snap-suggest"), hits = [], active = 0;
    function norm(s) { return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }
    var all = db.countries.map(function (c) {
      return { iso3: c.iso3, name: c.name, group: c.group,
               key: norm(c.name + " " + c.iso3 + " " + (db.imf_names[c.iso3] || "") + (c.group ? " group" : "")) };
    }).sort(function (a, b) { return a.name.localeCompare(b.name); });
    function render() {
      list.innerHTML = "";
      list.hidden = !hits.length;
      input.setAttribute("aria-expanded", String(!!hits.length));
      hits.forEach(function (h, i) {
        var li = el("li", i === active ? "snap-active" : null);
        li.setAttribute("role", "option");
        li.id = "snap-opt-" + i;
        var go = el("button", "snap-go");
        go.type = "button";
        go.innerHTML = esc(h.name) + ' <span class="snap-iso">' + (h.group ? "group · " : "") + h.iso3 + "</span>";
        go.addEventListener("mousedown", function (e) { e.preventDefault(); pick(h, false); });
        var plus = el("button", "snap-plus", "+ Compare");
        plus.type = "button";
        plus.title = "Add " + h.name + " to the charts";
        plus.addEventListener("mousedown", function (e) { e.preventDefault(); pick(h, true); });
        li.appendChild(go);
        li.appendChild(plus);
        list.appendChild(li);
      });
      if (hits.length) input.setAttribute("aria-activedescendant", "snap-opt-" + active);
    }
    function pick(h, compare) {
      input.value = "";
      hits = [];
      render();
      if (compare) add(h.iso3); else show(h.iso3);
    }
    input.addEventListener("input", function () {
      var t = norm(input.value.trim());
      active = 0;
      hits = !t ? [] : all.filter(function (c) { return c.key.indexOf(t) >= 0; }).sort(function (a, b) {
        return (norm(a.name).indexOf(t) === 0 ? 0 : 1) - (norm(b.name).indexOf(t) === 0 ? 0 : 1);
      }).slice(0, 8);
      render();
    });
    input.addEventListener("keydown", function (e) {
      if (!hits.length) return;
      if (e.key === "ArrowDown") { active = (active + 1) % hits.length; render(); e.preventDefault(); }
      else if (e.key === "ArrowUp") { active = (active + hits.length - 1) % hits.length; render(); e.preventDefault(); }
      else if (e.key === "Enter") { pick(hits[active], e.shiftKey); e.preventDefault(); }
      else if (e.key === "Escape") { hits = []; render(); }
    });
    input.addEventListener("blur", function () { setTimeout(function () { hits = []; render(); }, 150); });
  }

  function controls() {
    var groups = db.countries.filter(function (c) { return c.group; });
    var countries = db.countries.filter(function (c) { return !c.group; })
      .sort(function (a, b) { return a.name.localeCompare(b.name); });
    // the benchmark menu: the US, no line, then any group or country
    var sel = $("snap-bench");
    [["USA", "United States"], ["NONE", "None (no reference line)"]].forEach(function (o) {
      var opt = el("option", null, o[1]);
      opt.value = o[0];
      sel.appendChild(opt);
    });
    [["WEO groups", groups], ["Any country", countries]].forEach(function (g) {
      var og = el("optgroup");
      og.label = g[0];
      g[1].forEach(function (c) {
        if (c.iso3 === "USA") return;
        var opt = el("option", null, c.name);
        opt.value = c.iso3;
        og.appendChild(opt);
      });
      sel.appendChild(og);
    });
    sel.addEventListener("change", function () { state.bench = sel.value; update(); });
    $("snap-proj").addEventListener("change", function () { state.proj = $("snap-proj").checked; update(); });

    // the years: two range inputs on one track
    ["snap-y0", "snap-y1"].forEach(function (id, k) {
      var r = $(id);
      r.min = db.first;
      r.max = db.last;
      r.step = 1;
      r.addEventListener("input", function () {
        var a = +$("snap-y0").value, b = +$("snap-y1").value;
        if (b - a < 5) { if (k === 0) a = b - 5; else b = a + 5; }
        state.start = Math.max(db.first, a);
        state.end = Math.min(db.last, b);
        if (state.end - state.start < 5) { state.start = state.end - 5; }
        years();
      });
      r.addEventListener("change", function () { update(); });
    });

    $("snap-csv").addEventListener("click", function () {
      var url = URL.createObjectURL(new Blob([weo.csv(state)], { type: "text/csv" }));
      download("weo-snapshots_" + state.countries.join("-") + "_" + state.start + "-" + state.end + ".csv", url);
      setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
    });
    $("snap-share").addEventListener("click", function () {
      copyText(location.href.split("#")[0] + "#" + weo.format(state), $("snap-share"));
    });
    $("snap-reset").addEventListener("click", function () {
      state = weo.defaults(state.countries[0]);
      update();
    });

    // the quick links and the index of all countries and groups
    function link(c) {
      var a = el("a", null, c.name);
      a.href = "#c=" + c.iso3;
      a.dataset.iso = c.iso3;
      return a;
    }
    var byIso = {};
    db.countries.forEach(function (c) { byIso[c.iso3] = c; });
    var quick = $("snap-quick");
    JSON.parse(document.getElementById("snap-quicklinks").textContent).forEach(function (row, k) {
      if (k) quick.appendChild(el("span", "snap-sep", "/"));
      row.forEach(function (iso) {
        if (iso && iso.c) {                          // a comparison: {label, c: [iso3, ...]}
          var cmp = el("a", "snap-qlink", iso.label);
          cmp.href = "#c=" + iso.c.join(",");
          cmp.title = iso.c.map(function (x) { return byIso[x] ? byIso[x].name : x; }).join(", ");
          quick.appendChild(cmp);
          return;
        }
        if (!byIso[iso]) return;
        var a = link({ iso3: iso, name: byIso[iso].group ? byIso[iso].name : iso });
        a.title = byIso[iso].name;
        a.className = "snap-qlink";
        quick.appendChild(a);
      });
    });
    var ggrid = $("snap-index-groups");
    groups.forEach(function (c) { var li = el("li"); li.appendChild(link(c)); ggrid.appendChild(li); });
    var grid = $("snap-index-grid");
    countries.forEach(function (c) { var li = el("li"); li.appendChild(link(c)); grid.appendChild(li); });
    // links to a state (#c=...): the quick links, the index, the Explore questions
    document.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a[href^='#c=']");
      if (!a) return;
      e.preventDefault();
      e.stopPropagation();
      state = weo.parse(a.getAttribute("href"), state.countries[0]);
      update();
      var idx = $("snap-index");
      if (idx && idx.contains(a)) idx.open = false;
      scrollToSnapshot();
    }, true);
    window.addEventListener("hashchange", function () {
      var h = location.hash.replace(/^#/, "");
      if (!h || h === weo.format(state)) return;
      state = weo.parse(h, state.countries[0]);
      update();
    });
  }
  // after the page's load event (the browser and Quarto set the scroll position until then), and once more
  // when late layout (fonts, the table of contents) has settled
  function afterLoad() {
    function go() { scrollToSnapshot("auto"); setTimeout(function () { scrollToSnapshot("auto"); }, 300); }
    if (document.readyState === "complete") go(); else window.addEventListener("load", go, { once: true });
  }
  function scrollToSnapshot(behavior) {
    var top = state.focus ? cards[state.focus].card : $("snap-heading");
    top.scrollIntoView({ behavior: behavior || "smooth", block: "start" });
  }

  // ---- start ----------------------------------------------------------------------------------------
  function start(data) {
    db = data;
    weo = new WeoCore.Weo(db, panels, { benchmark: root.dataset.benchmark || "USA" });
    state = weo.parse(location.hash, root.dataset.default || "USA");
    var whole = codeBox("Show the Python code for the whole snapshot", function () { return weo.snapshotCode(state); });
    whole.id = "snap-whole";
    $("snap-wholebox").appendChild(whole);
    buildPanels();
    controls();
    search();
    root.classList.remove("snap-loading");
    $("snap-status").textContent = "";
    // a link to a view (from a chapter or a shared link) opens on its snapshot, once every chart is drawn
    scrollWhenDrawn = state.focus || /^#c=/.test(location.hash);
    update();
  }
  fetch(root.dataset.src).then(function (r) {
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
  }).then(start).catch(function (e) {
    $("snap-status").textContent = "The data could not be loaded (" + e.message + "). Reload the page to try again.";
  });
})();
