import dill, pickle
import gamepieces
import pyglet
from engineglobals import EngineGlobals
from bosses import PearlyPaul
from spike import Spike
from bandaid import Bandaid
from enemies import Enemy, Doggy, Cardi
from gamepieces import Door, NirvanaFruit
from lifecycle import LifeCycleManager
from sprite import makeSprite
from magic_map import Chunk
from mcswanson import McSwanson

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

    if hasattr(map, 'sprites'):
        for sprite in map.sprites.values():
            sprite.destroy()
        del map.sprites

    # the main map that loads when the game starts
    if not hasattr(map, 'filename') or map.filename == "map.dill":

        # ONE_OFFS_VERSION = 16
        # if hasattr(map, 'one_offs_version') and map.one_offs_version >= ONE_OFFS_VERSION:
        #     return
        # map.one_offs_version = ONE_OFFS_VERSION

        if hasattr(map.chunks[0], 'contained_sprites'):
            for sprite in map.chunks[0].contained_sprites.values():
                sprite.destroy()
        if hasattr(map, 'talker'):
            map.talker.destroy()
            del map.talker

        map.chunks[0].contained_sprites = dict()
        map.chunks[0].contained_sprites['door'] = makeSprite(Door, map.chunks[0], starting_position=(500,10), group='BACK', target_map="bossfight.dill", player_position=(250 ,250))
        #map.chunks[0].contained_sprites['sword-1'] = makeSprite(gamepieces.Sword, map.chunks[0], starting_position=(1000, 90))
        map.chunks[0].contained_sprites['scythe'] = makeSprite(gamepieces.Scythe, map.chunks[0], starting_position=(300, 41))
        map.chunks[0].contained_sprites['spudguy'] = makeSprite(Enemy, map.chunks[0], starting_position=(300 , 250))
        map.chunks[0].contained_sprites['testfruit1'] = makeSprite(NirvanaFruit, map.chunks[0], starting_position=(260, 50))
        #map.chunks[0].contained_sprites['cardi1'] = makeSprite(Cardi, map.chunks[0], starting_position=(500, 0))
        map.chunks[0].contained_sprites['mcswanson1'] = makeSprite(McSwanson, map.chunks[0], starting_position=(340, 200))

    # the boss fight with pearly paul
    elif map.filename == "bossfight.dill":

        # ONE_OFFS_VERSION = 8
        # if hasattr(map, 'one_offs_version') and map.one_offs_version >= ONE_OFFS_VERSION:
        #     return
        # map.one_offs_version = ONE_OFFS_VERSION

        # add some one-offs
        map.image = "lighthouse.png"
        if hasattr(map.chunks[0], 'contained_sprites'):
            for sprite in map.chunks[0].contained_sprites.values():
                sprite.destroy()
        map.chunks[0].contained_sprites = dict()
        map.chunks[0].contained_sprites['pearlypaul'] = makeSprite(PearlyPaul, map.chunks[0], (0, 0))


# This is a class John said this while we were coding it out
class GameMap():

    # save the playform as an engleberry
    # Voglio bere un caffe e daverro abbiamo scrivere piu codice. 
    def __init__(self, chunks = None, filename = 'map.dill'):

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

        if not hasattr(self, 'chunks') or not self.chunks:
            self.chunks = chunks
        if not hasattr(self, 'filename') or not self.filename:
            self.filename = filename
        # Austin was not getting his pilot license in 11/2023
        # print("maybe I should write better code")

        additional_map_definitions(self)

        with open(self.filename + "-debug.txt", "w") as dumpf:
            dumpf.write(str(self.__dict__))
            dumpf.write("\n")
            for idx, chunk in enumerate(self.chunks):
                chunk_to_dump = chunk.__dict__.copy()
                del chunk_to_dump['platform']
                dumpf.write("chunk{}:".format(idx) + str(chunk_to_dump))
                dumpf.write("\n")

    def __setstate__(self, state):
        # This function is called when dill is unpickling from a file to create the object
        if hasattr(state, 'filename'):
            del state['filename']
        self.__dict__.update(state)

    def __getstate__(self):
        # This function is called when dill is pickling the object into a file -- it needs
        # a dict representation of the object.
        state = self.__dict__.copy()
        del state['filename']
        return state

    def load_map(filename):

        # first, drop all sprites associated with the map that is unloading
        LifeCycleManager.dropAllObjects('PER_MAP')
        if hasattr(EngineGlobals, 'game_map'):
            for old_chunk in EngineGlobals.game_map.chunks:
                for y_row in old_chunk.platform:
                    for x_block in y_row:
                        if isinstance(x_block, gamepieces.Block):
                            x_block.sprite.delete()

        # We are loading our pickled environment here for loading when the game starts. Chicken pot pie
        with open(filename, 'rb') as f:

            game_map = dill.load(f)

            if hasattr(game_map, 'platform'):
                game_map.chunks = [Chunk(platform=game_map.platform)]
                del game_map.platform

            for chunk in game_map.chunks:
                for sprite in chunk.contained_sprites.values():
                    sprite.current_chunk = chunk

            game_map.__init__(chunks=game_map.chunks, filename=filename)
            EngineGlobals.game_map = game_map
            if hasattr(EngineGlobals, 'kenny'):
                EngineGlobals.kenny.current_chunk = game_map.chunks[0]
