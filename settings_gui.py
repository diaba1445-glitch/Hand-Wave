import tkinter as tk
from tkinter import ttk, messagebox
from config_manager import ConfigManager, DEFAULT_CONFIG, CONFIG_PATH
from actions import ACTION_CHOICES

class SettingsWindow:
    def __init__(self, root=None, config_manager=None, on_save_callback=None):
        self.own_root = False
        if root is None:
            self.root = tk.Tk()
            self.own_root = True
        else:
            self.root = tk.Toplevel(root)

        self.cfg = config_manager if config_manager else ConfigManager(CONFIG_PATH)
        self.on_save = on_save_callback

        self.root.title("HandWave — Settings")
        self.root.geometry("680x780")
        self.root.minsize(620, 560)
        self.root.configure(bg="#1e1e24")

        # Handle window close [X]
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Styling
        self.setup_styles()

        # Build UI
        self.build_ui()

        # Center Window
        self.center_window()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure colors
        style.configure(".", background="#1e1e24", foreground="#f0f0f5", font=("Segoe UI", 10))
        style.configure("TFrame", background="#1e1e24")
        style.configure("Card.TFrame", background="#282833", relief="flat")
        style.configure("TLabel", background="#1e1e24", foreground="#f0f0f5", font=("Segoe UI", 10))
        style.configure("Card.TLabel", background="#282833", foreground="#f0f0f5")
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#4cc9f0")
        style.configure("Subheader.TLabel", font=("Segoe UI", 10), foreground="#a0a0b2")
        style.configure("Section.TLabel", font=("Segoe UI", 10, "bold"), background="#282833", foreground="#9d4edd")
        
        style.configure("TCheckbutton", background="#282833", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
        style.map("TCheckbutton", background=[("active", "#282833")])

        style.configure("TCombobox", fieldbackground="#333344", background="#444455", foreground="#ffffff")
        style.map("TCombobox", fieldbackground=[("readonly", "#333344")], foreground=[("readonly", "#ffffff")])

        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), background="#4361ee", foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", "#3a0ca3")])
        
        style.configure("Secondary.TButton", font=("Segoe UI", 10), background="#3a3a4c", foreground="#ffffff")
        style.map("Secondary.TButton", background=[("active", "#4a4a5e")])

        # Notebook tabs styling
        style.configure("TNotebook", background="#1e1e24", borderwidth=0)
        style.configure("TNotebook.Tab", background="#282833", foreground="#a0a0b2", padding=[16, 7], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", "#3a3a4c"), ("active", "#333342")],
                  foreground=[("selected", "#4cc9f0"), ("active", "#ffffff")])

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

    def build_ui(self):
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True)

        # Header (Pinned Top)
        header_frame = ttk.Frame(container, padding=(20, 16, 20, 10))
        header_frame.pack(fill="x", side="top")
        header_lbl = ttk.Label(header_frame, text="Gesture Control Settings", style="Header.TLabel")
        header_lbl.pack(anchor="w")
        sub_lbl = ttk.Label(header_frame, text="Enable/disable gestures, assign actions, and configure safety clutch.", style="Subheader.TLabel")
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Bottom Buttons (Pinned Bottom)
        btn_frame = ttk.Frame(container, padding=(20, 10, 20, 16))
        btn_frame.pack(fill="x", side="bottom")

        reset_btn = ttk.Button(btn_frame, text="Reset Defaults", style="Secondary.TButton", command=self.reset_defaults)
        reset_btn.pack(side="left")

        save_btn = ttk.Button(btn_frame, text="Save & Apply", style="Primary.TButton", command=self.save_settings)
        save_btn.pack(side="right")

        # Scrollable Canvas
        canvas_container = ttk.Frame(container)
        canvas_container.pack(fill="both", expand=True, padx=(16, 4), pady=(0, 4))

        canvas = tk.Canvas(canvas_container, bg="#1e1e24", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="TFrame")

        def _on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", _on_frame_configure)
        frame_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def _on_canvas_configure(e):
            canvas.itemconfig(frame_window, width=e.width)

        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.root.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>") if e.widget == self.root else None)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Action choices dictionary for display
        self.action_display_to_id = {name: aid for aid, name in ACTION_CHOICES}
        self.action_id_to_display = {aid: name for aid, name in ACTION_CHOICES}
        action_names = [name for _, name in ACTION_CHOICES]

        self.unified_gesture_vars = {}
        self.right_gesture_vars = {}
        self.left_gesture_vars = {}

        # ----------------- Split Hands Mode Toggle Card -----------------
        mode_card = ttk.Frame(scrollable_frame, style="Card.TFrame", padding=14)
        mode_card.pack(fill="x", pady=(0, 15))

        mode_header = ttk.Frame(mode_card, style="Card.TFrame")
        mode_header.pack(fill="x")

        self.split_hands_var = tk.BooleanVar(value=self.cfg.is_split_hands_enabled())
        mode_chk = ttk.Checkbutton(
            mode_header,
            text="Split Hands Mode (Configure Left & Right Hands Separately)",
            variable=self.split_hands_var,
            command=self.toggle_hand_mode_ui
        )
        mode_chk.pack(side="left")

        mode_desc = ttk.Label(
            mode_card,
            text="When enabled, Left and Right hands have independent gesture actions. When disabled, both hands use Unified actions.",
            style="Subheader.TLabel"
        )
        mode_desc.pack(anchor="w", pady=(4, 0))

        # ----------------- Gestures Container -----------------
        self.gesture_container = ttk.Frame(scrollable_frame, style="TFrame")
        self.gesture_container.pack(fill="x", pady=(0, 15))

        # 1. Unified Card (Both Hands)
        self.unified_card = ttk.Frame(self.gesture_container, style="Card.TFrame", padding=14)
        card_title = ttk.Label(
            self.unified_card,
            text="Active Gestures & Mappings (Both Hands)",
            font=("Segoe UI", 11, "bold"),
            style="Card.TLabel",
            foreground="#4cc9f0"
        )
        card_title.pack(anchor="w", pady=(0, 10))

        gestures_data = self.cfg.config.get("gestures", {})
        self._build_gesture_rows(
            self.unified_card,
            gestures_data,
            DEFAULT_CONFIG["gestures"],
            self.unified_gesture_vars,
            action_names
        )

        # 2. Split Hands Notebook (Tabs for Right and Left)
        self.split_notebook = ttk.Notebook(self.gesture_container)

        # Tab: Right Hand
        right_tab = ttk.Frame(self.split_notebook, style="Card.TFrame", padding=14)
        right_title = ttk.Label(
            right_tab,
            text="🟢 Right Hand Gestures (Navigation & Primary Actions)",
            font=("Segoe UI", 11, "bold"),
            style="Card.TLabel",
            foreground="#40dc80"
        )
        right_title.pack(anchor="w", pady=(0, 10))

        right_data = self.cfg.config.get("right_hand", {}).get("gestures", {})
        self._build_gesture_rows(
            right_tab,
            right_data,
            DEFAULT_CONFIG["right_hand"]["gestures"],
            self.right_gesture_vars,
            action_names
        )
        self.split_notebook.add(right_tab, text="  🟢 Right Hand  ")

        # Tab: Left Hand
        left_tab = ttk.Frame(self.split_notebook, style="Card.TFrame", padding=14)
        left_title = ttk.Label(
            left_tab,
            text="🔵 Left Hand Gestures (Media & Multitasking Actions)",
            font=("Segoe UI", 11, "bold"),
            style="Card.TLabel",
            foreground="#4cc9f0"
        )
        left_title.pack(anchor="w", pady=(0, 10))

        left_data = self.cfg.config.get("left_hand", {}).get("gestures", {})
        self._build_gesture_rows(
            left_tab,
            left_data,
            DEFAULT_CONFIG["left_hand"]["gestures"],
            self.left_gesture_vars,
            action_names
        )
        self.split_notebook.add(left_tab, text="  🔵 Left Hand  ")

        # Display whichever mode is currently active
        self.toggle_hand_mode_ui()

        # Safety Clutch Card
        clutch_card = ttk.Frame(scrollable_frame, style="Card.TFrame", padding=14)
        clutch_card.pack(fill="x", pady=(0, 15))

        clutch_header = ttk.Frame(clutch_card, style="Card.TFrame")
        clutch_header.pack(fill="x", pady=(0, 4))

        clutch_cfg = self.cfg.config.get("safety_clutch", {})
        self.clutch_en_var = tk.BooleanVar(value=clutch_cfg.get("enabled", False))

        clutch_chk = ttk.Checkbutton(clutch_header, text="Two-Hand Safety Clutch (Guard Hand)", variable=self.clutch_en_var)
        clutch_chk.pack(side="left")

        clutch_desc = ttk.Label(clutch_card, text="Stops gestures on one hand until the other hand shows an activation sign.", style="Subheader.TLabel")
        clutch_desc.pack(anchor="w", pady=(0, 8))

        clutch_opts = ttk.Frame(clutch_card, style="Card.TFrame")
        clutch_opts.pack(fill="x")

        # Guard Sign Choices
        ttk.Label(clutch_opts, text="Guard Sign:", style="Card.TLabel").pack(side="left", padx=(0, 6))

        self.clutch_sign_map = {
            "Open Palm (✋)": "OPEN_PALM",
            "Peace / V-Sign (✌️)": "PEACE_SIGN",
            "Closed Fist (✊)": "FIST"
        }
        self.clutch_sign_rev = {v: k for k, v in self.clutch_sign_map.items()}
        curr_sign_id = clutch_cfg.get("sign", "OPEN_PALM")
        self.clutch_sign_var = tk.StringVar(value=self.clutch_sign_rev.get(curr_sign_id, "Open Palm (✋)"))

        sign_combo = ttk.Combobox(clutch_opts, textvariable=self.clutch_sign_var, values=list(self.clutch_sign_map.keys()), state="readonly", width=18)
        sign_combo.pack(side="left", padx=(0, 16))

        # Guard Mode Choices
        ttk.Label(clutch_opts, text="Mode:", style="Card.TLabel").pack(side="left", padx=(0, 6))
        self.clutch_mode_map = {
            "Hold to Activate (Clutch)": "HOLD",
            "Toggle On/Off": "TOGGLE"
        }
        self.clutch_mode_rev = {v: k for k, v in self.clutch_mode_map.items()}
        curr_mode_id = clutch_cfg.get("mode", "HOLD")
        self.clutch_mode_var = tk.StringVar(value=self.clutch_mode_rev.get(curr_mode_id, "Hold to Activate (Clutch)"))

        mode_combo = ttk.Combobox(clutch_opts, textvariable=self.clutch_mode_var, values=list(self.clutch_mode_map.keys()), state="readonly", width=22)
        mode_combo.pack(side="left")

        # Double-Gesture Confirmation Card
        double_card = ttk.Frame(scrollable_frame, style="Card.TFrame", padding=14)
        double_card.pack(fill="x", pady=(0, 15))

        double_header = ttk.Frame(double_card, style="Card.TFrame")
        double_header.pack(fill="x", pady=(0, 4))

        double_cfg = self.cfg.config.get("double_gesture", {})
        self.double_en_var = tk.BooleanVar(value=double_cfg.get("enabled", False))

        double_chk = ttk.Checkbutton(double_header, text="Double-Gesture Confirmation (Double-Tap to Fire)", variable=self.double_en_var)
        double_chk.pack(side="left")

        double_desc = ttk.Label(
            double_card,
            text="Requires repeating a gesture twice quickly to execute (like a mouse double-click). Great for single-hand use without accidental mistakes.",
            style="Subheader.TLabel"
        )
        double_desc.pack(anchor="w", pady=(0, 8))

        double_opts = ttk.Frame(double_card, style="Card.TFrame")
        double_opts.pack(fill="x")

        ttk.Label(double_opts, text="Double-Tap Window:", style="Card.TLabel").pack(side="left", padx=(0, 6))
        window_val = float(double_cfg.get("window_seconds", 0.75))
        self.double_window_lbl = ttk.Label(double_opts, text=f"{window_val:.2f}s", font=("Segoe UI", 10, "bold"), style="Card.TLabel", foreground="#00d7ff")
        self.double_window_lbl.pack(side="right")

        self.double_window_var = tk.DoubleVar(value=window_val)
        double_slider = ttk.Scale(
            double_card,
            from_=0.40,
            to=1.30,
            variable=self.double_window_var,
            command=lambda v: self.double_window_lbl.config(text=f"{float(v):.2f}s")
        )
        double_slider.pack(fill="x", pady=(4, 0))

        # Parameters Card
        param_card = ttk.Frame(scrollable_frame, style="Card.TFrame", padding=14)
        param_card.pack(fill="x", pady=(0, 10))

        param_title = ttk.Label(param_card, text="General Options", font=("Segoe UI", 11, "bold"), style="Card.TLabel", foreground="#4cc9f0")
        param_title.pack(anchor="w", pady=(0, 10))

        # Hold Time Slider
        slider_frame = ttk.Frame(param_card, style="Card.TFrame")
        slider_frame.pack(fill="x", pady=4)

        hold_time = self.cfg.config.get("hold_time_seconds", 0.35)
        ttk.Label(slider_frame, text="Hold Duration (Sensitivity):", style="Card.TLabel").pack(side="left")

        self.slider_lbl = ttk.Label(slider_frame, text=f"{hold_time:.2f}s", font=("Segoe UI", 10, "bold"), style="Card.TLabel", foreground="#4cc9f0")
        self.slider_lbl.pack(side="right")

        self.hold_var = tk.DoubleVar(value=hold_time)
        slider = ttk.Scale(param_card, from_=0.15, to=0.90, variable=self.hold_var, command=self.update_slider_label)
        slider.pack(fill="x", pady=(2, 10))

        # Camera & Topmost Row
        opts_frame = ttk.Frame(param_card, style="Card.TFrame")
        opts_frame.pack(fill="x", pady=2)

        ttk.Label(opts_frame, text="Camera Index:", style="Card.TLabel").pack(side="left", padx=(0, 8))
        self.cam_var = tk.IntVar(value=self.cfg.config.get("camera_index", 0))
        cam_spin = ttk.Spinbox(opts_frame, from_=0, to=4, textvariable=self.cam_var, width=4)
        cam_spin.pack(side="left", padx=(0, 20))

        self.topmost_var = tk.BooleanVar(value=self.cfg.config.get("topmost", True))
        ttk.Checkbutton(opts_frame, text="Keep on Top", variable=self.topmost_var).pack(side="left", padx=(0, 15))

        self.skeleton_var = tk.BooleanVar(value=self.cfg.config.get("draw_skeleton", True))
        ttk.Checkbutton(opts_frame, text="Show Skeleton", variable=self.skeleton_var).pack(side="left", padx=(0, 15))

        self.mirrored_var = tk.BooleanVar(value=self.cfg.config.get("mirrored", True))
        ttk.Checkbutton(opts_frame, text="Mirror Camera", variable=self.mirrored_var).pack(side="left")

    def _build_gesture_rows(self, parent_frame, gestures_data, default_data, store_dict, action_names):
        sections = [
            ("Static Poses & Pointing", ["THUMB_UP", "THUMB_DOWN", "POINT_RIGHT", "POINT_LEFT"]),
            ("Finger Pinches (Thumb Touches)", ["PINCH_INDEX", "PINCH_MIDDLE", "PINCH_RING", "PINCH_PINKY"]),
            ("Directional Swipes (Wave Hand)", ["SWIPE_RIGHT", "SWIPE_LEFT", "SWIPE_UP", "SWIPE_DOWN"])
        ]

        for sec_title, g_list in sections:
            sec_lbl = ttk.Label(parent_frame, text=sec_title, style="Section.TLabel")
            sec_lbl.pack(anchor="w", pady=(8, 4))

            for g_id in g_list:
                default_info = default_data.get(g_id, {})
                if g_id == "PINCH_INDEX" and "PINCH_INDEX" not in gestures_data and "PINCH" in gestures_data:
                    g_info = gestures_data["PINCH"]
                else:
                    g_info = gestures_data.get(g_id, default_info)

                row_frame = ttk.Frame(parent_frame, style="Card.TFrame")
                row_frame.pack(fill="x", pady=4)

                # Checkbox
                en_var = tk.BooleanVar(value=g_info.get("enabled", True))
                chk = ttk.Checkbutton(row_frame, text=g_info.get("label", g_id), variable=en_var)
                chk.pack(side="left", padx=(0, 10))

                # Action Combobox
                curr_action = g_info.get("action", "NONE")
                curr_display = self.action_id_to_display.get(curr_action, "None (Disabled)")
                act_var = tk.StringVar(value=curr_display)

                combo = ttk.Combobox(row_frame, textvariable=act_var, values=action_names, state="readonly", width=34)
                combo.pack(side="right")

                # Repeat Checkbox
                rep_var = tk.BooleanVar(value=g_info.get("repeat", False))

                store_dict[g_id] = {
                    "enabled": en_var,
                    "action": act_var,
                    "repeat": rep_var,
                    "label": g_info.get("label", g_id)
                }

    def toggle_hand_mode_ui(self):
        if self.split_hands_var.get():
            self.unified_card.pack_forget()
            self.split_notebook.pack(fill="x")
        else:
            self.split_notebook.pack_forget()
            self.unified_card.pack(fill="x")

    def update_slider_label(self, val):
        self.slider_lbl.config(text=f"{float(val):.2f}s")

    def _reset_dict_controls(self, store_dict, default_dict):
        for g_id, g_info in default_dict.items():
            if g_id in store_dict:
                store_dict[g_id]["enabled"].set(g_info["enabled"])
                disp = self.action_id_to_display.get(g_info["action"], "None (Disabled)")
                store_dict[g_id]["action"].set(disp)
                store_dict[g_id]["repeat"].set(g_info["repeat"])

    def reset_defaults(self):
        self.split_hands_var.set(DEFAULT_CONFIG.get("split_hands", False))
        self.toggle_hand_mode_ui()

        # Reset unified gestures
        self._reset_dict_controls(self.unified_gesture_vars, DEFAULT_CONFIG["gestures"])

        # Reset right hand gestures
        self._reset_dict_controls(self.right_gesture_vars, DEFAULT_CONFIG["right_hand"]["gestures"])

        # Reset left hand gestures
        self._reset_dict_controls(self.left_gesture_vars, DEFAULT_CONFIG["left_hand"]["gestures"])

        self.hold_var.set(DEFAULT_CONFIG["hold_time_seconds"])
        self.slider_lbl.config(text=f"{DEFAULT_CONFIG['hold_time_seconds']:.2f}s")
        self.cam_var.set(DEFAULT_CONFIG["camera_index"])
        self.topmost_var.set(DEFAULT_CONFIG["topmost"])
        self.skeleton_var.set(DEFAULT_CONFIG["draw_skeleton"])
        self.mirrored_var.set(DEFAULT_CONFIG.get("mirrored", True))

        # Reset Safety Clutch
        clutch_def = DEFAULT_CONFIG.get("safety_clutch", {})
        self.clutch_en_var.set(clutch_def.get("enabled", False))
        self.clutch_sign_var.set(self.clutch_sign_rev.get(clutch_def.get("sign", "OPEN_PALM"), "Open Palm (✋)"))
        self.clutch_mode_var.set(self.clutch_mode_rev.get(clutch_def.get("mode", "HOLD"), "Hold to Activate (Clutch)"))

        # Reset Double Gesture
        double_def = DEFAULT_CONFIG.get("double_gesture", {})
        self.double_en_var.set(double_def.get("enabled", False))
        def_win = float(double_def.get("window_seconds", 0.75))
        self.double_window_var.set(def_win)
        self.double_window_lbl.config(text=f"{def_win:.2f}s")

    def _extract_gesture_data(self, store_dict):
        result = {}
        for g_id, g_ctrl in store_dict.items():
            disp_act = g_ctrl["action"].get()
            act_id = self.action_display_to_id.get(disp_act, "NONE")
            result[g_id] = {
                "enabled": bool(g_ctrl["enabled"].get()),
                "action": act_id,
                "label": g_ctrl["label"],
                "repeat": bool(g_ctrl["repeat"].get())
            }
        return result

    def save_settings(self):
        clutch_sign_name = self.clutch_sign_var.get()
        clutch_sign_id = self.clutch_sign_map.get(clutch_sign_name, "OPEN_PALM")

        clutch_mode_name = self.clutch_mode_var.get()
        clutch_mode_id = self.clutch_mode_map.get(clutch_mode_name, "HOLD")

        new_data = {
            "split_hands": bool(self.split_hands_var.get()),
            "double_gesture": {
                "enabled": bool(self.double_en_var.get()),
                "window_seconds": round(float(self.double_window_var.get()), 2)
            },
            "gestures": self._extract_gesture_data(self.unified_gesture_vars),
            "right_hand": {
                "gestures": self._extract_gesture_data(self.right_gesture_vars)
            },
            "left_hand": {
                "gestures": self._extract_gesture_data(self.left_gesture_vars)
            },
            "hold_time_seconds": round(float(self.hold_var.get()), 2),
            "camera_index": int(self.cam_var.get()),
            "topmost": bool(self.topmost_var.get()),
            "draw_skeleton": bool(self.skeleton_var.get()),
            "mirrored": bool(self.mirrored_var.get()),
            "safety_clutch": {
                "enabled": bool(self.clutch_en_var.get()),
                "sign": clutch_sign_id,
                "mode": clutch_mode_id
            }
        }

        ok = self.cfg.save(new_data)
        if ok:
            if self.on_save:
                self.on_save(new_data)
            messagebox.showinfo("Saved", "Settings saved and applied successfully!", parent=self.root)
            if self.own_root:
                self.on_close()
        else:
            messagebox.showerror("Error", "Could not save settings.", parent=self.root)

    def on_close(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def run(self):
        if self.own_root:
            self.root.mainloop()

if __name__ == "__main__":
    app = SettingsWindow(config_manager=ConfigManager(CONFIG_PATH))
    app.run()
