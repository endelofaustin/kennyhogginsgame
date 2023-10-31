TODO LIST:
* Maps
   * ~~Be able to use different 32-pixel-square tiles in the maps~~
   * ~~When we save the map we get a ValueError because pickle cannot pickle pointers~~
   * We now have the ability to build out different types of Blocks upon which to jump!
   * But do we really. We need some sort of selector mechanism for the editor so we can select which block
       to place when we click in the map.
   * Build out dem blocks
* ~~Projectiles~~
   * ~~Create a projectile class that subclasses a Pyglet Sprite, but with different mechanics than the PhysicsSprite~~
   * ~~We now can shoot! (in two directions) with a spitting noise~~
   * ~~When the bullet hits the enemy then the enemy gets bloody and eventually dies.~~
   * Make it so when the bullet hits the enemy there is a blood spurt and the enemy dies more quickly
* ~~Kenny should be able to face left as well~~
* Enemies & sprite movement
   * The enemy movement is pretty weird, we should make it move back and forth and/or chase the player
* Crawling text intro
   * We now have vertically moving text ... separate it out into a separate game mode that plays at the beginning
* Placement of sprites & solid objects in the environment
   * We need a sprite selector for the editor
* ~~Saving/serializing the map to and from a file - pickle?~~
   * ~~We may want to keep track of different versions of the map class over time~~
* Characters / sprites
* Storyline
* Menus & configuration
* Serialization / save games
   * We can save the map but can't save player game progress yet
* ~~Running animations~~
* Sprite animations
   * Jumping should be tweaked a bit, needs more frames of animation and positioning moved a bit
   * Other actions Kenny can perform
   * Other sprites
* Make a door that leads to a new part of the map
   * We already have code to load the "platform" from a file -> extend this so that sprites/bosses/etc are loaded at the same time
   * Make a new MapLoader class that we will use to swap to the new map when going through a door
* Make a start menu with New game, Load game

VILLAIN ROSTER:
* Pippi Longstocking, vegan animal hater
* Levod Burtim, rainbow farting space engineer

OTHER PEEPS:
* Ronald McSwanson, life coach and dispenser of wisdom

COOL IDEAS:
* What if part of the game was having to fix a bad level design so that you could complete it
* One huge map but parts of it change when you're not looking
* Random text in the background like a poem or Kenny's thoughts
