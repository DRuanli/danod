"""
TUFCI Experiment Figures — PLOS ONE Revision  [v2: vivid colours, fixed legends, redesigned Fig4]
Generates Fig 1–7 from results/ directory CSVs.

Usage:  python plot_experiments.py
Output: figures/fig1.pdf ... figures/fig7.pdf  (+ .png)
"""

import os, warnings
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from matplotlib.ticker import MaxNLocator

warnings.filterwarnings("ignore")

# ── Global typography & style ─────────────────────────────────────────────────
matplotlib.rcParams.update({
    "font.family":        "serif",
    "font.serif":         ["Times New Roman", "DejaVu Serif"],
    "font.size":          11,
    "axes.titlesize":     12,
    "axes.titleweight":   "bold",
    "axes.labelsize":     11,
    "xtick.labelsize":    9.5,
    "ytick.labelsize":    9.5,
    "legend.fontsize":    9,
    "legend.framealpha":  0.88,
    "legend.edgecolor":   "#bbbbbb",
    "figure.dpi":         150,
    "axes.grid":          True,
    "grid.color":         "#dddddd",
    "grid.linestyle":     "-",
    "grid.linewidth":     0.7,
    "axes.axisbelow":     True,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.edgecolor":     "#444444",
    "axes.linewidth":     0.9,
    "lines.linewidth":    2.2,
    "lines.markersize":   7,
})

os.makedirs("figures", exist_ok=True)

# ── Vivid colour palette (high-contrast, distinct in colour AND greyscale) ─────
PALETTE = {
    "V1_BFS_Full":   "#D62728",   # strong red
    "V2_DFS_Full":   "#1F77B4",   # strong blue
    "V3_BFS_Search": "#2CA02C",   # strong green
    "V4_DFS_Search": "#FF7F0E",   # strong orange
    "TopKPFIM":      "#9467BD",   # vivid purple
    "ITUFP":         "#17BECF",   # vivid teal
}
MARKERS = {
    "V1_BFS_Full":   "o",
    "V2_DFS_Full":   "s",
    "V3_BFS_Search": "^",
    "V4_DFS_Search": "D",
    "TopKPFIM":      "*",
    "ITUFP":         "X",
}
LINESTYLES = {
    "V1_BFS_Full":   "-",
    "V2_DFS_Full":   "--",
    "V3_BFS_Search": "-.",
    "V4_DFS_Search": ":",
    "TopKPFIM":      (0, (3, 1, 1, 1)),
    "ITUFP":         (0, (5, 2)),
}
LABELS = {
    "V1_BFS_Full":   "TUFCI-BFS (Full P1–P7)",
    "V2_DFS_Full":   "TUFCI-DFS (Full P1–P7)",
    "V3_BFS_Search": "TUFCI-BFS (Search P1–P3)",
    "V4_DFS_Search": "TUFCI-DFS (Search P1–P3)",
    "TopKPFIM":      "TopKPFIM (Li et al. 2017)",
    "ITUFP":         "ITUFP (Davashi 2023)",
}
DATASET_NAMES = {
    "chess":             "Chess",
    "liquor_11frequent": "Liquor",
    "mushrooms":         "Mushrooms",
    "retail":            "Retail",
}

# Ablation
ABL_PALETTE = {
    "FULL":           "#D62728",
    "NO_G1_frontier": "#1F77B4",
    "NO_G2_item":     "#2CA02C",
    "NO_G3_upbound":  "#FF7F0E",
    "NO_G4_tidset":   "#9467BD",
    "ONLY_G1":        "#17BECF",
    "ONLY_G2_G3_G4":  "#E377C2",
}
ABL_LABELS = {
    "FULL":           "Full (baseline)",
    "NO_G1_frontier": "−G1 (no frontier term.)",
    "NO_G2_item":     "−G2 (no item admiss.)",
    "NO_G3_upbound":  "−G3 (no upper-bound)",
    "NO_G4_tidset":   "−G4 (no tidset short.)",
    "ONLY_G1":        "Only G1",
    "ONLY_G2_G3_G4":  "Only G2+G3+G4",
}

