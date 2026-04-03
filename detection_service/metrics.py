import pandas as pd
import numpy as np


def add_safety_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    leader_speed_map = df.set_index(["Frame_ID", "Vehicle_ID"])["v_Vel"].to_dict()

    def get_leader_vel(row):
        lid = row["leader_id"]
        if pd.isna(lid):
            return np.nan
        return leader_speed_map.get((row["Frame_ID"], lid), np.nan)

    df["leader_vel"] = df.apply(get_leader_vel, axis=1)
    df["rel_vel"] = df["v_Vel"] - df["leader_vel"]

    df["time_headway_s"] = np.where(
        df["v_Vel"] > 0,
        df["gap_distance"] / df["v_Vel"],
        np.nan,
    )

    df["ttc_s"] = np.where(
        df["rel_vel"] > 0,
        df["gap_distance"] / df["rel_vel"],
        np.inf,
    )

    return df
