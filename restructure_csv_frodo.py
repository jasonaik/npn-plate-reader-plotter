import pandas as pd
import sys

def extract_raw_blocks(path: str):
    """
    Extract each 8-row A–H plate block following
    each 'Raw Data' marker section in the CSV.
    Does NOT rely on specific column names.
    """

    # df = pd.read_csv(path, skiprows=2)
    df = pd.read_csv(path, skiprows=7)

    # Always treat first column by position
    first_col = df.iloc[:, 0]

    # Find marker rows like "1. Raw Data"
    marker_mask = (
        first_col.astype(str)
        .str.match(r"^\d+\.\s*Raw Data", na=False)
    )

    markers = df.index[marker_mask].tolist()

    boundaries = [-1] + markers + [len(df)]
    blocks = []

    for i in range(len(boundaries) - 1):
        start = boundaries[i] + 1
        end = boundaries[i + 1]

        block = df.iloc[start:end].copy()

        # Filter rows where first column is A–H
        block = block[
            block.iloc[:, 0].isin(list("ABCDEFGH"))
        ].iloc[:8]
        
        block = block.rename(columns={"Unnamed: 0": "row"})

        # Drop extra unnamed columns automatically
        block = block.loc[:, ~block.columns.str.contains("^Unnamed")]

        if len(block) == 0:
            continue

        blocks.append(block)

    return blocks
        

def wide_to_long(
    plate_df: pd.DataFrame,
    plate_name: str,
    row_map: dict,
    construct_names: list,
    reps_per_construct: int = 3,
    value_name: str = "value",
):
    df = plate_df.copy()

    # Keep only the rows you want
    df = df[df["row"].isin(row_map.keys())].copy()

    # Plate columns (96-well reader: 1–12)
    plate_cols = [str(i) for i in range(1, 13)]
    df = df[["row"] + plate_cols].copy()

    # Coerce numeric
    for c in plate_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Wide -> long
    long = df.melt(id_vars=["row"], var_name="col", value_name=value_name)
    long["col"] = long["col"].astype(int)

    # --- Row-major construct mapping (A1-3, A4-6, ..., then B1-3, ...) ---
    rows_order = list("ABCDEFGH")
    row_to_idx = {r: i for i, r in enumerate(rows_order)}

    blocks_per_row = 12 // reps_per_construct  # e.g. 4 blocks when reps_per_construct=3

    long["block_in_row"] = (long["col"] - 1) // reps_per_construct           # 0..blocks_per_row-1
    long["replicate"]   = ((long["col"] - 1) % reps_per_construct) + 1       # 1..reps_per_construct
    long["row_idx"]     = long["row"].map(row_to_idx)

    long["construct_index"] = long["row_idx"] * blocks_per_row + long["block_in_row"]

    mapping = dict(enumerate(construct_names))
    long["construct"] = long["construct_index"].map(mapping)

    # Drop wells beyond provided construct list
    long = long[long["construct"].notna()].copy()

    # Add identifiers
    long["plate"] = plate_name
    long["well"] = long["row"] + long["col"].astype(str)

    # Add row conditions safely
    long["npn_mM"] = long["row"].map(lambda r: row_map[r]["npn_mM"])
    long["time_label"] = long["row"].map(lambda r: row_map[r]["time_label"])
    long["time_s"] = long["row"].map(lambda r: row_map[r].get("time_s", pd.NA))

    # Clean up temp columns
    long = long.drop(columns=["block_in_row", "row_idx", "construct_index"])

    return long


def build_plate_long_with_raw(path: str, plate_name: str, row_map: dict, construct_names: list, num_reps: int = 3, value_names: list = ["od600", "raw_fluo_1", "raw_fluo_2"]) -> pd.DataFrame:
    """
    Uses:
      block 1 = OD600 (600 1)   -> od600
      block 2 = raw fluoresc 1  -> raw_fluo_1
      block 3 = raw fluoresc 2  -> raw_fluo_2
    Then computes normalized_fluo = raw_fluo_1 / od600
    And reorders columns so all numbers are at the right.
    """
    blocks = extract_raw_blocks(path)

    # Expecting at least 3 blocks in your files
    # If fewer exist, the missing columns will just remain NaN.
    out = None

    # block 1: OD600
    if len(blocks) >= 1:
        out = wide_to_long(blocks[0], plate_name, row_map, construct_names, num_reps, value_name=value_names[0])
    else:
        raise ValueError(f"No Raw Data blocks found in {path}")

    # block 2: raw fluorescence (355-15 2)
    if len(blocks) >= 2:
        raw1 = wide_to_long(blocks[1], plate_name, row_map, construct_names, num_reps, value_name=value_names[1])
        out = out.merge(raw1, on="well", how="left")

    # block 3: raw fluorescence (355-15 3)
    if len(blocks) >= 3:
        raw2 = wide_to_long(blocks[2], plate_name, row_map, construct_names, num_reps, value_name=value_names[2])
        out = out.merge(raw2, on="well", how="left")

    # normalized fluorescence
    out["normalized_fluo_450"] = round(out["raw_fluo_1"] / out["od600"])
    out["normalized_fluo_405"] = round(out["raw_fluo_2"] / out["od600"])

    # reorder: metadata first, numbers on the far right
    meta_cols = ["plate", "well", "row", "col", "construct", "replicate", "npn_mM", "time_label", "time_s"]
    meas_cols = ["od600", "raw_fluo_1", "raw_fluo_2", "normalized_fluo_450", "normalized_fluo_405"]
    out = out[meta_cols + meas_cols]

    return out
    
