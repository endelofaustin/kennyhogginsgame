
# A magic map loads different chunks in and out according to game logic. The
# chunks in a map don't occupy known coordinates in game space until they are
# loaded; a magic map is a sort of graph between rectangular chunks that can
# coalesce to 2d space according to the rules of chunk loading.
#
# - Each of a chunk's 4 edges can become adjacent to one other chunk, and the
#   adjacency can change at any time when triggered by game logic, causing new
#   chunks to be loaded/coalesced and old chunks to become hidden.
#
# - During an adjacency change, all the parameters determining which chunks are
#   adjacent to each other are re-checked.
#
# - Chunks do not all need to be the same size, but horizontally-adjacent chunks
#   need to have the same height and vertically-adjacent chunks need the same
#   width.
#
# - A chunk may be as big or as small as desired. Many chunks may be visible on
#   screen at a given time, or only one. Or none, though that obviates the need
#   for a magic map.
#
# - All visible chunks, and potentially many hidden chunks, must have been
#   loaded and coalesced into 2d game space. Hidden chunks may occupy the same
#   space as a visible chunk.
#
# - Sprites are pinned to whatever chunk they were most recently coalesced in,
#   and continue interacting even if the chunk is not visible. Sprites may move
#   from chunk to chunk if the chunks are adjacent at the time of a sprite
#   movement update.
#
# - An adjacency change may cause a coalesced chunk to warp to different 2d game
#   space than before the change. All sprites that are pinned to that chunk at
#   the time warp with it.
#
# - Sprite interactions are allowed between sprites in different chunks if
#   desired, but a sprite is pinned to only one chunk for purposes of
#   sprite-to-chunk interaction.
#
# - Chunk adjacency changes are blocked if they would cause the player character
#   to be in a hidden chunk. However, the player character can be warped to a
#   different chunk and trigger an adjacency change from that chunk, and that
#   chunk may look nearly the same or identical to the previous chunk. This
#   leads to effects like the entire map rewriting itself invisibly to the
#   player, just outside the bounds of the screen.

class Chunk:
    pass

class Map:
    pass
