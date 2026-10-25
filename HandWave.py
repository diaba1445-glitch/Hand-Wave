import os
import sys
import time
import subprocess
import ctypes
from pathlib import Path

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from config_manager import ConfigManager
from gestures import BONES, GestureClassifier, MotionDetector
from trigger import GestureTrigger

if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).parent

MODEL_PATH = APP_DIR / "hand_landmarker.task"
if not MODEL_PATH.exists():
    MODEL_PATH = APP_DIR / "_internal" / "hand_landmarker.task"
if not MODEL_PATH.exists() and hasattr(sys, '_MEIPASS'):
    MODEL_PATH = Path(sys._MEIPASS) / "hand_landmarker.task"

def resolve_physical_hand(category_name, mirrored=True):
    """
    Translates MediaPipe's detected handedness category into the user's physical hand.
    MediaPipe assumes unmirrored camera input. If the frame is flipped horizontally (mirrored),
    the detected anatomical handedness is inverted.
    """
    cat = (category_name or "").strip().upper()
    if mirrored:
        return "RIGHT" if cat == "LEFT" else "LEFT"
    else:
        return "LEFT" if cat == "LEFT" else "RIGHT"

def draw_skeleton(frame, landmarks_px, hand_label="RIGHT"):
    if hand_label == "LEFT":
        line_color = (235, 175, 40)   # Sky Blue / Cyan (BGR)
        joint_color = (0, 215, 255)   # Gold / Light Amber (BGR)
    else:
        line_color = (40, 220, 100)   # Emerald Green (BGR)
        joint_color = (0, 165, 255)   # Vivid Orange (BGR)

    for pt1_idx, pt2_idx in BONES:
        p1 = tuple(landmarks_px[pt1_idx].astype(int))
        p2 = tuple(landmarks_px[pt2_idx].astype(int))
        cv2.line(frame, p1, p2, line_color, 2, cv2.LINE_AA)

    for pt in landmarks_px:
        cv2.circle(frame, tuple(pt.astype(int)), 4, joint_color, -1, cv2.LINE_AA)

    # Draw hand label above wrist
    wrist_pt = landmarks_px[0].astype(int)
    cv2.putText(frame, hand_label, (max(10, wrist_pt[0] - 24), max(25, wrist_pt[1] - 12)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, line_color, 2, cv2.LINE_AA)

settings_proc = None
last_settings_open_time = 0.0

def open_settings_process():
    global settings_proc, last_settings_open_time
    now = time.monotonic()
    if now - last_settings_open_time < 0.8:
        return
    last_settings_open_time = now

    if settings_proc is not None and settings_proc.poll() is None:
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, "HandWave — Settings")
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                return
        except Exception:
            pass

    if getattr(sys, 'frozen', False):
        settings_proc = subprocess.Popen([sys.executable, "--settings"], cwd=str(APP_DIR))
    else:
        settings_proc = subprocess.Popen([sys.executable, str(APP_DIR / "HandWave.py"), "--settings"], cwd=str(APP_DIR))

