# kennyhogginsgame

Kenny is a pig. He likes being a pig. And a hog. Let’s go for a jog.

Kenny Hoggins Game is a Python/pyglet platform game with an in-game map editor, enemies, projectiles, boss maps, pickups, save-game progress, and several experimental gameplay modes.

## How to run Kenny Hoggins Game

### Requirements

- **Python 3.10 or newer**
- Git
- A desktop environment capable of opening an OpenGL window

> Important on macOS: do not build the virtual environment with Python 3.9. `pyglet==2.1.6` currently contains macOS code that uses Python 3.10+ union-type syntax (`X | None`). A Python 3.9 virtual environment can successfully install pyglet and then crash immediately when pyglet imports.

The Python dependencies are pinned in `requirements.txt`:

- `pyglet==2.1.6`
- `dill==0.3.6`

### 1. Clone the repository

```bash
git clone https://github.com/endelofaustin/kennyhogginsgame.git
cd kennyhogginsgame
```

### 2. Set up Python

#### macOS — recommended

The repository includes a setup helper that deliberately avoids Python 3.9:

```bash
chmod +x setup_mac.sh runit
./setup_mac.sh
./runit
```

`setup_mac.sh` looks for Python 3.13, 3.12, 3.11, or 3.10, removes an incompatible existing `.venv`, creates a fresh one, upgrades pip, and installs the dependencies.

If the script says that no compatible Python is installed and you use Homebrew:

```bash
brew install python@3.12
./setup_mac.sh
./runit
```

You can also do the setup manually:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Before creating the venv, verify the interpreter:

```bash
python3.12 --version
```

It must report Python 3.10 or newer.

#### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

#### Windows Command Prompt

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

#### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

### Fixing an existing macOS Python 3.9 virtual environment

If your traceback contains a path like:

```text
.venv/lib/python3.9/site-packages/pyglet/...
```

then the `.venv` itself was created with Python 3.9. Activating it or upgrading pip will not change its Python version. Rebuild it:

```bash
deactivate 2>/dev/null || true
rm -rf .venv
brew install python@3.12   # only if python3.12 is not already installed
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Or simply use:

```bash
./setup_mac.sh
./runit
```

### Troubleshooting

Run the game from the repository root. The game loads maps, artwork, and audio using paths relative to the project, so launching `main.py` from another working directory can cause missing-resource errors.

Check which Python your environment is actually using:

```bash
python --version
which python
```

On macOS, the path should point into this repository's `.venv/bin/python`, and the version must be 3.10+.

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
