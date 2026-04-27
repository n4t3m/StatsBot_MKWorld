import matplotlib

matplotlib.use("Agg")

from io import BytesIO

import matplotlib.gridspec as gridspec
import matplotlib.image as mpimg
import numpy as np
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from common.constants import get_mmr_definition, get_rank, rank_index


def create_plot(mmrhistory: list, season: int, player_name: str, game_mode: str):
    b = BytesIO()

    # Convert game_mode for display
    if season == 0 or season == 1:
        game_mode_display = None
    elif game_mode == "12p":
        game_mode_display = "12 player"
    elif game_mode == "24p":
        game_mode_display = "24 player"

    ranks = get_mmr_definition(season, game_mode)

    colors = [
        "#817876",
        "#E67E22",
        "#7D8396",
        "#F1C40F",
        "#3FABB8",
        "#286CD3",
        "#d51c5e",
        "#9CCBD6",
        "#0E0B0B",
        "#A3022C",
    ]

    matplotlib.rcParams.update(
        matplotlib.rc_params_from_file("src/common/lounge_style.mplstyle")
    )

    fig = Figure(figsize=(10, 6.5))
    gs = gridspec.GridSpec(
        3, 1, height_ratios=[0.10, 0.06, 1.0], hspace=0.0, figure=fig
    )

    # --- Header ---
    ax_header = fig.add_subplot(gs[0])
    ax_header.set_axis_off()
    try:
        favicon = mpimg.imread("src/common/favicon.ico")
        ax_inset = inset_axes(
            ax_header,
            width="4%",
            height="80%",
            loc="center left",
            borderpad=0.5,
        )
        ax_inset.imshow(favicon)
        ax_inset.set_axis_off()
    except Exception:
        pass
    ax_header.text(
        0.08,
        0.5,
        "MKCentral MKWorld Lounge",
        transform=ax_header.transAxes,
        fontsize=13,
        fontweight="bold",
        color="white",
        verticalalignment="center",
    )
    ax_header.axhline(y=0, color="white", linewidth=0.5, alpha=0.3)

    # --- Title ---
    ax_title = fig.add_subplot(gs[1])
    ax_title.set_axis_off()
    title_text = f"Season{season} : {player_name}"
    if game_mode_display:
        title_text = f"Season{season} ({game_mode_display}) : {player_name}"
    else:
        title_text = f"Season{season} : {player_name}"
    ax_title.text(
        0.5,
        0.5,
        title_text,
        transform=ax_title.transAxes,
        fontsize=11,
        color="white",
        horizontalalignment="center",
        verticalalignment="center",
    )

    # --- Main chart ---
    ax = fig.add_subplot(gs[2])
    xs = np.arange(len(mmrhistory))

    # Glow effect: thick semi-transparent line + thin line on top
    ax.plot(
        mmrhistory,
        color="white",
        linewidth=4.0,
        alpha=0.18,
        solid_capstyle="round",
    )
    ax.plot(mmrhistory, color="snow", linewidth=1.4, solid_capstyle="round")

    xmin, xmax, ymin, ymax = ax.axis()
    ax.set_ylabel("MMR")
    ax.grid(
        True,
        "both",
        "both",
        color="snow",
        linestyle=":",
        alpha=0.25,
        linewidth=0.5,
    )

    # Hide top and right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Smaller tick labels
    ax.tick_params(axis="both", labelsize=8)

    for i in range(len(ranks)):
        if ranks[i] > ymax:
            continue
        maxfill = ymax
        if i + 1 < len(ranks):
            if ranks[i] < ymin and ranks[i + 1] < ymin:
                continue
            if ranks[i + 1] < ymax:
                maxfill = ranks[i + 1]
        if ranks[i] < ymin:
            minfill = ymin
        else:
            minfill = ranks[i]
        if season == 0:
            ax.fill_between(xs, minfill, maxfill, color="#0E0B0B")
        else:
            ax.fill_between(xs, minfill, maxfill, color=colors[i])
    ax.fill_between(xs, ymin, mmrhistory, facecolor="#212121", alpha=0.4)

    # --- Rank milestone & Peak MMR annotations ---
    peak_mmr = max(mmrhistory)
    peak_idx = mmrhistory.index(peak_mmr)

    # Detect first time reaching each rank tier
    highest_rank_idx = -1
    milestones = []  # list of (x, mmr, rank_name)
    for idx, mmr_val in enumerate(mmrhistory):
        rank_name = get_rank(mmr_val, season, game_mode)
        ri = rank_index(rank_name)
        if ri > highest_rank_idx:
            highest_rank_idx = ri
            milestones.append((idx, mmr_val, rank_name))

    # Draw milestone markers (skip the very first point)
    for mx, my, mrank in milestones:
        if mx == 0:
            continue
        ax.plot(mx, my, "o", color="white", markersize=5, zorder=5)
        ax.annotate(
            f"Event #{mx + 1}\n{mrank}",
            xy=(mx, my),
            xytext=(0, 12),
            textcoords="offset points",
            fontsize=6,
            color="white",
            ha="center",
            va="bottom",
            bbox=dict(
                boxstyle="round,pad=0.2",
                facecolor="#0a2d61",
                edgecolor="white",
                alpha=0.7,
                linewidth=0.5,
            ),
        )

    # Peak MMR marker
    ax.plot(peak_idx, peak_mmr, "*", color="#FFD700", markersize=10, zorder=5)
    ax.annotate(
        f"Peak MMR\n{peak_mmr}",
        xy=(peak_idx, peak_mmr),
        xytext=(0, 14),
        textcoords="offset points",
        fontsize=7,
        fontweight="bold",
        color="#FFD700",
        ha="center",
        va="bottom",
        bbox=dict(
            boxstyle="round,pad=0.2",
            facecolor="#0a2d61",
            edgecolor="#FFD700",
            alpha=0.7,
            linewidth=0.5,
        ),
    )

    fig.savefig(b, format="png", bbox_inches="tight", dpi=150)
    b.seek(0)
    fig.clf()

    return b


