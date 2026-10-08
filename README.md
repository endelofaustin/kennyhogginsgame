# kennyhogginsgame

Kenny is a pig. He likes being a pig. And a hog. Let’s go for a jog.

Kenny Hoggins Game is a Python/pyglet platform game with an in-game map editor, enemies, rear-fired projectiles, boss maps, pickups, save-game progress, a level-select screen, and five themed dill-map levels.

## How to run Kenny Hoggins Game

### Requirements

- Python 3.10 or newer
- Git
- A desktop environment capable of opening an OpenGL window

The Python dependencies are pinned in `requirements.txt`:

- `pyglet==2.1.6`
- `dill==0.3.6`

### macOS — project-local setup

The easiest setup keeps Python 3.11, uv, and the virtual environment entirely inside this repository. It does **not** replace your system/default Python.

```bash
cd /path/to/kennyhogginsgame
chmod +x setup_mac.sh runit
./setup_mac.sh
./runit
```

`setup_mac.sh` creates:

```text
kennyhogginsgame/
├── .uv-bin/    # project-local uv executable
├── .python/    # project-local Python 3.11
└── .venv/      # project virtual environment with pip + dependencies
```

All three directories are ignored by Git.

To activate the environment manually:

```bash
source .venv/bin/activate
python --version
python main.py
```

The version should report Python 3.11.x.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

### Linux

Use any installed Python 3.10+:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

## Starting a game

Choose **Start** on the main menu. The game then opens the level-select screen:

- **Escape from the Farm** — `farm.dill`, Lucinda boss
- **Van Down by the River** — `river.dill`, van scene and Pippi boss
- **Karate Dojo** — `dojo.dill`, Jackie Flan boss
- **Writing Rainbomb** — `space.dill`, Levod Burtim boss and autoscroller
- **Escape Vesuvius** — `pompeii.dill`, Pompeii lava/autoscroller level

All authored game maps remain `.dill` files and load through the existing `GameMap.load_map(...)` flow. No JSON map loader is used.

Each themed level has custom artwork, story text, enemies, hazards, and its own boss/content setup through `additional_map_definitions()`.

## Controls

- **Left / Right arrows** — move
- **Down arrow** — crouch
- **Ctrl or Up arrow** — jump / double jump
- **Space** — fire Kenny’s projectile from his **butt**, opposite the direction he is facing
- **C** — sword/scythe attack
- **D** — interact with doors and locked gates
- **P** — open/close the jigsaw puzzle
- **A** — toggle the autoscroller challenge manually
- **F5** — quick save
- **F9** — quick load

Kenny now uses four-frame custom jump animation sheets in both directions.

### Map editor

- **1** — normal block
- **2** — hazard block
- **3** — breakable block
- **4** — enemy
- **5** — door
- **6** — key pickup
- **7** — locked gate
- **8** — spike
- **Ctrl+S** — save the current dill map
- **Ctrl+L** — reload `map.dill`
- **Ctrl+N** — clear the current map/chunks

For block tools, left click places a solid foreground block and right click places a non-solid background block. Clicking an existing matching block removes it.

## Gameplay additions

- Collectible keys and locked gates
- Sword pickup tutorial
- Optional/autostarting autoscroller levels
- Keyboard-driven jigsaw puzzle
- Separate opening text-crawl mode
- Enemy patrol/chase movement
- JSON player-progress save file while maps remain dill
- Intentionally ridiculous projectile-hit blood explosion with roughly 50 animated particles/blobs
- Faster enemy projectile deaths
- Custom character art for Lucinda, Jackie Flan, Levod Burtim, Pippi, the river van, and Vesuvius
- Custom themed backdrop art for farm, river, dojo, space, and Pompeii

## Game engine design

### Main graphics and update loops

The simulation runs at 60 updates per second. Pyglet calls `main_update_callback` in `main.py`, which clears the collision grid, asks lifecycle managers to update game objects, and updates visible map chunks relative to the camera.

### Sprites and the Player object

`PhysicsSprite` provides collision and movement behavior. `Player` builds on it with movement, shooting, sword/scythe attacks, pickups, doors, keys, quick save/load, and damage handling.

### Maps

The game remains dill-based. Existing `.dill` map serialization and `GameMap.load_map(...)` are retained. The five themed maps are separate `.dill` files and are customized through the existing map-definition hook.

### Gameplay systems

`gameplay.py` contains shared systems including player progress, keys/locked gates, the jigsaw puzzle, autoscrolling, and the exaggerated blood effect.

## Troubleshooting

Run the game from the repository root because artwork, audio, and dill maps are loaded relative to the project.

On macOS, verify the project-local interpreter:

```bash
.venv/bin/python --version
```

It should be Python 3.10+ (the setup script installs 3.11).

If a previous `.venv` used Python 3.9, run `./setup_mac.sh`; it replaces only this repository’s `.venv` and does not modify your system Python.

## Tools/libraries/components used

- Pyglet — game engine — https://pyglet.org/
- Dill — map serialization
- Piskel — sprite designer — https://www.piskelapp.com/p/create/sprite
- BobSprite — sprite designer — https://bobsprite.com/editor
- Aseprite — sprite designer — https://www.aseprite.org/
