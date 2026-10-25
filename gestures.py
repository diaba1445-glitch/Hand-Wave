import math
from collections import deque
import numpy as np

# Landmark Indices
WRIST = 0
THUMB_CMC, THUMB_MCP, THUMB_IP, THUMB_TIP = 1, 2, 3, 4
INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP = 5, 6, 7, 8
MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP = 9, 10, 11, 12
RING_MCP, RING_PIP, RING_DIP, RING_TIP = 13, 14, 15, 16
PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP = 17, 18, 19, 20

BONES = [
    (0, 1), (1, 2), (2, 3), (3, 4),           # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),           # Index
    (5, 9), (9, 10), (10, 11), (11, 12),       # Middle
    (9, 13), (13, 14), (14, 15), (15, 16),    # Ring
    (13, 17), (17, 18), (18, 19), (19, 20),   # Pinky
    (0, 17)                                   # Palm base
]

def joint_angle(a, b, c):
    """3D angle at vertex b between vectors b->a and b->c (in degrees)."""
    ba = a - b
    bc = c - b
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)
    if norm_ba < 1e-6 or norm_bc < 1e-6:
        return 180.0
    cosine = np.dot(ba, bc) / (norm_ba * norm_bc)
    cosine = np.clip(cosine, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))

def vector_direction_2d(base_pt, tip_pt, cone_deg=35.0):
    """
    Returns 'RIGHT', 'LEFT', 'UP', 'DOWN', or None if diagonal.
    base_pt and tip_pt are (x, y) coordinates.
    """
    dx = tip_pt[0] - base_pt[0]
    dy = tip_pt[1] - base_pt[1]
    if abs(dx) < 1e-5 and abs(dy) < 1e-5:
        return None
    deg = math.degrees(math.atan2(dy, dx))
    
    # Check Right (0 deg)
    if abs(deg) <= cone_deg:
        return "RIGHT"
    # Check Left (180 / -180 deg)
    if abs(deg) >= (180.0 - cone_deg):
        return "LEFT"
    # Check Up (-90 deg in image coords where Y increases downwards)
    if abs(deg - (-90.0)) <= cone_deg:
        return "UP"
    # Check Down (+90 deg)
    if abs(deg - 90.0) <= cone_deg:
        return "DOWN"
    return None

