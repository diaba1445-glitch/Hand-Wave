import json
import os
from pathlib import Path

DEFAULT_GESTURES = {
    "THUMB_UP": {
        "enabled": True,
        "action": "VOLUME_UP",
        "label": "Thumbs Up",
        "repeat": True
    },
    "THUMB_DOWN": {
        "enabled": True,
        "action": "VOLUME_DOWN",
        "label": "Thumbs Down",
        "repeat": True
    },
    "POINT_RIGHT": {
        "enabled": True,
        "action": "RIGHT",
        "label": "Point Right (Index)",
        "repeat": False
    },
    "POINT_LEFT": {
        "enabled": True,
        "action": "LEFT",
        "label": "Point Left (Index)",
        "repeat": False
    },
    "PINCH_INDEX": {
        "enabled": True,
        "action": "SPACE",
        "label": "Pinch (Thumb + Index)",
        "repeat": False
    },
    "PINCH_MIDDLE": {
        "enabled": True,
        "action": "ENTER",
        "label": "Pinch (Thumb + Middle)",
        "repeat": False
    },
    "PINCH_RING": {
        "enabled": True,
        "action": "PAGE_DOWN",
        "label": "Pinch (Thumb + Ring)",
        "repeat": False
    },
    "PINCH_PINKY": {
        "enabled": True,
        "action": "MUTE",
        "label": "Pinch (Thumb + Pinky)",
        "repeat": False
    },
    "SWIPE_RIGHT": {
        "enabled": True,
        "action": "RIGHT",
        "label": "Swipe Right (Wave Right)",
        "repeat": False
    },
    "SWIPE_LEFT": {
        "enabled": True,
        "action": "LEFT",
        "label": "Swipe Left (Wave Left)",
        "repeat": False
    },
    "SWIPE_UP": {
        "enabled": True,
        "action": "PAGE_UP",
        "label": "Swipe Up (Wave Up)",
        "repeat": False
    },
    "SWIPE_DOWN": {
        "enabled": True,
        "action": "PAGE_DOWN",
        "label": "Swipe Down (Wave Down)",
        "repeat": False
    }
}

DEFAULT_RIGHT_GESTURES = {
    "THUMB_UP": {
        "enabled": True,
        "action": "VOLUME_UP",
        "label": "Thumbs Up",
        "repeat": True
    },
    "THUMB_DOWN": {
        "enabled": True,
        "action": "VOLUME_DOWN",
        "label": "Thumbs Down",
        "repeat": True
    },
    "POINT_RIGHT": {
        "enabled": True,
        "action": "RIGHT",
        "label": "Point Right (Index)",
        "repeat": False
    },
    "POINT_LEFT": {
        "enabled": True,
        "action": "LEFT",
        "label": "Point Left (Index)",
        "repeat": False
    },
    "PINCH_INDEX": {
        "enabled": True,
        "action": "PAGE_DOWN",
        "label": "Pinch (Thumb + Index)",
        "repeat": False
    },
    "PINCH_MIDDLE": {
        "enabled": True,
        "action": "PAGE_UP",
        "label": "Pinch (Thumb + Middle)",
        "repeat": False
    },
    "PINCH_RING": {
        "enabled": True,
        "action": "HOME",
        "label": "Pinch (Thumb + Ring)",
        "repeat": False
    },
    "PINCH_PINKY": {
        "enabled": True,
        "action": "END",
        "label": "Pinch (Thumb + Pinky)",
        "repeat": False
    },
    "SWIPE_RIGHT": {
        "enabled": True,
        "action": "RIGHT",
        "label": "Swipe Right (Wave Right)",
        "repeat": False
    },
    "SWIPE_LEFT": {
        "enabled": True,
        "action": "LEFT",
        "label": "Swipe Left (Wave Left)",
        "repeat": False
    },
    "SWIPE_UP": {
        "enabled": True,
        "action": "PAGE_UP",
        "label": "Swipe Up (Wave Up)",
        "repeat": False
    },
    "SWIPE_DOWN": {
        "enabled": True,
        "action": "PAGE_DOWN",
        "label": "Swipe Down (Wave Down)",
        "repeat": False
    }
}

