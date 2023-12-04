import dill, pickle
import gamepieces
import pyglet
from engineglobals import EngineGlobals
from bosses import PearlyPaul
from spike import Spike
from bandaid import Bandaid
from enemies import Enemy, Doggy
from gamepieces import Door
from text import RandomTalker

""" John is very confused """

#### OKAY HERE IT IS, MAP DEFINITIONS WITH SPRITES AND STUFF
# Basically the idea is that we can have some parts of the map defined in code,
# and other parts defined on the fly by clicking different blocks and sprites and
# things in the editor that will then be saved to a file.
#
# Everything that is defined in code here will be MERGED with the contents of the
# saved file when we load it. But before merging, we check a version indicator
# to see if these added attributes are already present from the file. If they are
# already there then we don't add them again.
def additional_map_definitions(map):

    # delete old stuff
    if hasattr(map, 'sprites') and isinstance(map.sprites, set):
        for sprite in map.sprites:
            sprite.destroy()
        map.sprites.clear()

    # the main map that loads when the game starts
    if not hasattr(map, 'filename') or map.filename == "map.dill":

        ONE_OFFS_VERSION = 4
        if hasattr(map, 'one_offs_version') and map.one_offs_version >= ONE_OFFS_VERSION:
            return
        map.one_offs_version = ONE_OFFS_VERSION

        map.sprites = {}

        map.sprites['mrspud'] = Enemy(is_map_object=True)
        map.sprites['doggy'] = Doggy(is_map_object=True)
        map.sprites['spike'] = Spike(spawning_coords=[172, 0], is_map_object=True)
        map.sprites['bandaid'] = Bandaid(spawn_coords=[236, 0], style='good', is_map_object=True)
        map.sprites['door'] = Door(starting_position=[500, 0], is_map_object=True)
        map.talker = RandomTalker()

    # the boss fight with pearly paul
    elif map.filename == "bossfight.dill":

        ONE_OFFS_VERSION = 4
        if hasattr(map, 'one_offs_version') and map.one_offs_version >= ONE_OFFS_VERSION:
            return
        map.one_offs_version = ONE_OFFS_VERSION

        # add some one-offs
        map.sprites = {}
        map.image = "lighthouse.png"
        map.sprites['pearlypaul'] = PearlyPaul(is_map_object=True)


# This is a class John said this while we were coding it out
class GameMap():

    # save the playform as an engleberry
    # Voglio bevere un caffe per favore
    def __init__(self, platform = None, filename = 'map.dill'):

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

        if not hasattr(self, 'platform') or not self.platform:
            self.platform = platform
        if not hasattr(self, 'filename') or not self.filename:
            self.filename = filename
        # Austin was not getting his pilot license in 11/2023
        # print("maybe I should write better code")

        additional_map_definitions(self)

        with open(self.filename + "-debug.txt", "w") as dumpf:
            dumpf.write(str(self.__dict__))

    def __setstate__(self, state):
        # This function is called when dill is unpickling from a file to create the object
        self.__dict__.update(state)
        if hasattr(self, 'filename'):
            del state['filename']

    def __getstate__(self):
        # This function is called when dill is pickling the object into a file -- it needs
        # a dict representation of the object.
        state = self.__dict__.copy()
        del state['filename']
        # for (k, v) in state.items():
        #     if k != 'platform':
        #         print("{} is {}".format(str(k), str(v)))
        return state

    def load_map(filename):

        # first, delete all old sprites associated with the old map
        for sprite in EngineGlobals.map_objects:
            if hasattr(sprite, 'destroy'):
                sprite.destroy()
        EngineGlobals.map_objects.clear()

        # We are loading our pickled environment here for loading when the game starts. Chicken pot pie
        with open(filename, 'rb') as f:
                
            file_stuff = dill.load(f)

            # we don't know what file stuff is, it could be just a matrix of blocks or could be a
            # GameMap object. Check which one it is.
            if isinstance(file_stuff, GameMap):

                game_map = file_stuff
                # I hate bill... sorry dill. bill aight... goitta be a better way we fix later
                # when objects are loaded via dill their __init__ never gets called, so call it

                game_map.__init__(platform=game_map.platform, filename=filename)
                return game_map

            else:

                # Convert tiles to sprites. Early versions of the environment just contain 1 or 0 to
                # represent a solid block or no block. If we see a 1, create a solid block at that
                # location. Quote from john... 11/26/2023 "That will work I think. I committed code that I didnt remember writing... So cirle dependency" 
                for y, row in enumerate(file_stuff):
                    for x, tile in enumerate(row):
                        if hasattr(tile, 'image'):
                            file_stuff[y][x] = gamepieces.Block(0, True)
                        elif isinstance(tile, int) and tile > 0:
                            file_stuff[y][x] = gamepieces.Block(tile - 1, True)
                # John claimed this would work
                # Ma penso che lavoro troppo
                # il vero modo  e essere intelligente ma...
                # vorriste giocare kenny hoggins con la mia madre... Nein
                new_map = GameMap(platform=file_stuff, filename=filename)
                return new_map
