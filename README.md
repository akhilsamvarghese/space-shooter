# 🚀 Space Shooter

A fast-paced, retro-style arcade game built with **Pygame**.  
Pilot your yellow fighter, blast incoming enemy fleets, and survive as long as you can.  
Works out-of-the-box—no external assets required—but ready to accept your own pixel-art for ships, lasers, and backgrounds.

---

## ✨ Features
- **Zero-setup fallback graphics & sounds** – the game runs even if you provide no assets  
- **3 enemy types** (red / green / blue) with unique laser colors  
- **Procedural starfield** background  
- **Explosion animations** & laser trails  
- **Thrust flame** on the player ship  
- **Health bar & lives counter**  
- **Progressive difficulty** – enemy waves grow larger every level  
- **Pew-pew sound** (plays if you drop a file into `assets/`)

---

## 🎮 Controls
| Key | Action |
|-----|--------|
| W A S D | Move |
| Space | Shoot |
| Mouse click | Start game from menu |

---

## 🛠️ Requirements
- Python 3.7+
- pygame 2.x  
Install in one line:
```bash
pip install pygame
```

---

## 🚀 Quick Start
1. Clone or download the repo  
2. Run either file (they are identical):
   ```bash
   python main.py
   # or
   python laser.py
   ```
3. Click the window → play!

---

## 🎨 Customising Assets
Drop your own files into the auto-created `assets/` folder.  
Accepted file names (PNG or SVG for background):

```
assets/
├── pixel_ship_red_small.png
├── pixel_ship_green_small.png
├── pixel_ship_blue_small.png
├── pixel_ship_yellow.png
├── pixel_laser_red.png
├── pixel_laser_green.png
├── pixel_laser_blue.png
├── pixel_laser_yellow.png
├── Space_Stars2.svg            (750×750 recommended)
└── Pew! Sound Effect [Pew Pew Pew]-[AudioTrimmer.com]-2.mp3
```

Missing files? No problem—colorful placeholder sprites and a generated starfield are used automatically.

---

## 🧱 Code Overview
| File | Purpose |
|------|---------|
| `main.py` / `laser.py` | Full game (identical copies, pick either) |
| `assets/` | Optional sprites, lasers, background, sound |
| Classes | `Player`, `Enemy`, `Laser`, `Explosion`, `StarField` |
| Helpers | `load_image()` with fallback, `collide()` pixel-perfect mask collision |

---

## 🎯 Tips
- Hold Space for rapid fire (30-frame cooldown).  
- Enemies deal **20 damage** on crash, **10** per laser hit.  
- Every cleared wave spawns **+5 enemies**.  
- Explosions are cosmetic—use them to judge hits!

---


---

**Have fun, pilot!**
