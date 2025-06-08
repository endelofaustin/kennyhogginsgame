
# A magic map loads different chunks in and out according to game logic. The chunks in a map don't occupy known
# coordinates in game space until they are loaded; a magic map is a sort of serialized graph among rectangular chunks
# that can coalesce to 2d space according to the rules of chunk loading.
#
# - Each of a chunk's 4 edges can become adjacent to one other chunk, and the adjacency can change at any time when
#   triggered by game logic, causing new chunks to be loaded/coalesced and old chunks to become hidden.
#
# - During an adjacency change, all the parameters determining which chunks are adjacent to each other are re-checked.
#
# - Chunks do not all need to be the same size, but horizontally-adjacent chunks need to have the same height and
#   vertically-adjacent chunks need the same width. <May revisit this and allow more granular adjacency - think of an
#   adjacency where multiple narrow chunks have pinned coordinates where they are adjacent to a wider chunk.>
#
# - A chunk may be as big or as small as desired. Many chunks may be visible on screen at a given time, or only one. <Or
#   none, though that obviates the need for a magic map.>
#
# - All visible chunks, and potentially many hidden chunks, must have been loaded and coalesced into 2d game space.
#   Hidden chunks may occupy the same space as a visible chunk. Chunks are coalesced at the time of chunk adjacency
#   changes, meaning they are given definite coordinates and their contents interact with the rest of the game; but
#   they can still be lazy loaded at an indeterminate time after coalescing (i.e. when the first sprite update or
#   player interaction with the chunk happens)
#
# - Sprites are pinned to whatever chunk they were most recently coalesced in, and continue interacting even if the
#   chunk is not visible. Sprites may move from chunk to chunk if the chunks are adjacent at the time of a sprite
#   movement update.
#
# - An adjacency change may cause a coalesced chunk to warp to different 2d game space than before the change. All
#   sprites that are pinned to that chunk at the time warp with it. Adjacency changes may have a cascading effect as all
#   coalesced chunks that are adjacent to a warping chunk must also warp.
#
# - Sprite interactions are allowed between sprites in different chunks if desired, but a sprite is pinned to only one
#   chunk for purposes of sprite-to-chunk interaction.
#
# - Chunk adjacency changes are blocked if they would cause the player character to be in a hidden chunk. However, the
#   player character can be warped to a different chunk and trigger an adjacency change from that chunk, and that chunk
#   may look nearly the same or identical to the previous chunk. This leads to effects like the entire map rewriting
#   itself invisibly to the player, just outside the bounds of the screen.

from decimal import Decimal
from enum import Enum

class ChunkEdge(Enum):
    TOP = 1
    BOTTOM = 2
    LEFT = 3
    RIGHT = 4

class Chunk:
    def __init__(self, platform = None) -> None:
        self.hidden = False
        self.contained_sprites = dict()
        self.coalesced_x = Decimal(0)
        self.coalesced_y = Decimal(0)
        self.platform = platform
        self.width = 0 if not self.platform else len(self.platform[0])
        self.height = 0 if not self.platform else len(self.platform)
        self.adjacencies = {}

    def hide(self):
        self.hidden = True

    def coalesce(self, x, y):
        self.hidden = False
        old_x = self.coalesced_x
        old_y = self.coalesced_y
        if x != self.coalesced_x or y != self.coalesced_y:
            self.coalesced_x = x
            self.coalesced_y = y
            for sprite in self.contained_sprites:
                self.warp_sprite(sprite, old_x, old_y)

    def warp_sprite(self, sprite, old_x, old_y):
        sprite.dpos[0] = self.coalesced_x + (sprite.dpos[0] - old_x)
        sprite.dpos[1] = self.coalesced_y + (sprite.dpos[1] - old_y)

    def __getstate__(self):
        s = self.__dict__.copy()
        del s['contained_sprites']
        return s

    def __setstate__(self, state):
        self.__init__(state['platform'])

