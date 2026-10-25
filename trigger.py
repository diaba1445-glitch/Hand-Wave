import time
from actions import trigger_action

class GestureTrigger:
    def __init__(self, config_manager):
        self.cfg = config_manager
        self.active_gesture = None
        self.active_hand = None
        self.gesture_start_time = 0.0
        self.last_fire_time = 0.0
        self.fired_once = False

        # Double-gesture confirmation state
        self.pending_gesture = None
        self.pending_hand = None
        self.pending_expire_time = 0.0
        self.has_released_since_first = False

    def get_pending_confirmation(self):
        """
        Returns info about pending first tap:
        (gesture, hand, time_left, ratio 0.0-1.0) or None
        """
        if not self.pending_gesture:
            return None
        now = time.monotonic()
        if now > self.pending_expire_time:
            self.pending_gesture = None
            self.pending_hand = None
            return None
        window = self.cfg.get_double_gesture_window()
        time_left = max(0.0, self.pending_expire_time - now)
        ratio = time_left / max(0.01, window)
        return (self.pending_gesture, self.pending_hand, time_left, ratio)

    def cancel_pending(self):
        self.pending_gesture = None
        self.pending_hand = None
        self.pending_expire_time = 0.0
        self.has_released_since_first = False

    def update(self, detected_gesture, hand=None):
        """
        Feed the gesture detected in the current frame.
        hand: 'LEFT', 'RIGHT', or None
        Returns: (fired_action_name or None, hold_progress 0.0-1.0)
        """
        now = time.monotonic()
        hold_time = self.cfg.config.get("hold_time_seconds", 0.35)
        double_mode = self.cfg.is_double_gesture_enabled()
        window = self.cfg.get_double_gesture_window()

        # Check pending expiration
        if self.pending_gesture and now > self.pending_expire_time:
            self.pending_gesture = None
            self.pending_hand = None
            self.has_released_since_first = False

        # Track release for double-tap
        if self.pending_gesture is not None:
            if detected_gesture is None or detected_gesture != self.pending_gesture or hand != self.pending_hand:
                self.has_released_since_first = True

        # If gesture or hand changed
        if detected_gesture != self.active_gesture or (hand != self.active_hand and detected_gesture is not None):
            self.active_gesture = detected_gesture
            self.active_hand = hand
            self.gesture_start_time = now
            self.last_fire_time = 0.0
            self.fired_once = False

        if not self.active_gesture:
            return None, 0.0

        # Check if enabled in configuration for this hand
        if not self.cfg.is_gesture_enabled(self.active_gesture, hand=self.active_hand):
            return None, 0.0

        action = self.cfg.get_action(self.active_gesture, hand=self.active_hand)
        if not action or action == "NONE":
            return None, 0.0

        elapsed = now - self.gesture_start_time
        # Pinches are discrete taps and should trigger snappily
        effective_hold_time = min(0.18, hold_time * 0.6) if self.active_gesture.startswith("PINCH") else hold_time
        progress = min(1.0, elapsed / max(0.01, effective_hold_time))
        allow_repeat = self.cfg.is_repeat_allowed(self.active_gesture, hand=self.active_hand)

        # ---------------- DOUBLE GESTURE LOGIC ----------------
        if double_mode:
            # Gesture reached trigger threshold
            ready_to_trigger = False
            if self.active_gesture.startswith("SWIPE_"):
                ready_to_trigger = not self.fired_once
            else:
                ready_to_trigger = (elapsed >= effective_hold_time)

            if ready_to_trigger:
                # Is this the second tap confirming the first tap?
                is_second_tap = (
                    self.pending_gesture == self.active_gesture and
                    self.pending_hand == self.active_hand and
                    self.has_released_since_first and
                    now <= self.pending_expire_time
                )

                if is_second_tap:
                    if not self.fired_once:
                        trigger_action(action)
                        self.fired_once = True
                        self.last_fire_time = now
                        self.cancel_pending()
                        return action, 1.0
                    elif allow_repeat and not self.active_gesture.startswith("SWIPE_"):
                        repeat_interval = 0.12
                        if now - self.last_fire_time >= repeat_interval:
                            trigger_action(action)
                            self.last_fire_time = now
                            return action, 1.0
                else:
                    # First tap: Arm pending confirmation
                    if not self.fired_once:
                        self.pending_gesture = self.active_gesture
                        self.pending_hand = self.active_hand
                        self.pending_expire_time = now + window
                        self.has_released_since_first = False
                        self.fired_once = True
                        self.last_fire_time = now
            return None, progress

        # ---------------- STANDARD SINGLE-TAP LOGIC ----------------
        if self.active_gesture.startswith("SWIPE_"):
            if not self.fired_once:
                trigger_action(action)
                self.fired_once = True
                self.last_fire_time = now
                return action, 1.0
            return None, 1.0

        if elapsed >= effective_hold_time:
            if not self.fired_once:
                # First fire
                trigger_action(action)
                self.fired_once = True
                self.last_fire_time = now
                return action, 1.0
            elif allow_repeat:
                # Repeat fire every 0.12s
                repeat_interval = 0.12
                if now - self.last_fire_time >= repeat_interval:
                    trigger_action(action)
                    self.last_fire_time = now
                    return action, 1.0

        return None, progress