# Sensitivity
PARAM_PALETTE = {
    "alpha": "#D62728",
    "rho":   "#1F77B4",
    "p_min": "#2CA02C",
    "p_max": "#FF7F0E",
}
PARAM_LABELS = {
    "alpha": r"$\alpha$",
    "rho":   r"$\rho$",
    "p_min": r"$p_{\min}$",
    "p_max": r"$p_{\max}$",
}

# Group dominance
G_COLORS = {"G1": "#D62728", "G2": "#1F77B4", "G3": "#2CA02C", "G4": "#FF7F0E"}
G_LABELS_LONG = {
    "G1": "G1\n(Frontier\nterm.)",
    "G2": "G2\n(Item\nadmiss.)",
    "G3": "G3\n(Upper-\nbound)",
    "G4": "G4\n(Tidset\nshort.)",
}


# ── Shared line-plot helper ────────────────────────────────────────────────────
def _make_line_handle(algo):
    """Return a correctly-styled legend handle (line + marker) for algo."""
    return mlines.Line2D(
        [], [],
        color=PALETTE[algo],
        linestyle=LINESTYLES[algo],
        marker=MARKERS[algo],
        markersize=7,
        markerfacecolor=PALETTE[algo],
        markeredgecolor="white",
        markeredgewidth=0.9,
        linewidth=2.2,
        label=LABELS[algo],
    )


def _draw_lines(ax, df, dataset, algos, metric):
    sub    = df[df["dataset"] == dataset]
    k_vals = sorted(sub["k"].unique())
    for algo in algos:
        g     = sub[sub["algorithm"] == algo].groupby("k")[metric]
        means = g.mean().reindex(k_vals)
        stds  = g.std().reindex(k_vals).fillna(0)
        ax.errorbar(
            k_vals, means.values, yerr=stds.values,
            color=PALETTE[algo],
            linestyle=LINESTYLES[algo],
            marker=MARKERS[algo],
            markersize=7,
            markerfacecolor=PALETTE[algo],
            markeredgecolor="white",
            markeredgewidth=0.9,
            linewidth=2.2,
            capsize=3, capthick=1.2, elinewidth=1.0,
            zorder=3,
        )
    ax.set_xlabel("k")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_title(DATASET_NAMES.get(dataset, dataset), pad=6)


