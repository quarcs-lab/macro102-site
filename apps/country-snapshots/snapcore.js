/* snapcore.js — the Country Snapshots logic, with no DOM: state and URL, the charts and the Python code.
   Generated into macro102-site/apps/country-snapshots/ by /write-country-snapshots (do not edit there).
   The page (app.js) and the tests (check_code.cjs, in Node) share it, so the code a reader copies is
   checked against the very charts the page draws. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.SnapCore = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  // ---- constants --------------------------------------------------------------------------------
  var BLUE = "#16528c", GREEN = "#7fb23a", ORANGE = "#c4651a", GRAY = "#8a96a3";
  // one color per compared country (all have hand-picked dark versions in plotly-theme.html)
  var COMPARE = [BLUE, ORANGE, "#008070", "#8e5ea2", "#e0a33b"];
  var MAX_COUNTRIES = COMPARE.length;
  var LEVELS = "LEV";
  var CSV_URL = "https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/" +
                "data/snapshots/country_snapshots.csv";
  var FONT = "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif";
  // the light look of the book's charts (plotly_white); plotly-theme.html recolors it in dark mode
  var RULE = "#ebf0f8";
  var TEMPLATE = { layout: {
    paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff", font: { color: "#2a3f5f", family: FONT, size: 12 },
    xaxis: { gridcolor: RULE, linecolor: RULE, zerolinecolor: RULE, ticks: "", automargin: true },
    yaxis: { gridcolor: RULE, linecolor: RULE, zerolinecolor: RULE, ticks: "", automargin: true },
    hoverlabel: { font: { family: FONT } }
  } };

  // ---- data access ------------------------------------------------------------------------------
  function Snap(db, panels) {
    this.db = db;
    this.panels = panels;
    this.byId = {};
    var self = this;
    panels.forEach(function (p) { self.byId[p.id] = p; });
    this.names = {};
    db.countries.forEach(function (c) { self.names[c.iso3] = c.name; });
    this.world = db.world.iso3;
  }

  Snap.prototype.years = function (state) {
    var out = [];
    for (var y = state.start; y <= state.end; y++) out.push(y);
    return out;
  };
  // the column of one country over [start, end] (an array of numbers and nulls; all nulls if absent)
  Snap.prototype.column = function (iso, col, state) {
    var all = (this.db.data[iso] || {})[col], first = this.db.first;
    return this.years(state).map(function (y) {
      var v = all ? all[y - first] : null;
      return v === undefined ? null : v;
    });
  };
  // the last value available of a column over all years (the "latest" benchmark), with its year
  Snap.prototype.latest = function (iso, col) {
    var all = (this.db.data[iso] || {})[col];
    if (!all) return null;
    for (var i = all.length - 1; i >= 0; i--) if (all[i] !== null) return { value: all[i], year: this.db.first + i };
    return null;
  };
  Snap.prototype.name = function (iso) { return this.names[iso] || iso; };

  // ---- state and URL ----------------------------------------------------------------------------
  // state = {countries: [iso3...], bench: iso3 | "WLD" | "LEV", start, end, show: {panel: 0|1}, log: {panel: bool},
  //          focus: panel id or null}
  Snap.prototype.defaults = function (iso) {
    return { countries: [iso], bench: "USA", start: this.db.first, end: this.db.last, show: {}, log: {}, focus: null };
  };
  Snap.prototype.parse = function (text, fallback) {
    var self = this, st = this.defaults(fallback);
    text = String(text || "").replace(/^[#?]/, "");
    if (!text) return st;
    if (/^[A-Za-z]{3}$/.test(text)) text = "c=" + text;          // #KOR
    text.split("&").forEach(function (part) {
      var kv = part.split("="), k = kv[0], v = decodeURIComponent(kv.slice(1).join("=") || "");
      if (k === "c") {
        var list = v.toUpperCase().split(",").filter(function (c) { return self.db.data[c] && c !== self.world; });
        list = list.filter(function (c, i) { return list.indexOf(c) === i; }).slice(0, MAX_COUNTRIES);
        if (list.length) st.countries = list;
      } else if (k === "b") {
        v = v.toUpperCase();
        if (v === LEVELS || self.db.data[v]) st.bench = v;
      } else if (k === "y") {
        var m = v.match(/^(\d{4})-(\d{4})$/);
        if (m) {
          var a = Math.max(self.db.first, +m[1]), b = Math.min(self.db.last, +m[2]);
          if (a < b) { st.start = a; st.end = b; }
        }
      } else if (k === "s" || k === "l") {
        v.split(",").forEach(function (pair) {
          var q = pair.split(":"), id = q[0];
          if (!self.byId[id]) return;
          if (k === "s" && self.byId[id].series.length > 1) st.show[id] = q[1] === "1" ? 1 : 0;
          if (k === "l") st.log[id] = q[1] !== "0";
        });
      } else if (k === "p" && self.byId[v]) {
        st.focus = v;
      }
    });
    return st;
  };
  Snap.prototype.format = function (st) {
    var self = this, parts = ["c=" + st.countries.join(",")];
    if (st.bench !== "USA") parts.push("b=" + st.bench);
    if (st.start !== this.db.first || st.end !== this.db.last) parts.push("y=" + st.start + "-" + st.end);
    var show = Object.keys(st.show).filter(function (id) { return st.show[id] === 1; });
    if (show.length) parts.push("s=" + show.map(function (id) { return id + ":1"; }).join(","));
    var log = Object.keys(st.log).filter(function (id) { return st.log[id] !== !!self.byId[id].log; });
    if (log.length) parts.push("l=" + log.map(function (id) { return id + ":" + (st.log[id] ? 1 : 0); }).join(","));
    if (st.focus) parts.push("p=" + st.focus);
    return parts.join("&");
  };

  // ---- what a panel shows -----------------------------------------------------------------------
  // The benchmark actually used: Levels when the only country shown is the benchmark itself (as Jones's
  // US page), else the reader's choice.
  Snap.prototype.bench = function (st) {
    return st.countries.length === 1 && st.countries[0] === st.bench ? LEVELS : st.bench;
  };
  Snap.prototype.isLog = function (p, st) { return st.log[p.id] === undefined ? !!p.log : st.log[p.id]; };
  // the series drawn: all of them for one country, the chosen one when comparing
  Snap.prototype.seriesShown = function (p, st) {
    if (st.countries.length === 1) return p.series.map(function (s, i) { return i; });
    return [p.series.length > 1 && st.show[p.id] === 1 ? 1 : 0];
  };
  Snap.prototype.relative = function (p, st) { return !!p.benchmark && this.bench(st) !== LEVELS; };
  // the column read for series i (Levels mode may read another one: TFP -> tfp_index)
  Snap.prototype.col = function (p, i, st) {
    var s = p.series[i];
    return p.benchmark && !this.relative(p, st) && p.levels && p.levels.col ? p.levels.col : s.col;
  };
  Snap.prototype.decimals = function (p, i, st) {
    return p.benchmark && !this.relative(p, st) && p.levels && p.levels.decimals != null ? p.levels.decimals
                                                                                         : p.series[i].decimals;
  };
  // the y-axis unit of series i, with the benchmark's name (and, for "latest", its year) filled in
  Snap.prototype.unit = function (p, i, st) {
    if (i === 1 && p.axis2) return p.axis2;
    if (p.benchmark && !this.relative(p, st)) return p.levels.unit;
    var b = this.bench(st), u = p.unit.replace("{B}", this.benchName(b));
    if (p.benchmark === "latest") {
      var l = this.latest(b, p.series[i].col);
      u = u.replace("{Y}", l ? l.year : this.db.last);
    }
    return u;
  };
  Snap.prototype.benchName = function (b) {
    return b === this.world ? this.db.world.name : this.name(b);
  };
  // the values of series i for country iso, as plotted
  Snap.prototype.values = function (p, i, iso, st) {
    var v = this.column(iso, this.col(p, i, st), st);
    if (!this.relative(p, st)) return v;
    var b = this.bench(st), col = p.series[i].col;
    if (p.benchmark === "same_year") {
      var w = this.column(b, col, st);
      return v.map(function (x, k) { return x === null || w[k] === null ? null : 100 * x / w[k]; });
    }
    var base = this.latest(b, col);
    return v.map(function (x) { return x === null || !base ? null : 100 * x / base.value; });
  };
  function lastValue(ys) {
    for (var i = ys.length - 1; i >= 0; i--) if (ys[i] !== null && isFinite(ys[i])) return ys[i];
    return null;
  }
  // the average annual growth rate of GDP per capita over the years shown: 100 ln(last/first) / years
  Snap.prototype.averageGrowth = function (iso, st) {
    var ys = this.column(iso, "gdp_pc", st), x = this.years(st), a = -1, b = -1;
    for (var i = 0; i < ys.length; i++) if (ys[i] !== null) { if (a < 0) a = i; b = i; }
    if (a < 0 || b <= a) return null;
    return 100 * Math.log(ys[b] / ys[a]) / (x[b] - x[a]);
  };
  function fmt(v, d) {
    if (v === null || v === undefined || !isFinite(v)) return "n/a";
    return v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  Snap.prototype.fmt = fmt;

  // ---- the chart --------------------------------------------------------------------------------
  // -> {data, layout, title, unit, empty}: a Plotly figure plus the panel's title (with the latest values,
  //    as Jones's titles) and unit line for the card header.
  Snap.prototype.figure = function (p, st) {
    var self = this, x = this.years(st), single = st.countries.length === 1, shown = this.seriesShown(p, st);
    var traces = [], shapes = [], titleParts = [];
    var dual = single && p.axis2 && p.series.length > 1;
    if (single) {
      var iso = st.countries[0];
      shown.forEach(function (i) {
        var y = self.values(p, i, iso, st), d = self.decimals(p, i, st);
        traces.push({
          type: "scatter", mode: "lines", x: x, y: y, name: p.series[i].label,
          yaxis: dual && i === 1 ? "y2" : "y",
          line: { color: i === 0 ? BLUE : dual ? ORANGE : GREEN, width: 2.2, dash: i === 0 ? "solid" : "dash" },
          hovertemplate: "%{y:,." + d + "f}<extra>" + p.series[i].label + "</extra>", connectgaps: false
        });
        titleParts.push(p.series[i].label + " (" + fmt(lastValue(y), d) + ")");
      });
      if (p.average) {
        var avg = this.averageGrowth(iso, st);
        titleParts = [p.series[0].label + " (average is " + fmt(avg, 2) + ")"];
        if (avg !== null) shapes.push(hline(avg, GREEN, "dash"));
      }
    } else {
      var i = shown[0], d = this.decimals(p, i, st);
      st.countries.forEach(function (iso, k) {
        var y = self.values(p, i, iso, st);
        var tag = p.average ? "avg " + fmt(self.averageGrowth(iso, st), 2) : fmt(lastValue(y), d);
        traces.push({
          type: "scatter", mode: "lines", x: x, y: y, name: self.name(iso) + " (" + tag + ")",
          line: { color: COMPARE[k % COMPARE.length], width: 2.2 },
          hovertemplate: "%{y:,." + d + "f}<extra>" + self.name(iso) + "</extra>", connectgaps: false
        });
      });
      titleParts.push(p.series[i].label);
    }
    if (p.zero) shapes.push(hline(0, GRAY, "dot"));
    var empty = traces.every(function (t) { return t.y.every(function (v) { return v === null; }); });
    var units = shown.map(function (i) { return self.unit(p, i, st); });
    var layout = {
      template: TEMPLATE, height: 330, autosize: true,
      margin: { l: 10, r: dual ? 10 : 16, t: traces.length > 1 ? 34 : 12, b: 36 },
      font: { family: FONT, size: 12 },
      hovermode: "x unified",
      showlegend: traces.length > 1,
      legend: { orientation: "h", x: 0, xanchor: "left", y: 1.02, yanchor: "bottom", font: { size: 11 } },
      xaxis: { range: [st.start - 0.5, st.end + 0.5], showgrid: false, fixedrange: false },
      // the unit is in the card header; only a two-axis chart names its axes (one series each)
      yaxis: { title: { text: dual ? p.series[0].label : "", font: { size: 11 } },
               type: this.isLog(p, st) ? "log" : "linear" },
      shapes: shapes, annotations: []
    };
    if (dual) {
      layout.yaxis.title.font.color = BLUE;
      layout.yaxis.tickfont = { color: BLUE };
      layout.yaxis2 = { title: { text: p.series[1].label, font: { size: 11, color: ORANGE } }, tickfont: { color: ORANGE },
                        overlaying: "y", side: "right", showgrid: false, automargin: true };
    }
    if (empty) {
      layout.annotations.push({ text: this.emptyText(p, st), showarrow: false, xref: "paper", yref: "paper",
                                x: 0.5, y: 0.5, font: { size: 13, color: GRAY } });
      layout.yaxis.type = "linear";
      layout.yaxis.showticklabels = false;
    }
    var title = single ? titleParts.join(" and ") : titleParts[0];
    var unitLine = units.filter(function (u, k) { return units.indexOf(u) === k; }).join(" · ");
    if (p.benchmark && this.bench(st) === LEVELS && st.bench !== LEVELS)
      unitLine += " (levels: " + this.name(st.countries[0]) + " is the benchmark)";
    return { data: traces, layout: layout, title: title, unit: unitLine, empty: empty };
  };
  Snap.prototype.emptyText = function (p, st) {
    var self = this, rel = this.relative(p, st), b = this.bench(st);
    if (rel && !this.column(b, p.series[0].col, { start: this.db.first, end: this.db.last })
                    .some(function (v) { return v !== null; }))
      return "No " + p.title.toLowerCase() + " data for the benchmark (" + this.benchName(b) + ")";
    var who = st.countries.map(function (c) { return self.name(c); }).join(", ");
    return "No data for " + who + " in " + st.start + "–" + st.end;
  };
  function hline(y, color, dash) {
    return { type: "line", xref: "paper", x0: 0, x1: 1, yref: "y", y0: y, y1: y,
             line: { color: color, width: 1.5, dash: dash } };
  }

  // ---- the Python code --------------------------------------------------------------------------
  function q(s) { return '"' + String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"'; }
  function list(xs) { return "[" + xs.map(q).join(", ") + "]"; }
  // a comment wrapped at 88 characters
  function comment(text) {
    var lines = [], line = "#";
    String(text).split(" ").forEach(function (w) {
      if ((line + " " + w).length > 88 && line !== "#") { lines.push(line); line = "#"; }
      line += " " + w;
    });
    return lines.concat([line]).join("\n");
  }
  // a px.line call, one keyword argument per line (the book's style for long calls); an argument given as
  // [name, [[key, value]...]] is a dict, written on one line or, when that is too long, one item per line
  function pxLine(frame, args) {
    var lines = ["fig = px.line(", "    " + frame + ","];
    args.forEach(function (a) {
      if (typeof a === "string") { lines.push("    " + a + ","); return; }
      var items = a[1].map(function (kv) { return q(kv[0]) + ": " + q(kv[1]); });
      var one = "    " + a[0] + "={" + items.join(", ") + "},";
      if (one.length <= 88) { lines.push(one); return; }
      lines.push("    " + a[0] + "={");
      items.forEach(function (it) { lines.push("        " + it + ","); });
      lines.push("    },");
    });
    return lines.concat([")"]).join("\n");
  }

  // the steps of one panel: [{comment, code}] (numbered by the caller)
  Snap.prototype.panelSteps = function (p, st) {
    var self = this, single = st.countries.length === 1, shown = this.seriesShown(p, st);
    var cols = shown.map(function (i) { return self.col(p, i, st); });
    var rel = this.relative(p, st), steps = [], frame = "data";
    var title = single ? p.title : p.series[shown[0]].label;
    if (rel) {
      frame = p.id;
      var base = p.series.map(function (s) { return s.col; }).filter(function (c, k) { return shown.indexOf(k) >= 0; });
      if (p.benchmark === "same_year") {
        var lines = ["bench = df[df[\"iso3\"] == BENCHMARK][" + list(["year"].concat(base)) + "]",
                     frame + " = data.merge(bench, on=\"year\", suffixes=(\"\", \"_bench\"))"];
        base.forEach(function (c) {
          lines.push(frame + "[" + q(c) + "] = 100 * " + frame + "[" + q(c) + "] / " + frame + "[" + q(c + "_bench") + "]");
        });
        steps.push({ comment: "divide by the benchmark in the same year (benchmark = 100)", code: lines.join("\n") });
      } else {
        var c = base[0];
        steps.push({ comment: "divide by the benchmark's latest value (benchmark = 100); ffill() carries " +
                              "each value forward, so the last row holds the latest one",
                     code: "base = df[df[\"iso3\"] == BENCHMARK][" + q(c) + "].ffill().iloc[-1]\n" +
                           frame + " = data.assign(" + c + "=100 * data[" + q(c) + "] / base)" });
      }
    }
    var log = this.isLog(p, st) ? ["log_y=True"] : [];
    if (single && p.average) {
      steps.push({ comment: "the average annual growth rate between the first and the last year",
                   code: ["g = data.dropna(subset=[\"gdp_pc\"])",
                          "years = g[\"year\"].iloc[-1] - g[\"year\"].iloc[0]",
                          "avg = 100 * np.log(g[\"gdp_pc\"].iloc[-1] / g[\"gdp_pc\"].iloc[0]) / years"].join("\n") });
      steps.push({ comment: "draw the yearly growth rates and their average (dashed)",
                   code: pxLine(frame, ["x=\"year\"", "y=\"growth\""].concat(log, [
                           "title=f\"Growth rate of GDP per capita (average is {avg:.2f})\"",
                           ["labels", [["growth", this.unit(p, 0, st)]]]])) +
                         "\nfig.add_hline(y=avg, line_dash=\"dash\")\nfig.show()" });
      return steps;
    }
    if (single && p.axis2 && cols.length > 1) {
      steps.push({ comment: "draw " + p.series[0].label + ", then add " + p.series[1].label + " on a second y-axis",
                   code: pxLine(frame, ["x=\"year\"", "y=" + q(cols[0])].concat(log, [
                           "title=" + q(p.title),
                           ["labels", [[cols[0], this.unit(p, 0, st)]]]])) + "\n" +
                         "fig.add_scatter(\n    x=" + frame + "[\"year\"],\n    y=" + frame + "[" + q(cols[1]) + "],\n" +
                         "    name=" + q(p.series[1].label) + ",\n    yaxis=\"y2\",\n    line_dash=\"dash\",\n)\n" +
                         "fig.update_layout(\n    yaxis2=dict(title=" + q(p.series[1].label) +
                         ", overlaying=\"y\", side=\"right\"),\n)\nfig.show()" });
      return steps;
    }
    var args = ["x=\"year\""];
    if (cols.length > 1) {
      args.push("y=" + list(cols));
    } else {
      args.push("y=" + q(cols[0]));
    }
    if (!single) args.push("color=\"country\"");
    args = args.concat(log, ["title=" + q(title)]);
    args.push(cols.length > 1 ? ["labels", [["value", this.unit(p, shown[0], st)], ["variable", ""]]]
                              : ["labels", [[cols[0], this.unit(p, shown[0], st)]]]);
    steps.push({ comment: "draw " + (single ? "the chart" : "one line per country"),
                 code: pxLine(frame, args) + "\nfig.show()" });
    return steps;
  };

  // the shared steps 1-3 (reading the data, the choices, the rows kept)
  Snap.prototype.header = function (st, panels, title) {
    var self = this, rel = panels.some(function (p) { return self.relative(p, st); });
    var np = st.countries.length === 1 && panels.some(function (p) { return p.average; });
    var codes = st.countries.map(function (c) { return self.name(c); }).join(", ");
    var out = [comment("Country Snapshots: " + title),
               "# Data: Penn World Table 11.0, prepared for the book",
               "# \"Data Science and Macroeconomic Models\""];
    if (np) out.push("import numpy as np");
    out.push("import pandas as pd", "import plotly.express as px", "",
             "# Step 1: read the data (one row per country and year)",
             "URL = (\"https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/\"",
             "       \"data/snapshots/country_snapshots.csv\")",
             "df = pd.read_csv(URL)", "",
             "# Step 2: your choices (change them and run the cell again)",
             comment("(" + codes + ")"),
             "COUNTRIES = " + list(st.countries) + "  # three-letter country codes");
    if (rel) out.push("BENCHMARK = " + q(this.bench(st)) + "  # a country code, or \"WLD\" (World average)");
    out.push("START, END = " + st.start + ", " + st.end + "  # first and last year", "",
             "# Step 3: keep the chosen countries and years",
             "data = df[df[\"iso3\"].isin(COUNTRIES) & df[\"year\"].between(START, END)]");
    return out.join("\n");
  };
  // the code of one panel, ready to paste into an empty Colab notebook
  Snap.prototype.panelCode = function (p, st) {
    var n = 3;
    return this.header(st, [p], p.title) + "\n\n" + this.panelSteps(p, st).map(function (s) {
      n += 1;
      return comment("Step " + n + ": " + s.comment) + "\n" + s.code;
    }).join("\n\n") + "\n";
  };
  // the code of the whole snapshot: steps 1-3 once, then every panel
  Snap.prototype.snapshotCode = function (st) {
    var self = this;
    var who = st.countries.map(function (c) { return self.name(c); }).join(", ");
    var blocks = this.panels.map(function (p, k) {
      var steps = self.panelSteps(p, st);
      return "# ---- Panel " + (k + 1) + ": " + p.title + " ----\n" + steps.map(function (s, j) {
        return comment((k + 1) + "." + (j + 1) + ": " + s.comment) + "\n" + s.code;
      }).join("\n\n");
    });
    return this.header(st, this.panels, who) + "\n\n" + blocks.join("\n\n") + "\n";
  };

  // ---- the CSV download -------------------------------------------------------------------------
  Snap.prototype.csv = function (st) {
    var self = this, cols = this.db.columns, x = this.years(st);
    var rows = [["iso3", "country", "year"].concat(cols).join(",")];
    st.countries.forEach(function (iso) {
      var data = cols.map(function (c) { return self.column(iso, c, st); });
      x.forEach(function (y, k) {
        var name = self.name(iso);
        if (/[",]/.test(name)) name = '"' + name.replace(/"/g, '""') + '"';
        rows.push([iso, name, y].concat(data.map(function (d) { return d[k] === null ? "" : d[k]; })).join(","));
      });
    });
    return rows.join("\n") + "\n";
  };

  return { Snap: Snap, MAX_COUNTRIES: MAX_COUNTRIES, LEVELS: LEVELS, CSV_URL: CSV_URL, fmt: fmt };
});
