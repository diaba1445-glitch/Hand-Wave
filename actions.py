import ctypes
import time

user32 = ctypes.windll.user32

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

# Virtual Key definitions
VK_MAP = {
    # Media & Volume
    "VOLUME_UP": (0xAF, True),
    "VOLUME_DOWN": (0xAE, True),
    "MUTE": (0xAD, True),
    "PLAY_PAUSE": (0xB3, True),
    "NEXT_TRACK": (0xB0, True),
    "PREV_TRACK": (0xB1, True),

    # Navigation & Control
    "RIGHT": (0x27, True),       # VK_RIGHT
    "LEFT": (0x25, True),        # VK_LEFT
    "UP": (0x26, True),          # VK_UP
    "DOWN": (0x28, True),        # VK_DOWN
    "PAGE_UP": (0x21, True),     # VK_PRIOR
    "PAGE_DOWN": (0x22, True),   # VK_NEXT
    "HOME": (0x24, True),        # VK_HOME
    "END": (0x23, True),         # VK_END

    # Common Keys
    "SPACE": (0x20, False),      # VK_SPACE
    "ENTER": (0x0D, False),      # VK_RETURN
    "ESCAPE": (0x1B, False),     # VK_ESCAPE
    "TAB": (0x09, False),        # VK_TAB
    "BACKSPACE": (0x08, False),  # VK_BACK
}

# Multi-Key Hotkeys (Windows Touchpad & Multitasking gestures)
HOTKEY_MAP = {
    # Virtual Desktop Navigation (4-finger swipe touchpad equivalents)
    "SWITCH_DESKTOP_RIGHT": [(0x5B, True), (0x11, False), (0x27, True)],  # Win + Ctrl + Right
    "SWITCH_DESKTOP_LEFT": [(0x5B, True), (0x11, False), (0x25, True)],   # Win + Ctrl + Left

    # Windows Multitasking (3-finger / 4-finger touchpad equivalents)
    "TASK_VIEW": [(0x5B, True), (0x09, False)],                            # Win + Tab
    "SHOW_DESKTOP": [(0x5B, True), (0x44, False)],                         # Win + D
    "APP_SWITCH": [(0x12, False), (0x09, False)],                          # Alt + Tab

    # Window Management
    "WINDOW_MAXIMIZE": [(0x5B, True), (0x26, True)],                       # Win + Up
    "WINDOW_MINIMIZE": [(0x5B, True), (0x28, True)],                       # Win + Down
    "CLOSE_WINDOW": [(0x12, False), (0x73, False)],                        # Alt + F4
}

ACTION_CHOICES = [
    # Desktop & Multitasking (Touchpad Functions)
    ("SWITCH_DESKTOP_RIGHT", "Switch Desktop Right (Win+Ctrl+Right)"),
    ("SWITCH_DESKTOP_LEFT", "Switch Desktop Left (Win+Ctrl+Left)"),
    ("TASK_VIEW", "Task View / Window Overview (Win+Tab)"),
    ("SHOW_DESKTOP", "Show Desktop / Minimize All (Win+D)"),
    ("APP_SWITCH", "Switch Application (Alt+Tab)"),

    # Window Management
    ("WINDOW_MAXIMIZE", "Maximize Window (Win+Up)"),
    ("WINDOW_MINIMIZE", "Minimize Window (Win+Down)"),
    ("CLOSE_WINDOW", "Close Window (Alt+F4)"),

    # Media & Volume
    ("VOLUME_UP", "Volume Up"),
    ("VOLUME_DOWN", "Volume Down"),
    ("MUTE", "Volume Mute"),
    ("PLAY_PAUSE", "Media Play/Pause"),
    ("NEXT_TRACK", "Media Next Track"),
    ("PREV_TRACK", "Media Previous Track"),

    # Navigation & Control
    ("SPACE", "Space / Play-Pause"),
    ("RIGHT", "Right Arrow (Next Slide / Seek)"),
    ("LEFT", "Left Arrow (Prev Slide / Seek)"),
    ("UP", "Up Arrow"),
    ("DOWN", "Down Arrow"),
    ("PAGE_UP", "Page Up"),
    ("PAGE_DOWN", "Page Down"),
    ("HOME", "Home"),
    ("END", "End"),
    ("ESCAPE", "Escape (Exit Fullscreen)"),
    ("ENTER", "Enter"),

    # Mouse & None
    ("MOUSE_LEFT", "Mouse Left Click"),
    ("MOUSE_RIGHT", "Mouse Right Click"),
    ("NONE", "None (Disabled)"),
]

def press_key(vk_code, extended=False):
    scan_code = user32.MapVirtualKeyW(vk_code, 0)
    flags = KEYEVENTF_EXTENDEDKEY if extended else 0
    user32.keybd_event(vk_code, scan_code, flags, 0)
    time.sleep(0.015)
    user32.keybd_event(vk_code, scan_code, flags | KEYEVENTF_KEYUP, 0)

def press_hotkey(keys):
    """
    Simulates pressing a key combination together and releasing in reverse order.
    keys: list of (vk_code, extended_bool)
    """
    for vk, ext in keys:
        scan = user32.MapVirtualKeyW(vk, 0)
        flags = KEYEVENTF_EXTENDEDKEY if ext else 0
        user32.keybd_event(vk, scan, flags, 0)
    time.sleep(0.02)
    for vk, ext in reversed(keys):
        scan = user32.MapVirtualKeyW(vk, 0)
        flags = (KEYEVENTF_EXTENDEDKEY if ext else 0) | KEYEVENTF_KEYUP
        user32.keybd_event(vk, scan, flags, 0)

def mouse_click(button="LEFT"):
    if button == "LEFT":
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.015)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    elif button == "RIGHT":
        user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.015)
        user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

def trigger_action(action_name):
    if not action_name or action_name == "NONE":
        return
    if action_name == "MOUSE_LEFT":
        mouse_click("LEFT")
        return
    if action_name == "MOUSE_RIGHT":
        mouse_click("RIGHT")
        return

    if action_name in HOTKEY_MAP:
        press_hotkey(HOTKEY_MAP[action_name])
        return

    if action_name in VK_MAP:
        vk_code, extended = VK_MAP[action_name]
        press_key(vk_code, extended)