class GestureClassifier:
    def __init__(self):
        self.was_pinching = False

    def detect_guard_sign(self, landmarks_px, landmarks_world):
        """
        Detects if this hand is displaying an activation guard sign:
        'OPEN_PALM' (✋), 'PEACE_SIGN' (✌️), 'FIST' (✊), or None.
        """
        if landmarks_world is None or len(landmarks_world) < 21:
            return None

        world = np.array(landmarks_world)
        px = np.array(landmarks_px)

        index_bend = joint_angle(world[INDEX_MCP], world[INDEX_PIP], world[INDEX_DIP])
        middle_bend = joint_angle(world[MIDDLE_MCP], world[MIDDLE_PIP], world[MIDDLE_DIP])
        ring_bend = joint_angle(world[RING_MCP], world[RING_PIP], world[RING_DIP])
        pinky_bend = joint_angle(world[PINKY_MCP], world[PINKY_PIP], world[PINKY_DIP])

        index_straight = index_bend > 130.0
        middle_straight = middle_bend > 130.0
        ring_straight = ring_bend > 130.0
        pinky_straight = pinky_bend > 130.0

        index_curled = index_bend < 135.0
        middle_curled = middle_bend < 135.0
        ring_curled = ring_bend < 135.0
        pinky_curled = pinky_bend < 135.0

        thumb_tip_dist = np.linalg.norm(world[THUMB_TIP] - world[PINKY_MCP])
        thumb_ip_dist = np.linalg.norm(world[THUMB_IP] - world[PINKY_MCP])
        thumb_out = (thumb_tip_dist / max(1e-5, thumb_ip_dist)) > 1.08

        # 1. OPEN_PALM: 4 fingers extended straight + thumb out
        straight_count = sum([index_straight, middle_straight, ring_straight, pinky_straight])
        if straight_count >= 4 and thumb_out:
            return "OPEN_PALM"

        # 2. PEACE_SIGN: Index & Middle straight, Ring & Pinky curled
        if index_straight and middle_straight and ring_curled and pinky_curled:
            v_dist = np.linalg.norm(world[INDEX_TIP] - world[MIDDLE_TIP])
            palm_size_w = np.linalg.norm(world[WRIST] - world[MIDDLE_MCP])
            if v_dist > max(1e-4, palm_size_w) * 0.18:
                return "PEACE_SIGN"

        # 3. FIST: All 4 fingers curled + thumb across fingers
        curled_count = sum([index_curled, middle_curled, ring_curled, pinky_curled])
        if curled_count == 4 and not thumb_out:
            return "FIST"

        return None

    def classify(self, landmarks_px, landmarks_world):
        """
        landmarks_px: (21, 2) array of pixel coordinates (mirrored)
        landmarks_world: (21, 3) array in meters (hand-centred 3D)
        Returns: gesture name ('THUMB_UP', 'THUMB_DOWN', 'POINT_RIGHT', 'POINT_LEFT', 'PINCH') or None
        """
        if landmarks_world is None or len(landmarks_world) < 21:
            return None

        world = np.array(landmarks_world)
        px = np.array(landmarks_px)

        # 1. Check finger curl angles in 3D world coordinates
        # Natural relaxed fists have PIP angles around 125-135 deg; straight fingers are > 130 deg
        index_bend = joint_angle(world[INDEX_MCP], world[INDEX_PIP], world[INDEX_DIP])
        middle_bend = joint_angle(world[MIDDLE_MCP], world[MIDDLE_PIP], world[MIDDLE_DIP])
        ring_bend = joint_angle(world[RING_MCP], world[RING_PIP], world[RING_DIP])
        pinky_bend = joint_angle(world[PINKY_MCP], world[PINKY_PIP], world[PINKY_DIP])

        index_straight = index_bend > 130.0
        middle_straight = middle_bend > 130.0
        ring_straight = ring_bend > 130.0
        pinky_straight = pinky_bend > 130.0

        index_curled = index_bend < 135.0
        middle_curled = middle_bend < 135.0
        ring_curled = ring_bend < 135.0
        pinky_curled = pinky_bend < 135.0

        # Check Palm Scale (in 3D meters and in 2D pixels)
        palm_size_w = np.linalg.norm(world[WRIST] - world[MIDDLE_MCP])
        if palm_size_w < 1e-4:
            palm_size_w = 0.1
        palm_size_px = np.linalg.norm(px[WRIST] - px[MIDDLE_MCP])
        if palm_size_px < 1e-4:
            palm_size_px = 100.0

        # 2. Check Pinch / Touch between Thumb and Fingers
        # Measures pad-to-pad, pad-to-tip, and tip-to-tip across 2D & 3D space
        def get_contact_ratio(f_tip_idx, f_dip_idx):
            thumb_pad = (world[THUMB_TIP] + world[THUMB_IP]) * 0.5
            finger_pad = (world[f_tip_idx] + world[f_dip_idx]) * 0.5

            d3 = min(
                np.linalg.norm(world[THUMB_TIP] - world[f_tip_idx]),
                np.linalg.norm(world[THUMB_TIP] - world[f_dip_idx]),
                np.linalg.norm(world[f_tip_idx] - thumb_pad),
                np.linalg.norm(thumb_pad - finger_pad)
            )
            ratio_3d = d3 / palm_size_w

            thumb_pad_px = (px[THUMB_TIP] + px[THUMB_IP]) * 0.5
            finger_pad_px = (px[f_tip_idx] + px[f_dip_idx]) * 0.5

            d2 = min(
                np.linalg.norm(px[THUMB_TIP] - px[f_tip_idx]),
                np.linalg.norm(px[THUMB_TIP] - px[f_dip_idx]),
                np.linalg.norm(px[f_tip_idx] - thumb_pad_px),
                np.linalg.norm(thumb_pad_px - finger_pad_px)
            )
            ratio_2d = d2 / palm_size_px

            # Check depth difference so fingers on different planes don't false-trigger
            z_diff = abs(world[THUMB_TIP][2] - world[f_tip_idx][2])
            if z_diff < 0.065:
                # Fused contact: pick the closer metric (allowing angled / side hand poses)
                return min(ratio_3d, ratio_2d * 1.15), d3
            return ratio_3d, d3

        pinch_candidates = [
            ("PINCH_INDEX", *get_contact_ratio(INDEX_TIP, INDEX_DIP)),
            ("PINCH_MIDDLE", *get_contact_ratio(MIDDLE_TIP, MIDDLE_DIP)),
            ("PINCH_RING", *get_contact_ratio(RING_TIP, RING_DIP)),
            ("PINCH_PINKY", *get_contact_ratio(PINKY_TIP, PINKY_DIP)),
        ]
        pinch_candidates.sort(key=lambda x: x[1])
        closest_name, closest_ratio, closest_d3 = pinch_candidates[0]

        is_pinching = False
        if self.was_pinching == closest_name:
            if closest_ratio < 0.45:
                is_pinching = True
        else:
            second_ratio = pinch_candidates[1][1]
            if closest_ratio < 0.35 and (closest_ratio < second_ratio * 0.90 or closest_ratio < 0.22):
                is_pinching = True

        if is_pinching:
            self.was_pinching = closest_name
            return closest_name
        else:
            self.was_pinching = None

        # 3. Check Thumb Extended away from fist
        thumb_tip_dist = np.linalg.norm(world[THUMB_TIP] - world[PINKY_MCP])
        thumb_ip_dist = np.linalg.norm(world[THUMB_IP] - world[PINKY_MCP])
        thumb_out = (thumb_tip_dist / max(1e-5, thumb_ip_dist)) > 1.08

        # Count curled non-thumb fingers (3 or 4 fingers curled)
        curled_count = sum([index_curled, middle_curled, ring_curled, pinky_curled])

        # 4. Check Thumbs Up / Thumbs Down
        if thumb_out and curled_count >= 3:
            thumb_dir = vector_direction_2d(px[THUMB_CMC], px[THUMB_TIP], cone_deg=50.0)
            if thumb_dir == "UP":
                return "THUMB_UP"
            elif thumb_dir == "DOWN":
                return "THUMB_DOWN"

        # 5. Check Pointing Right / Left
        # Index finger extended straight, other fingers curled
        other_curled = sum([middle_curled, ring_curled, pinky_curled]) >= 2
        if index_straight and other_curled:
            index_dir = vector_direction_2d(px[INDEX_MCP], px[INDEX_TIP], cone_deg=48.0)
            if index_dir == "RIGHT":
                return "POINT_RIGHT"
            elif index_dir == "LEFT":
                return "POINT_LEFT"

        return None

