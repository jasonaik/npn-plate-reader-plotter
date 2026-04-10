import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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

construct_names = [
        "ICR73",
        "Empty Vector Control",
        "Pore Only Control",
        "ICR183+189",
        "ICR187+190",
        "ICR229+195",
        "ICR183+198",
        "ICR187+198",
    ]

filename = "restructured-OD600-jsa50-26-03-dark.csv"

df = pd.read_csv(f"data/{filename}")

# Ensure consistent construct order
df["construct"] = pd.Categorical(
    df["construct"],
    categories=construct_names,
    ordered=True
)

# Ensure concentration order is correct
conc_order = ["1", "1/2", "1/4", "1/8", "1/16", "1/32", "1/64", "1/128", "1/256", "1/512", "1/1024", "0"]
df["conc"] = pd.Categorical(df["conc"].astype(str), categories=conc_order, ordered=True)

date = datetime.date.today()
os.makedirs(f"plots/pdf/{date}", exist_ok=True)
os.makedirs(f"plots/svg/{date}", exist_ok=True)

def plot_construct_od600(ax, sub_df, construct_name):
    summary = (
        sub_df.groupby("conc", observed=True)["od600"]
        .agg(mean="mean", sd="std")
        .reset_index()
    )

    summary = summary.sort_values("conc")
    x = np.arange(len(summary))

    ax.bar(
        x,
        summary["mean"],
        yerr=summary["sd"],
        capsize=3,
        color="#d86ecc",
        edgecolor="black",
        linewidth=0.7,
        alpha=0.7,
        error_kw={"elinewidth": 0.7, "capthick": 0.7},
    )

    # replicate points
    rng = np.random.default_rng(0)
    jitter_scale = 0.05

    for i, conc in enumerate(summary["conc"]):
        vals = sub_df[sub_df["conc"] == conc]["od600"].dropna().values
        if len(vals) == 0:
            continue

        jitter = rng.normal(0, jitter_scale, size=len(vals))
        ax.scatter(
            np.full(len(vals), i) + jitter,
            vals,
            s=25,
            color="white",
            edgecolor="black",
            linewidth=0.6,
            zorder=3,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(summary["conc"].astype(str), rotation=45, ha="right")
    ax.set_ylabel(r"OD$_{600}$")
    ax.set_xlabel("Concentration (mg/mL)")
    ax.set_title(construct_name, fontsize=14)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, linestyle="-", linewidth=0.8, alpha=0.4)
    ax.set_axisbelow(True)

for construct in construct_names:
    sub_df = df[df["construct"] == construct].copy()
    if sub_df.empty:
        continue

    fig, ax = plt.subplots(figsize=(7, 5))
    plot_construct_od600(ax, sub_df, construct)
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