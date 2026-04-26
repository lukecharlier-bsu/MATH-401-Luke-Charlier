import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

BG         = "#1C1C1C"
BAR_BLUE   = "#0033A0"
BAR_ORANGE = "#D64309"
BAR_WHITE  = "#FFFFFF"
WHITE      = "#FFFFFF"
GREY       = "#AAAAAA"
GRIDLINE   = "#2E2E2E"
SAVE_DIR   = Path("/Users/lukecharlier/senior project")

def _save(fig, name):
    path = SAVE_DIR / f"{name}.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=BG)
    print(f"Saved → {path}")


def plot_accuracy_bars(sim_nfl, sim_total, sim_cap, real_nfl, real_total, real_cap):
    """
    # Input Variables: sim_nfl, sim_total, sim_cap, real_nfl, real_total, real_cap (floats) — proportion of tiebreaks won by the higher FPI team
    # Output Variables: None — displays and saves tiebreaker_accuracy.png
    # Purpose: Plots a horizontal bar chart comparing tiebreaker accuracy across NFL rules, total margin, and capped margin for simulated and real NFL data
    # Example: plot_accuracy_bars(0.50, 0.58, 0.64, 0.55, 0.65, 0.73)
    """
    # rows 1-3 = simulated, rows 5-7 = real nfl, row 4 is the gap
    bar_rows   = [1, 2, 3, 5, 6, 7]
    values     = [sim_nfl, sim_total, sim_cap, real_nfl, real_total, real_cap]
    colors     = [BAR_BLUE, WHITE, BAR_ORANGE, BAR_BLUE, WHITE, BAR_ORANGE]
    bar_labels = ["NFL Rules", "Total Margin", "Capped Margin",
                  "NFL Rules", "Total Margin", "Capped Margin"]

    plt.figure(figsize=(12, 6), facecolor=BG)
    ax = plt.gca()
    ax.set_facecolor(BG)

    for row, val, color in zip(bar_rows, values, colors):
        ax.barh(row, val, color=color, height=0.78, zorder=3)

    # value labels inside bars
    for row, val, color in zip(bar_rows, values, colors):
        text_color = BG if color == WHITE else WHITE
        plt.text(val - 0.02, row, f"{val*100:.0f}%",
                 va="center", ha="right",
                 color=text_color, fontsize=16, fontweight="bold")

    # section headers in gap rows
    plt.text(0.44, 0.2, "Simulated", va="center", ha="center",
             color=WHITE, fontsize=16, fontweight="bold")
    plt.text(0.44, 4.2, "Real NFL", va="center", ha="center",
             color=WHITE, fontsize=16, fontweight="bold")

    # axis formatting
    ax.set_yticks(bar_rows)
    ax.set_yticklabels(bar_labels, fontsize=14, color=WHITE)
    ax.set_xlim(0, 0.88)
    ax.set_ylim(7.8, -0.5)
    ax.xaxis.set_visible(False)
    ax.tick_params(length=0)

    for spine in ax.spines.values():
        spine.set_visible(False)

    # divider between simulated and real nfl
    ax.axhline(3.7, color="#333333", linewidth=1.2, zorder=4)

    # legend
    legend_patches = [
        mpatches.Patch(color=BAR_BLUE,   label="NFL Rules"),
        mpatches.Patch(color=WHITE,      label="Total Margin"),
        mpatches.Patch(color=BAR_ORANGE, label="Capped Margin"),
    ]
    plt.gcf().legend(handles=legend_patches, loc="lower center", ncol=3,
                     frameon=False, fontsize=16, labelcolor=WHITE,
                     bbox_to_anchor=(0.5, -0.02), handlelength=3, handleheight=1.5)

    plt.title("Does the Stronger Team Win Tiebreakers?",
              color=WHITE, fontsize=22, fontweight="bold", pad=14)

    plt.tight_layout(rect=[0, 0.12, 1, 1])
    plt.savefig("/Users/lukecharlier/senior project/tiebreaker_accuracy.png",
                dpi=300, bbox_inches="tight", facecolor=BG)
    plt.show()


