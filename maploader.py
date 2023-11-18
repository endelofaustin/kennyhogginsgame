import dill, pickle
import gamepieces
import pyglet
from engineglobals import EngineGlobals

""" John is very confused """

# This is a class
class GameMap():

    # save the playform as an engleberry
    # Voglio bevere un caffe per favore
    def __init__(self, platform):

        # This can of worms has been opened. Goes bad July 2025
        # # self.image = "lighthouse.png"
        # create a sprite htat is not a member of the class and it wont try to pickle the sprite
        # which is great. When it goes to the load the class from the dill file  
        # it will __init__ the class and create the background as normal Pie Throw #legit
        # John doesnt like this it is incomprehensible, "i wonder what the elegant solution is" <--- John 11/16
        if hasattr(self, "image"):
            EngineGlobals.background_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image(self.image), 
                                     batch=EngineGlobals.main_batch, 
                                     group=EngineGlobals.bg_group)
            
         
        self.platform = platform
        # Austin was not getting his pilot license in 11/2023
        # print("maybe I should write better code")
       
    def __setstate__(self, state):
            
        self.__dict__.update(state)
        self.__init__(self.platform)
    
    def __getstate__(self):
        
        state = self.__dict__.copy()
        return state

    def load_map(file_name):
    
        # We are loading our pickled environment here for loading when the game starts. Chicken pot pie
        with open(file_name, 'rb') as f:
                
            platform = dill.load(f)
            # Convert tiles to sprites. Early versions of the environment just contain 1 or 0 to
            # represent a solid block or no block. If we see a 1, create a solid block at that
            # location.
            if isinstance(platform, GameMap):
                return platform

            # this will detect whether or not a GameMap object or a matrix of blocks was loaded.   
            else:
                    
                for y, row in enumerate(platform):
                    for x, tile in enumerate(row):
                        if hasattr(tile, 'image'):
                            platform[y][x] = gamepieces.Block(0, True)
                        elif isinstance(tile, int) and tile > 0:
                            platform[y][x] = gamepieces.Block(tile - 1, True)
                # John claimed this would work
                # Ma penso che lavoro
                new_map = GameMap(platform)
                return new_map
