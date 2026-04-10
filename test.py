import pandas as pd

df = pd.read_csv("data\\26-04-08-second-half-rep-1-restructured.csv")

df = df[["construct", "plate", "od600"]]

df.loc[df["plate"] == "light", "plate"] = "blue_light"
df.loc[df["plate"] == "dark", "plate"] = "blue_dark"

df.to_csv("data\\26-04-08-second-half-rep-1-restructured-long.csv", index=False)

blue = pd.read_csv("data\\26-04-08-second-half-rep-1-restructured-long.csv")
violet = pd.read_csv("data\\restructured-09-04-26-od600-8fold-dilution-both-long.csv")

combined = pd.concat([blue, violet], ignore_index=True)
combined.to_csv("data\\26-04-09-combined.csv", index=False)