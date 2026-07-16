"""Generate the empirical study charts (section 7) from benchmark results.

Reads data/outputs/results_all.json (written by benchmark_manager.py) and
produces PNG figures in docs/figures/:

  fig1_escala_media.png       mean latency per operation type vs N (AVL),
                              with a fitted c*log2(n) theoretical reference
  fig2_escala_percentis.png   overall p50/p99 vs N (AVL, both insert orders)
  fig3_theta.png              theta sensitivity of mean latency per op type
  fig4_altura.png             final tree height vs live keys, all structures,
                              with log2(n) and n references
  fig5_baseline.png           AVL vs naive BST mean latency (crossover study)

Every figure is rendered from the group's own measurements; the machine and
methodology are recorded by benchmark_manager.py in data/outputs/run_info.json.
"""

import json
import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator

RESULTS_PATH = os.path.join("data", "outputs", "results_all.json")
FIG_DIR = os.path.join("docs", "figures")

# Validated categorical palette (fixed slot order — see report methodology)
BLUE = "#2a78d6"     # slot 1
AQUA = "#1baf7a"     # slot 2
YELLOW = "#eda100"   # slot 3
VIOLET = "#4a3aa7"   # slot 5

SURFACE = "#fcfcfb"
GRID = "#e1e0d9"
MUTED = "#898781"
INK = "#0b0b0b"
SECONDARY = "#52514e"

OP_COLORS = {"insert": BLUE, "delete": AQUA, "search": YELLOW}
OP_LABELS = {"insert": "inserção (I)", "delete": "remoção (D)", "search": "busca (S)"}


def style_axes(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(True, which="major", color=GRID, linewidth=0.8)
    ax.grid(False, which="minor")
    ax.tick_params(colors=SECONDARY, labelsize=9)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(MUTED)
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)
    ax.title.set_color(INK)


def new_fig(ncols=1, width=7.0, height=4.2):
    fig, axes = plt.subplots(1, ncols, figsize=(width * ncols if ncols > 1 else width, height))
    fig.patch.set_facecolor(SURFACE)
    if ncols == 1:
        style_axes(axes)
    else:
        for ax in axes:
            style_axes(ax)
    return fig, axes


def save(fig, name):
    os.makedirs(FIG_DIR, exist_ok=True)
    path = os.path.join(FIG_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)
    print(f"[Salvo] {path}")


def rows_where(results, **conditions):
    out = []
    for r in results:
        if all(r.get(k) == v for k, v in conditions.items()):
            out.append(r)
    return sorted(out, key=lambda r: r["ops"])


def fig_escala_media(results):
    """Mean latency per op type vs N (AVL), log-log, with c*log2(n) reference."""
    fig, axes = new_fig(ncols=2, width=5.6)

    for ax, order in zip(axes, ("sorted", "shuffle")):
        rows = rows_where(results, experiment="escala", structure="avl", order=order)
        if not rows:
            continue

        ns = [r["ops"] for r in rows]
        for op in ("insert", "delete", "search"):
            ys = [r["stats"]["per_op"][op]["mean_ns"] for r in rows]
            ax.plot(ns, ys, marker="o", markersize=5, linewidth=2,
                    color=OP_COLORS[op], label=OP_LABELS[op])

        # Theoretical reference c*log2(n), c fitted on the largest point of insert
        ref_rows = rows[-1]
        c = ref_rows["stats"]["per_op"]["insert"]["mean_ns"] / math.log2(ref_rows["ops"])
        theo = [c * math.log2(n) for n in ns]
        ax.plot(ns, theo, linestyle="--", linewidth=1.5, color=MUTED,
                label="referência c·log₂(n)")

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Número de operações (N)")
        ax.set_ylabel("Tempo médio por operação (ns)")
        ax.set_title(f"AVL — ordem de inserção: {order}", fontsize=10)
        ax.legend(fontsize=8, frameon=False, labelcolor=SECONDARY)

    fig.suptitle("Escala: tempo médio por operação vs N (dados wiki, θ=0.6)",
                 fontsize=11, color=INK)
    save(fig, "fig1_escala_media.png")


def fig_escala_percentis(results):
    """Overall p50/p99 vs N for AVL, both insert orders."""
    fig, ax = new_fig()

    styles = {"sorted": "-", "shuffle": ":"}
    for order in ("sorted", "shuffle"):
        rows = rows_where(results, experiment="escala", structure="avl", order=order)
        if not rows:
            continue
        ns = [r["ops"] for r in rows]
        p50 = [r["stats"]["overall"]["p50_ns"] for r in rows]
        p99 = [r["stats"]["overall"]["p99_ns"] for r in rows]
        ax.plot(ns, p50, styles[order], marker="o", markersize=5, linewidth=2,
                color=BLUE, label=f"p50 ({order})")
        ax.plot(ns, p99, styles[order], marker="s", markersize=5, linewidth=2,
                color=VIOLET, label=f"p99 ({order})")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Número de operações (N)")
    ax.set_ylabel("Latência (ns)")
    ax.set_title("Escala: percentis p50 e p99 vs N (AVL, wiki, θ=0.6)", fontsize=11)
    ax.legend(fontsize=8, frameon=False, labelcolor=SECONDARY)
    save(fig, "fig2_escala_percentis.png")


