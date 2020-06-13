
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
#   adjacency where one or more narrow chunks have pinned coordinates where they are adjacent to a wider chunk.>
#
# - A chunk may be as big or as small as desired. Many chunks may be visible on screen at a given time, or only one. <Or
#   none, though that obviates the need for a magic map.>
#
# - All visible chunks, and potentially many hidden chunks, must have been loaded and coalesced into 2d game space.
#   Hidden chunks may occupy the same space as a visible chunk.
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

class Chunk:
    pass

class Map:
    ''' change_adjacencies:
        Make some chunk pairs adjacent to each other along the given edges.

        'edge_changes' - A list of 2-tuples: [({edge: chunk, edge: chunk}), ...]

        We solve this by treating the chunks in a map as nodes in an undirected graph, and breaking the adjacency
        between chunks when a new adjacency is requested on one of the 4 chunk edges if it already has an adjacency.
        When breaking the adjacency, we do a depth-first traversal starting from the chunks that are no longer adjacent
        and, if a chunk containing a player character is not encountered, we make those chunks hidden. Then we do
        breadth-first traversal (for efficiency I guess, shouldn't seem to matter) from the newly-adjacent chunks to
        make them visible and warp them if needed.
    '''
    def change_adjacencies(self, edge_changes):
        for adjacency in edge_changes:
            # Check if either chunk is already adjacent to a different chunk along the desired edge. If so, we have to try and break the old adjacency and make the new
            # adjacency, and see if any chunk warping is needed.
            edge_names = adjacency.keys()
            if edge_names[0] == 'top' and edge_names[1] == 'bottom':
                pass
            elif edge_names[0] == 'bottom' and edge_names[1] == 'top':
                pass
            elif edge_names[0] == 'left' and edge_names[1] == 'right':
                pass
            elif edge_names[0] == 'right' and edge_names[1] == 'left':
                pass