def create_tiers_plot(
    tier_rows: list,
    season: int,
    player_name: str,
    country_code: str,
    game_mode: str,
):
    """Render a per-tier breakdown as a styled image table.

    tier_rows: list of dicts with keys
        tier, n, win_rate, avg_delta, total, avg_rank, avg_score,
        firsts, podiums, bottoms
    """
    b = BytesIO()

    matplotlib.rcParams.update(
        matplotlib.rc_params_from_file("src/common/lounge_style.mplstyle")
    )

    if game_mode == "12p":
        game_mode_display = "12 player"
    elif game_mode == "24p":
        game_mode_display = "24 player"
    else:
        game_mode_display = game_mode

    headers = [
        "Tier",
        "Events",
        "W%",
        "Avg Δ",
        "Total",
        "Avg Rk",
        "Avg Sc",
        "1sts",
        "Top¼",
        "Btm¼",
    ]

    cell_text = []
    delta_values = []
    for r in tier_rows:
        cell_text.append(
            [
                r["tier"],
                f"{r['n']}",
                f"{r['win_rate']:.0f}%",
                f"{r['avg_delta']:+.0f}",
                f"{r['total']:+d}",
                f"{r['avg_rank']:.1f}",
                f"{r['avg_score']:.1f}",
                f"{r['firsts']}",
                f"{r['tops']}",
                f"{r['bottoms']}",
            ]
        )
        delta_values.append(r["avg_delta"])

    n_rows = len(cell_text)
    row_h = 0.40
    header_h = 0.45
    title_h = 0.30
    table_h = row_h * (n_rows + 1)
    fig_height = header_h + title_h + table_h
    fig = Figure(figsize=(10, fig_height))
    gs = gridspec.GridSpec(
        3,
        1,
        height_ratios=[header_h, title_h, table_h],
        hspace=0.0,
        figure=fig,
    )

    # --- Header ---
    ax_header = fig.add_subplot(gs[0])
    ax_header.set_axis_off()
    try:
        favicon = mpimg.imread("src/common/favicon.ico")
        ax_inset = inset_axes(
            ax_header,
            width="4%",
            height="80%",
            loc="center left",
            borderpad=0.5,
        )
        ax_inset.imshow(favicon)
        ax_inset.set_axis_off()
    except Exception:
        pass
    ax_header.text(
        0.08,
        0.5,
        "MKCentral MKWorld Lounge",
        transform=ax_header.transAxes,
        fontsize=13,
        fontweight="bold",
        color="white",
        verticalalignment="center",
    )
    ax_header.axhline(y=0, color="white", linewidth=0.5, alpha=0.3)

    # --- Title ---
    ax_title = fig.add_subplot(gs[1])
    ax_title.set_axis_off()
    flag = f" [{country_code}]" if country_code else ""
    title_text = f"Season {season} ({game_mode_display}) Tier Data: {player_name}{flag}"
    ax_title.text(
        0.5,
        0.5,
        title_text,
        transform=ax_title.transAxes,
        fontsize=11,
        color="white",
        horizontalalignment="center",
        verticalalignment="center",
    )

    # --- Table ---
    ax = fig.add_subplot(gs[2])
    ax.set_axis_off()

    table = ax.table(
        cellText=cell_text,
        colLabels=headers,
        cellLoc="center",
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)

    n_cols = len(headers)
    avg_delta_col = headers.index("Avg Δ")
    total_col = headers.index("Total")

    for col in range(n_cols):
        header_cell = table[(0, col)]
        header_cell.set_facecolor("#08234a")
        header_cell.set_edgecolor("white")
        header_cell.set_text_props(color="white", fontweight="bold")

    for row_i in range(1, n_rows + 1):
        for col in range(n_cols):
            cell = table[(row_i, col)]
            cell.set_edgecolor("#3a5a8a")
            cell.set_linewidth(0.5)
            cell.set_facecolor("#0a2d61" if row_i % 2 == 1 else "#0d3674")
            cell.set_text_props(color="white")

        for col in (avg_delta_col, total_col):
            val_str = cell_text[row_i - 1][col]
            color = "#7CFF9E" if val_str.startswith("+") else "#FF7C8A"
            if val_str in ("+0", "0"):
                color = "white"
            table[(row_i, col)].set_text_props(color=color, fontweight="bold")

        tier_cell = table[(row_i, 0)]
        tier_cell.set_text_props(color="white", fontweight="bold")

    fig.savefig(b, format="png", bbox_inches="tight", dpi=150, pad_inches=0.1)
    b.seek(0)
    fig.clf()

    return b