def fig_theta(results):
    """Theta sensitivity: mean latency per op type at fixed N."""
    fig, axes = new_fig(ncols=2, width=5.6)

    for ax, order in zip(axes, ("sorted", "shuffle")):
        rows = [r for r in results if r["experiment"] == "theta"
                and r["structure"] == "avl" and r["order"] == order]
        rows.sort(key=lambda r: r["theta"])
        if not rows:
            continue

        thetas = [r["theta"] for r in rows]
        for op in ("insert", "delete", "search"):
            ys = [r["stats"]["per_op"][op]["mean_ns"] for r in rows]
            ax.plot(thetas, ys, marker="o", markersize=5, linewidth=2,
                    color=OP_COLORS[op], label=OP_LABELS[op])

        ax.set_xlabel("θ (enviesamento Zipfiano)")
        ax.set_ylabel("Tempo médio por operação (ns)")
        ax.set_title(f"ordem de inserção: {order}", fontsize=10)
        ax.set_xticks(thetas)
        ax.legend(fontsize=8, frameon=False, labelcolor=SECONDARY)

    fig.suptitle("Sensibilidade ao enviesamento: latência média vs θ (AVL, N=1M)",
                 fontsize=11, color=INK)
    save(fig, "fig3_theta.png")


def fig_altura(results):
    """Final height vs live keys for every structure/order, with references."""
    fig, ax = new_fig()

    series = [
        ("avl", "sorted", BLUE, "-", "AVL, sorted"),
        ("avl", "shuffle", BLUE, ":", "AVL, shuffle"),
        ("naive", "sorted", AQUA, "-", "BST ingênua, sorted"),
        ("naive", "shuffle", AQUA, ":", "BST ingênua, shuffle"),
    ]

    max_size = 0
    for structure, order, color, ls, label in series:
        rows = rows_where(results, experiment="escala", structure=structure, order=order)
        if not rows:
            continue
        sizes = [r["stats"]["final_size"] for r in rows]
        heights = [r["stats"]["final_height"] for r in rows]
        max_size = max(max_size, max(sizes))
        ax.plot(sizes, heights, ls, marker="o", markersize=5, linewidth=2,
                color=color, label=label)

    if max_size:
        xs = [2 ** e for e in range(4, int(math.log2(max_size)) + 1)]
        ax.plot(xs, [math.log2(x) for x in xs], "--", linewidth=1.5, color=MUTED,
                label="log₂(n)")
        ax.plot(xs, [1.44 * math.log2(x) for x in xs], "-.", linewidth=1.2, color=MUTED,
                label="1,44·log₂(n) (limite AVL)")
        ax.plot(xs, xs, linestyle=(0, (1, 3)), linewidth=1.5, color=MUTED, label="n (degenerada)")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Chaves vivas ao final (n)")
    ax.set_ylabel("Altura final da árvore")
    ax.set_title("Caso patológico: altura final vs n", fontsize=11)
    ax.legend(fontsize=8, frameon=False, labelcolor=SECONDARY)
    save(fig, "fig4_altura.png")


def fig_baseline(results):
    """AVL vs naive BST mean latency per N (crossover study), per order."""
    fig, axes = new_fig(ncols=2, width=5.6)

    for ax, order in zip(axes, ("sorted", "shuffle")):
        for structure, color, label in (("avl", BLUE, "AVL aumentada"),
                                        ("naive", AQUA, "BST ingênua")):
            rows = rows_where(results, experiment="escala", structure=structure, order=order)
            if not rows:
                continue
            ns = [r["ops"] for r in rows]
            ys = [r["stats"]["overall"]["mean_ns"] for r in rows]
            ax.plot(ns, ys, marker="o", markersize=5, linewidth=2, color=color, label=label)

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Número de operações (N)")
        ax.set_ylabel("Tempo médio por operação (ns)")
        ax.set_title(f"ordem de inserção: {order}", fontsize=10)
        ax.legend(fontsize=8, frameon=False, labelcolor=SECONDARY)

    fig.suptitle("Linha de base: AVL vs BST sem balanceamento (wiki, θ=0.6)",
                 fontsize=11, color=INK)
    save(fig, "fig5_baseline.png")


def main():
    if not os.path.exists(RESULTS_PATH):
        print(f"Erro: '{RESULTS_PATH}' não encontrado. Rode benchmark_manager.py primeiro.",
              file=sys.stderr)
        sys.exit(1)

    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        results = json.load(f)

    fig_escala_media(results)
    fig_escala_percentis(results)
    fig_theta(results)
    fig_altura(results)
    fig_baseline(results)
    print("\nGráficos gerados em docs/figures/.")


if __name__ == "__main__":
    main()
