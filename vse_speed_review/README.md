# VSE Speed Review

A Blender 5.1 extension that adds keyboard-driven playback speed control to the Video Sequencer.
Speed is achieved via frame-skipping — it **never** affects render output.

## Speed levels

| Level  | Label  | Effective speed | Frame-skip rule                  |
|--------|--------|-----------------|----------------------------------|
| NORMAL | 1x     | 1×  = 30 fps    | No skipping                      |
| FAST   | 1.33x  | 1.33× = 40 fps  | +1 extra every 3rd frame         |
| FASTER | 1.5x   | 1.5× = 45 fps   | +1 extra every other frame       |
| DOUBLE | 2x     | 2×  = 60 fps    | +1 extra every frame             |
| TRIPLE | 3x     | 3×  = 90 fps    | +2 extra every frame             |

(fps figures assume 30 fps source)

## Hotkeys (while VSE has focus)

| Key | Action |
|-----|--------|
| `.` | Increase speed |
| `,` | Decrease speed |

## Required playback setting

Set **Sync** to **Frame Dropping** (bottom of the VSE, or via the Speed Review sidebar panel).
With "Sync Scene Time", Blender already drops frames to match wall-clock time and the extra skipping becomes erratic.

## Installation

1. Zip the folder:
   ```
   zip -r vse_speed_review.zip vse_speed_review/
   ```
2. Open Blender 5.1+.
3. Go to **Edit → Preferences → Add-ons**.
4. Click **Install from Disk…** and select the `.zip`.
5. Enable **VSE Speed Review**.

## Usage

1. Open a project in the **Video Sequence Editor**.
2. Set Sync to **Frame Dropping** (see sidebar panel).
3. Press **Space** to start playback.
4. Press `.` / `,` to step speed up/down.
5. Open the **N panel → Speed Review tab** to see/change speed and sync settings in one place.
