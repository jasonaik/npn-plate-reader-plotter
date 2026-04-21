import pandas as pd
import numpy as np

concs = [
    "1",
    "1/2",
    "1/4",
    "1/8",
    "1/16",
    "1/32",
    "1/64",
    "0",
    "1",
    "1/2",
    "1/4",
    "1/8",
    "1/16",
    "1/32",
    "1/64",
    "0",
]

df = pd.read_csv("data\\restructured-OD600-26-04-19.csv")

idx = np.arange(len(df))
mask = idx % 12 >= 10
group = idx // 12

valid = mask & (group < len(concs))

df.loc[valid, 'conc'] = np.array(concs)[group[valid]]

df.loc[mask, "construct"] = "Blocked Pore Control"


zero_mask = df.index % 12 == 9
df.loc[zero_mask, "conc"] = 0

# df = df[["construct", "plate", "od600"]]

# df.loc[df["plate"] == "light", "plate"] = "blue_light"
# df.loc[df["plate"] == "dark", "plate"] = "blue_dark"

# df.to_csv("data\\26-04-08-second-half-rep-1-restructured-long.csv", index=False)

# blue = pd.read_csv("data\\26-04-08-second-half-rep-1-restructured-long.csv")
# violet = pd.read_csv("data\\restructured-09-04-26-od600-8fold-dilution-both-long.csv")

# combined = pd.concat([blue, violet], ignore_index=True)

df.to_csv("data\\restructured-OD600-26-04-19-edited.csv", index=False)