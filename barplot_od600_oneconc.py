import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import datetime
import os

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial"],  
    "font.size": 10,                   
    "axes.labelsize": 12,
    "axes.titlesize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})

def p_to_star(p):
    if p < 0.0001:
        return "****"
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"

construct_names = [
        "Empty Vector Control",
        "Pore Only Control",
        "ICR213+192",
        "ICR219+193",
        "ICR225+194",
        "ICR226+194",
        "ICR235+194",
        "ICR237+196",
        "ICR216+192",
        "ICR223+194",
        "ICR227+194",
        "ICR228+194",
        "ICR229+195",
]

filename = "26-04-09-combined"

df = pd.read_csv(f"data/{filename}.csv")

# ---- Custom colours ----
colors = {
    "blue_dark":  "#bfbfbf",
    "blue_light": "#d86ecc",
    "violet_dark": "#5a5a5a",
    "violet_light": "#FF00E1",
    
}

def plot_metric(ax, metric_name, title):
    summary = (
        df.groupby(["construct", "plate"], observed=True)[metric_name]
          .agg(mean="mean", sd="std")
          .reset_index()
    )

    mean_p = summary.pivot(index="construct", columns="plate", values="mean")
    sd_p   = summary.pivot(index="construct", columns="plate", values="sd")

    present = [c for c in construct_names if c in mean_p.index]
    mean_p = mean_p.reindex(present)
    sd_p   = sd_p.reindex(present)

    constructs = mean_p.index.tolist()
    x = np.arange(len(constructs))
    width = 0.18
    
    plate_order = ["blue_dark", "blue_light", "violet_dark", "violet_light"]
    
    offsets = {
            "blue_dark":   -1.7 * width,
            "blue_light":  -0.7 * width,
            "violet_dark":  0.7 * width,
            "violet_light": 1.7 * width,
        }
    
    for plate in plate_order:
        
        if plate not in mean_p.columns:
            continue
        
        xpos = x + offsets[plate]

        ax.bar(
            xpos,
            mean_p[plate].values,
            width,
            yerr=sd_p[plate].values,
            capsize=3,
            label=plate,
            color=colors[plate],
            edgecolor="black",
            linewidth=0.7,
            alpha=0.6,
            error_kw={"elinewidth": 0.7, "capthick": 0.7},
        )

        rng = np.random.default_rng(0)
        jitter_scale = 0.05

        for idx, c in enumerate(constructs):
            sub = df[(df["plate"] == plate) & (df["construct"] == c)][metric_name].dropna().values
            if len(sub) == 0:
                continue

            base_x = idx + offsets[plate]
            jitter = rng.normal(0, jitter_scale, size=len(sub))

            ax.scatter(
                np.full_like(sub, base_x, dtype=float) + jitter,
                sub,
                s=25,
                color=colors[plate],
                edgecolor="black",
                linewidth=0.5,
                zorder=3,
            )

    # # ---- Significance (dark vs light per construct) ----
    # have_both = ("dark" in mean_p.columns) and ("light" in mean_p.columns)
    # if have_both:
    #     # Top baseline for brackets (similar to your global_star_y idea)
    #     # Use mean+sd; ignore NaNs safely.
    #     global_star_y = np.nanmax((mean_p + sd_p).to_numpy()) * 1.15

    #     for gi, c in enumerate(constructs):
    #         vals_dark = df[(df["plate"] == "dark") & (df["construct"] == c)][metric_name].dropna().values
    #         vals_light = df[(df["plate"] == "light") & (df["construct"] == c)][metric_name].dropna().values

    #         # Need both groups and at least 2 total points to test; you can tighten this if you want
    #         if len(vals_dark) == 0 or len(vals_light) == 0:
    #             continue

    #         stat, p = ttest_ind(vals_dark, vals_light, equal_var=False)  # Welch's t-test
    #         stars = p_to_star(p)
    #         if stars == "ns":
    #             continue

    #         # x positions for the bracket
    #         x_center = x[gi]
    #         x1 = x_center - width / 2
    #         x2 = x_center + width / 2

    #         y = global_star_y

    #         # bracket
    #         ax.plot([x1, x1, x2, x2],
    #                 [y * 0.98, y, y, y * 0.98],
    #                 lw=1, c="black")

    #         # stars
    #         ax.text((x1 + x2) / 2, y * 1.02, stars,
    #                 ha="center", va="bottom", fontsize=11)

    #     ax.set_ylim(top=global_star_y * 1.15)

    # ---- Labels ----
    ax.set_xticks(x)
    ax.set_xticklabels(constructs, rotation=45, ha="right")
    ax.set_ylabel(metric_name)
    ax.set_title(title)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, linestyle="-", linewidth=0.8, alpha=0.4)
    ax.set_axisbelow(True)


# ---- Plot 1: 450 nm ----
fig1, ax1 = plt.subplots(
    figsize=(max(10, len(construct_names)*0.6), 5)
)

plot_metric(
    ax1,
    "od600",
    "Dark vs Light (OD600)"
)

ax1.legend(frameon=False, fontsize=12, loc="center left", bbox_to_anchor=(1, 0.5))
ax1.set_ylabel(r"OD$_{600}$")
plt.tight_layout()
plt.show()

date = datetime.date.today()

os.makedirs(f"plots/pdf/{date}", exist_ok=True)
os.makedirs(f"plots/svg/{date}", exist_ok=True)

fig1.savefig(
        f"plots/pdf/{date}/450-{filename}.pdf",
        bbox_inches="tight",   # trims white space
        dpi=300,               # for raster elements (still vector overall)
        transparent=True       # if you want transparent background
    )

fig1.savefig(
        f"plots/svg/{date}/450-{filename}.svg",
        bbox_inches="tight",   # trims white space
        dpi=300,               # for raster elements (still vector overall)
        transparent=True       # if you want transparent background
    )


# # ---- Plot 2: 405 nm ----
# fig2, ax2 = plt.subplots(
#     figsize=(max(10, len(construct_names)*0.6), 5)
# )

# plot_metric(
#     ax2,
#     "normalized_fluo_405",
#     "Dark vs Light (405nm Normalized Fluorescence)"
# )

# ax2.legend(frameon=False)
# plt.tight_layout()
# plt.show()

# fig2.savefig(
#         f"plots/pdf/{date}/405-{filename}.pdf",
#         bbox_inches="tight",   # trims white space
#         dpi=300,               # for raster elements (still vector overall)
#         transparent=True       # if you want transparent background
#     )

# fig2.savefig(
#         f"plots/svg/{date}/405-{filename}.svg",
#         bbox_inches="tight",   # trims white space
#         dpi=300,               # for raster elements (still vector overall)
#         transparent=True       # if you want transparent background
#     )

