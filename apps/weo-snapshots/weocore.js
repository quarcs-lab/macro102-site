/* weocore.js — the WEO Snapshots logic, with no DOM: state and URL, the charts, the table and the Python code.
   Generated into macro102-site/apps/weo-snapshots/ by /write-weo-snapshots (do not edit there).
   The page (app.js) and the tests (check_code.cjs, in Node) share it, so the code a reader copies is
   checked against the very charts the page draws. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.WeoCore = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  // ---- constants --------------------------------------------------------------------------------
  var BLUE = "#16528c", GREEN = "#7fb23a", ORANGE = "#c4651a", GRAY = "#8a96a3";
  // one color per compared country (all have hand-picked dark versions in plotly-theme.html)
  var COMPARE = [BLUE, ORANGE, "#008070", "#8e5ea2", "#e0a33b"];
  var MAX_COUNTRIES = COMPARE.length;
  var NONE = "NONE";                                     // no reference line
  var PROJ = "IMF projection";
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
  function Weo(db, panels, defaults) {
    this.db = db;
    this.panels = panels;
    this.byId = {};
    this.defaultBench = (defaults && defaults.benchmark) || "USA";
    var self = this;
    panels.forEach(function (p) { self.byId[p.id] = p; });
    this.names = {};
    this.groups = {};
    db.countries.forEach(function (c) { self.names[c.iso3] = c.name; if (c.group) self.groups[c.iso3] = true; });
  }

  Weo.prototype.years = function (st) {
    var out = [];
    for (var y = st.start; y <= st.end; y++) out.push(y);
    return out;
  };
  Weo.prototype.lastActual = function (iso, v) {
    var l = (this.db.last_actual[iso] || {})[v];
    return l === undefined ? null : l;
  };
  // the values of one variable over [start, end] (numbers and nulls), without the projections if they are
  // switched off
  Weo.prototype.column = function (iso, v, st) {
    var all = (this.db.data[iso] || {})[v], first = this.db.first, la = this.lastActual(iso, v);
    return this.years(st).map(function (y) {
      var x = all ? all[y - first] : null;
      if (x === undefined || x === null) return null;
      return !st.proj && la !== null && y > la ? null : x;
    });
  };
  // the latest actual value of a variable (over all years), with its year
  Weo.prototype.latest = function (iso, v, st) {
    var all = (this.db.data[iso] || {})[v], la = this.lastActual(iso, v);
    if (!all) return null;
    var hi = Math.min(st ? st.end : this.db.last, la === null ? this.db.last : la) - this.db.first;
    var lo = st ? st.start - this.db.first : 0;
    for (var i = hi; i >= lo; i--) if (all[i] !== null && all[i] !== undefined) return { value: all[i], year: this.db.first + i };
    return null;
  };
  Weo.prototype.value = function (iso, v, year) {
    var all = (this.db.data[iso] || {})[v];
    var x = all ? all[year - this.db.first] : null;
    return x === undefined ? null : x;
  };
  Weo.prototype.name = function (iso) { return this.names[iso] || iso; };
  Weo.prototype.isGroup = function (iso) { return !!this.groups[iso]; };

  // ---- state and URL ----------------------------------------------------------------------------
  // state = {countries: [code...], bench: code | "NONE", start, end, proj: bool, show: {panel: 0|1},
  //          focus: panel id or null}
  Weo.prototype.defaults = function (iso) {
    return { countries: [iso], bench: this.defaultBench, start: this.db.first, end: this.db.last, proj: true,
             show: {}, focus: null };
  };
  Weo.prototype.parse = function (text, fallback) {
    var self = this, st = this.defaults(fallback);
    text = String(text || "").replace(/^[#?]/, "");
    if (!text) return st;
    if (/^[A-Za-z0-9]{3,6}$/.test(text) && this.db.data[text.toUpperCase()]) text = "c=" + text;   // #KOR
    text.split("&").forEach(function (part) {
      var kv = part.split("="), k = kv[0], v = decodeURIComponent(kv.slice(1).join("=") || "");
      if (k === "c") {
        var list = v.toUpperCase().split(",").filter(function (c) { return self.db.data[c]; });
        list = list.filter(function (c, i) { return list.indexOf(c) === i; }).slice(0, MAX_COUNTRIES);
        if (list.length) st.countries = list;
      } else if (k === "b") {
        v = v.toUpperCase();
        if (v === NONE || self.db.data[v]) st.bench = v;
      } else if (k === "y") {
        var m = v.match(/^(\d{4})-(\d{4})$/);
        if (m) {
          var a = Math.max(self.db.first, +m[1]), b = Math.min(self.db.last, +m[2]);
          if (a < b) { st.start = a; st.end = b; }
        }
      } else if (k === "f") {
        st.proj = v !== "0";
      } else if (k === "s") {
        v.split(",").forEach(function (pair) {
          var q = pair.split(":"), id = q[0];
          if (self.byId[id] && self.byId[id].series.length > 1) st.show[id] = q[1] === "1" ? 1 : 0;
        });
      } else if (k === "p" && self.byId[v]) {
        st.focus = v;
      }
    });
    return st;
  };
  Weo.prototype.format = function (st) {
    var parts = ["c=" + st.countries.join(",")];
    if (st.bench !== this.defaultBench) parts.push("b=" + st.bench);
    if (st.start !== this.db.first || st.end !== this.db.last) parts.push("y=" + st.start + "-" + st.end);
    if (!st.proj) parts.push("f=0");
    var show = Object.keys(st.show).filter(function (id) { return st.show[id] === 1; });
    if (show.length) parts.push("s=" + show.map(function (id) { return id + ":1"; }).join(","));
    if (st.focus) parts.push("p=" + st.focus);
    return parts.join("&");
  };

  // ---- what a panel shows -----------------------------------------------------------------------
  // the reference line: the benchmark, unless there is none or it is one of the countries shown
  Weo.prototype.reference = function (st) {
    return st.bench !== NONE && st.countries.indexOf(st.bench) < 0 ? st.bench : null;
  };
  // the series drawn: all of them for one country, the chosen one when comparing
  Weo.prototype.seriesShown = function (p, st) {
    if (st.countries.length === 1) return p.series.map(function (s, i) { return i; });
    return [p.series.length > 1 && st.show[p.id] === 1 ? 1 : 0];
  };
  Weo.prototype.unit = function (p, i) { return i === 1 && p.axis2 ? p.axis2 : p.unit; };
  // the recessions (years when the first country's real GDP fell) and the first projected year of its real
  // GDP growth, over the years shown: the gray bands of every chart
  Weo.prototype.bands = function (st) {
    var iso = st.countries[0], g = this.column(iso, "growth", st), x = this.years(st), la = this.lastActual(iso, "growth");
    var rec = x.filter(function (y, k) { return g[k] !== null && g[k] < 0; });
    var proj = st.proj ? x.filter(function (y, k) { return g[k] !== null && la !== null && y > la; }) : [];
    return { recessions: rec, projection: proj.length ? proj[0] : null };
  };
  // the mean of the first country's real GDP growth over the years shown (the growth panel's dashed line)
  Weo.prototype.average = function (iso, st) {
    var g = this.column(iso, "growth", st).filter(function (v) { return v !== null; });
    if (!g.length) return null;
    return g.reduce(function (a, b) { return a + b; }, 0) / g.length;
  };
  function fmt(v, d) {
    if (v === null || v === undefined || !isFinite(v)) return "n/a";
    return v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  Weo.prototype.fmt = fmt;
  Weo.prototype.latestText = function (iso, s, st) {
    var l = this.latest(iso, s.var, st);
    return l ? fmt(l.value, s.decimals) + " in " + l.year : "n/a";
  };

  // one line split in its actual part (solid) and its projected part (dotted). The projected part starts at
  // the last actual year, so the two parts join (the Python code repeats that row the same way).
  Weo.prototype.parts = function (iso, v, st) {
    var y = this.column(iso, v, st), x = this.years(st), la = this.lastActual(iso, v);
    var actual = y.map(function (val, k) { return la === null || x[k] <= la ? val : null; });
    var proj = y.map(function (val, k) { return st.proj && la !== null && x[k] >= la ? val : null; });
    return { x: x, actual: actual, proj: proj };
  };

  // ---- the chart --------------------------------------------------------------------------------
  // -> {data, layout, title, unit, empty}: a Plotly figure plus the panel's title (with the latest actual
  //    values) and unit line for the card header.
  Weo.prototype.figure = function (p, st) {
    var self = this, single = st.countries.length === 1, shown = this.seriesShown(p, st);
    var traces = [], shapes = [], annotations = [], titleParts = [];
    var dual = single && p.axis2 && p.series.length > 1;
    function line(iso, v, name, color, width, axis, hoverName) {
      var parts = self.parts(iso, v, st), d = self.decimalsOf(v);
      [["actual", parts.actual, "solid"], [PROJ, parts.proj, "dot"]].forEach(function (q, k) {
        traces.push({
          type: "scatter", mode: "lines", x: parts.x, y: q[1], name: name, legendgroup: name,
          showlegend: k === 0, yaxis: axis || "y",
          line: { color: color, width: width, dash: q[2] }, connectgaps: false,
          hovertemplate: "%{y:,." + d + "f}<extra>" + hoverName + (k ? " (IMF projection)" : "") + "</extra>"
        });
      });
    }
    if (single) {
      var iso = st.countries[0];
      shown.forEach(function (i) {
        var s = p.series[i];
        line(iso, s.var, s.label, i === 0 ? BLUE : dual ? ORANGE : GREEN, 2.2, dual && i === 1 ? "y2" : "y", s.label);
        titleParts.push(s.label + " (" + self.latestText(iso, s, st) + ")");
      });
      if (p.average) {
        var avg = this.average(iso, st);
        titleParts = [p.series[0].label + " (average is " + fmt(avg, 1) + ")"];
        if (avg !== null) shapes.push(hline(avg, GREEN, "dash"));
      }
    } else {
      var s0 = p.series[shown[0]];
      st.countries.forEach(function (iso, k) {
        line(iso, s0.var, self.name(iso) + " (" + self.latestText(iso, s0, st) + ")", COMPARE[k % COMPARE.length], 2.2,
             "y", self.name(iso));
      });
      titleParts.push(s0.label);
    }
    // the gray reference line: the benchmark's first series shown, actual and projected years together
    var ref = this.reference(st);
    if (ref) {
      var rv = p.series[shown[0]].var;
      traces.push({
        type: "scatter", mode: "lines", x: this.years(st), y: this.column(ref, rv, st), name: this.name(ref),
        line: { color: GRAY, width: 1.6 }, connectgaps: false,
        hovertemplate: "%{y:,." + this.decimalsOf(rv) + "f}<extra>" + this.name(ref) + "</extra>"
      });
    }
    if (p.zero) shapes.push(hline(0, GRAY, "dot"));
    var bands = this.bands(st);
    bands.recessions.forEach(function (y) { shapes.push(band(y - 0.5, y + 0.5, 0.18)); });
    if (bands.projection !== null) {
      shapes.push(band(bands.projection - 0.5, st.end + 0.5, 0.08));
      annotations.push({ text: "IMF projections", showarrow: false, xref: "x", yref: "paper",
                         x: st.end + 0.5, xanchor: "right", y: 1, yanchor: "top",
                         font: { size: 10, color: GRAY } });
    }
    var main = traces.filter(function (t) { return t.line.color !== GRAY; });
    var empty = main.every(function (t) { return t.y.every(function (v) { return v === null; }); });
    var logAxis = shown.length === 1 && p.series[shown[0]].log;
    var layout = {
      template: TEMPLATE, height: 330, autosize: true,
      margin: { l: 10, r: dual ? 10 : 16, t: traces.length > 2 ? 34 : 12, b: 36 },
      font: { family: FONT, size: 12 },
      hovermode: "x unified",
      showlegend: traces.length > 2,
      legend: { orientation: "h", x: 0, xanchor: "left", y: 1.02, yanchor: "bottom", font: { size: 11 } },
      xaxis: { range: [st.start - 0.5, st.end + 0.5], showgrid: false, fixedrange: false },
      // the unit is in the card header; only a two-axis chart names its axes (one series each)
      yaxis: { title: { text: dual ? p.series[0].label : "", font: { size: 11 } }, type: logAxis ? "log" : "linear" },
      shapes: shapes, annotations: annotations
    };
    if (dual) {
      layout.yaxis.title.font.color = BLUE;
      layout.yaxis.tickfont = { color: BLUE };
      layout.yaxis2 = { title: { text: p.series[1].label, font: { size: 11, color: ORANGE } }, tickfont: { color: ORANGE },
                        overlaying: "y", side: "right", showgrid: false, automargin: true,
                        type: p.series[1].log ? "log" : "linear" };
    }
    if (empty) {
      layout.annotations = [{ text: this.emptyText(p, st), showarrow: false, xref: "paper", yref: "paper",
                              x: 0.5, y: 0.5, font: { size: 13, color: GRAY } }];
      layout.shapes = [];
      layout.yaxis.type = "linear";
      layout.yaxis.showticklabels = false;
    }
    var units = shown.map(function (i) { return self.unit(p, i); });
    var unitLine = units.filter(function (u, k) { return units.indexOf(u) === k; }).join(" · ");
    if (logAxis || (dual && p.series[1].log)) unitLine += " · ratio scale" + (dual ? " (right)" : "");
    return { data: traces, layout: layout, title: single ? titleParts.join(" and ") : titleParts[0], unit: unitLine, empty: empty };
  };
  Weo.prototype.decimalsOf = function (v) {
    for (var i = 0; i < this.panels.length; i++)
      for (var j = 0; j < this.panels[i].series.length; j++)
        if (this.panels[i].series[j].var === v) return this.panels[i].series[j].decimals;
    return 1;
  };
  Weo.prototype.emptyText = function (p, st) {
    var self = this, who = st.countries.map(function (c) { return self.name(c); }).join(", ");
    return "No " + p.title.toLowerCase() + " data for " + who + " in " + st.start + "–" + st.end;
  };
  function hline(y, color, dash) {
    return { type: "line", xref: "paper", x0: 0, x1: 1, yref: "y", y0: y, y1: y,
             line: { color: color, width: 1.5, dash: dash } };
  }
  function band(x0, x1, opacity) {
    return { type: "rect", xref: "x", x0: x0, x1: x1, yref: "paper", y0: 0, y1: 1, fillcolor: GRAY,
             opacity: opacity, line: { width: 0 }, layer: "below" };
  }

  // ---- the latest-values table ------------------------------------------------------------------
  // -> {years: [last actual, current year, next year], rows: [{panel, label, unit, cells: [[{text, proj}...]
  //    per country]}]}: each panel's main series, its latest actual value and the IMF's numbers for this year
  //    and next
  Weo.prototype.table = function (st) {
    var self = this, y0 = this.db.vintage.year, years = st.proj ? [y0, y0 + 1] : [];
    var rows = [];
    this.panels.forEach(function (p, k) {
      [p.series[0]].forEach(function (s, i) {
        rows.push({
          panel: k + 1, id: p.id, label: s.label, unit: self.unit(p, i),
          cells: st.countries.map(function (iso) {
            var l = self.latest(iso, s.var), la = self.lastActual(iso, s.var);
            var out = [{ text: l ? fmt(l.value, s.decimals) : "–", year: l ? l.year : null, proj: false }];
            years.forEach(function (y) {
              var v = self.value(iso, s.var, y);
              out.push({ text: v === null ? "–" : fmt(v, s.decimals), proj: v !== null && la !== null && y > la });
            });
            return out;
          })
        });
      });
    });
    return { years: years, rows: rows };
  };

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
  function pxLine(target, frame, args) {
    var lines = [target + " = px.line(", "    " + frame + ","];
    args.forEach(function (a) {
      if (typeof a === "string") { lines.push("    " + a + ","); return; }
      var items = a[1].map(function (kv) { return q(kv[0]) + ": " + (kv[2] ? kv[1] : q(kv[1])); });
      var one = "    " + a[0] + "={" + items.join(", ") + "},";
      if (one.length <= 88) { lines.push(one); return; }
      lines.push("    " + a[0] + "={");
      items.forEach(function (it) { lines.push("        " + it + ","); });
      lines.push("    },");
    });
    return lines.concat([")"]).join("\n");
  }
  var ORDER = ["category_orders", [["status", '["actual", "' + PROJ + '"]', true]]];

  // the steps of one panel: [{comment, code}] (numbered by the caller)
  Weo.prototype.panelSteps = function (p, st) {
    var single = st.countries.length === 1, shown = this.seriesShown(p, st);
    var vars = shown.map(function (i) { return p.series[i].var; });
    var dual = single && p.axis2 && vars.length > 1, ref = this.reference(st);
    var tail = (ref ? "add_reference(fig, " + q(vars[0]) + ")\n" : "") + "shade(fig)\nfig.show()";
    var steps = [];
    if (dual) {
      var s0 = p.series[0], s1 = p.series[1];
      steps.push({ comment: "draw " + s0.label + ", then add " + s1.label + " on a second y-axis " +
                            "(dotted: IMF projections)",
                   code: "rows = pick(" + list(vars) + ")\n" +
                         pxLine("fig", "rows[rows[\"variable\"] == " + q(s0.var) + "]", ["x=\"year\"", "y=\"value\"",
                           "line_dash=\"status\"", ORDER, "title=" + q(p.title),
                           ["labels", [["value", this.unit(p, 0)], ["status", ""]]]]) + "\n" +
                         pxLine("right", "rows[rows[\"variable\"] == " + q(s1.var) + "]", ["x=\"year\"", "y=\"value\"",
                           "line_dash=\"status\"", ORDER]) + "\n" +
                         "right.update_traces(yaxis=\"y2\", line_color=\"" + ORANGE + "\", showlegend=False)\n" +
                         "fig.add_traces(right.data)\n" +
                         "fig.update_layout(\n    yaxis2=dict(\n        title=" + q(s1.label) + ",\n" +
                         "        overlaying=\"y\",\n        side=\"right\",\n" +
                         (s1.log ? "        type=\"log\",\n" : "") + "    ),\n)\n" + tail });
      return steps;
    }
    var title = single ? p.title : p.series[shown[0]].label;
    var args = ["x=\"year\"", "y=\"value\"", single && vars.length > 1 ? "color=\"variable\"" : null,
                single ? null : "color=\"country\"", "line_dash=\"status\"", ORDER,
                p.series[shown[0]].log ? "log_y=True" : null].filter(Boolean);
    var code = "rows = pick(" + list(vars) + ")\n";
    if (single && p.average) {
      steps.push({ comment: "the average growth rate over the years shown (the mean of the yearly rates)",
                   code: "avg = growth[\"value\"].mean()" });
      args.push("title=f\"" + p.title + " (average is {avg:.1f})\"");
      args.push(["labels", [["value", this.unit(p, 0)], ["status", ""]]]);
      steps.push({ comment: "draw the yearly growth rates (dotted: IMF projections) and their average (dashed)",
                   code: code + pxLine("fig", "rows", args) + "\nfig.add_hline(y=avg, line_dash=\"dash\")\n" + tail });
      return steps;
    }
    args.push("title=" + q(title));
    args.push(["labels", [["value", this.unit(p, shown[0])], ["status", ""]].concat(
      single && vars.length > 1 ? [["variable", ""]] : [])]);
    steps.push({ comment: "draw " + (single ? (vars.length > 1 ? "the two series" : "the chart") : "one line per country") +
                          " (dotted: IMF projections)" + (ref ? ", with the benchmark in gray" : ""),
                 code: code + pxLine("fig", "rows", args) + "\n" + tail });
    return steps;
  };

  // the shared steps 1-4 (reading the data, the choices, the rows kept, the helpers)
  Weo.prototype.header = function (st, panels, title) {
    var self = this, ref = this.reference(st);
    var who = st.countries.map(function (c) { return self.name(c); }).join(", ");
    var out = [comment("WEO Snapshots: " + title),
               "# Data: IMF World Economic Outlook (" + this.db.vintage.name + "), prepared for the book",
               "# \"Data Science and Macroeconomic Models\"",
               "import pandas as pd", "import plotly.express as px", "",
               "# Step 1: read the data (one row per country, year and variable)",
               "URL = (\"https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/\"",
               "       \"data/snapshots/weo_snapshots.csv\")",
               "df = pd.read_csv(URL)", "",
               "# Step 2: your choices (change them and run the cell again)",
               comment("(" + who + ")"),
               "# three-letter country codes, or WEO group codes (G001 = World)",
               "COUNTRIES = " + list(st.countries)];
    if (ref) out.push("BENCHMARK = " + q(ref) + "  # the gray reference line: any country or group code");
    out.push("START, END = " + st.start + ", " + st.end + "  # first and last year",
             "SHOW_PROJECTIONS = " + (st.proj ? "True" : "False") + "  # False hides the IMF projections", "",
             "# Step 3: keep the chosen years (and drop the projections if you hide them)",
             "data = df[df[\"year\"].between(START, END)]",
             "if not SHOW_PROJECTIONS:",
             "    data = data[data[\"status\"] == \"actual\"]", "",
             "# Step 4: the helpers that every chart uses",
             "def pick(variables):",
             "    \"\"\"The rows of these variables for the chosen countries.",
             "",
             "    The last actual year is repeated as a projection, so that the solid (actual)",
             "    and dotted (projected) parts of each line join.",
             "    \"\"\"",
             "    rows = data[data[\"iso3\"].isin(COUNTRIES) & data[\"variable\"].isin(variables)]",
             "    if SHOW_PROJECTIONS:",
             "        edge = rows[rows[\"year\"] == rows[\"last_actual\"]]",
             "        rows = pd.concat([rows, edge.assign(status=\"" + PROJ + "\")])",
             "    return rows.sort_values(\"year\")", "", "",
             "# the real GDP growth of the first country: its recessions (the years when GDP fell)",
             "# and the years the IMF projects",
             "growth = data[(data[\"iso3\"] == COUNTRIES[0]) & (data[\"variable\"] == \"growth\")]",
             "recessions = growth.loc[growth[\"value\"] < 0, \"year\"]",
             "projected = growth.loc[growth[\"status\"] != \"actual\", \"year\"]", "", "",
             "def shade(fig):",
             "    \"\"\"Gray bands: the recessions, and the years of IMF projections.\"\"\"",
             "    for year in recessions:",
             "        fig.add_vrect(x0=year - 0.5, x1=year + 0.5, fillcolor=\"gray\", opacity=0.18,",
             "                      line_width=0)",
             "    if len(projected):",
             "        fig.add_vrect(x0=projected.min() - 0.5, x1=END + 0.5, fillcolor=\"gray\",",
             "                      opacity=0.08, line_width=0, annotation_text=\"IMF projections\")");
    if (ref) {
      out.push("", "",
               "def add_reference(fig, variable):",
               "    \"\"\"Add the benchmark's line (gray) to a chart.\"\"\"",
               "    ref = data[(data[\"iso3\"] == BENCHMARK) & (data[\"variable\"] == variable)]",
               "    fig.add_scatter(x=ref[\"year\"], y=ref[\"value\"], name=BENCHMARK, line_color=\"gray\")");
    }
    return out.join("\n");
  };
  // the code of one panel, ready to paste into an empty Colab notebook
  Weo.prototype.panelCode = function (p, st) {
    var n = 4;
    return this.header(st, [p], p.title) + "\n\n\n" + this.panelSteps(p, st).map(function (s) {
      n += 1;
      return comment("Step " + n + ": " + s.comment) + "\n" + s.code;
    }).join("\n\n") + "\n";
  };
  // the code of the whole snapshot: steps 1-4 once, then every panel
  Weo.prototype.snapshotCode = function (st) {
    var self = this;
    var who = st.countries.map(function (c) { return self.name(c); }).join(", ");
    var blocks = this.panels.map(function (p, k) {
      var steps = self.panelSteps(p, st);
      return "# ---- Panel " + (k + 1) + ": " + p.title + " ----\n" + steps.map(function (s, j) {
        return comment((k + 1) + "." + (j + 1) + ": " + s.comment) + "\n" + s.code;
      }).join("\n\n");
    });
    return this.header(st, this.panels, who) + "\n\n\n" + blocks.join("\n\n") + "\n";
  };

  // ---- the CSV download (the rows of weo_snapshots.csv for the countries and years shown) ---------
  Weo.prototype.csv = function (st) {
    var self = this, x = this.years(st);
    var rows = ["iso3,country,year,variable,value,status,last_actual"];
    st.countries.forEach(function (iso) {
      var name = self.name(iso);
      if (/[",]/.test(name)) name = '"' + name.replace(/"/g, '""') + '"';
      self.db.variables.forEach(function (v) {
        var y = self.column(iso, v, st), la = self.lastActual(iso, v);
        x.forEach(function (year, k) {
          if (y[k] === null) return;
          rows.push([iso, name, year, v, y[k], la !== null && year > la ? PROJ : "actual", la].join(","));
        });
      });
    });
    return rows.join("\n") + "\n";
  };

  return { Weo: Weo, MAX_COUNTRIES: MAX_COUNTRIES, NONE: NONE, fmt: fmt };
});
