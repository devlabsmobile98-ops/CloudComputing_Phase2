import pandas as pd


def add_scenario_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["is_near_collision"] = (df["ttc_s"] < 1.5) & (df["rel_vel"] > 0)
    df["is_sudden_braking"] = df["v_Acc"] <= -3
    df["is_lane_change_point"] = df.groupby("Vehicle_ID")["Lane_ID"].diff().fillna(0) != 0
    df["is_car_following_candidate"] = (
        df["leader_id"].notna()
        & (df["gap_distance"] > 0)
        & (df["time_headway_s"] > 0.5)
        & (df["time_headway_s"] < 2.0)
    )

    return df


def extract_events(df: pd.DataFrame):
    events = {
        "near_collision": [],
        "sudden_braking": [],
        "lane_change": [],
        "car_following": [],
    }

    for _, group in df.groupby("Vehicle_ID"):
        group = group.sort_values("Frame_ID")

        for _, row in group[group["is_near_collision"]].iterrows():
            events["near_collision"].append({
                "scenario_type": "near_collision",
                "vehicle_id": int(row["Vehicle_ID"]),
                "start_frame": int(row["Frame_ID"]),
                "end_frame": int(row["Frame_ID"]),
                "mid_frame": int(row["Frame_ID"]),
            })

        for _, row in group[group["is_sudden_braking"]].iterrows():
            events["sudden_braking"].append({
                "scenario_type": "sudden_braking",
                "vehicle_id": int(row["Vehicle_ID"]),
                "start_frame": int(row["Frame_ID"]),
                "end_frame": int(row["Frame_ID"]),
                "mid_frame": int(row["Frame_ID"]),
            })

        for _, row in group[group["is_lane_change_point"]].iterrows():
            events["lane_change"].append({
                "scenario_type": "lane_change",
                "vehicle_id": int(row["Vehicle_ID"]),
                "start_frame": int(row["Frame_ID"]),
                "end_frame": int(row["Frame_ID"]),
                "mid_frame": int(row["Frame_ID"]),
            })

        cf = group[group["is_car_following_candidate"]]
        if not cf.empty:
            sampled = cf.iloc[::10]
            for _, row in sampled.iterrows():
                events["car_following"].append({
                    "scenario_type": "car_following",
                    "vehicle_id": int(row["Vehicle_ID"]),
                    "start_frame": int(row["Frame_ID"]),
                    "end_frame": int(row["Frame_ID"]),
                    "mid_frame": int(row["Frame_ID"]),
                })

    return events