DEFAULT_LEFT_GESTURES = {
    "THUMB_UP": {
        "enabled": True,
        "action": "VOLUME_UP",
        "label": "Thumbs Up",
        "repeat": True
    },
    "THUMB_DOWN": {
        "enabled": True,
        "action": "VOLUME_DOWN",
        "label": "Thumbs Down",
        "repeat": True
    },
    "POINT_RIGHT": {
        "enabled": True,
        "action": "NEXT_TRACK",
        "label": "Point Right (Index)",
        "repeat": False
    },
    "POINT_LEFT": {
        "enabled": True,
        "action": "PREV_TRACK",
        "label": "Point Left (Index)",
        "repeat": False
    },
    "PINCH_INDEX": {
        "enabled": True,
        "action": "SPACE",
        "label": "Pinch (Thumb + Index)",
        "repeat": False
    },
    "PINCH_MIDDLE": {
        "enabled": True,
        "action": "MUTE",
        "label": "Pinch (Thumb + Middle)",
        "repeat": False
    },
    "PINCH_RING": {
        "enabled": True,
        "action": "TASK_VIEW",
        "label": "Pinch (Thumb + Ring)",
        "repeat": False
    },
    "PINCH_PINKY": {
        "enabled": True,
        "action": "SHOW_DESKTOP",
        "label": "Pinch (Thumb + Pinky)",
        "repeat": False
    },
    "SWIPE_RIGHT": {
        "enabled": True,
        "action": "SWITCH_DESKTOP_RIGHT",
        "label": "Swipe Right (Wave Right)",
        "repeat": False
    },
    "SWIPE_LEFT": {
        "enabled": True,
        "action": "SWITCH_DESKTOP_LEFT",
        "label": "Swipe Left (Wave Left)",
        "repeat": False
    },
    "SWIPE_UP": {
        "enabled": True,
        "action": "TASK_VIEW",
        "label": "Swipe Up (Wave Up)",
        "repeat": False
    },
    "SWIPE_DOWN": {
        "enabled": True,
        "action": "SHOW_DESKTOP",
        "label": "Swipe Down (Wave Down)",
        "repeat": False
    }
}

DEFAULT_CONFIG = {
    "split_hands": False,
    "gestures": DEFAULT_GESTURES,
    "right_hand": {
        "gestures": DEFAULT_RIGHT_GESTURES
    },
    "left_hand": {
        "gestures": DEFAULT_LEFT_GESTURES
    },
    "hold_time_seconds": 0.35,
    "camera_index": 0,
    "topmost": True,
    "draw_skeleton": True,
    "mirrored": True,
    "safety_clutch": {
        "enabled": False,
        "sign": "OPEN_PALM",
        "mode": "HOLD"
    },
    "double_gesture": {
        "enabled": False,
        "window_seconds": 0.75
    }
}

import copy
import sys

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

CONFIG_PATH = get_base_dir() / "config.json"

