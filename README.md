# HandWave 🖐️

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg?style=for-the-badge)](https://github.com/diaba1445-glitch/Hand-Wave/releases/latest)
[![Release](https://img.shields.io/github/v/release/diaba1445-glitch/Hand-Wave?style=for-the-badge&color=2ea44f)](https://github.com/diaba1445-glitch/Hand-Wave/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blueviolet.svg?style=for-the-badge&logo=windows)](https://github.com/diaba1445-glitch/Hand-Wave/releases/latest)

Control your PC with webcam-powered hand gestures in real-time. Built with Python, OpenCV, and Google MediaPipe.

---

## 📥 Download (Standalone Windows App — No Python Required)

The fastest and easiest way to use HandWave is to download the standalone portable release:

1. Go to the [**GitHub Releases page**](https://github.com/diaba1445-glitch/Hand-Wave/releases/latest) or download [**HandWave-v1.0.0-windows-x64.zip**](https://github.com/diaba1445-glitch/Hand-Wave/releases/download/v1.0.0/HandWave-v1.0.0-windows-x64.zip).
2. Extract the downloaded `.zip` file anywhere on your computer.
3. Double-click **`HandWave.exe`** (or **`Start_HandWave.bat`**) to launch!

> [!TIP]
> No Python installation, compiler, or command line tools are required for the standalone release. Everything is bundled and ready out of the box.

---

## ⚡ Features

- **Real-Time Hand Tracking:** High-speed landmark detection with Google MediaPipe.
- **Two-Hand Safety Clutch:** Require a guard sign from your secondary hand (Open Palm, Peace Sign, or Fist) before action gestures can fire, preventing accidental inputs while typing, drinking coffee, or talking.
- **Double-Gesture Confirmation:** Optional double-tap gesture confirmation to eliminate false triggers with a single hand.
- **Split Hands Mode:** Independent gesture profiles and actions for Left and Right hands (e.g. Right hand for navigation/mouse, Left hand for media/multitasking).
- **Customizable Actions:** Configure keyboard shortcuts, media keys, volume control, window snapping, virtual desktop switching, and mouse clicks.
- **Settings GUI:** Built-in settings window for interactive mapping, sensitivity adjustment, and profile management.
- **100% Offline & Private:** All processing runs locally on your computer. No data or video is ever transmitted.

---

## 🚀 Developers: Run from Source

If you prefer to run from source code or modify HandWave:

### Prerequisites

- **OS:** Windows 10 or 11 (64-bit)
- **Webcam:** Any standard internal or USB webcam
- **Python:** Python 3.10+ installed and added to your system `PATH`

### 1. Clone Repository

```bash
git clone https://github.com/diaba1445-glitch/Hand-Wave.git
cd Hand-Wave
```

### 2. Install Dependencies

Double-click `Install_Dependencies.bat` or run:

```bash
pip install -r requirements.txt
```

### 3. Start HandWave

Double-click `Start_HandWave.bat` or run:

```bash
python HandWave.py
```

---

## ⚙️ In-App Hotkeys

| Key | Action |
|:---:|:---|
| **C** | Toggle Two-Hand Safety Clutch ON / OFF |
| **D** | Toggle Double-Gesture Confirmation ON / OFF |
| **H** | Toggle Split Hands Mode ON / OFF |
| **S** | Open the Settings Window |
| **P** | Pause / Resume gesture tracking |
| **1 – 8** | Quick toggle specific gestures on/off |
| **Q / Esc** | Quit application |

---

## 🛠️ Settings & Configuration

To open the settings panel at any time:
- Press **S** while the camera feed is active, OR
- Double-click `Open_Settings.bat` or run `python settings_gui.py`.

In Settings, you can configure:
- Hand profile mappings (Unified or Split Hands mode)
- Action assignments per gesture
- Gesture hold duration & trigger cooldowns
- Two-Hand Safety Clutch settings & Guard signs
- Double-Tap confirmation window timing

Configuration is saved in `config.json` and hot-reloads dynamically.

---

## 📦 Project Structure

```text
HandWave/
├── .github/workflows/
│   └── release.yml          # Automated GitHub Actions Windows build & release
├── HandWave.py              # Main application entry point & camera HUD loop
├── settings_gui.py          # Tkinter settings GUI for gesture mapping
├── config_manager.py        # Configuration loading, validation, and auto-reload
├── gestures.py              # Geometric gesture classifiers & motion detector
├── trigger.py               # Gesture triggering logic, clutch & debounce timing
├── actions.py               # Windows ctypes keyboard and system action dispatcher
├── config.json              # Default user settings and gesture mapping config
├── hand_landmarker.task     # MediaPipe hand tracking model
├── requirements.txt         # Python package dependencies
├── Install_Dependencies.bat # 1-click batch installer for dependencies
├── Start_HandWave.bat       # 1-click launcher for HandWave (auto-detects exe or python)
├── Open_Settings.bat        # 1-click launcher for Settings GUI
├── HOW_TO_USE.txt           # Detailed user guide and troubleshooting tips
├── LICENSE                  # MIT License
├── THIRD_PARTY_LICENSES.md  # Attributions for Google MediaPipe, OpenCV, NumPy
└── README.md                # Project documentation
```

---

## 🔒 Privacy & Security

All camera frames and computer vision landmarks are processed entirely in memory on your local machine. Nothing is recorded, saved, or uploaded to any server.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details. Free for personal and commercial use.

Third-party open-source components and models are documented in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
