# kennyhogginsgame
Kenny is a pig. He likes being a pig. And a hog. Let’s go for a jog.


Pig will jump on platform. There will be input and a game loop and sprites

## Game engine design

 * The main graphics and update loops
    * ### Update loop stuff
    * The update loop happens 120 times per second
    * Pyglet calls `main_update_callback` in main.py 120 times per second
    * The main_update_callback looks at a list of all objects in the game that
      need updating, and updates them. Then if any of them have been marked for
      deletion, it deletes them.
 * Sprites and the Player object
 * Physics, actions and events
 * The EngineGlobals static object
 * Blocks and map components
 * Editing and pickling of maps
