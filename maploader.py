import dill, pickle
import gamepieces

def load_map(file_name):

    # We are loading our pickled environment here for loading when the game starts. Chicken pot pie
    with open(file_name, 'rb') as f:
            
        platform = dill.load(f)
        # Convert tiles to sprites. Early versions of the environment just contain 1 or 0 to
        # represent a solid block or no block. If we see a 1, create a solid block at that
        # location.
        for y, row in enumerate(platform):
            for x, tile in enumerate(row):
                if hasattr(tile, 'image'):
                    platform[y][x] = gamepieces.Block(0, True)
                elif isinstance(tile, int) and tile > 0:
                    platform[y][x] = gamepieces.Block(tile - 1, True)
    
    return platform
