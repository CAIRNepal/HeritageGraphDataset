#!/usr/bin/env python3
"""PDF figures for the paper, written to docs/paper/figures/ (also run by tools/paper/stats.py).

  alignment_progress.pdf  SHACL results (log scale) and undeclared terms after each alignment step (S0 to B5) of
                          docs/sync/SYNC_LOG.md, as two panels on one step axis; step groups shaded and labelled
  monument_map.pdf        monuments with coordinates, by type group, over Nepal's province boundaries
                          (geoBoundaries NPL ADM1, tools/paper/data/SOURCE.md), with an inset of the Kathmandu Valley
  condition_by_type.pdf   condition per monument type as stacked horizontal bars (first condition value DANAM lists,
                          i.e. the value on the crm:E3_Condition_State, so each monument counts once)

Sized for one column (3.4 in wide), 7-8 pt text, no titles. Colours: categorical slots 1-3 (validated all-pairs for
colour-vision deficiency) plus grey for the map; status colours for condition. Each figure also uses a second channel
(marker shape, labels) so no information depends on colour alone.

Usage (standalone; builds the graph):
  uv run --no-project --with-requirements tools/sync/requirements.txt python tools/paper/figures.py
"""
import json
import math
import os
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon, Rectangle  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [REPO, os.path.join(REPO, "tests")]
BOUNDARIES = os.path.join(REPO, "tools", "paper", "data", "geoBoundaries-NPL-ADM1_simplified.geojson")
SYNC_LOG = os.path.join(REPO, "docs", "sync", "SYNC_LOG.md")

WIDTH = 3.4  # inches, one column
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]  # categorical slots 1-3
OTHER = "#a9a8a1"
STATUS = {"Good": "#0ca30c", "Restored": "#2a78d6", "Damaged": "#ec835a", "Ruined": "#d03b3b", "No status": "#d6d5ce"}

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 7.5, "axes.labelsize": 7.5, "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5, "legend.fontsize": 6.5, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "pdf.fonttype": 42, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
})


# ── alignment progress ────────────────────────────────────────────────────────────────────────────────────────────
def alignment_steps(log_path=SYNC_LOG):
    """(step, SHACL results, undeclared terms) for S0 and the alignment steps up to B5 (the F fixes are excluded)."""
    steps = []
    for block in re.split(r"\n(?=## )", open(log_path, encoding="utf-8").read()):
        mh = re.match(r"## (\S+): ", block)
        sh = re.search(r"SHACL results: (?:[\d,]+ → )?\*\*([\d,]+)\*\*", block)
        un = re.search(r"Undeclared terms: (?:[\d,]+ → )?\*\*([\d,]+)\*\*", block)
        if mh and sh and un:
            name = mh.group(1)
            if name.startswith("F"):
                break
            steps.append((name, int(sh.group(1).replace(",", "")), int(un.group(1).replace(",", ""))))
    return steps


def group_of(step):
    if step in ("S0",):
        return "start"
    if step == "B5":
        return "B5"
    return re.match(r"[A-Z]+", step).group(0)


def fig_alignment(path, log_path=SYNC_LOG):
    steps = alignment_steps(log_path)
    x = list(range(len(steps)))
    names = [s[0] for s in steps]
    fig, (a1, a2) = plt.subplots(2, 1, sharex=True, figsize=(WIDTH, 2.6),
                                 gridspec_kw={"height_ratios": [2, 1.15], "hspace": 0.12})
    # shaded step groups (alternating), labelled above the top panel
    groups = []
    for i, n in enumerate(names):
        g = group_of(n)
        if groups and groups[-1][0] == g:
            groups[-1][2] = i
        else:
            groups.append([g, i, i])
    label = {"A": "A: use the ontology's IRIs", "B": "B", "C": "C", "E": "E: extension terms",
             "V": "", "R": "", "S": "", "B5": "B5", "start": ""}
    for k, (g, i0, i1) in enumerate(groups):
        if g == "start":
            continue
        for ax in (a1, a2):
            ax.axvspan(i0 - 0.5, i1 + 0.5, color="#f0efec" if k % 2 else "#e6e5df", lw=0, zorder=0)
        if label.get(g):
            a1.text((i0 + i1) / 2, 1.02, label[g], transform=a1.get_xaxis_transform(), ha="center", va="bottom",
                    fontsize=6, color=INK2)
    a1.plot(x, [s[1] for s in steps], color=SERIES[0], lw=1.4, marker="o", ms=2.6, zorder=3)
    a1.set_yscale("log")
    a1.set_ylim(100, 200000)
    a1.set_ylabel("SHACL results")
    a2.step(x, [s[2] for s in steps], where="mid", color=SERIES[0], lw=1.4, zorder=3)
    a2.plot(x, [s[2] for s in steps], ls="none", marker="o", ms=2.6, color=SERIES[0], zorder=3)
    a2.set_ylim(-2, 40)
    a2.set_yticks([0, 10, 20, 30])
    a2.set_ylabel("Undeclared\nterms")
    for ax in (a1, a2):
        ax.grid(axis="y", color=GRID, lw=0.5, zorder=1)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(length=2)
    # direct labels at start and end
    a1.annotate(f"{steps[0][1]:,}", (0, steps[0][1]), xytext=(3, 4), textcoords="offset points", fontsize=6, color=INK2)
    a1.annotate(f"{steps[-1][1]:,}", (x[-1], steps[-1][1]), xytext=(-3, 5), textcoords="offset points", fontsize=6,
                color=INK2, ha="right")
    a2.annotate(f"{steps[0][2]}", (0, steps[0][2]), xytext=(2, -9), textcoords="offset points", fontsize=6, color=INK2)
    a2.annotate(f"{steps[-1][2]}", (x[-1], steps[-1][2]), xytext=(-3, 4), textcoords="offset points", fontsize=6,
                color=INK2, ha="right")
    a2.set_xticks(x)
    a2.set_xticklabels(names, rotation=90, fontsize=5.2)
    a2.set_xlim(-0.6, x[-1] + 0.6)
    a2.set_xlabel("Alignment step (docs/sync/SYNC\\_LOG.md)".replace("\\_", "_"))
    fig.savefig(path)
    plt.close(fig)
    return steps


