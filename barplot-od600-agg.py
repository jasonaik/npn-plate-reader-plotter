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
    "ICR229+195",
    "ICR213+192",
    "Nterminal Control",
    "IL6 Control",
]

filename = "restructured-OD600-26-04-21"

df = pd.read_csv(f"data/{filename}.csv")

# Ensure consistent construct order
df["construct"] = pd.Categorical(
    df["construct"],
    categories=construct_names,
    ordered=True
)

# Ensure concentration order
# conc_order = ["1", "1/2", "1/4", "1/8", "1/16", "1/32", "1/64", "1/128", "1/256", "1/512", "1/1024", "0"]
    
conc_order = [
        "1/4",
        "1/8",
        "1/12",
        "1/16",
        "1/24",
        "1/32",
        "1/48",
        "1/64",
    ]
    

if "conc" not in df.columns:
    block_size = 8

    # One full cycle (96 values: 12 concs × 8 each)
    one_cycle = np.repeat(conc_order, block_size)

    # Repeat enough times to cover df
    repeats = int(np.ceil(len(df) / len(one_cycle)))

    df["conc"] = np.tile(one_cycle, repeats)[:len(df)]
    
df = df[(df["od600"] >= 0) & (df["od600"] <= 40)]

colors = {
    "dark": "#bfbfbf",
    "light": "#d86ecc",
}

def plot_od600(ax, sub_df, construct_name):
    summary = (
        sub_df.groupby(["conc", "plate"], observed=True)["od600"]
        .agg(mean="mean", sd="std")
        .reset_index()
    )

    mean_p = summary.pivot(index="conc", columns="plate", values="mean")
    sd_p   = summary.pivot(index="conc", columns="plate", values="sd")

    present = [c for c in conc_order if c in mean_p.index]
    mean_p = mean_p.reindex(present)
    sd_p   = sd_p.reindex(present)

    concs = mean_p.index.tolist()
    x = np.arange(len(concs))
    width = 0.36

    # ---- Bars + replicate points ----
    for cond in ["dark", "light"]:
        if cond not in mean_p.columns:
            continue

        xpos = x + (-width/2 if cond == "dark" else width/2)

        ax.bar(
            xpos,
            mean_p[cond].values,
            width,
            yerr=sd_p[cond].values,
            capsize=3,
            label=cond,
            color=colors[cond],
            edgecolor="black",
            linewidth=0.7,
            alpha=0.6,
            error_kw={"elinewidth": 0.7, "capthick": 0.7},
        )

        rng = np.random.default_rng(0)
        jitter_scale = 0.05

        for idx, conc in enumerate(concs):
            vals = sub_df[
                (sub_df["plate"] == cond) &
                (sub_df["conc"] == conc)
            ]["od600"].dropna().values

            if len(vals) == 0:
                continue

            base_x = idx + (-width/2 if cond == "dark" else width/2)
            jitter = rng.normal(0, jitter_scale, size=len(vals))

            ax.scatter(
                np.full(len(vals), base_x) + jitter,
                vals,
                s=25,
                color=colors[cond],
                edgecolor="black",
                linewidth=0.5,
                zorder=3,
            )

    # # ---- Significance: dark vs light at each concentration ----
    # have_both = ("dark" in mean_p.columns) and ("light" in mean_p.columns)
    # if have_both:
    #     ymax = np.nanmax((mean_p + sd_p).to_numpy())
    #     if np.isfinite(ymax):
    #         global_star_y = ymax * 1.15

    #         for gi, conc in enumerate(concs):
    #             vals_dark = sub_df[
    #                 (sub_df["plate"] == "dark") &
    #                 (sub_df["conc"] == conc)
    #             ]["od600"].dropna().values

    #             vals_light = sub_df[
    #                 (sub_df["plate"] == "light") &
    #                 (sub_df["conc"] == conc)
    #             ]["od600"].dropna().values

    #             if len(vals_dark) == 0 or len(vals_light) == 0:
    #                 continue

    #             stat, p = ttest_ind(vals_dark, vals_light, equal_var=False)
    #             stars = p_to_star(p)

    #             if stars == "ns":
    #                 continue

    #             x_center = x[gi]
    #             x1 = x_center - width/2
    #             x2 = x_center + width/2
    #             y = global_star_y

    #             ax.plot(
    #                 [x1, x1, x2, x2],
    #                 [y * 0.98, y, y, y * 0.98],
    #                 lw=1,
    #                 c="black"
    #             )

    #             ax.text(
    #                 (x1 + x2) / 2,
    #                 y * 1.02,
    #                 stars,
    #                 ha="center",
    #                 va="bottom",
    #                 fontsize=11
    #             )

    #         ax.set_ylim(top=global_star_y * 1.15)

    # ---- Labels ----
    ax.set_xticks(x)
    ax.set_xticklabels(concs, rotation=45, ha="right")
    ax.set_ylabel(r"OD$_{600}$")
    ax.set_xlabel("Concentration (mg/mL)")
    ax.set_title(construct_name)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, linestyle="-", linewidth=0.8, alpha=0.4)
    ax.set_axisbelow(True)

date = datetime.date.today()
os.makedirs(f"plots/pdf/{date}", exist_ok=True)
os.makedirs(f"plots/svg/{date}", exist_ok=True)

for construct in construct_names:
    sub_df = df[df["construct"] == construct].copy()
    if sub_df.empty:
        continue

    fig, ax = plt.subplots(figsize=(8, 5))

    plot_od600(ax, sub_df, construct)

    ax.legend(frameon=False, fontsize=11, loc="center left", bbox_to_anchor=(1, 0.5))

    plt.tight_layout()
    plt.show()

    safe_name = construct.replace(" ", "_").replace("/", "_")

    fig.savefig(
        f"plots/pdf/{date}/od600_{safe_name}_{filename}.pdf",
        bbox_inches="tight",
        dpi=300,
        transparent=True
    )

    fig.savefig(
        f"plots/svg/{date}/od600_{safe_name}_{filename}.svg",
        bbox_inches="tight",
        dpi=300,
        transparent=True
    )

    plt.close(fig)