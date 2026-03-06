import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import datetime
import os

construct_names=[
    "Empty Vector Control", 
    "Pore Only Control",
    "ICR183+189",
    "ICR187+190"
]

colors = {
    0:  "#bfbfbf",
    10: "#0072B2",
}

filename = "violet-light-dark-only"

df = pd.read_csv(f"data/{filename}.csv")

for name in construct_names:
    
    # raw data (for actual points)
    raw_subset = df[df["construct"] == name]
    
    # grouped summary
    summary = raw_subset.groupby(["time_s", "npn_mM"])["normalized_fluo"]\
        .agg(mean="mean", sd="std").reset_index()
    
    for npn_mM in summary["npn_mM"].unique():
        
        npn_summary = summary[summary["npn_mM"] == npn_mM]
        npn_raw = raw_subset[raw_subset["npn_mM"] == npn_mM]

        # mean line + error bars
        plt.errorbar(
            npn_summary["time_s"],
            npn_summary["mean"],
            yerr=npn_summary["sd"],
            marker='o',
            capsize=3,
            label=f"{npn_mM} mM NPN",
            color=colors[npn_mM]
        )

        # actual points
        plt.scatter(
            npn_raw["time_s"],
            npn_raw["normalized_fluo"],
            alpha=0.4,
            s=20,
            color=colors[npn_mM]
        )
        
    plt.xlabel("Time (s)")
    plt.ylabel("Normalized Fluorescence (450 nm)")
    plt.title(f"{name} - Violet Light - Dark Only")
    
    plt.legend(frameon=False, fontsize=12, loc="center left", bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    ax = plt.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, linestyle="-", linewidth=0.8, alpha=0.4)
    ax.set_axisbelow(True)
    
    plt.show()
    date = datetime.date.today()

    os.makedirs(f"plots/pdf/{date}", exist_ok=True)
    os.makedirs(f"plots/svg/{date}", exist_ok=True)

    plt.savefig(
            f"plots/pdf/{date}/450-{filename}.pdf",
            bbox_inches="tight",   # trims white space
            dpi=300,               # for raster elements (still vector overall)
            transparent=True       # if you want transparent background
        )