TODO LIST:
* Maps
   * ~~Be able to use different 32-pixel-square tiles in the maps~~
   * ~~When we save the map we get a ValueError because pickle cannot pickle pointers~~
   * ~~We now have the ability to build out different types of Blocks upon which to jump!~~
   * ~~But do we really. We need some sort of selector mechanism for the editor so we can select which block~~
       ~~to place when we click in the map.~~
   * ~~Build out dem blocks — normal, hazard, and breakable block tools~~
   * ~~Be able to clear the map and start from a blank slate (Ctrl+N)~~
* ~~Projectiles~~
   * ~~Create a projectile class that subclasses a Pyglet Sprite, but with different mechanics than the PhysicsSprite~~
   * ~~We now can shoot! (in two directions) with a spitting noise~~
   * ~~When the bullet hits the enemy then the enemy gets bloody and eventually dies.~~
   * ~~Make it so when the bullet hits the enemy there is a blood spurt and the enemy dies more quickly — now an intentionally ridiculous exploding particle spray~~
   * ~~Keep the projectile coming out of Kenny's butt, not the front~~
* ~~Kenny should be able to face left as well~~
* Gameplay mechanics
   * ~~Collect keys to unlock blocks/gates leading to boss content~~
   * ~~Tutorials for when you collect the sword on how to use it~~
   * ~~Autoscroller where the screen moves on its own and you have to keep up with it and avoid obstacles and shoot things~~
   * ~~Solve a jigsaw puzzle~~
* Themes
   * ~~Escape from the farm (Lucinda) — `farm.dill`, custom farm art, Lucinda boss~~
   * ~~Van down by the river — `river.dill`, custom river art, van prop, Pippi boss~~
   * ~~Karate dojo where you fight Jackie Flan — `dojo.dill`, custom dojo art and Jackie Flan boss~~
   * ~~Outer space dogfight / exploding spaceship / Levod Burtim and Writing Rainbomb — `space.dill`, custom space art and autoscroller~~
   * ~~Escaping Vesuvius lava through Pompeii — `pompeii.dill`, custom Pompeii/Vesuvius art and autoscroller~~
* Enemies & sprite movement
   * ~~Replace weird random enemy movement with patrol/chase behavior~~
* Crawling text intro
   * ~~Separate the vertically moving text into a beginning Intro game mode~~
* Placement of sprites & solid objects in the environment
   * ~~Sprite selector for the editor — keys 1–8 select block/sprite tools~~
* ~~Saving/serializing the map to and from a file - dill~~
   * ~~We may want to keep track of different versions of the map class over time~~
* ~~Characters / sprites — new custom Lucinda, Jackie Flan, Levod Burtim, Pippi, van, and Vesuvius art plus editor-placeable sprites~~
* ~~Storyline — each selectable themed dill map now has its own story text shown in the intro crawl~~
* Menus & configuration
   * ~~New Game / Start, Load Game, working Settings toggle~~
   * ~~Level-select screen after Start with all five themed dill maps~~
* Serialization / save games
   * ~~Player game progress now saves separately to `savegame.json` (F5/F9) while maps remain dill~~
* ~~Running animations~~
* Sprite animations
   * ~~Jumping now uses custom four-frame left/right animation sheets with positioning anchors~~
   * ~~Other actions Kenny can perform — crouch, shoot, slash, interact, puzzle, quick-save/load~~
   * ~~Other sprites — editor placement and lifecycle support expanded~~
* ~~Make a door that leads to a new part of the map~~
   * ~~We already have code to load the "platform" from a file -> extend this so that sprites/bosses/etc are loaded at the same time~~
   * ~~Make a new MapLoader class that we will use to swap to the new map when going through a door~~
* ~~Make a start menu with New game, Load game~~

VILLAIN ROSTER:
* ~~Pippi Longstocking, vegan animal hater — implemented as themed boss~~
* ~~Levod Burtim, rainbow farting space engineer — implemented as themed boss~~

OTHER PEEPS:
* ~~Ronald McSwanson, life coach and dispenser of wisdom — existing NPC retained~~

COOL IDEAS:
* What if part of the game was having to fix a bad level design so that you could complete it
* One huge map but parts of it change when you're not looking
* Random text in the background like a poem or Kenny's thoughts
* Generate an infinite map from randomized saved chunks

TO REFACTOR:
 * ~~main.py cleanup — startup and update/render wiring simplified~~
 * map loader -> convert to JSON? or something — intentionally NOT done; project remains dill-based per repository direction
 * ~~move gameplay/save/puzzle/autoscroller concerns out of EngineGlobals into dedicated classes~~
 * use decorators or pub/sub or better model for event handling instead of random callback functions — intentionally NOT done; no architecture rewrite
 * state machines for player and other sprites — intentionally NOT done; no architecture rewrite
