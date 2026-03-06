import pandas as pd

df = pd.read_csv("data\\05-03-ICR193-195-196.csv")

# 10mM NPN comparison between light and dark plates, at 15 minutes for light and 5 minutes for dark
# df.query("(plate == 'Dark' and Incubation_min == 5 and NPN_mM == 10) or (plate == 'Light' and Incubation_min == 15 and NPN_mM == 10)", inplace=True)

# 10mM NPN comparison between light and dark plates, at 5 minutes for both
# df.query("(plate == 'Dark' and Incubation_min == 5 and NPN_mM == 10) or (plate == 'Light' and Incubation_min == 5 and NPN_mM == 10)", inplace=True)

# # dark plate only
# df.query("plate == 'dark'", inplace=True)

# # light plate only
# df.query("plate == 'Light'", inplace=True)

# df.loc[df["plate"] == "Dark", "plate"] = "dark"
# df.loc[df["plate"] == "Light", "plate"] = "light"

# df.loc[df["construct"] == "Empty vector control", "construct"] = "Empty Vector Control"
# df.loc[df["construct"] == "Pore only control", "construct"] = "Pore Only Control"

# df["normalized_fluo"] = df["Raw355_2"] / df["Abs600"]

df = df [df["od600"] > 0.03]

df.to_csv("data\\05-03-ICR193-195-196-no-out.csv", index=False)   
