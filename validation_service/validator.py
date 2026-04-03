from pathlib import Path
import pandas as pd


def validate_window_file(csv_path: Path):
    df = pd.read_csv(csv_path, low_memory=False)
    if df.empty:
        return {"file": str(csv_path), "status": "failed", "reason": "empty_window"}

    ego_rows = df[df["is_ego"] == True].sort_values("Frame_ID")
    if ego_rows.empty:
        return {"file": str(csv_path), "status": "failed", "reason": "missing_ego"}

    ego_frames = ego_rows["Frame_ID"].astype(int).tolist()
    expected = list(range(min(ego_frames), min(ego_frames) + len(ego_frames)))
    if ego_frames != expected:
        return {"file": str(csv_path), "status": "failed", "reason": "ego_non_sequential", "ego_frame_count": len(ego_frames)}

    bad_surrounding = []
    for vid, group in df.groupby("Vehicle_ID"):
        frames = group.sort_values("Frame_ID")["Frame_ID"].astype(int).tolist()
        if frames != ego_frames:
            bad_surrounding.append(int(vid))

    if bad_surrounding:
        return {
            "file": str(csv_path),
            "status": "failed",
            "reason": "surrounding_frame_mismatch",
            "bad_vehicle_ids": bad_surrounding,
        }

    return {
        "file": str(csv_path),
        "status": "passed",
        "reason": "ok",
        "ego_frame_count": len(ego_frames),
        "vehicle_count": int(df["Vehicle_ID"].nunique()),
    }
