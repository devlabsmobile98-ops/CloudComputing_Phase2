import pandas as pd
import numpy as np


def find_leader_vehicle(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["leader_id"] = np.nan
    df["gap_distance"] = np.nan

    for (_, _), group in df.groupby(["Frame_ID", "Lane_ID"]):
        group = group.sort_values("Local_Y")
        idxs = group.index.tolist()
        ys = group["Local_Y"].tolist()
        vids = group["Vehicle_ID"].tolist()

        for i in range(len(idxs) - 1):
            ego_idx = idxs[i]
            df.at[ego_idx, "leader_id"] = vids[i + 1]
            df.at[ego_idx, "gap_distance"] = ys[i + 1] - ys[i]

    return df
