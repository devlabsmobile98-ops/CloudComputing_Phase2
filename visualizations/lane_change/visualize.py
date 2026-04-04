import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import numpy as np

# =========================
# CONFIG
# =========================
file_path = "output_lane_change_lane_change_veh1052_mid2790.csv"
scenario = "lane_change"
window_status = "VALID WINDOW"   # or "REJECTED"
output_video = "lane_change_veh1052_mid2790_cinematic.mp4"
save_midframe_png = True

# Camera / styling
X_RANGE = 120   # Local_Y view width
Y_RANGE = 45    # Local_X view height
TRAIL_LENGTH = 12
FPS = 10

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(file_path)
df = df.sort_values(["Frame_ID", "Vehicle_ID"]).copy()

if df["is_ego"].dtype == object:
    df["is_ego"] = df["is_ego"].astype(str).str.lower().isin(["true", "1", "yes"])

frames = sorted(df["Frame_ID"].unique())
mid_frame = frames[len(frames) // 2]

# Safety fallback if columns missing
if "v_length" not in df.columns:
    df["v_length"] = 15.0
if "v_Width" not in df.columns:
    df["v_Width"] = 6.0
if "v_Acc" not in df.columns:
    df["v_Acc"] = 0.0
if "Lane_ID" not in df.columns:
    df["Lane_ID"] = -1

# =========================
# FIGURE LAYOUT
# =========================
fig = plt.figure(figsize=(14, 7))
gs = fig.add_gridspec(2, 2, width_ratios=[3.7, 1.3], height_ratios=[1, 1], wspace=0.25, hspace=0.25)

ax_main = fig.add_subplot(gs[:, 0])
ax_speed = fig.add_subplot(gs[0, 1])
ax_acc = fig.add_subplot(gs[1, 1])

history = {}
ego_speed_series = []
ego_acc_series = []
played_frames = []

def draw_lane_lines(ax, x_min, x_max, y_min, y_max):
    # Local_X is lateral direction, so horizontal lane guide lines work nicely
    lane_step = 12
    start = int(np.floor(y_min / lane_step) * lane_step)
    for lane_y in range(start, int(y_max + lane_step), lane_step):
        ax.hlines(
            lane_y, x_min, x_max,
            linestyles="dashed",
            linewidth=1.0,
            alpha=0.22,
            color="gray",
            zorder=0
        )

def draw_vehicle(ax, x_center, y_center, length, width, facecolor, edgecolor="black", alpha=1.0, z=3):
    # x_center uses Local_Y, y_center uses Local_X
    rect = Rectangle(
        (x_center - length / 2, y_center - width / 2),
        length, width,
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=1.0,
        alpha=alpha,
        zorder=z
    )
    ax.add_patch(rect)

def render_side_plots():
    ax_speed.clear()
    ax_acc.clear()

    ax_speed.plot(played_frames, ego_speed_series, linewidth=2)
    ax_speed.set_title("Ego Speed")
    ax_speed.set_xlabel("Frame")
    ax_speed.set_ylabel("ft/s")
    ax_speed.grid(True, alpha=0.3)

    ax_acc.plot(played_frames, ego_acc_series, linewidth=2)
    ax_acc.set_title("Ego Acceleration")
    ax_acc.set_xlabel("Frame")
    ax_acc.set_ylabel("ft/s²")
    ax_acc.grid(True, alpha=0.3)

def render_frame(frame, save_png=False):
    ax_main.clear()

    frame_data = df[df["Frame_ID"] == frame].copy()
    ego_vehicle = frame_data[frame_data["is_ego"] == True]

    if ego_vehicle.empty:
        return

    ego_id = int(ego_vehicle["Vehicle_ID"].iloc[0])
    ego_x = float(ego_vehicle["Local_Y"].iloc[0])
    ego_y = float(ego_vehicle["Local_X"].iloc[0])
    ego_speed = float(ego_vehicle["v_Vel"].iloc[0])
    ego_acc = float(ego_vehicle["v_Acc"].iloc[0])
    ego_lane = int(ego_vehicle["Lane_ID"].iloc[0])

    played_frames.append(frame)
    ego_speed_series.append(ego_speed)
    ego_acc_series.append(ego_acc)

    # Find closest vehicles to ego
    distances = {}
    for vid in frame_data["Vehicle_ID"].unique():
        vehicle = frame_data[frame_data["Vehicle_ID"] == vid]
        x = float(vehicle["Local_Y"].iloc[0])
        y = float(vehicle["Local_X"].iloc[0])
        dist = np.sqrt((x - ego_x) ** 2 + (y - ego_y) ** 2)
        distances[int(vid)] = dist

    closest_vehicles = sorted(distances, key=distances.get)
    closest_vehicles = [vid for vid in closest_vehicles if vid != ego_id][:3]

    # Camera follows ego
    x_min = ego_x - X_RANGE / 2
    x_max = ego_x + X_RANGE / 2
    y_min = ego_y - Y_RANGE / 2
    y_max = ego_y + Y_RANGE / 2

    draw_lane_lines(ax_main, x_min, x_max, y_min, y_max)

    # Plot all vehicles
    for vid in frame_data["Vehicle_ID"].unique():
        vid = int(vid)
        vehicle = frame_data[frame_data["Vehicle_ID"] == vid]

        x = float(vehicle["Local_Y"].iloc[0])
        y = float(vehicle["Local_X"].iloc[0])
        length = float(vehicle["v_length"].iloc[0])
        width = float(vehicle["v_Width"].iloc[0])

        if vid not in history:
            history[vid] = []
        history[vid].append((x, y))

        trail = history[vid][-TRAIL_LENGTH:]
        trail_x = [t[0] for t in trail]
        trail_y = [t[1] for t in trail]

        if vid == ego_id:
            draw_vehicle(ax_main, x, y, length, width, facecolor="red", edgecolor="black", alpha=1.0, z=6)
            ax_main.plot(trail_x, trail_y, linewidth=2.5, color="red", zorder=5)
            ax_main.text(x + 2, y + 1.8, f"EGO {vid}", fontsize=10, weight="bold", color="red", zorder=7)

        elif vid in closest_vehicles:
            draw_vehicle(ax_main, x, y, length, width, facecolor="orange", edgecolor="black", alpha=0.95, z=5)
            ax_main.plot(trail_x, trail_y, linestyle="dashed", linewidth=1.8, color="orange", alpha=0.9, zorder=4)
            ax_main.text(x + 1.5, y + 1.2, f"{vid}", fontsize=8, zorder=6)

        else:
            draw_vehicle(ax_main, x, y, length, width, facecolor="steelblue", edgecolor="black", alpha=0.75, z=4)
            ax_main.plot(trail_x, trail_y, linestyle="dashed", linewidth=1.1, color="steelblue", alpha=0.35, zorder=3)

    ax_main.set_xlim(x_min, x_max)
    ax_main.set_ylim(y_min, y_max)
    ax_main.set_xlabel("Longitudinal Position (Local Y)")
    ax_main.set_ylabel("Lateral Position (Local X)")
    ax_main.set_title(f"{scenario.upper()}  |  Frame {frame}", fontsize=15, weight="bold")
    ax_main.grid(True, alpha=0.18)

    # Top-left info box
    info_text = (
        f"Ego ID: {ego_id}\n"
        f"Speed: {ego_speed:.2f} ft/s\n"
        f"Acceleration: {ego_acc:.2f} ft/s²\n"
        f"Lane ID: {ego_lane}\n"
        f"Vehicles shown: {frame_data['Vehicle_ID'].nunique()}"
    )
    ax_main.text(
        0.015, 0.98, info_text,
        transform=ax_main.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.75)
    )

    # Top-right validation badge
    badge_color = "green" if window_status.upper().startswith("VALID") else "red"
    ax_main.text(
        0.985, 0.98, window_status,
        transform=ax_main.transAxes,
        fontsize=11,
        color=badge_color,
        weight="bold",
        ha="right",
        va="top",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", alpha=0.8)
    )

    # Progress indicator
    progress_text = f"{len(played_frames)}/{len(frames)} frames"
    ax_main.text(
        0.985, 0.90, progress_text,
        transform=ax_main.transAxes,
        fontsize=9,
        ha="right",
        va="top"
    )

    render_side_plots()

    if save_png:
        plt.savefig(f"{scenario}_frame_{frame}_cinematic.png", dpi=220, bbox_inches="tight")

def update(frame):
    render_frame(frame, save_png=False)

ani = animation.FuncAnimation(
    fig,
    update,
    frames=frames,
    interval=100,
    repeat=False
)

ani.save(output_video, writer="ffmpeg", fps=FPS, dpi=180)

if save_midframe_png:
    render_frame(mid_frame, save_png=True)

plt.tight_layout()
plt.show()