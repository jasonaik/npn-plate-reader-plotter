import pandas as pd
import numpy as np

def restructure_csv_1(filename, construct_names, concs, reps_per_construct, plate):

    df = pd.read_csv(filename, skiprows=5)

    df = df.rename(columns={0: "od600"})

    # df["od600"] = df["od600"].str.split().str[1]  

    df["construct"] = [name for name in construct_names for _ in range(reps_per_construct)]

    df["conc"] = concs * 8
    
    df["plate"] = plate

    df.to_csv(f"data/restructured-{filename.split('/')[-1]}", index=False)
    
def restructure_csv_2(filename, construct_names, concs, reps_per_construct, plate):
    # 1. Load the file (skip metadata rows at the top)
    df = pd.read_csv(filename, skiprows=5)
    
    # 2. Keep only the OD600 column
    df_od = df[["Raw Data (600 1)", "Well"]]

    # 3. Rename the column
    df_od = df_od.rename(columns={"Raw Data (600 1)": "od600"})
        
    df_od["construct"] = [name for name in construct_names for _ in range(reps_per_construct)]

    # If you are doing multiple conc series, omit if you are doing just one conc 
    df_od["conc"] = concs * len(construct_names)
    
    df_od["plate"] = plate

    return df_od

def restructure_csv_3(filename, construct_names, concs, reps_per_construct, plate):
    # 1. Load the file (skip metadata rows at the top)
    df = pd.read_csv(filename, skiprows=5)
    
    # 2. Keep only the OD600 column
    df_od = df[["Raw Data (600 1)", "Well"]]

    # 3. Rename the column
    df_od = df_od.rename(columns={"Raw Data (600 1)": "od600"})
        
    df_od["construct"] = construct_names * len(concs)
    df_od["conc"] = [conc for conc in concs for _ in range(len(construct_names))]
    
    df_od["plate"] = plate

    return df_od

if __name__ == "__main__":

    # construct_names = [
    #     "Empty Vector Control",
    #     "Pore Only Control",
    #     "ICR183+189",
    #     "ICR187+190",
    #     "ICR229+195",
    #     "ICR183+198",
    #     "ICR187+198",
    #     "ICR206+191",
    # ]
    
    construct_names = [ 
        "Empty Vector Control",
        "Empty Vector Control",
        "Pore Only Control",
        "Pore Only Control",
        "ICR229+195",
        "ICR229+195",
        "ICR213+192",
        "ICR213+192",
        "Nterminal Control",
        "Nterminal Control",
        "IL6 Control",
        "IL6 Control",
    ]
    

    # concs = [
    #     "1",
    #     "1/2",
    #     "1/4",
    #     "1/8",
    #     "1/16",
    #     "1/32",
    #     "1/64",
    #     "1/128",
    #     "1/256",
    #     "1/512",
    #     "1/1024",
    #     "0",
    # ]
    
    concs = [
        "1/4",
        "1/8",
        "1/12",
        "1/16",
        "1/24",
        "1/32",
        "1/48",
        "1/64",
    ]
    
    dark_filename = "raw-data/2026-04-21-dark.CSV"
    light_filename = "raw-data/2026-04-21-light.CSV"
    
    reps_per_construct = 8
    
    dark = restructure_csv_3(dark_filename, construct_names, concs, reps_per_construct, plate="dark")
    # dark.loc[(dark["plate"] == "dark") & (dark["od600"] > 0.1), "od600"] *= 8
    
    light = restructure_csv_3(light_filename, construct_names, concs, reps_per_construct, plate="light")
    
    combined = pd.concat([dark, light], ignore_index=True)
    combined.to_csv("data/restructured-OD600-26-04-21.csv", index=False)
    
    # combined = restructure_csv_2("raw-data/09-04-26-od600-8fold-dilution-both-long.csv", construct_names, concs, reps_per_construct, light_condition="light")
    
    # n = len(combined)
    
    # combined["plate"] = np.where(combined.index < n/2, "violet_light", "violet_dark")
    
    # combined = combined[combined["construct"] != "Empty"]  # Remove empty rows if they exist
    
    # combined["od600"] = combined["od600"] * 8
    
    # combined.to_csv("data/restructured-09-04-26-od600-8fold-dilution-both-long.csv", index=False)