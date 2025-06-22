import pyglet
from math import floor
from pyglet.gl import *

hintable_shader_txt = """#version 150 core
    in vec4 vertex_colors;
    in vec3 texture_coords;
    out vec4 final_colors;

    uniform sampler2D sprite_texture;
    uniform bool useDither;

    // 4x4 Bayer matrix (threshold map scaled to 0–1 range)
    float bayerDither(vec2 pos) {
        int x = int(mod(pos.x, 4.0));
        int y = int(mod(pos.y, 4.0));
        int index = x + y * 4;

        float thresholdMatrix[16] = float[16](
            0.0,  8.0,  2.0, 10.0,
            12.0,  4.0, 14.0,  6.0,
            3.0, 11.0,  1.0,  9.0,
            15.0,  7.0, 13.0,  5.0
        );

        return thresholdMatrix[index] / 16.0;
    }

    void main()
    {
        vec4 color = texture(sprite_texture, texture_coords.xy) * vertex_colors;

        float baseAlpha = color.a * 0.5;
        float threshold = bayerDither(gl_FragCoord.xy);
        float ditheredAlpha = baseAlpha < threshold ? 0.0 : baseAlpha;

        // Apply effect only if useDither is true
        float finalAlpha = useDither ? ditheredAlpha : color.a;

        final_colors = vec4(color.rgb, finalAlpha);
    }
"""

class HintableShaderGroup(pyglet.graphics.ShaderGroup):
    def __init__(self, shader_program, get_dither_flag=None, parent=None, order: int = 0):
        super().__init__(program=shader_program, order=order, parent=parent)
        if get_dither_flag:
            self.get_dither_flag = get_dither_flag  # Function returning bool
        else:
            self.get_dither_flag = lambda: False

        # Cache uniform locations
        self.useDither_loc = glGetUniformLocation(shader_program._id, b"useDither")
        # self.resolution_loc = glGetUniformLocation(shader_program._id, b"resolution")

    def set_state(self):
        super().set_state()

        # Send dynamic toggle
        dither_flag = self.get_dither_flag()
        glUniform1i(self.useDither_loc, int(dither_flag))

class EngineGlobals:
    # scale up all pixel art by this amount
    scale_factor = 2
    tile_size = 16 * scale_factor

    # the window width and height in pixels
    width, height = 400 * scale_factor, 300 * scale_factor
    editor_addl_width = 164

    # width/height of each cell in the collision grid
    collision_cell_size = 64

    # hint tiles
    hint_tiles = [True]

    # do a bunch of engine initialization
    def init():
        pyglet.options.dpi_scaling = 'stretch'
        # set the GL_NEAREST texture filter in order to create a precise pixelated look instead of blurring
        # pixels together when they get upscaled
        pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST
        pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST

        # add some folders to the resource module so that it knows where files live
        pyglet.resource.path = ['./artwork', './audio']
        pyglet.resource.reindex()

        # create a display window
        EngineGlobals.window = pyglet.window.Window(width=EngineGlobals.width + EngineGlobals.editor_addl_width * EngineGlobals.scale_factor,
                                                    height=EngineGlobals.height,
                                                    caption='All The Way To the Bacon Zone', vsync=False)
        pyglet.gl.glClearColor(.5, .5, .5, 1)

        # set up a key state handler
        EngineGlobals.keys = pyglet.window.key.KeyStateHandler()
        EngineGlobals.window.push_handlers(EngineGlobals.keys)

        # playing with shaders
        # vert_shader = pyglet.graphics.shader.Shader(pyglet.sprite.vertex_source, 'vertex')
        # frag_shader = pyglet.graphics.shader.Shader(no_hint_shader, 'fragment')
        # program = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)
        EngineGlobals.hintable_shader = pyglet.gl.current_context.create_program(
            (pyglet.sprite.vertex_source, 'vertex'),
            (hintable_shader_txt, 'fragment')
        )

        # for now, we will use one big graphics batch that every display element gets added to for efficiency
        EngineGlobals.main_batch = pyglet.graphics.Batch()
        EngineGlobals.bg_group = pyglet.graphics.Group(0)
        # EngineGlobals.tiles_back_group = pyglet.graphics.Group(1)
        EngineGlobals.tiles_back_group = HintableShaderGroup(EngineGlobals.hintable_shader, order=1)
        EngineGlobals.sprites_back_group = pyglet.graphics.Group(2)
        EngineGlobals.sprites_front_group = pyglet.graphics.Group(3)
        # EngineGlobals.tiles_front_group = pyglet.graphics.Group(4)
        EngineGlobals.tiles_front_group = HintableShaderGroup(EngineGlobals.hintable_shader, lambda: EngineGlobals.hint_tiles[0], order=4)
        EngineGlobals.editor_group_back = pyglet.graphics.Group(5)
        EngineGlobals.editor_group_mid = pyglet.graphics.Group(6)
        EngineGlobals.editor_group_front = pyglet.graphics.Group(7)

        EngineGlobals.render_fps = 0
        EngineGlobals.sim_fps = 0
        EngineGlobals.last_render = 0
        EngineGlobals.last_sim = 0

        EngineGlobals.hay_block = pyglet.resource.image('firstblock.png')
        # John says that is the act of passing off the creative work of another as your own. such as farm work, art. 
        # cant plagiarize a farm or music. You can now all of a sudden
        EngineGlobals.tilesheet = pyglet.resource.image('steel_tiles.png')
        #EngineGlobals.tilesheet_as_grid = pyglet.image.TextureGrid(pyglet.image.ImageGrid(EngineGlobals.tilesheet, 11, 10, 16, 16))
        #EngineGlobals.tilesheet_as_anim = pyglet.image.Animation.from_image_sequence(EngineGlobals.tilesheet_as_grid, duration=1, loop=False)
        EngineGlobals.show_menu = True

    def get_tile(idx):
        tile_x = idx % floor(EngineGlobals.tilesheet.width / 16) * 16
        tile_y = floor(idx / floor(EngineGlobals.tilesheet.width / 16)) * 16
        if tile_y >= EngineGlobals.tilesheet.height:
            tile_x, tile_y = (0, 0)
        return EngineGlobals.tilesheet.get_region(tile_x, tile_y, 16, 16)

    def pixel_coord(in_coord):
        return int(in_coord / EngineGlobals.scale_factor) * EngineGlobals.scale_factor

    def screen_x(in_x):
        return in_x - EngineGlobals.our_screen.x if hasattr(EngineGlobals, 'our_screen') else in_x

    def screen_y(in_y):
        return in_y - EngineGlobals.our_screen.y if hasattr(EngineGlobals, 'our_screen') else in_y