# ── monument map ──────────────────────────────────────────────────────────────────────────────────────────────────
TYPE_GROUPS = [  # (label, classes) in priority order: a monastic building that is also a temple counts as Buddhist
    ("Buddhist monastery or caitya", ("BuddhistMonument", "Chaitya")),
    ("Rest house (pāṭī, sattal)", ("Pati", "Sattal")),
    ("Temple", ("Temple",)),
]
MARKERS = ["^", "s", "o"]


def monument_points(g):
    import build_kg
    from rdflib import RDF, Namespace
    HG, HGN, GEO = build_kg.HG, Namespace(build_kg.HGN_BASE), build_kg.GEO
    local = {HGN.BuddhistMonument: "BuddhistMonument"}
    pts = []
    for m in g.subjects(RDF.type, HG.ArchitecturalStructure):
        lat, lon = g.value(m, GEO.lat), g.value(m, GEO.long)
        if lat is None or lon is None:
            continue
        types = {local.get(t, str(t).rsplit("/", 1)[-1]) for t in g.objects(m, RDF.type)}
        grp = next((i for i, (_, cls) in enumerate(TYPE_GROUPS) if types & set(cls)), len(TYPE_GROUPS))
        pts.append((float(lon), float(lat), grp))
    return pts


def draw_provinces(ax, feats):
    for f in feats:
        geom = f["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            ax.add_patch(Polygon(poly[0], closed=True, facecolor="#f4f3ef", edgecolor=AXIS, lw=0.5, zorder=1))


def scatter_groups(ax, pts, size, edge, alpha=1.0):
    for grp in [len(TYPE_GROUPS)] + list(range(len(TYPE_GROUPS) - 1, -1, -1)):  # other first, then rarer on top
        sel = [(x, y) for x, y, gp in pts if gp == grp]
        if not sel:
            continue
        colour = OTHER if grp == len(TYPE_GROUPS) else SERIES[grp]
        marker = "." if grp == len(TYPE_GROUPS) else MARKERS[grp]
        ax.scatter([p[0] for p in sel], [p[1] for p in sel], s=size * (0.8 if marker == "." else 1), c=colour,
                   marker=marker, linewidths=edge, edgecolors="white", alpha=alpha, zorder=3)


def fig_map(path, g):
    pts = monument_points(g)
    feats = json.load(open(BOUNDARIES, encoding="utf-8"))["features"]
    fig, ax = plt.subplots(figsize=(WIDTH, 2.45))
    draw_provinces(ax, feats)
    scatter_groups(ax, pts, 7, 0.25)
    ax.set_xlim(80.0, 88.3)
    ax.set_ylim(24.9, 30.5)
    ax.set_aspect(1 / math.cos(math.radians(28)))
    ax.axis("off")
    # Kathmandu Valley inset (lower left, over India, where the map is empty)
    box = (85.25, 27.60, 85.50, 27.77)
    ax.add_patch(Rectangle((box[0], box[1]), box[2] - box[0], box[3] - box[1], fill=False, ec=INK2, lw=0.6, zorder=4))
    ins = ax.inset_axes([0.0, 0.0, 0.40, 0.42])
    draw_provinces(ins, feats)
    scatter_groups(ins, pts, 6, 0.0, alpha=0.8)
    ins.set_xlim(box[0], box[2])
    ins.set_ylim(box[1], box[3])
    ins.set_aspect(1 / math.cos(math.radians(27.68)))
    ins.set_xticks([])
    ins.set_yticks([])
    for s in ins.spines.values():
        s.set_edgecolor(INK2)
        s.set_linewidth(0.6)
    ins.text(0.03, 0.04, "Kathmandu Valley", transform=ins.transAxes, fontsize=6, color=INK2, zorder=5,
             bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.0, "alpha": 0.9})
    ax.indicate_inset_zoom(ins, edgecolor=INK2, lw=0.5, alpha=0.8)
    # legend with counts (top right, over the Tibetan plateau, where the map is empty)
    counts = [sum(1 for p in pts if p[2] == i) for i in range(len(TYPE_GROUPS) + 1)]
    handles = [plt.Line2D([], [], ls="none", marker=MARKERS[i], color=SERIES[i], ms=4, mec="white", mew=0.3,
                          label=f"{TYPE_GROUPS[i][0]} ({counts[i]:,})") for i in range(len(TYPE_GROUPS))]
    handles.append(plt.Line2D([], [], ls="none", marker="o", color=OTHER, ms=3, label=f"Other ({counts[-1]:,})"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2, frameon=False,
              handletextpad=0.2, columnspacing=1.0, borderaxespad=0.0, labelspacing=0.3, fontsize=6)
    fig.savefig(path)
    plt.close(fig)
    return counts


# ── condition by type ─────────────────────────────────────────────────────────────────────────────────────────────
COND_TYPES = [("Temple", "Temple"), ("Pati", "Pāṭī"), ("BuddhistMonument", "Monastic bldg."),
              ("DhungeDhara", "Water spout"), ("Sattal", "Sattal"), ("Chaitya", "Caitya")]


def condition_rows(g):
    import build_kg
    from rdflib import RDF, Namespace
    HG, CRM, HGN = build_kg.HG, build_kg.CRM, Namespace(build_kg.HGN_BASE)
    rows = []
    for key, label in COND_TYPES:
        cls = HGN.BuddhistMonument if key == "BuddhistMonument" else HG[key]
        counts = dict.fromkeys(STATUS, 0)
        ms = set(g.subjects(RDF.type, cls))
        for m in ms:
            st = [g.value(s, HG.hasConditionType) for a_ in g.objects(m, CRM.P34i_was_assessed_by)
                  for s in g.objects(a_, CRM.P35_has_identified)]
            st = [s for s in st if s is not None]
            counts[str(st[0]).split("#")[-1] if st else "No status"] += 1
        rows.append((label, len(ms), counts))
    return rows


def fig_condition(path, g):
    rows = condition_rows(g)
    fig, ax = plt.subplots(figsize=(WIDTH, 2.0))
    ys = list(range(len(rows)))[::-1]
    for y, (label, n, counts) in zip(ys, rows):
        left = 0.0
        for st, colour in STATUS.items():
            w = 100 * counts[st] / n
            if w <= 0:
                continue
            ax.barh(y, w, left=left, height=0.62, color=colour, edgecolor="white", linewidth=0.8, zorder=2)
            if w >= 9:
                dark_text = st in ("No status", "Damaged")
                ax.text(left + w / 2, y, f"{w:.0f}", ha="center", va="center", fontsize=6,
                        color=INK if dark_text else "white", zorder=3)
            left += w
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{label} ({n:,})" for label, n, _ in rows], color=INK2)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Share of monuments of the type (%)")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=2)
    handles = [Rectangle((0, 0), 1, 1, color=c, ec="white") for c in STATUS.values()]
    ax.legend(handles, list(STATUS), loc="lower left", bbox_to_anchor=(0, 1.0), ncol=5, frameon=False,
              handlelength=1.0, handletextpad=0.3, columnspacing=0.8, borderaxespad=0.2, fontsize=6)
    fig.savefig(path)
    plt.close(fig)
    return rows


def make_all(g, out_dir, log_path=SYNC_LOG):
    os.makedirs(out_dir, exist_ok=True)
    steps = fig_alignment(os.path.join(out_dir, "alignment_progress.pdf"), log_path)
    counts = fig_map(os.path.join(out_dir, "monument_map.pdf"), g)
    rows = fig_condition(os.path.join(out_dir, "condition_by_type.pdf"), g)
    return {"steps": steps, "map_counts": counts, "condition_rows": rows}


if __name__ == "__main__":
    import build_kg
    from conftest import EVENTS, MONUMENTS, OBJECTS
    graph, _ = build_kg.build_knowledge_graph(MONUMENTS, EVENTS, OBJECTS)
    out = make_all(graph, os.path.join(REPO, "docs", "paper", "figures"))
    print("steps:", len(out["steps"]) - 1, "map:", out["map_counts"])
