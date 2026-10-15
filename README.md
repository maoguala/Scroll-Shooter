# Scroll Shooter

A top-down Python Pygame shooter where you control a fly-like ship, dodge enemies, fire bullets, and survive as long as you can.

## Install Steps

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install Pygame:

   ```bash
   pip install pygame
   ```

3. Run the game:

   ```bash
   python game.py
   ```

## Build an executable

If you want to package the game as a Windows `.exe` or a Linux `.out`, use PyInstaller.

1. Install PyInstaller:

   ```bash
   pip install pyinstaller
   ```

2. Build for Windows:

   ```bash
   pyinstaller --onefile --windowed game.py
   ```

3. Build for Linux:

   ```bash
   pyinstaller --onefile --windowed --name game.out game.py
   ```

The generated file will be placed in the `dist/` folder. You can also build from the existing spec file with:

```bash
pyinstaller game.spec
```

## Controls

- Move: Arrow keys or WASD
- Shoot: `Space`
- Shotgun blast: `E`
- Restart after game over: `R`