def _line_figure(df, algos, metric, ylabel, suptitle, outname, ncol_legend=3):
    datasets  = sorted(df["dataset"].unique())
    n_ds      = len(datasets)
    fig, axes = plt.subplots(1, n_ds, figsize=(4.6 * n_ds, 4.2), sharey=False)
    if n_ds == 1:
        axes = [axes]

    for i, (ax, ds) in enumerate(zip(axes, datasets)):
        _draw_lines(ax, df, ds, algos, metric)
        ax.set_ylabel(ylabel if i == 0 else "")

    handles = [_make_line_handle(a) for a in algos]
    fig.legend(handles=handles, loc="lower center",
               ncol=min(ncol_legend, len(algos)),
               bbox_to_anchor=(0.5, -0.13),
               framealpha=0.9, edgecolor="#bbbbbb",
               handlelength=2.8, handleheight=1.2)
    fig.suptitle(suptitle, fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(f"figures/{outname}.pdf", bbox_inches="tight")
    fig.savefig(f"figures/{outname}.png", bbox_inches="tight")
    print(f"  ✓ {outname} saved")
    plt.close(fig)


# ── Data loaders ──────────────────────────────────────────────────────────────
def load_exp1():
    dfs = []
    for ds in ["chess", "liquor_11frequent", "mushrooms", "retail"]:
        p = f"results/exp1/{ds}_main_comparison_raw.csv"
        if os.path.exists(p):
            dfs.append(pd.read_csv(p))
    if not dfs:
        raise FileNotFoundError("No exp1 CSVs in results/exp1/")
    return pd.concat(dfs, ignore_index=True)


def load_exp3():
    dfs = []
    for ds in ["chess_uncertain", "liquor_11frequent_uncertain",
               "mushrooms_uncertain", "retail_uncertain"]:
        p = f"results/exp3/{ds}_sensitivity_jaccard.csv"
        if os.path.exists(p):
            dfs.append(pd.read_csv(p))
    if not dfs:
        raise FileNotFoundError("No exp3 sensitivity_jaccard CSVs found.")
    return pd.concat(dfs, ignore_index=True)


def load_exp4a():
    dfs = []
    for f in os.listdir("results/exp4a"):
        if f.endswith("_group_ablation_raw.csv"):
            dfs.append(pd.read_csv(os.path.join("results/exp4a", f)))
    if not dfs:
        raise FileNotFoundError("No exp4a CSVs found.")
    return pd.concat(dfs, ignore_index=True)


def load_exp4b():
    dfs = []
    for f in os.listdir("results/exp4b"):
        if f.endswith("_group_dominance_heatmap.csv"):
            dfs.append(pd.read_csv(os.path.join("results/exp4b", f)))
    if not dfs:
        raise FileNotFoundError("No exp4b CSVs found.")
    return pd.concat(dfs, ignore_index=True)


def load_exp8():
    dfs = []
    for ds in ["chess", "liquor_11frequent", "mushrooms", "retail"]:
        p = f"results/exp8/{ds}_memory_profile.csv"
        if os.path.exists(p):
            dfs.append(pd.read_csv(p))
    if not dfs:
        raise FileNotFoundError("No exp8 CSVs found.")
    return pd.concat(dfs, ignore_index=True)


# ── Fig 1 ─────────────────────────────────────────────────────────────────────
def fig1(df):
    _line_figure(df,
                 algos=["V1_BFS_Full", "TopKPFIM", "ITUFP"],
                 metric="runtime_ms", ylabel="Runtime (ms)",
                 suptitle="Fig 1 — Runtime: TUFCI-BFS (Full) vs External Baselines",
                 outname="fig1", ncol_legend=3)


# ── Fig 2 ─────────────────────────────────────────────────────────────────────
def fig2(df):
    _line_figure(df,
                 algos=["V1_BFS_Full", "V2_DFS_Full", "V3_BFS_Search", "V4_DFS_Search"],
                 metric="runtime_ms", ylabel="Runtime (ms)",
                 suptitle="Fig 2 — Runtime: TUFCI-BFS (Full) vs Internal Variants",
                 outname="fig2", ncol_legend=4)


# ── Fig 3 ─────────────────────────────────────────────────────────────────────
def fig3(df):
    _line_figure(df,
                 algos=["V1_BFS_Full", "V2_DFS_Full", "V3_BFS_Search", "V4_DFS_Search"],
                 metric="closure_checks", ylabel="Closure checks",
                 suptitle="Fig 3 — Closure Checks: 4 Internal Variants",
                 outname="fig3", ncol_legend=4)


# ── Fig 4 — Ablation: slowdown factor, horizontal bar, clean layout ────────────
def fig4(df4a):
    df = df4a.copy()
    df["ds"] = df["dataset"].apply(
        lambda x: os.path.splitext(os.path.basename(str(x)))[0]
                    .replace("processed_data/", "").replace("_uncertain", ""))

    CONFIG_ORDER = ["FULL", "NO_G1_frontier", "NO_G2_item",
                    "NO_G3_upbound", "NO_G4_tidset", "ONLY_G1", "ONLY_G2_G3_G4"]
    datasets = sorted(df["ds"].unique())
    configs  = [c for c in CONFIG_ORDER if c in df["config"].unique()]

    n_ds  = len(datasets)
    fig, axes = plt.subplots(1, n_ds,
                             figsize=(5.4 * n_ds, 4.8),
                             sharey=True)            # shared y → aligned labels
    if n_ds == 1:
        axes = [axes]

    for ax, ds in zip(axes, datasets):
        sub   = df[df["ds"] == ds]
        means = sub.groupby("config")["runtime_ms"].mean().reindex(configs)
        stds  = sub.groupby("config")["runtime_ms"].std().reindex(configs).fillna(0)

        full_val  = means["FULL"] if "FULL" in means.index else means.iloc[0]
        slowdown  = means / full_val
        sd_err    = stds  / full_val

        y_pos  = np.arange(len(configs))
        colors = [ABL_PALETTE.get(c, "#aaaaaa") for c in configs]
        alphas = [1.0 if c == "FULL" else 0.82 for c in configs]

        for yi, (slw, err, clr, alp, cfg) in enumerate(
                zip(slowdown, sd_err, colors, alphas, configs)):
            ax.barh(yi, slw, xerr=err,
                    color=clr, alpha=alp,
                    edgecolor="white", linewidth=0.7, height=0.62,
                    error_kw=dict(elinewidth=1.3, capsize=4,
                                  ecolor="#333333", capthick=1.2))
            # Value label
            x_lbl = slw + err + 0.03
            ax.text(x_lbl, yi, f"{slw:.2f}×",
                    va="center", ha="left", fontsize=8.8,
                    fontweight="bold" if cfg == "FULL" else "normal",
                    color="#111111")

        # Baseline reference
        ax.axvline(1.0, color="#D62728", linestyle="--",
                   linewidth=1.8, zorder=5)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([ABL_LABELS.get(c, c) for c in configs], fontsize=9.5)
        ax.set_xlabel("Slowdown vs Full  (×)", fontsize=10)
        ax.set_title(DATASET_NAMES.get(ds, ds), pad=7)
        x_max = max(slowdown.fillna(0)) + max(sd_err.fillna(0)) + 0.5
        ax.set_xlim(0, max(x_max, 1.4))
        ax.invert_yaxis()
        # Subtle band on FULL row (top after invert)
        ax.axhspan(len(configs) - 1 - 0.38,
                   len(configs) - 1 + 0.38,
                   color="#D62728", alpha=0.07, zorder=0)

    # Legend
    cfg_handles = [
        mpatches.Patch(facecolor=ABL_PALETTE.get(c, "#aaa"),
                       edgecolor="white", alpha=0.9,
                       label=ABL_LABELS.get(c, c))
        for c in configs
    ]
    baseline_handle = mlines.Line2D([], [], color="#D62728", linestyle="--",
                                    linewidth=1.8, label="Full baseline (1.0×)")
    fig.legend(handles=cfg_handles + [baseline_handle],
               loc="lower center", ncol=min(4, len(cfg_handles) + 1),
               bbox_to_anchor=(0.5, -0.12),
               framealpha=0.92, edgecolor="#bbbbbb", fontsize=9)

    fig.suptitle("Fig 4 — Ablation Study: Slowdown Factor per Pruning Configuration",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig("figures/fig4.pdf", bbox_inches="tight")
    fig.savefig("figures/fig4.png", bbox_inches="tight")
    print("  ✓ fig4 saved")
    plt.close(fig)


# ── Fig 5 — Sensitivity runtime ────────────────────────────────────────────────
def fig5(df3):
    df = df3.copy()
    df["ds"] = df["dataset"].str.replace("_uncertain", "", regex=False)
    datasets = sorted(df["ds"].unique())
    PARAMS   = ["alpha", "rho", "p_min", "p_max"]

    n_ds  = len(datasets)
    fig, axes = plt.subplots(1, n_ds, figsize=(5.8 * n_ds, 4.4), sharey=False)
    if n_ds == 1:
        axes = [axes]

    for ax, ds in zip(axes, datasets):
        sub    = df[df["ds"] == ds]
        x_pos  = 0
        xticks, xlabels = [], []
        grp_mid, grp_nm = [], []

        for param in PARAMS:
            p_sub = sub[sub["param"] == param].sort_values("value")
            if p_sub.empty:
                continue
            vals = p_sub["value"].tolist()
            rts  = p_sub["runtime_mean_ms"].tolist()
            xs   = np.arange(len(vals), dtype=float) + x_pos   # avoids float arange endpoint bug
            ax.bar(xs, rts,
                   color=PARAM_PALETTE[param], width=0.72,
                   edgecolor="white", linewidth=0.5, zorder=3)
            for xi, v in zip(xs, vals):
                xticks.append(xi); xlabels.append(str(v))
            grp_mid.append(float(np.mean(xs)))
            grp_nm.append(PARAM_LABELS[param])
            x_pos += len(vals) + 1.8

        ax.set_xticks(xticks)
        ax.set_xticklabels(xlabels, rotation=0, fontsize=8.5)
        ax.set_ylabel("Runtime (ms)" if ax is axes[0] else "")
        ax.set_title(DATASET_NAMES.get(ds, ds), pad=6)

        # Group labels below tick labels
        ymin, ymax = ax.get_ylim()
        drop = (ymax - ymin) * 0.16
        for mx, nm in zip(grp_mid, grp_nm):
            ax.text(mx, ymin - drop, nm,
                    ha="center", va="top",
                    fontsize=11, fontweight="bold",
                    color="#222222")
        ax.set_ylim(bottom=ymin - (ymax - ymin) * 0.04)

    handles = [mpatches.Patch(facecolor=PARAM_PALETTE[p], edgecolor="white",
                              label=PARAM_LABELS[p]) for p in PARAMS]
    fig.legend(handles=handles, loc="lower center", ncol=4,
               bbox_to_anchor=(0.5, -0.10),
               framealpha=0.9, edgecolor="#bbbbbb", fontsize=10)
    fig.suptitle("Fig 5 — Parameter Sensitivity: Runtime vs Uncertainty Parameters",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig("figures/fig5.pdf", bbox_inches="tight")
    fig.savefig("figures/fig5.png", bbox_inches="tight")
    print("  ✓ fig5 saved")
    plt.close(fig)


# ── Fig 6 — Group dominance ────────────────────────────────────────────────────
def fig6(df4b):
    datasets = sorted(df4b["dataset"].unique())
    GROUPS   = ["G1", "G2", "G3", "G4"]
    bar_w    = 0.38

    n_ds  = len(datasets)
    fig, axes = plt.subplots(1, n_ds, figsize=(5.2 * n_ds, 4.4), sharey=False)
    if n_ds == 1:
        axes = [axes]

    for ax, ds in zip(axes, datasets):
        sub = df4b[df4b["dataset"] == ds].set_index("group")
        x   = np.arange(len(GROUPS))
        marg = [float(sub.loc[g, "marginal_benefit_pct"])
                if g in sub.index else 0.0 for g in GROUPS]
        excl = [float(sub.loc[g, "exclusive_benefit_pct"])
                if g in sub.index else 0.0 for g in GROUPS]

        for gi, (g, mg, ex) in enumerate(zip(GROUPS, marg, excl)):
            clr = G_COLORS[g]
            b1 = ax.bar(gi - bar_w / 2, mg, bar_w,
                        color=clr, edgecolor="white", linewidth=0.6)
            b2 = ax.bar(gi + bar_w / 2, ex, bar_w,
                        color=clr, edgecolor="white", linewidth=0.6,
                        alpha=0.42, hatch="///")
            top = max(marg + excl)
            for b, v in [(b1[0], mg), (b2[0], ex)]:
                ax.text(b.get_x() + b.get_width() / 2,
                        v + top * 0.015,
                        f"{v:.1f}%",
                        ha="center", va="bottom",
                        fontsize=8.5, fontweight="bold", color="#111111")

        ax.set_xticks(x)
        ax.set_xticklabels([G_LABELS_LONG[g] for g in GROUPS], fontsize=9.5)
        ax.set_ylabel("Benefit (%)" if ax is axes[0] else "")
        ax.set_title(DATASET_NAMES.get(ds, ds), pad=6)
        top = max(marg + excl)
        ax.set_ylim(0, top * 1.22 + 2)

    h_mg = mpatches.Patch(facecolor="#777777", edgecolor="white",
                          label="Marginal benefit (slowdown without this group)")
    h_ex = mpatches.Patch(facecolor="#777777", edgecolor="white",
                          alpha=0.42, hatch="///",
                          label="Exclusive benefit (this group alone vs none)")
    g_h  = [mpatches.Patch(facecolor=G_COLORS[g], edgecolor="white",
                            label=f"Group {g}") for g in GROUPS]
    fig.legend(handles=[h_mg, h_ex] + g_h,
               loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, -0.15),
               framealpha=0.9, edgecolor="#bbbbbb", fontsize=9)
    fig.suptitle("Fig 6 — Pruning Group Dominance: Marginal vs Exclusive Benefit",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig("figures/fig6.pdf", bbox_inches="tight")
    fig.savefig("figures/fig6.png", bbox_inches="tight")
    print("  ✓ fig6 saved")
    plt.close(fig)


# ── Fig 7 — Peak frontier size ────────────────────────────────────────────────
def fig7(df8=None, df1=None):
    INTERNAL = ["V1_BFS_Full", "V2_DFS_Full"]
    src = df8 if df8 is not None else df1
    col = "max_frontier_size" if df8 is not None else "max_queue_size"

    datasets  = sorted(src["dataset"].unique())
    n_ds      = len(datasets)
    fig, axes = plt.subplots(1, n_ds, figsize=(4.6 * n_ds, 4.2), sharey=False)
    if n_ds == 1:
        axes = [axes]

    for i, (ax, ds) in enumerate(zip(axes, datasets)):
        sub    = src[(src["dataset"] == ds) & (src["algorithm"].isin(INTERNAL))]
        k_vals = sorted(sub["k"].unique())
        for algo in INTERNAL:
            g     = sub[sub["algorithm"] == algo].groupby("k")[col]
            means = g.mean().reindex(k_vals)
            stds  = g.std().reindex(k_vals).fillna(0)
            lo    = (means - stds).clip(lower=0).values
            hi    = (means + stds).values
            ax.fill_between(k_vals, lo, hi,
                            color=PALETTE[algo], alpha=0.14)
            ax.plot(k_vals, means.values,
                    color=PALETTE[algo],
                    linestyle=LINESTYLES[algo],
                    marker=MARKERS[algo],
                    markersize=7,
                    markerfacecolor=PALETTE[algo],
                    markeredgecolor="white",
                    markeredgewidth=0.9,
                    linewidth=2.2, zorder=3)
        ax.set_xlabel("k")
        ax.set_ylabel("Peak frontier size" if i == 0 else "")
        ax.set_title(DATASET_NAMES.get(ds, ds), pad=6)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    handles = [_make_line_handle(a) for a in INTERNAL]
    fig.legend(handles=handles, loc="lower center", ncol=2,
               bbox_to_anchor=(0.5, -0.12),
               framealpha=0.9, edgecolor="#bbbbbb", handlelength=2.8)
    fig.suptitle("Fig 7 — Peak Frontier Size: Priority Queue (BFS) vs Stack (DFS)",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig("figures/fig7.pdf", bbox_inches="tight")
    fig.savefig("figures/fig7.png", bbox_inches="tight")
    print("  ✓ fig7 saved")
    plt.close(fig)


def _make_line_handle(algo):
    return mlines.Line2D(
        [], [],
        color=PALETTE[algo], linestyle=LINESTYLES[algo],
        marker=MARKERS[algo], markersize=7,
        markerfacecolor=PALETTE[algo],
        markeredgecolor="white", markeredgewidth=0.9,
        linewidth=2.2, label=LABELS[algo])


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Loading exp1 …")
    df1 = load_exp1()
    print(f"  {len(df1)} rows | datasets: {sorted(df1['dataset'].unique())}")

    print("Fig 1 …"); fig1(df1)
    print("Fig 2 …"); fig2(df1)
    print("Fig 3 …"); fig3(df1)

    print("Fig 4 …")
    try:
        fig4(load_exp4a())
    except FileNotFoundError as e:
        print(f"  [skip] {e}")

    print("Fig 5 …")
    try:
        fig5(load_exp3())
    except FileNotFoundError as e:
        print(f"  [skip] {e}")

    print("Fig 6 …")
    try:
        fig6(load_exp4b())
    except FileNotFoundError as e:
        print(f"  [skip] {e}")

    print("Fig 7 …")
    try:
        fig7(df8=load_exp8())
    except FileNotFoundError:
        print("  exp8 not found — using max_queue_size from exp1")
        fig7(df1=df1)

    print("\nDone → figures/  (PDF + PNG)")


if __name__ == "__main__":
    main()