def plot_season_length(results_df_summary):
    """
    # Input Variables: results_df_summary (dataframe with columns: Season_Length, Best_FPI_Team_1_Seed_Prob)
    # Output Variables: None — displays and saves season_length_convergence.png
    # Purpose: Log-log scatter plot of Season_Length vs Best_FPI_Team_1_Seed_Prob, showing how longer seasons surface the best team more reliably
    # Example: plot_season_length(results_df_summary)
    """
    x = results_df_summary["Season_Length"]
    y = results_df_summary["Best_FPI_Team_1_Seed_Prob"]

    plt.figure(figsize=(11, 8), facecolor=BG)
    ax = plt.gca()
    ax.set_facecolor(BG)

    # scatter points
    ax.scatter(x, y, color=BAR_ORANGE, s=100, zorder=3)

    ax.set_xscale("log")
    ax.set_ylim(0.25, 1)

    # label each dot with its season length; nudge 16 and 17 to avoid overlap
    offsets = {16: (6, -14), 17: (6, 4)}
    for xi, yi in zip(x, y):
        xytext = offsets.get(xi, (6, 4))
        ax.annotate(str(xi), (xi, yi), textcoords="offset points", xytext=xytext,
                    color=WHITE, fontsize=14, fontweight="bold")

    # default log scale ticks, no scientific notation
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f"{int(val):,}"))
    ax.tick_params(axis="both", colors=WHITE, length=4)
    plt.setp(ax.get_xticklabels(), color=WHITE, fontsize=16)

    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f"{val:.1f}"))
    plt.setp(ax.get_yticklabels(), color=WHITE, fontsize=16)

    ax.set_xlabel("Season Length (games)", color=WHITE, fontsize=16)
    ax.set_ylabel("Probability Best Team Gets #1 Seed", color=WHITE, fontsize=16)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.yaxis.grid(True, color=GRIDLINE, linewidth=0.6, zorder=0)
    ax.xaxis.grid(True, color=GRIDLINE, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)

    plt.title("Season Length and Playoff Seeding Accuracy (Log Scale)",
              color=WHITE, fontsize=20, fontweight="bold", pad=14)

    plt.tight_layout()
    plt.savefig("/Users/lukecharlier/senior project/season_length_convergence.png",
                dpi=300, bbox_inches="tight", facecolor=BG)
    plt.show()


def plot_1seed_histogram(one_seed_ranks_df, max_rank=16):
    """
    # Input Variables: one_seed_ranks_df (dataframe with column Conf_FPI_Rank), max_rank (int, default 16)
    # Output Variables: None — displays and saves 1seed_fpi_rank_histogram.png
    # Purpose: Plots a bar chart showing the distribution of conference FPI ranks among teams that earned a 1-seed across simulated seasons
    # Example: plot_1seed_histogram(one_seed_ranks_df, max_rank=16)
    """
    ranks  = one_seed_ranks_df["Conf_FPI_Rank"]
    total  = len(ranks)
    counts = ranks.value_counts().sort_index()
    counts = counts[counts.index <= max_rank].reindex(range(1, max_rank + 1), fill_value=0)
    props  = counts / total

    plt.figure(figsize=(11, 8), facecolor=BG)
    ax = plt.gca()
    ax.set_facecolor(BG)

    bars = plt.bar(props.index, props.values, color=BAR_BLUE, width=0.6, zorder=3)

    # percentage labels on top of each bar
    for rect, val in zip(bars, props.values):
        if val > .04:
            plt.text(rect.get_x() + rect.get_width() / 2,
                     rect.get_height() + 0.005,
                     f"{val:.1%}",
                     ha="center", va="bottom",
                     color=WHITE, fontsize=16, fontweight="bold")
        else:
            plt.text(rect.get_x() + rect.get_width() / 2,
                     rect.get_height() + 0.005,
                     f"{val:.1%}",
                     ha="center", va="bottom",
                     color=WHITE, fontsize=14, fontweight="bold")

    ax.set_xticks(range(1, max_rank + 1))
    ax.set_xticklabels([f"#{i}" for i in range(1, max_rank + 1)], color=WHITE, fontsize=16)
    ax.set_ylim(0, .42)
    ax.set_xlabel("Conference FPI Rank  (1 = Strongest in Conference)", color=WHITE, fontsize=16)
    ax.set_ylabel("Share of #1 Seeds", color=WHITE, fontsize=16)
    ax.tick_params(colors=WHITE, length=0)
    ax.yaxis.grid(True, color=GRIDLINE, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.title("Which Teams Actually Earn a #1 Seed?\n(10,000 Simulated Seasons)",
              color=WHITE, fontsize=22, fontweight="bold", pad=14)

    plt.tight_layout()
    plt.savefig("/Users/lukecharlier/senior project/1seed_fpi_rank_histogram.png",
                dpi=300, bbox_inches="tight", facecolor=BG)
    plt.show()
