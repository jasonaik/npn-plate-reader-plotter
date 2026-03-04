import pandas as pd

df = pd.read_csv("raw-data/blue-light.csv")

# 10mM NPN comparison between light and dark plates, at 15 minutes for light and 5 minutes for dark
# df.query("(plate == 'Dark' and Incubation_min == 5 and NPN_mM == 10) or (plate == 'Light' and Incubation_min == 15 and NPN_mM == 10)", inplace=True)

# 10mM NPN comparison between light and dark plates, at 5 minutes for both
# df.query("(plate == 'Dark' and Incubation_min == 5 and NPN_mM == 10) or (plate == 'Light' and Incubation_min == 5 and NPN_mM == 10)", inplace=True)

# # dark plate only
# df.query("plate == 'dark'", inplace=True)

# light plate only
df.query("plate == 'Light'", inplace=True)

df.to_csv("raw-data/blue-light.csv", index=False)   
