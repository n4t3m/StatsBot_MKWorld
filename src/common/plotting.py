import matplotlib

matplotlib.use("Agg")

from io import BytesIO

import matplotlib.gridspec as gridspec
import matplotlib.image as mpimg
import matplotlib.patches
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


def create_h2h_plot(
    stats: dict,
    season: int,
    game_mode: str,
):
    """Render a head-to-head comparison as a styled image.

    stats keys:
        p1_name, p2_name, p1_country, p2_country,
        p1_mmr, p2_mmr,
        shared, teammate_count, opponent_count,
        teammate_wins, teammate_losses,
        p1_beats_p2, p2_beats_p1, ties,
        p1_avg_score, p2_avg_score,
        p1_avg_rank, p2_avg_rank,
        p1_outscored, p2_outscored,
        p1_mmr_delta, p2_mmr_delta,
        p1_biggest_win, p2_biggest_win  (each: dict with date, tier,
            game_mode, my_score, other_score, or None),
        recent (list of dicts: date, tier, side, p1_score, p1_delta,
                p2_score, p2_delta, p1_rank, p2_rank)
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

    p1, p2 = stats["p1_name"], stats["p2_name"]
    recent = stats["recent"]

    # --- Layout sizing ---
    header_h = 0.45
    title_h = 0.30
    body_h = 2.6  # player columns flanking the H2H block
    highlight_h = 1.0
    recent_rows = len(recent)
    recent_h = 0.40 * (recent_rows + 1) if recent_rows else 0.0

    fig_height = header_h + title_h + body_h + highlight_h + recent_h + 0.4
    fig = Figure(figsize=(11, fig_height))
    gs = gridspec.GridSpec(
        5,
        1,
        height_ratios=[
            header_h,
            title_h,
            body_h,
            highlight_h,
            max(recent_h, 0.001),
        ],
        hspace=0.18,
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
    title_text = f"Season {season} ({game_mode_display}) Head-to-Head"
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

    # --- Body: P1 stats | center H2H | P2 stats ---
    gs_body = gs[2].subgridspec(1, 3, width_ratios=[1, 1, 1], wspace=0.05)

    def _draw_player_column(ax, name, country, mmr, avg_score, avg_rank, mmr_delta):
        ax.set_axis_off()
        flag = f" [{country}]" if country else ""
        ax.text(
            0.5, 0.93, f"{name}{flag}",
            transform=ax.transAxes, ha="center", va="center",
            color="white", fontsize=14, fontweight="bold",
        )
        if mmr is not None:
            ax.text(
                0.5, 0.83, f"{mmr:,} mmr",
                transform=ax.transAxes, ha="center", va="center",
                color="#9CCBD6", fontsize=9,
            )
        # Stat 1: avg score
        ax.text(
            0.5, 0.62, f"{avg_score:.2f}",
            transform=ax.transAxes, ha="center", va="center",
            color="white", fontsize=20, fontweight="bold",
        )
        ax.text(
            0.5, 0.52, "avg score",
            transform=ax.transAxes, ha="center", va="center",
            color="#9CCBD6", fontsize=9,
        )
        # Stat 2: avg placement
        ax.text(
            0.5, 0.36, f"{avg_rank:.2f}",
            transform=ax.transAxes, ha="center", va="center",
            color="white", fontsize=20, fontweight="bold",
        )
        ax.text(
            0.5, 0.26, "avg placement",
            transform=ax.transAxes, ha="center", va="center",
            color="#9CCBD6", fontsize=9,
        )
        # Stat 3: mmr delta
        delta_color = (
            "#7CFF9E" if mmr_delta > 0
            else ("#FF7C8A" if mmr_delta < 0 else "white")
        )
        ax.text(
            0.5, 0.10, f"{mmr_delta:+,d}",
            transform=ax.transAxes, ha="center", va="center",
            color=delta_color, fontsize=20, fontweight="bold",
        )
        ax.text(
            0.5, 0.00, "mmr delta",
            transform=ax.transAxes, ha="center", va="center",
            color="#9CCBD6", fontsize=9,
        )

    ax_p1 = fig.add_subplot(gs_body[0])
    _draw_player_column(
        ax_p1, p1, stats.get("p1_country", ""), stats.get("p1_mmr"),
        stats["p1_avg_score"], stats["p1_avg_rank"], stats["p1_mmr_delta"],
    )

    ax_center = fig.add_subplot(gs_body[1])
    ax_center.set_axis_off()
    h2h_str = (
        f"{stats['p1_beats_p2']}-{stats['ties']}-{stats['p2_beats_p1']}"
    )
    ax_center.text(
        0.5, 0.62, h2h_str,
        transform=ax_center.transAxes, ha="center", va="center",
        color="white", fontsize=28, fontweight="bold",
    )
    ax_center.text(
        0.5, 0.48, "head-to-head record",
        transform=ax_center.transAxes, ha="center", va="center",
        color="white", fontsize=11,
    )
    sub_caption = (
        f"S{season} · {game_mode_display} · "
        f"{stats['shared']} opponent match"
        + ("es" if stats["shared"] != 1 else "")
    )
    ax_center.text(
        0.5, 0.36, sub_caption,
        transform=ax_center.transAxes, ha="center", va="center",
        color="#9CCBD6", fontsize=8,
    )

    ax_p2 = fig.add_subplot(gs_body[2])
    _draw_player_column(
        ax_p2, p2, stats.get("p2_country", ""), stats.get("p2_mmr"),
        stats["p2_avg_score"], stats["p2_avg_rank"], stats["p2_mmr_delta"],
    )

    # --- Highlight cards: biggest win per player ---
    gs_high = gs[3].subgridspec(1, 2, wspace=0.04)

    def _short(n, max_len=12):
        return n if len(n) <= max_len else n[: max_len - 1] + "…"

    def _draw_highlight(ax, owner, win, other):
        ax.set_axis_off()
        ax.add_patch(
            matplotlib.patches.FancyBboxPatch(
                (0.01, 0.05), 0.98, 0.9,
                boxstyle="round,pad=0.01,rounding_size=0.02",
                linewidth=0.8,
                edgecolor="#3a5a8a",
                facecolor="#0a2d61",
                transform=ax.transAxes,
            )
        )
        ax.text(
            0.04, 0.78, f"{owner}'s biggest score differential",
            transform=ax.transAxes, ha="left", va="center",
            color="white", fontsize=11, fontweight="bold",
        )
        if win:
            meta_parts = [win["date"], f"tier {win['tier']}"]
            if win.get("table_id") is not None:
                meta_parts.append(f"table {win['table_id']}")
            ax.text(
                0.04, 0.50, " · ".join(meta_parts),
                transform=ax.transAxes, ha="left", va="center",
                color="#9CCBD6", fontsize=9,
            )
            line = (
                f"{_short(owner)} scored {win['my_score']} vs "
                f"{_short(other)}'s {win['other_score']}  "
                f"(+{win['diff']} diff)"
            )
            ax.text(
                0.04, 0.22, line,
                transform=ax.transAxes, ha="left", va="center",
                color="white", fontsize=9,
            )
        else:
            ax.text(
                0.04, 0.40, "No matches where this player outscored the other.",
                transform=ax.transAxes, ha="left", va="center",
                color="#9CCBD6", fontsize=9,
            )

    ax_h1 = fig.add_subplot(gs_high[0])
    _draw_highlight(ax_h1, p1, stats.get("p1_biggest_win"), p2)
    ax_h2 = fig.add_subplot(gs_high[1])
    _draw_highlight(ax_h2, p2, stats.get("p2_biggest_win"), p1)

    # --- Recent matches ---
    if recent:
        ax_rec = fig.add_subplot(gs[4])
        ax_rec.set_axis_off()
        n1, n2 = _short(p1, 10), _short(p2, 10)
        rec_headers = [
            "Date",
            "Tier",
            f"{n1}\nScore (Δ)",
            f"{n2}\nScore (Δ)",
            f"{n1}\nRank",
            f"{n2}\nRank",
        ]
        rec_cells = []
        for r in recent:
            rec_cells.append(
                [
                    r["date"],
                    r["tier"],
                    f"{r['p1_score']} ({r['p1_delta']:+d})",
                    f"{r['p2_score']} ({r['p2_delta']:+d})",
                    f"{r['p1_rank']}",
                    f"{r['p2_rank']}",
                ]
            )
        rec_table = ax_rec.table(
            cellText=rec_cells,
            colLabels=rec_headers,
            cellLoc="center",
            bbox=[0, 0, 1, 1],
        )
        rec_table.auto_set_font_size(False)
        rec_table.set_fontsize(10)
        n_cols = len(rec_headers)
        for col in range(n_cols):
            h = rec_table[(0, col)]
            h.set_facecolor("#08234a")
            h.set_edgecolor("white")
            h.set_text_props(color="white", fontweight="bold")
        for row_i in range(1, len(rec_cells) + 1):
            for col in range(n_cols):
                cell = rec_table[(row_i, col)]
                cell.set_edgecolor("#3a5a8a")
                cell.set_linewidth(0.5)
                cell.set_facecolor("#0a2d61" if row_i % 2 == 1 else "#0d3674")
                cell.set_text_props(color="white")
            # color delta values in score columns
            for col, key in ((2, "p1_delta"), (3, "p2_delta")):
                delta = recent[row_i - 1][key]
                if delta > 0:
                    rec_table[(row_i, col)].set_text_props(
                        color="#7CFF9E", fontweight="bold"
                    )
                elif delta < 0:
                    rec_table[(row_i, col)].set_text_props(
                        color="#FF7C8A", fontweight="bold"
                    )

    fig.savefig(b, format="png", bbox_inches="tight", dpi=150, pad_inches=0.1)
    b.seek(0)
    fig.clf()

    return b
