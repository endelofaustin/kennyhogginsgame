import dill, pickle
import gamepieces
import pyglet
from engineglobals import EngineGlobals
from bosses import PearlyPaul
from spike import Spike
from bandaid import Bandaid
from enemies import Enemy, Doggy
from gamepieces import Door, NirvanaFruit
from text import RandomTalker
from lifecycle import LifeCycleManager
from sprite import makeSprite

""" John is very cool """

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

    # the main map that loads when the game starts
    if not hasattr(map, 'filename') or map.filename == "map.dill":

        ONE_OFFS_VERSION = 8
        if hasattr(map, 'one_offs_version') and map.one_offs_version >= ONE_OFFS_VERSION:
            return
        map.one_offs_version = ONE_OFFS_VERSION

        map.sprites = dict()
        map.sprites['door'] = makeSprite(Door, starting_position=(0,15), group='BACK', target_map="bossfight.dill", player_position=(250 ,250))
        map.sprites['sword-1'] = makeSprite(gamepieces.Sword, (2500, 90))
        map.sprites['scythe'] = makeSprite(gamepieces.Scythe, (200, 41))

    # the boss fight with pearly paul
    elif map.filename == "bossfight.dill":

        ONE_OFFS_VERSION = 6
        if hasattr(map, 'one_offs_version') and map.one_offs_version >= ONE_OFFS_VERSION:
            return
        map.one_offs_version = ONE_OFFS_VERSION

        # add some one-offs
        map.image = "lighthouse.png"
        map.sprites = dict()
        map.sprites['pearlypaul'] = makeSprite(PearlyPaul, (0, 0))


# This is a class John said this while we were coding it out
class GameMap():

    # save the playform as an engleberry
    # Voglio bere un caffe e daverro abbiamo scrivere piu codice. 
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
        return state

    def load_map(filename):

        # first, drop all sprites associated with the map that is unloading
        LifeCycleManager.dropAllObjects('PER_MAP')

        # We are loading our pickled environment here for loading when the game starts. Chicken pot pie
        with open(filename, 'rb') as f:

            game_map = dill.load(f)
            game_map.__init__(platform=game_map.platform, filename=filename)
            return game_map