class MotionDetector:
    def __init__(self, cooldown=0.45):
        self.histories = {}  # hand_id -> deque of (x, y, timestamp)
        self.last_swipe_time = 0.0
        self.cooldown = cooldown

    def clear(self):
        self.histories.clear()

    def update(self, hand_id, palm_center_norm, now):
        """
        palm_center_norm: (x, y) in [0.0, 1.0] (mirrored image space)
        now: monotonic timestamp in seconds
        Returns: 'SWIPE_RIGHT', 'SWIPE_LEFT', 'SWIPE_UP', 'SWIPE_DOWN', or None
        """
        if now - self.last_swipe_time < self.cooldown:
            return None

        x, y = palm_center_norm

        if hand_id not in self.histories:
            self.histories[hand_id] = deque(maxlen=20)

        hist = self.histories[hand_id]

        # Teleport jump detection (hand swapped slot or sudden glitch)
        if hist and (now - hist[-1][2] < 0.10):
            instant_dist = math.hypot(x - hist[-1][0], y - hist[-1][1])
            if instant_dist > 0.30:
                hist.clear()

        # Prune points older than 0.50s
        while hist and (now - hist[0][2] > 0.50):
            hist.popleft()

        hist.append((x, y, now))

        # Check movement against past points in a 0.10s - 0.40s window
        for old_x, old_y, old_t in list(hist):
            dt = now - old_t
            if 0.10 <= dt <= 0.40:
                dx = x - old_x
                dy = y - old_y
                abs_dx = abs(dx)
                abs_dy = abs(dy)

                # Horizontal swipe
                if abs_dx > 0.14 and abs_dx > 1.35 * abs_dy:
                    vel = abs_dx / dt
                    if 0.50 <= vel <= 3.8:
                        self.last_swipe_time = now
                        self.histories[hand_id].clear()
                        return "SWIPE_RIGHT" if dx > 0 else "SWIPE_LEFT"

                # Vertical swipe (Y decreases when moving upwards on screen)
                if abs_dy > 0.14 and abs_dy > 1.35 * abs_dx:
                    vel = abs_dy / dt
                    if 0.50 <= vel <= 3.8:
                        self.last_swipe_time = now
                        self.histories[hand_id].clear()
                        return "SWIPE_UP" if dy < 0 else "SWIPE_DOWN"

        return None