def main():
    if "--settings" in sys.argv:
        from settings_gui import SettingsWindow
        cfg = ConfigManager(APP_DIR / "config.json")
        app = SettingsWindow(config_manager=cfg)
        app.run()
        return

    cfg = ConfigManager(APP_DIR / "config.json")
    classifier = GestureClassifier()
    motion_detector = MotionDetector(cooldown=0.45)
    trigger = GestureTrigger(cfg)

    if not MODEL_PATH.exists():
        print(f"Error: Model not found at {MODEL_PATH}")
        sys.exit(1)

    # Initialize MediaPipe Hand Landmarker
    base_options = mp_python.BaseOptions(model_asset_path=str(MODEL_PATH))
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2
    )
    landmarker = vision.HandLandmarker.create_from_options(options)

    camera_idx = cfg.config.get("camera_index", 0)
    cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print(f"Error: Could not open camera {camera_idx}")
        # Try default backend
        cap = cv2.VideoCapture(camera_idx)
        if not cap.isOpened():
            print("Failed to open camera.")
            sys.exit(1)

    window_name = "HandWave"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 960, 540)

    curr_topmost = cfg.config.get("topmost", True)
    if curr_topmost:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

    paused = False
    last_fired_action = None
    last_fired_hand = None
    action_banner_timer = 0.0
    settings_banner_timer = 0.0
    split_banner_timer = 0.0
    double_banner_timer = 0.0

    clutch_toggled_armed = False
    clutch_debounce_timer = 0.0

    print("HandWave is running!")
    print("Keys: [C] Clutch | [D] Double-Tap | [H] Split Hands | [P] Pause | [S] Settings | [1-8] Gestures | [Q/Esc] Quit")

    start_time = time.monotonic()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Camera frame dropped or camera disconnected.")
            break

        # Check for config file updates from Settings Window
        if cfg.reload_if_changed():
            now_reload = time.monotonic()
            settings_banner_timer = now_reload + 1.8
            print("Settings reloaded successfully from config.json!")

            # Dynamic update: topmost
            new_topmost = cfg.config.get("topmost", True)
            if new_topmost != curr_topmost:
                curr_topmost = new_topmost
                cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1 if curr_topmost else 0)

            # Dynamic update: camera index
            new_cam_idx = cfg.config.get("camera_index", 0)
            if new_cam_idx != camera_idx:
                print(f"Switching camera to index {new_cam_idx}...")
                cap.release()
                camera_idx = new_cam_idx
                cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                if not cap.isOpened():
                    cap = cv2.VideoCapture(camera_idx)

        clutch_enabled = cfg.is_safety_clutch_enabled()
        clutch_sign = cfg.get_clutch_sign()
        clutch_mode = cfg.get_clutch_mode()

        # Mirror frame
        is_mirrored = cfg.config.get("mirrored", True)
        if is_mirrored:
            frame = cv2.flip(frame, 1)

        h, w, _ = frame.shape
        now = time.monotonic()
        frame_timestamp_ms = int((now - start_time) * 1000)

        detected_gesture = None
        detected_hand = None
        action_fired = None
        progress = 0.0
        is_armed = not clutch_enabled

        if not paused:
            # Process with MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)

            if result.hand_landmarks and len(result.hand_landmarks) > 0:
                hands_data = []
                for hand_idx, lms in enumerate(result.hand_landmarks):
                    world_lms = (
                        result.hand_world_landmarks[hand_idx]
                        if result.hand_world_landmarks and hand_idx < len(result.hand_world_landmarks)
                        else None
                    )

                    # Extract handedness from MediaPipe
                    cat_name = "Right"
                    if result.handedness and hand_idx < len(result.handedness) and len(result.handedness[hand_idx]) > 0:
                        cat_name = result.handedness[hand_idx][0].category_name

                    physical_hand = resolve_physical_hand(cat_name, mirrored=is_mirrored)

                    px_coords = np.array([[lm.x * w, lm.y * h] for lm in lms])
                    world_coords = np.array([[wlm.x, wlm.y, wlm.z] for wlm in world_lms]) if world_lms else None

                    if cfg.config.get("draw_skeleton", True):
                        draw_skeleton(frame, px_coords, physical_hand)

                    hands_data.append((px_coords, world_coords, physical_hand))

                guard_hand_idx = None
                if clutch_enabled:
                    # Check if any hand is displaying the guard sign
                    for idx, (px_c, w_c, h_label) in enumerate(hands_data):
                        sign = classifier.detect_guard_sign(px_c, w_c)
                        if sign == clutch_sign:
                            guard_hand_idx = idx
                            break

                    if clutch_mode == "HOLD":
                        is_armed = (guard_hand_idx is not None)
                    elif clutch_mode == "TOGGLE":
                        if guard_hand_idx is not None and now > clutch_debounce_timer:
                            clutch_toggled_armed = not clutch_toggled_armed
                            clutch_debounce_timer = now + 1.0
                        is_armed = clutch_toggled_armed
                else:
                    is_armed = True

                # Only process action gestures if system is armed
                if is_armed:
                    for idx, (px_c, w_c, h_label) in enumerate(hands_data):
                        # Skip the hand holding the guard sign in HOLD mode
                        if clutch_enabled and clutch_mode == "HOLD" and idx == guard_hand_idx:
                            continue

                        # 1. Check dynamic directional swipe motion first (tracked by hand label)
                        palm_center_norm = ((px_c[0][0] + px_c[9][0]) * 0.5 / w, (px_c[0][1] + px_c[9][1]) * 0.5 / h)
                        swipe = motion_detector.update(h_label, palm_center_norm, now)
                        if swipe:
                            if cfg.is_gesture_enabled(swipe, hand=h_label):
                                detected_gesture = swipe
                                detected_hand = h_label
                                break
                            elif detected_gesture is None:
                                detected_gesture = swipe
                                detected_hand = h_label

                        # 2. Check static hand pose
                        g = classifier.classify(px_c, w_c)
                        if g:
                            if cfg.is_gesture_enabled(g, hand=h_label):
                                detected_gesture = g
                                detected_hand = h_label
                                break
                            elif detected_gesture is None:
                                detected_gesture = g
                                detected_hand = h_label
                else:
                    motion_detector.clear()

                # Check trigger & dispatch for the active gesture
                action_fired, progress = trigger.update(detected_gesture, hand=detected_hand)
                if action_fired:
                    last_fired_action = action_fired
                    last_fired_hand = detected_hand
                    action_banner_timer = now + 1.2
            else:
                motion_detector.clear()
                trigger.update(None)

        # ----------------- HUD OVERLAY -----------------
        # Top banner: Active gesture & progress
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 75), (20, 20, 25), -1)
        cv2.rectangle(overlay, (0, h - 45), (w, h), (20, 20, 25), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        pending_conf = trigger.get_pending_confirmation()

        if paused:
            cv2.putText(frame, "PAUSED (Press P to Resume)", (30, 48),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 165, 255), 2, cv2.LINE_AA)
        elif pending_conf is not None:
            # Double-Tap Waiting for 2nd Tap Confirmation
            pend_g, pend_h, time_left, ratio = pending_conf
            pend_act = cfg.get_action(pend_g, pend_h)
            h_str = f"[{pend_h} HAND] " if (cfg.is_split_hands_enabled() and pend_h) else ""
            status_text = f"DOUBLE-TAP: Repeat {h_str}{pend_g} to fire [{pend_act}] ({time_left:.1f}s)"
            cv2.putText(frame, status_text, (30, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 215, 255), 2, cv2.LINE_AA)

            # Amber countdown bar
            bar_x, bar_y, bar_w, bar_h = 30, 55, 300, 8
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (60, 60, 60), -1)
            fill_w = int(bar_w * ratio)
            if fill_w > 0:
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), (0, 215, 255), -1)
        else:
            if detected_gesture:
                is_enabled = cfg.is_gesture_enabled(detected_gesture, hand=detected_hand)
                action_name = cfg.get_action(detected_gesture, hand=detected_hand)
                hand_prefix = f"[{detected_hand} HAND] " if (cfg.is_split_hands_enabled() and detected_hand) else ""

                if is_enabled:
                    status_text = f"{hand_prefix}Gesture: {detected_gesture} -> [{action_name}]"
                    color = (0, 255, 120)
                else:
                    status_text = f"{hand_prefix}Gesture: {detected_gesture} (DISABLED in Settings)"
                    color = (150, 150, 150)

                cv2.putText(frame, status_text, (30, 45),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2, cv2.LINE_AA)

                # Hold Progress Bar
                bar_x, bar_y, bar_w, bar_h = 30, 55, 300, 8
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (60, 60, 60), -1)
                fill_w = int(bar_w * progress)
                if fill_w > 0:
                    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), (0, 255, 120), -1)
            else:
                if clutch_enabled and not is_armed:
                    sign_icons = {"OPEN_PALM": "Open Palm", "PEACE_SIGN": "Peace Sign", "FIST": "Closed Fist"}
                    disp_sign = sign_icons.get(clutch_sign, clutch_sign)
                    cv2.putText(frame, f"LOCKED: Show {disp_sign} on other hand to unlock", (30, 45),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2, cv2.LINE_AA)
                else:
                    cv2.putText(frame, "Show a hand gesture...", (30, 45),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (200, 200, 200), 2, cv2.LINE_AA)

        # Status Badges in Top Right
        badge_x = w - 30
        if clutch_enabled and not paused and is_armed:
            badge_x -= 190
            cv2.putText(frame, "CLUTCH: ARMED", (badge_x, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.70, (0, 255, 120), 2, cv2.LINE_AA)
        if cfg.is_split_hands_enabled() and not paused:
            badge_x -= 160
            cv2.putText(frame, "SPLIT: ON", (badge_x, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.70, (235, 175, 40), 2, cv2.LINE_AA)
        if cfg.is_double_gesture_enabled() and not paused:
            badge_x -= 190
            cv2.putText(frame, "DOUBLE-TAP: ON", (badge_x, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.70, (0, 215, 255), 2, cv2.LINE_AA)

        # Action Fired or Status Notifications
        if now < action_banner_timer and last_fired_action:
            hand_str = f" ({last_fired_hand})" if (cfg.is_split_hands_enabled() and last_fired_hand) else ""
            sent_str = f"FIRED: {last_fired_action}{hand_str}"
            cv2.putText(frame, sent_str, (w - 320, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
        elif now < double_banner_timer:
            mode_str = "DOUBLE-TAP: ON" if cfg.is_double_gesture_enabled() else "DOUBLE-TAP: OFF"
            cv2.putText(frame, mode_str, (w - 320, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 215, 255), 2, cv2.LINE_AA)
        elif now < split_banner_timer:
            mode_str = "SPLIT HANDS: ON" if cfg.is_split_hands_enabled() else "SPLIT HANDS: OFF"
            cv2.putText(frame, mode_str, (w - 340, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (235, 175, 40), 2, cv2.LINE_AA)
        elif now < settings_banner_timer:
            cv2.putText(frame, "SETTINGS APPLIED", (w - 320, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

        # Bottom status bar
        controls_str = "[C] Clutch   [D] Double-Tap   [H] Split   [P] Pause   [S] Settings   [1-8] Gestures   [Q/Esc] Quit"
        cv2.putText(frame, controls_str, (25, h - 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (220, 220, 220), 1, cv2.LINE_AA)

        cv2.imshow(window_name, frame)

        # Process Windows events and check keyboard shortcuts
        key = cv2.waitKey(1) & 0xFF

        # 1. Quit on Q or Esc
        if key in (ord('q'), ord('Q'), 27):
            break

        # 2. Check if window was closed via Windows [X] button
        try:
            prop = cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE)
            if prop < 1:
                break
        except Exception:
            break

        if sys.platform == "win32":
            hwnd = ctypes.windll.user32.FindWindowW(None, window_name)
            if hwnd == 0:
                break

        # 3. Handle interactive keys
        if key in (ord('p'), ord('P')):
            paused = not paused
        elif key in (ord('s'), ord('S')):
            print("Opening Settings Window...")
            open_settings_process()
        elif key in (ord('d'), ord('D')):
            curr_d = cfg.is_double_gesture_enabled()
            if "double_gesture" not in cfg.config:
                cfg.config["double_gesture"] = {"enabled": True, "window_seconds": 0.75}
            cfg.config["double_gesture"]["enabled"] = not curr_d
            cfg.save()
            trigger.cancel_pending()
            double_banner_timer = now + 1.8
            mode_name = "ENABLED (Double-Tap to Fire)" if not curr_d else "DISABLED (Single-Tap)"
            print(f"Double-Tap Confirmation toggled: {mode_name}")
        elif key in (ord('h'), ord('H')):
            curr_split = cfg.is_split_hands_enabled()
            cfg.config["split_hands"] = not curr_split
            cfg.save()
            split_banner_timer = now + 1.8
            mode_name = "SPLIT (Independent Left/Right)" if not curr_split else "UNIFIED (Both Hands)"
            print(f"Hand Mode toggled: {mode_name}")
        elif key in (ord('c'), ord('C')):
            curr_c = cfg.is_safety_clutch_enabled()
            if "safety_clutch" not in cfg.config:
                cfg.config["safety_clutch"] = {"enabled": True, "sign": "OPEN_PALM", "mode": "HOLD"}
            cfg.config["safety_clutch"]["enabled"] = not curr_c
            cfg.save()
            print(f"Safety Clutch toggled: {'ENABLED' if not curr_c else 'DISABLED'}")
        elif ord('1') <= key <= ord('8'):
            g_keys = [
                "THUMB_UP", "THUMB_DOWN",
                "POINT_RIGHT", "POINT_LEFT",
                "PINCH_INDEX", "PINCH_MIDDLE", "PINCH_RING", "PINCH_PINKY"
            ]
            idx = key - ord('1')
            if idx < len(g_keys):
                target_g = g_keys[idx]
                target_dict = cfg.get_gesture_dict(detected_hand)
                curr_en = bool(target_dict.get(target_g, {}).get("enabled", True))
                if target_g not in target_dict:
                    target_dict[target_g] = {"enabled": True, "action": "NONE", "label": target_g}
                target_dict[target_g]["enabled"] = not curr_en
                cfg.save()
                hand_info = f" ({detected_hand} hand)" if cfg.is_split_hands_enabled() and detected_hand else ""
                print(f"Toggled {target_g}{hand_info}: {'ENABLED' if not curr_en else 'DISABLED'}")

    # Terminate child settings process if open
    if settings_proc is not None and settings_proc.poll() is None:
        try:
            settings_proc.terminate()
        except Exception:
            pass

    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)

if __name__ == "__main__":
    main()
