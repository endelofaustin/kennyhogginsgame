# kennyhogginsgame

Kenny is a pig. He likes being a pig. And a hog. Let’s go for a jog.

Kenny Hoggins Game is a Python/pyglet platform game with an in-game map editor, enemies, projectiles, boss maps, pickups, save-game progress, and several experimental gameplay modes.

## How to run Kenny Hoggins Game

### Requirements

- Python 3.10 or newer
- Git
- A desktop environment capable of opening an OpenGL window

The Python dependencies are pinned in `requirements.txt`:

- `pyglet==2.1.6`
- `dill==0.3.6`

### 1. Clone the repository

```bash
git clone https://github.com/endelofaustin/kennyhogginsgame.git
cd kennyhogginsgame
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Start the game

With the virtual environment activated:

```bash
python main.py
```

On macOS/Linux you can also run:

```bash
./runit
```

On Git Bash/WSL for Windows, `./runit` will also detect the Windows virtual-environment layout.

### Troubleshooting

Run the game from the repository root. The game loads maps, artwork, and audio using paths relative to the project, so launching `main.py` from another working directory can cause missing-resource errors.

If `python` is not available on Windows, use:

```powershell
py main.py
```

If the window cannot be created, verify that your graphics/OpenGL drivers are available and current.

## Controls

- **Left / Right arrows** — move
- **Down arrow** — crouch
- **Ctrl or Up arrow** — jump / double jump
- **Space** — shoot
- **C** — sword/scythe attack
- **D** — interact with doors and locked gates
- **P** — open/close the jigsaw puzzle
- **A** — toggle the autoscroller challenge
- **F5** — quick save
- **F9** — quick load

### Map editor

- **1** — normal block
- **2** — hazard block
- **3** — breakable block
- **4** — enemy
- **5** — door
- **6** — key pickup
- **7** — locked gate
- **8** — spike
- **Ctrl+S** — save the current map
- **Ctrl+L** — reload `map.dill`
- **Ctrl+N** — clear the current map/chunks

For block tools, left click places a solid foreground block and right click places a non-solid background block. Clicking an existing matching block removes it.

## Game engine design

### Main graphics and update loops

The main simulation loop runs at 60 updates per second. Pyglet calls `main_update_callback` in `main.py`, which clears the collision grid, asks the lifecycle managers to update game objects, and updates visible map chunks relative to the camera.

### Sprites and the Player object

`PhysicsSprite` provides collision and movement behavior. `Player` builds on it with movement states, shooting, sword/scythe attacks, pickups, doors, keys, quick save/load, and damage handling.

### Maps and editor

Maps still load existing `.dill` data for backward compatibility. The editor can place tile/block variants and several sprite types. Player progress is stored separately in human-readable `savegame.json`.

### Gameplay systems

`gameplay.py` contains shared systems including player progress, keys/locked gates, the jigsaw puzzle, autoscrolling, themes/story data, and the intentionally ridiculous projectile blood explosion.

## Tools/libraries/components used

- Pyglet — game engine — https://pyglet.org/
- Dill — map serialization compatibility
- Piskel — sprite designer — https://www.piskelapp.com/p/create/sprite
- BobSprite — sprite designer with adjustable alpha transparency — https://bobsprite.com/editor
- Aseprite — sprite designer — https://www.aseprite.org/
