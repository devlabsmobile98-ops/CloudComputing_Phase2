import pandas as pd


def load_and_clean_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, dtype=str, low_memory=False)

    numeric_cols = [
        "Vehicle_ID", "Frame_ID", "Total_Frames", "Global_Time",
        "Local_X", "Local_Y", "Global_X", "Global_Y",
        "v_length", "v_Width", "v_Class", "v_Vel", "v_Acc",
        "Lane_ID", "Preceding", "Following",
        "Space_Headway", "Time_Headway"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    required_cols = ["Vehicle_ID", "Frame_ID", "Global_Time",
                     "Local_X", "Local_Y", "Lane_ID", "v_Vel", "v_Acc"]
    df = df.dropna(subset=[c for c in required_cols if c in df.columns])

    df = df.sort_values(["Vehicle_ID", "Frame_ID"]).reset_index(drop=True)

    if "Global_Time" in df.columns:
        df["time_s"] = df["Global_Time"] / 1000.0

    frame_diff = df.groupby("Vehicle_ID")["Frame_ID"].diff()
    df["is_sequential_from_prev"] = frame_diff.fillna(1).eq(1)
    df["sequence_break"] = (~df["is_sequential_from_prev"]).astype(int)
    df["sequence_id"] = df.groupby("Vehicle_ID")["sequence_break"].cumsum()
    df["sequence_length"] = df.groupby(["Vehicle_ID", "sequence_id"])["Frame_ID"].transform("count")

    return df