class ConfigManager:
    def __init__(self, path=None):
        if path is None:
            path = CONFIG_PATH
        self.path = Path(path)
        self.last_mtime = 0
        self.config = self.load()

    def _merge_gesture_dict(self, target_dict, default_dict):
        for g_key, g_val in default_dict.items():
            if g_key not in target_dict:
                target_dict[g_key] = copy.deepcopy(g_val)
            else:
                for subk, subv in g_val.items():
                    target_dict[g_key].setdefault(subk, subv)

    def load(self):
        if not self.path.exists():
            self.save(DEFAULT_CONFIG)
            return copy.deepcopy(DEFAULT_CONFIG)
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Merge defaults if missing keys
            merged = copy.deepcopy(DEFAULT_CONFIG)
            merged.update(data)

            # Ensure split_hands key exists
            merged.setdefault("split_hands", False)

            # Merge double_gesture
            if "double_gesture" not in merged or not isinstance(merged["double_gesture"], dict):
                merged["double_gesture"] = copy.deepcopy(DEFAULT_CONFIG["double_gesture"])
            else:
                merged["double_gesture"].setdefault("enabled", False)
                merged["double_gesture"].setdefault("window_seconds", 0.75)

            # Merge unified gestures
            if "gestures" not in merged:
                merged["gestures"] = copy.deepcopy(DEFAULT_GESTURES)
            else:
                self._merge_gesture_dict(merged["gestures"], DEFAULT_GESTURES)

            # Merge right hand gestures
            if "right_hand" not in merged or not isinstance(merged["right_hand"], dict):
                merged["right_hand"] = {"gestures": copy.deepcopy(DEFAULT_RIGHT_GESTURES)}
            else:
                merged["right_hand"].setdefault("gestures", copy.deepcopy(DEFAULT_RIGHT_GESTURES))
                self._merge_gesture_dict(merged["right_hand"]["gestures"], DEFAULT_RIGHT_GESTURES)

            # Merge left hand gestures
            if "left_hand" not in merged or not isinstance(merged["left_hand"], dict):
                merged["left_hand"] = {"gestures": copy.deepcopy(DEFAULT_LEFT_GESTURES)}
            else:
                merged["left_hand"].setdefault("gestures", copy.deepcopy(DEFAULT_LEFT_GESTURES))
                self._merge_gesture_dict(merged["left_hand"]["gestures"], DEFAULT_LEFT_GESTURES)

            self.last_mtime = os.path.getmtime(self.path)
            self.config = merged
            return self.config
        except Exception as e:
            print(f"Error loading {self.path}: {e}. Using defaults.")
            return copy.deepcopy(DEFAULT_CONFIG)

    def reload_if_changed(self):
        """
        Reloads configuration if the file has been modified on disk.
        Returns: True if reloaded, False otherwise.
        """
        if self.path.exists():
            try:
                mtime = os.path.getmtime(self.path)
                if mtime != self.last_mtime:
                    self.load()
                    return True
            except Exception:
                pass
        return False

    def save(self, data=None):
        if data is None:
            data = self.config
        else:
            self.config = data
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.last_mtime = os.path.getmtime(self.path)

            # Keep _internal/config.json in parity if it exists
            internal_cfg = get_base_dir() / "_internal" / "config.json"
            if internal_cfg.exists() and internal_cfg.resolve() != self.path.resolve():
                try:
                    with open(internal_cfg, "w", encoding="utf-8") as f_int:
                        json.dump(data, f_int, indent=2)
                except Exception:
                    pass

            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def is_split_hands_enabled(self):
        return bool(self.config.get("split_hands", False))

    def get_gesture_dict(self, hand=None):
        """
        Returns the appropriate gesture dictionary.
        If split_hands is enabled and hand is specified ('LEFT' or 'RIGHT'),
        returns that hand's gestures. Otherwise returns unified gestures.
        """
        if self.is_split_hands_enabled() and hand:
            key = "left_hand" if str(hand).upper() == "LEFT" else "right_hand"
            hand_cfg = self.config.get(key, {})
            if "gestures" in hand_cfg:
                return hand_cfg["gestures"]
        return self.config.get("gestures", {})

    def is_gesture_enabled(self, gesture_name, hand=None):
        g_dict = self.get_gesture_dict(hand)
        g = g_dict.get(gesture_name)
        if not g and gesture_name == "PINCH_INDEX":
            g = g_dict.get("PINCH")
        return bool(g and g.get("enabled", True))

    def get_action(self, gesture_name, hand=None):
        g_dict = self.get_gesture_dict(hand)
        g = g_dict.get(gesture_name)
        if not g and gesture_name == "PINCH_INDEX":
            g = g_dict.get("PINCH")
        if g and g.get("enabled", True):
            return g.get("action", "NONE")
        return "NONE"

    def is_repeat_allowed(self, gesture_name, hand=None):
        g_dict = self.get_gesture_dict(hand)
        g = g_dict.get(gesture_name)
        if not g and gesture_name == "PINCH_INDEX":
            g = g_dict.get("PINCH")
        return bool(g and g.get("repeat", False))

    def is_safety_clutch_enabled(self):
        return bool(self.config.get("safety_clutch", {}).get("enabled", False))

    def get_clutch_sign(self):
        return self.config.get("safety_clutch", {}).get("sign", "OPEN_PALM")

    def get_clutch_mode(self):
        return self.config.get("safety_clutch", {}).get("mode", "HOLD")

    def is_double_gesture_enabled(self):
        return bool(self.config.get("double_gesture", {}).get("enabled", False))

    def get_double_gesture_window(self):
        return float(self.config.get("double_gesture", {}).get("window_seconds", 0.75))
