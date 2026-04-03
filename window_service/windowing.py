import os
import pandas as pd
from common.config import DEFAULT_WINDOW_SIZE


def _expected_frames(mid_frame: int, window_size: int = DEFAULT_WINDOW_SIZE):
    half = window_size // 2
    start = mid_frame - half
    end = mid_frame + half - 1
    return list(range(start, end + 1)), start, end


def _frames_match_exact(frame_series, expected_frames):
    return frame_series.sort_values().astype(int).tolist() == expected_frames


def save_event_windows(df: pd.DataFrame, events, output_dir="output", max_per_type=50, window_size: int = DEFAULT_WINDOW_SIZE):
    summary_rows = []
    rejected_rows = []

    os.makedirs(output_dir, exist_ok=True)

    if not events:
        pd.DataFrame(summary_rows).to_csv(os.path.join(output_dir, "windows_summary.csv"), index=False)
        pd.DataFrame(rejected_rows).to_csv(os.path.join(output_dir, "windows_rejected.csv"), index=False)
        return pd.DataFrame(summary_rows), pd.DataFrame(rejected_rows)

    for scenario_type in sorted(set(e["scenario_type"] for e in events)):
        scenario_events = [e for e in events if e["scenario_type"] == scenario_type][:max_per_type]
        scenario_dir = os.path.join(output_dir, scenario_type)
        os.makedirs(scenario_dir, exist_ok=True)

        for event in scenario_events:
            vehicle_id = int(event["vehicle_id"])
            mid_frame = int(event["mid_frame"])
            expected_frames, start_frame, end_frame = _expected_frames(mid_frame, window_size)

            ego_rows = df[
                (df["Vehicle_ID"] == vehicle_id)
                & (df["Frame_ID"] >= start_frame)
                & (df["Frame_ID"] <= end_frame)
            ].copy()

            if ego_rows.empty:
                rejected_rows.append({
                    "scenario": scenario_type,
                    "vehicle_id": vehicle_id,
                    "mid_frame": mid_frame,
                    "reason": "ego_missing_window",
                })
                continue

            ego_rows = ego_rows.sort_values("Frame_ID")
            if not _frames_match_exact(ego_rows["Frame_ID"], expected_frames):
                rejected_rows.append({
                    "scenario": scenario_type,
                    "vehicle_id": vehicle_id,
                    "mid_frame": mid_frame,
                    "reason": "ego_non_sequential_or_incomplete",
                    "ego_frame_count": int(ego_rows["Frame_ID"].nunique()),
                    "expected_frame_count": len(expected_frames),
                })
                continue

            ego_local_y_map = ego_rows.set_index("Frame_ID")["Local_Y"].to_dict()
            candidate_rows = df[df["Frame_ID"].isin(expected_frames)].copy()
            candidate_rows["ego_Local_Y"] = candidate_rows["Frame_ID"].map(ego_local_y_map)
            candidate_rows["distance_from_ego_y"] = candidate_rows["Local_Y"] - candidate_rows["ego_Local_Y"]
            candidate_rows = candidate_rows[candidate_rows["distance_from_ego_y"].abs() <= 70].copy()

            kept_vehicle_ids = [vehicle_id]
            rejected_surrounding = []
            for other_vid, veh_group in candidate_rows.groupby("Vehicle_ID"):
                other_vid = int(other_vid)
                veh_group = veh_group.sort_values("Frame_ID")
                if other_vid == vehicle_id:
                    continue
                if _frames_match_exact(veh_group["Frame_ID"], expected_frames):
                    kept_vehicle_ids.append(other_vid)
                else:
                    rejected_surrounding.append(other_vid)

            scenario_window = candidate_rows[candidate_rows["Vehicle_ID"].isin(kept_vehicle_ids)].copy()
            scenario_window = scenario_window.sort_values(["Frame_ID", "Vehicle_ID"]).reset_index(drop=True)
            scenario_window["is_ego"] = scenario_window["Vehicle_ID"] == vehicle_id
            scenario_window["scenario_label"] = scenario_type
            scenario_window["window_valid"] = True
            scenario_window["expected_window_size"] = len(expected_frames)

            if scenario_window[scenario_window["is_ego"]]["Frame_ID"].nunique() != len(expected_frames):
                rejected_rows.append({
                    "scenario": scenario_type,
                    "vehicle_id": vehicle_id,
                    "mid_frame": mid_frame,
                    "reason": "ego_failed_post_filter_validation",
                })
                continue

            if scenario_window["Vehicle_ID"].nunique() < 2:
                rejected_rows.append({
                    "scenario": scenario_type,
                    "vehicle_id": vehicle_id,
                    "mid_frame": mid_frame,
                    "reason": "no_valid_surrounding_vehicle_with_full_window",
                })
                continue

            filename = f"{scenario_type}_veh{vehicle_id}_mid{mid_frame}.csv"
            filepath = os.path.join(scenario_dir, filename)
            scenario_window.to_csv(filepath, index=False)

            summary_rows.append({
                "scenario": scenario_type,
                "vehicle_id": vehicle_id,
                "mid_frame": mid_frame,
                "start_frame": start_frame,
                "end_frame": end_frame,
                "expected_frame_count": len(expected_frames),
                "ego_frame_count": int(ego_rows["Frame_ID"].nunique()),
                "rows_saved": len(scenario_window),
                "unique_vehicles": scenario_window["Vehicle_ID"].nunique(),
                "kept_surrounding_vehicles": max(0, scenario_window["Vehicle_ID"].nunique() - 1),
                "rejected_surrounding_vehicles": len(rejected_surrounding),
                "validation_status": "passed",
                "file": filepath,
            })

    summary_df = pd.DataFrame(summary_rows)
    rejected_df = pd.DataFrame(rejected_rows)
    summary_df.to_csv(os.path.join(output_dir, "windows_summary.csv"), index=False)
    rejected_df.to_csv(os.path.join(output_dir, "windows_rejected.csv"), index=False)
    return summary_df, rejected_df