if __name__ == "__main__":
    
    row_map={
            "A": {"npn_mM": 0.03125, "time_label": 15, "time_s": 15*60},
            "B": {"npn_mM": 0.03125, "time_label": 15, "time_s": 15*60},
            "C": {"npn_mM": 0.03125, "time_label": 15, "time_s": 15*60},
            "D": {"npn_mM": 0.03125, "time_label": 15, "time_s": 15*60},
            "E": {"npn_mM": 0.03125, "time_label": 15, "time_s": 15*60},
            "F": {"npn_mM": 0.03125, "time_label": 15, "time_s": 15*60},
            "G": {"npn_mM": 0.03125, "time_label": 15, "time_s": 15*60},
            "H": {"npn_mM": 0.03125, "time_label": 15, "time_s": 15*60},
        }
      
    # construct_names=[
    #         "Empty Vector Control", 
    #         "Pore Only Control",
    #         "ICR183+189",
    #         "ICR187+190",
    #     ]  
    construct_names=[
            "Empty Vector Control", 
            "Pore Only Control",
            "ICR211+192",
            "ICR212+192",
            "ICR213+192",
            "ICR214+192",
            "ICR215+192",
            "ICR216+192",   
            "ICR235+196",
            "ICR236+196",
            "ICR237+196",
            "ICR238+196",
            "ICR239+196",
            "ICR240+196",
        ]
    
    # construct_names = [
    #     "Empty Vector Control",
    #     "Empty Vector Control",
    #     "Empty Vector Control",
    #     "Empty Vector Control",
    #     "Empty Vector Control",
    #     "Empty Vector Control",
    #     "Empty Vector Control",
    #     "Empty Vector Control",
    #     "Pore Only Control",
    #     "Pore Only Control",
    #     "Pore Only Control",
    #     "Pore Only Control",
    #     "Pore Only Control",
    #     "Pore Only Control",      
    #     "Pore Only Control",
    #     "Pore Only Control",
    #     "Pore Only Control",
    #     "Pore Only Control",
    #     "Pore Only Control",
    #     "Pore Only Control",           
    #     "ICR229+195",
    #     "ICR229+195",
    #     "ICR229+195",
    #     "ICR229+195",
    #     "ICR229+195",
    #     "ICR229+195",
    #     "ICR229+195",
    #     "ICR229+195",
    #     "ICR229+195",
    #     "ICR229+195",
    #     "ICR229+195",
    #     "ICR229+195",
    # ]
    
    # construct_names = [
    # "Empty Vector Control",
    # "Pore Only Control",
    # "ICR183+190",
    # "ICR184+190",
    # "ICR185+190",
    # "ICR186+190",
    # "ICR187+190",
    # "ICR188+190",
    # "ICR183+198",
    # "ICR184+198",
    # "ICR185+198",
    # "ICR186+198",
    # "ICR187+198",
    # "ICR188+198",
    # "ICR205+191",
    # "ICR206+191",
    # "ICR207+191",
    # "ICR208+191",
    # "ICR209+191",
    # "ICR210+191",
    # "ICR205+199",
    # "ICR206+199",
    # "ICR207+199",
    # "ICR208+199",
    # "ICR209+199",
    # "ICR210+199",
    # "ICR229+195",
    # "ICR230+195",
    # "ICR231+195",
    # "ICR232+195",
    # "ICR233+195",
    # "ICR234+195"
    # ]
    
    
    light_path = "26-04-05-series-repeat-light.csv"
    dark_path = "26-04-05-series-repeat-dark.csv"
    output_filename = "26-04-05-series-repeat-restructured"
    
    light_long = build_plate_long_with_raw(f"raw-data/{light_path}", "light", row_map, construct_names, num_reps=3)
    dark_long = build_plate_long_with_raw(f"raw-data/{dark_path}", "dark", row_map, construct_names, num_reps=3)
    
    combined = pd.concat([dark_long, light_long], ignore_index=True)
    combined.to_csv(f"data/{output_filename}.csv", index=False)