class Map:
    ''' change_adjacencies:
        Make some chunk pairs adjacent to each other along the given edges.

        'edge_changes' - A list of 2-tuples: [((edge, chunk), (edge, chunk)), ...]
                         where edge is TOP, BOTTOM, LEFT or RIGHT

        We treat the chunks in a map as nodes in an undirected graph, and break the adjacency between chunks when a new
        adjacency is requested on one of the 4 chunk edges if it already has an adjacency. When breaking an adjacency,
        we put the no-longer-adjacent chunk in a set of chunks that may need to be hidden later. We traverse the graph
        from each of those chunks to see if they are connected to the player chunk, and if not, each chunk traversed
        becomes hidden.
    '''
    def change_adjacencies(self, edge_changes, player):
        broken_adjacent_chunks = set()
        # take all the incoming adjacencies, check if making a new adjacency needs to break an old one. if so, add the
        # chunks where adjacency was broken to a set that we will potentially hide later
        for adjacency in edge_changes:
            new_adjacent_edge_1 = adjacency[0][0]
            new_adjacent_edge_2 = adjacency[1][0]
            new_adjacent_chunk_1 = adjacency[0][1]
            new_adjacent_chunk_2 = adjacency[1][1]
            if new_adjacent_edge_1 in new_adjacent_chunk_1.adjacencies:
                    broken_adjacent_chunks.insert(new_adjacent_chunk_1.adjacencies[new_adjacent_edge_1])
                    new_adjacent_chunk_1.adjacencies[new_adjacent_edge_1] = new_adjacent_chunk_2
            if new_adjacent_edge_2 in new_adjacent_chunk_2.adjacencies:
                    broken_adjacent_chunks.insert(new_adjacent_chunk_2.adjacencies[new_adjacent_edge_2])
                    new_adjacent_chunk_2.adjacencies[new_adjacent_edge_2] = new_adjacent_chunk_1
        # next, starting with the chunk the player is in, traverse the graph of adjacent chunks to make them visible.
        chunks_to_coalesce = set((player.current_chunk, player.current_chunk.coalesced_x, player.current_chunk.coalesced_y))
        while len(chunks_to_coalesce) > 0:
            (chunk, coalesce_x, coalesce_y) = chunks_to_coalesce.pop()
            chunk.coalesce(coalesce_x, coalesce_y)
            for edge, adj in chunk.adjacencies.items():
                if edge == ChunkEdge.TOP:
                    chunks_to_coalesce.insert((adj, chunk.coalesced_x, chunk.coalesced_y + chunk.chunk_height))
                elif edge == ChunkEdge.BOTTOM:
                    chunks_to_coalesce.insert((adj, chunk.coalesced_x, chunk.coalesced_y - adj.chunk_height))
                elif edge == ChunkEdge.LEFT:
                    chunks_to_coalesce.insert((adj, chunk.coalesced_x - adj.chunk_width, chunk.coalesced_y))
                else: # ChunkEdge.RIGHT
                    chunks_to_coalesce.insert((adj, chunk.coalesced_x + chunk.width, chunk.coalesced_y))
        # Chunks whose adjacency had to be broken may need to be hidden -- as long as there is no route
        # to them from the current player chunk. Start with a chunk whose adjacency was broken, and do a
        # breadth-first traversal placing all visited chunks on a stack. If the player chunk is seen, then
        # none of the visited chunks need to be hidden. Repeat for all chunks who were not yet visited
        # and whose adjacency was broken.
        all_chunks_to_hide = set()
        while len(broken_adjacent_chunks) > 0:
            traversal_queue = [broken_adjacent_chunks.pop()]
            chunks_to_hide = set()
            while len(traversal_queue) > 0:
                chunk = traversal_queue.pop()
                if chunk == player.current_chunk:
                    chunks_to_hide.clear()
                    break
                if chunk not in chunks_to_hide:
                    chunks_to_hide.insert(chunk)
                    for edge, adj in chunk.adjacencies.items():
                        traversal_queue.append(adj)
            all_chunks_to_hide.update(chunks_to_hide)

        # finally, hide all chunks that had no route to the player-containing chunk
        for chunk in all_chunks_to_hide:
            chunk.hide()
