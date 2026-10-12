"""Theo's Trailer: a cramped Nevada trailer and arm-wrestling encounter."""

import math
import random
from decimal import Decimal

import pyglet

import gamepieces
from engineglobals import EngineGlobals
from lifecycle import GameObject


class DustPuff(GameObject):
    """Small dust cloud from the strip of Nevada sand tracked into the trailer."""

    def __init__(self, world_x, world_y):
        self.life = 22.0
        self.parts = []
        sx = float(EngineGlobals.screen_x(world_x))
        sy = float(EngineGlobals.screen_y(world_y))
        for _ in range(5):
            dot = pyglet.shapes.Circle(
                sx + random.uniform(-8, 8),
                sy + random.uniform(0, 5),
                random.uniform(2, 5),
                color=random.choice(((194, 160, 103), (214, 184, 125), (166, 132, 83))),
                batch=EngineGlobals.main_batch,
                group=EngineGlobals.editor_group_mid,
            )
            self.parts.append((dot, random.uniform(-0.7, 0.7), random.uniform(0.25, 0.9)))
        super().__init__(lifecycle_manager="PER_MAP")

    def updateloop(self, dt):
        self.life -= float(dt)
        for dot, vx, vy in self.parts:
            dot.x += vx * float(dt)
            dot.y += vy * float(dt)
            if hasattr(dot, "opacity"):
                dot.opacity = max(0, int(255 * self.life / 22.0))
        if self.life <= 0:
            self.destroy()

    def on_finalDeletion(self):
        for dot, _, _ in self.parts:
            dot.delete()
        self.parts.clear()


class TheoTrailerEncounter(GameObject):
    """World-space Theo/table plus the accepted screen-space arm-wrestling minigame."""

    IDLE = "idle"
    COUNTDOWN = "countdown"
    WRESTLING = "wrestling"
    RESULT = "result"

    def __init__(self, chunk, player_spawn, table_position):
        self.chunk = chunk
        self.player_spawn = player_spawn
        self.table_x = Decimal(str(table_position[0]))
        # Put Theo on Kenny's starting floor and carve a straight walk-up lane.
        self.table_y = Decimal(str(player_spawn[1]))
        self.state = self.IDLE
        self.meter = 0.0
        self.match_frames = 0.0
        self.countdown_frames = 0.0
        self.result_frames = 0.0
        self.winner = None
        self.theo_phase = random.uniform(0, math.tau)
        self.theo_burst = 0.0
        self.c_press_flash = 0.0
        self.fish_progress = 0.0
        self.fish_loops = 0
        self.dust_timer = 0.0

        self.world_shapes = []
        self.fixed_shapes = []
        self.world_labels = []
        self.fixed_labels = []
        self.overlay_shapes = []
        self.overlay_labels = []
        self.fish_shapes = []

        self._prepare_walkway()

        self.sand_left = Decimal(str(player_spawn[0])) - Decimal(24)
        self.sand_right = min(self.table_x - Decimal(105), self.sand_left + Decimal(190))
        self.sand_bottom = self.table_y - Decimal(8)
        self.sand_top = self.table_y + Decimal(42)

        EngineGlobals.arm_wrestling_active = False
        EngineGlobals.on_sand = False

        super().__init__(lifecycle_manager="PER_MAP")
        try:
            self._build_world_scene()
            EngineGlobals.window.push_handlers(self)
        except Exception:
            self._cleanup_graphics()
            raise

    def _delete_block_sprite(self, block):
        if isinstance(block, gamepieces.Block) and hasattr(block, "sprite"):
            try:
                block.sprite.delete()
            except Exception:
                pass

    def _prepare_walkway(self):
        """Flatten the walk from Kenny to Theo and remove overhead collision junk."""
        platform = getattr(self.chunk, "platform", None)
        if not platform or not platform[0]:
            return

        tile = int(EngineGlobals.tile_size)
        width = len(platform[0])
        height = len(platform)
        chunk_x = int(getattr(self.chunk, "coalesced_x", 0))
        chunk_y = int(getattr(self.chunk, "coalesced_y", 0))

        standing_y = int(self.table_y)
        floor_world_y = standing_y - tile - 1
        floor_from_bottom = max(0, int((floor_world_y - chunk_y) // tile))
        floor_row = height - 1 - floor_from_bottom
        floor_row = max(0, min(height - 1, floor_row))

        left_world = min(int(self.player_spawn[0]), int(self.table_x)) - tile * 2
        right_world = max(int(self.player_spawn[0]), int(self.table_x)) + tile * 10
        left_col = max(0, int((left_world - chunk_x) // tile))
        right_col = min(width - 1, int((right_world - chunk_x) // tile))

        # Five tiles of head room is enough for Kenny's stable collision box.
        clear_top = max(0, floor_row - 6)
        for column in range(left_col, right_col + 1):
            for row in range(clear_top, floor_row):
                old = platform[row][column]
                if old != 0:
                    self._delete_block_sprite(old)
                    platform[row][column] = 0

            old_floor = platform[floor_row][column]
            if not isinstance(old_floor, gamepieces.Block) or isinstance(
                old_floor, (gamepieces.HazardBlock, gamepieces.BreakableBlock)
            ) or not getattr(old_floor, "solid", False):
                self._delete_block_sprite(old_floor)
                platform[floor_row][column] = gamepieces.Block(column % 12, True)

    def _world_rect(self, world_x, world_y, width, height, color, group):
        shape = pyglet.shapes.Rectangle(
            0,
            0,
            width,
            height,
            color=color,
            batch=EngineGlobals.main_batch,
            group=group,
        )
        self.world_shapes.append((shape, Decimal(str(world_x)), Decimal(str(world_y))))
        return shape

    def _world_circle(self, world_x, world_y, radius, color, group):
        shape = pyglet.shapes.Circle(
            0,
            0,
            radius,
            color=color,
            batch=EngineGlobals.main_batch,
            group=group,
        )
        self.world_shapes.append((shape, Decimal(str(world_x)), Decimal(str(world_y))))
        return shape

    def _world_label(self, text, world_x, world_y, font_size=13, color=(35, 25, 20, 255)):
        label = pyglet.text.Label(
            text,
            x=0,
            y=0,
            anchor_x="center",
            font_size=font_size,
            weight=pyglet.text.Weight.BOLD,
            color=color,
            batch=EngineGlobals.main_batch,
            group=EngineGlobals.editor_group_front,
        )
        self.world_labels.append((label, Decimal(str(world_x)), Decimal(str(world_y))))
        return label

    def _build_world_scene(self):
        """Build the inside of a sun-baked, cluttered Nevada trailer."""
        batch = EngineGlobals.main_batch
        bg = EngineGlobals.bg_group
        mid = EngineGlobals.editor_group_mid
        front = EngineGlobals.editor_group_front

        # Trailer shell: nicotine-tan paneling, low ceiling, worn linoleum.
        self.fixed_shapes.append(
            pyglet.shapes.Rectangle(
                0,
                0,
                EngineGlobals.width,
                EngineGlobals.height,
                color=(166, 135, 92),
                batch=batch,
                group=bg,
            )
        )
        self.fixed_shapes.append(
            pyglet.shapes.Rectangle(
                0,
                0,
                EngineGlobals.width,
                118,
                color=(113, 91, 67),
                batch=batch,
                group=bg,
            )
        )
        self.fixed_shapes.append(
            pyglet.shapes.Rectangle(
                0,
                EngineGlobals.height - 70,
                EngineGlobals.width,
                70,
                color=(118, 101, 80),
                batch=batch,
                group=bg,
            )
        )
        for x in range(0, EngineGlobals.width, 92):
            self.fixed_shapes.append(
                pyglet.shapes.Rectangle(
                    x,
                    118,
                    3,
                    EngineGlobals.height - 188,
                    color=(111, 86, 60),
                    batch=batch,
                    group=bg,
                )
            )

        # A tiny window showing the Nevada desert so the location reads immediately.
        self.fixed_shapes.append(
            pyglet.shapes.Rectangle(65, 352, 205, 128, color=(73, 59, 48), batch=batch, group=bg)
        )
        self.fixed_shapes.append(
            pyglet.shapes.Rectangle(75, 362, 185, 108, color=(184, 211, 220), batch=batch, group=bg)
        )
        self.fixed_shapes.append(
            pyglet.shapes.Rectangle(75, 362, 185, 38, color=(196, 151, 87), batch=batch, group=bg)
        )
        self.fixed_shapes.append(
            pyglet.shapes.Rectangle(164, 362, 5, 108, color=(226, 214, 188), batch=batch, group=bg)
        )
        self.fixed_shapes.append(
            pyglet.shapes.Rectangle(75, 414, 185, 5, color=(226, 214, 188), batch=batch, group=bg)
        )
        self.fixed_labels.append(
            pyglet.text.Label(
                "NEVADA",
                x=168,
                y=430,
                anchor_x="center",
                font_size=11,
                weight=pyglet.text.Weight.BOLD,
                color=(112, 70, 45, 255),
                batch=batch,
                group=mid,
            )
        )

        # Trailer clutter: sagging couch, mini-fridge, AC, crooked wall frame.
        self.fixed_shapes.extend(
            [
                pyglet.shapes.Rectangle(34, 126, 210, 72, color=(92, 111, 73), batch=batch, group=mid),
                pyglet.shapes.Rectangle(45, 184, 188, 37, color=(104, 123, 83), batch=batch, group=mid),
                pyglet.shapes.Rectangle(55, 126, 18, 20, color=(56, 49, 41), batch=batch, group=mid),
                pyglet.shapes.Rectangle(205, 126, 18, 20, color=(56, 49, 41), batch=batch, group=mid),
                pyglet.shapes.Rectangle(674, 118, 94, 132, color=(203, 199, 180), batch=batch, group=mid),
                pyglet.shapes.Rectangle(684, 185, 74, 4, color=(129, 124, 111), batch=batch, group=mid),
                pyglet.shapes.Rectangle(686, 201, 9, 26, color=(92, 87, 77), batch=batch, group=mid),
                pyglet.shapes.Rectangle(550, 454, 118, 62, color=(194, 188, 164), batch=batch, group=mid),
                pyglet.shapes.Rectangle(560, 464, 98, 42, color=(102, 112, 101), batch=batch, group=mid),
                pyglet.shapes.Rectangle(380, 402, 95, 68, color=(83, 61, 47), batch=batch, group=mid),
                pyglet.shapes.Rectangle(388, 410, 79, 52, color=(201, 172, 112), batch=batch, group=mid),
            ]
        )

        # A little tracked-in sand keeps the requested sand movement/dust mechanic.
        sand_width = float(max(0, self.sand_right - self.sand_left))
        if sand_width > 0:
            self._world_rect(self.sand_left, self.sand_bottom, sand_width, 34, (190, 151, 94), mid)
            for i in range(18):
                sx = self.sand_left + Decimal((i * 31) % max(1, int(sand_width)))
                sy = self.sand_bottom + Decimal(4 + (i * 11) % 24)
                self._world_rect(sx, sy, 3, 2, (139, 104, 65), mid)

        # Arm-wrestling table in the clear lane.
        self._world_rect(self.table_x - Decimal(88), self.table_y + Decimal(31), 176, 22, (83, 52, 36), front)
        self._world_rect(self.table_x - Decimal(68), self.table_y - Decimal(29), 18, 61, (66, 43, 32), front)
        self._world_rect(self.table_x + Decimal(50), self.table_y - Decimal(29), 18, 61, (66, 43, 32), front)
        self._world_rect(self.table_x - Decimal(20), self.table_y + Decimal(47), 40, 8, (132, 33, 29), front)
        self._world_label("ARM WRESTLING", self.table_x, self.table_y + Decimal(78), font_size=12)

        self._build_theo(self.table_x + Decimal(126), self.table_y + Decimal(39))
        self._world_label("COUSIN THEO", self.table_x + Decimal(126), self.table_y + Decimal(185), font_size=13)

        self.prompt_label = pyglet.text.Label(
            "Walk up to Theo's table and press D",
            x=EngineGlobals.width // 2,
            y=565,
            anchor_x="center",
            font_size=16,
            weight=pyglet.text.Weight.BOLD,
            color=(245, 236, 208, 255),
            batch=batch,
            group=front,
        )
        self.fixed_labels.append(self.prompt_label)
        self._sync_world_scene()

    def _build_theo(self, x, y):
        """Chunky Kenny-like pixel Theo preserving the original weird doodle silhouette."""
        front = EngineGlobals.editor_group_front
        outline = (31, 25, 22)
        skin = (222, 172, 127)
        skin_hi = (239, 193, 148)
        hair = (48, 34, 29)
        shirt = (79, 67, 58)
        jeans = (69, 78, 87)
        shoe = (35, 31, 29)

        # Hair spikes and oversized blocky head.
        for ox, oy, w, h in [(-24, 105, 7, 22), (-13, 112, 7, 22), (-2, 108, 7, 27), (9, 114, 7, 19), (20, 104, 7, 25)]:
            self._world_rect(x + Decimal(ox), y + Decimal(oy), w, h, hair, front)
        self._world_rect(x - Decimal(24), y + Decimal(67), 54, 44, outline, front)
        self._world_rect(x - Decimal(19), y + Decimal(72), 45, 34, skin, front)
        self._world_rect(x - Decimal(14), y + Decimal(94), 32, 8, skin_hi, front)

        # Horse-ish long nose from the hand-drawn Theo.
        self._world_rect(x + Decimal(23), y + Decimal(82), 38, 14, outline, front)
        self._world_rect(x + Decimal(23), y + Decimal(85), 34, 8, skin, front)
        self._world_rect(x + Decimal(53), y + Decimal(83), 12, 12, outline, front)
        self._world_rect(x + Decimal(54), y + Decimal(86), 8, 6, skin_hi, front)

        # Eyes, mustache and little goatee.
        self._world_rect(x - Decimal(10), y + Decimal(91), 5, 5, (15, 15, 15), front)
        self._world_rect(x + Decimal(11), y + Decimal(91), 5, 5, (15, 15, 15), front)
        self._world_rect(x + Decimal(9), y + Decimal(75), 24, 6, hair, front)
        self._world_rect(x + Decimal(17), y + Decimal(63), 8, 13, hair, front)

        # Skinny, awkward body with blocky elbows/hands.
        self._world_rect(x - Decimal(11), y + Decimal(8), 24, 55, outline, front)
        self._world_rect(x - Decimal(6), y + Decimal(13), 14, 45, shirt, front)
        self._world_rect(x - Decimal(48), y + Decimal(42), 39, 8, outline, front)
        self._world_rect(x - Decimal(45), y + Decimal(44), 35, 4, shirt, front)
        self._world_rect(x + Decimal(12), y + Decimal(38), 43, 8, outline, front)
        self._world_rect(x + Decimal(14), y + Decimal(40), 38, 4, shirt, front)
        self._world_rect(x - Decimal(54), y + Decimal(38), 10, 14, skin, front)
        self._world_rect(x + Decimal(52), y + Decimal(35), 11, 14, skin, front)

        # Uneven stick legs and tiny shoes keep the awkward stance.
        self._world_rect(x - Decimal(17), y - Decimal(43), 9, 52, outline, front)
        self._world_rect(x - Decimal(14), y - Decimal(40), 5, 47, jeans, front)
        self._world_rect(x + Decimal(10), y - Decimal(48), 9, 57, outline, front)
        self._world_rect(x + Decimal(13), y - Decimal(45), 5, 52, jeans, front)
        self._world_rect(x - Decimal(28), y - Decimal(50), 23, 8, shoe, front)
        self._world_rect(x + Decimal(9), y - Decimal(55), 25, 8, shoe, front)

    def _sync_world_scene(self):
        for shape, wx, wy in self.world_shapes:
            shape.x = float(EngineGlobals.screen_x(wx))
            shape.y = float(EngineGlobals.screen_y(wy))
        for label, wx, wy in self.world_labels:
            label.x = float(EngineGlobals.screen_x(wx))
            label.y = float(EngineGlobals.screen_y(wy))

    def _near_table(self):
        kenny = getattr(EngineGlobals, "kenny", None)
        if kenny is None:
            return False
        dx = abs(Decimal(kenny.x_position) - self.table_x)
        dy = abs(Decimal(kenny.y_position) - self.table_y)
        return dx <= Decimal(125) and dy <= Decimal(105)

    def _update_sand(self, dt):
        if self.state != self.IDLE:
            EngineGlobals.on_sand = False
            return
        kenny = getattr(EngineGlobals, "kenny", None)
        if kenny is None:
            EngineGlobals.on_sand = False
            return

        x = Decimal(kenny.x_position)
        y = Decimal(kenny.y_position)
        in_sand = self.sand_left <= x <= self.sand_right and self.sand_bottom <= y <= self.sand_top
        EngineGlobals.on_sand = in_sand

        if in_sand and abs(Decimal(kenny.x_speed)) > Decimal("0.2"):
            self.dust_timer -= float(dt)
            if self.dust_timer <= 0:
                DustPuff(kenny.x_position + Decimal(18), kenny.y_position + Decimal(2))
                self.dust_timer = 8.0
        else:
            self.dust_timer = 0.0

    def _add_overlay_shape(self, shape):
        self.overlay_shapes.append(shape)
        return shape

    def _add_overlay_label(self, label):
        self.overlay_labels.append(label)
        return label

    def _build_match_overlay(self):
        # Keep the already accepted giant-arm overlay unchanged.
        self._clear_match_overlay()
        batch = EngineGlobals.main_batch
        front = EngineGlobals.editor_group_front

        self._add_overlay_shape(pyglet.shapes.Rectangle(55, 55, 690, 500, color=(45, 38, 38), batch=batch, group=front))
        self._add_overlay_shape(pyglet.shapes.Rectangle(70, 70, 660, 470, color=(232, 216, 174), batch=batch, group=front))

        self.kenny_label = self._add_overlay_label(
            pyglet.text.Label("KENNY", x=175, y=505, anchor_x="center", font_size=28, weight=pyglet.text.Weight.BOLD,
                              color=(60, 87, 158, 255), batch=batch, group=front)
        )
        self.theo_label = self._add_overlay_label(
            pyglet.text.Label("THEO", x=625, y=505, anchor_x="center", font_size=28, weight=pyglet.text.Weight.BOLD,
                              color=(158, 69, 56, 255), batch=batch, group=front)
        )
        self.status_label = self._add_overlay_label(
            pyglet.text.Label("GET READY", x=400, y=505, anchor_x="center", font_size=22, weight=pyglet.text.Weight.BOLD,
                              color=(35, 25, 20, 255), batch=batch, group=front)
        )
        self.timer_label = self._add_overlay_label(
            pyglet.text.Label("D started it — mash C to overpower Theo", x=400, y=465, anchor_x="center", font_size=14,
                              color=(35, 25, 20, 255), batch=batch, group=front)
        )

        self._add_overlay_shape(pyglet.shapes.Rectangle(95, 420, 230, 22, color=(84, 77, 70), batch=batch, group=front))
        self.kenny_power = self._add_overlay_shape(pyglet.shapes.Rectangle(99, 424, 0, 14, color=(77, 124, 212), batch=batch, group=front))
        self._add_overlay_shape(pyglet.shapes.Rectangle(475, 420, 230, 22, color=(84, 77, 70), batch=batch, group=front))
        self.theo_power = self._add_overlay_shape(pyglet.shapes.Rectangle(701, 424, 0, 14, color=(199, 86, 70), batch=batch, group=front))
        self._add_overlay_label(pyglet.text.Label("KENNY POWER", x=210, y=445, anchor_x="center", font_size=11,
                                                  color=(35, 25, 20, 255), batch=batch, group=front))
        self._add_overlay_label(pyglet.text.Label("THEO POWER", x=590, y=445, anchor_x="center", font_size=11,
                                                  color=(35, 25, 20, 255), batch=batch, group=front))

        self._add_overlay_shape(pyglet.shapes.Rectangle(150, 105, 500, 32, color=(84, 77, 70), batch=batch, group=front))
        self.tug_fill = self._add_overlay_shape(pyglet.shapes.Rectangle(400, 110, 0, 22, color=(89, 170, 95), batch=batch, group=front))
        self._add_overlay_shape(pyglet.shapes.Rectangle(397, 99, 6, 44, color=(250, 248, 232), batch=batch, group=front))
        self._add_overlay_label(pyglet.text.Label("THEO", x=150, y=82, anchor_x="center", font_size=11,
                                                  color=(35, 25, 20, 255), batch=batch, group=front))
        self._add_overlay_label(pyglet.text.Label("KENNY", x=650, y=82, anchor_x="center", font_size=11,
                                                  color=(35, 25, 20, 255), batch=batch, group=front))

        self.kenny_shoulder = self._add_overlay_shape(pyglet.shapes.Circle(115, 250, 64, color=(225, 151, 153), batch=batch, group=front))
        self.kenny_bicep = self._add_overlay_shape(pyglet.shapes.Circle(205, 285, 59, color=(235, 163, 164), batch=batch, group=front))
        self.kenny_upper = self._add_overlay_shape(pyglet.shapes.Rectangle(120, 245, 180, 72, color=(235, 163, 164), batch=batch, group=front))
        self.kenny_elbow = self._add_overlay_shape(pyglet.shapes.Circle(300, 280, 40, color=(226, 149, 151), batch=batch, group=front))
        self.kenny_forearm = self._add_overlay_shape(pyglet.shapes.Rectangle(300, 260, 100, 54, color=(238, 169, 170), batch=batch, group=front))
        self.kenny_fist = self._add_overlay_shape(pyglet.shapes.Circle(400, 287, 33, color=(241, 176, 177), batch=batch, group=front))

        self.theo_shoulder = self._add_overlay_shape(pyglet.shapes.Circle(685, 250, 64, color=(205, 151, 105), batch=batch, group=front))
        self.theo_bicep = self._add_overlay_shape(pyglet.shapes.Circle(595, 285, 59, color=(219, 166, 119), batch=batch, group=front))
        self.theo_upper = self._add_overlay_shape(pyglet.shapes.Rectangle(500, 245, 180, 72, color=(219, 166, 119), batch=batch, group=front))
        self.theo_elbow = self._add_overlay_shape(pyglet.shapes.Circle(500, 280, 40, color=(207, 151, 103), batch=batch, group=front))
        self.theo_forearm = self._add_overlay_shape(pyglet.shapes.Rectangle(400, 260, 100, 54, color=(225, 175, 127), batch=batch, group=front))
        self.theo_fist = self._add_overlay_shape(pyglet.shapes.Circle(400, 287, 33, color=(229, 181, 134), batch=batch, group=front))

        self._add_overlay_shape(pyglet.shapes.Circle(160, 318, 31, color=(244, 180, 181), batch=batch, group=front))
        self._add_overlay_shape(pyglet.shapes.Circle(640, 318, 31, color=(232, 187, 143), batch=batch, group=front))
        self._update_overlay_visuals()

    def _clear_match_overlay(self):
        for shape in self.fish_shapes:
            shape.delete()
        self.fish_shapes = []
        for label in self.overlay_labels:
            label.delete()
        self.overlay_labels = []
        for shape in self.overlay_shapes:
            shape.delete()
        self.overlay_shapes = []

    def _update_overlay_visuals(self):
        if not self.overlay_shapes:
            return

        kenny_fraction = max(0.0, min(1.0, (self.meter + 100.0) / 200.0))
        theo_fraction = 1.0 - kenny_fraction
        self.kenny_power.width = 222 * kenny_fraction
        theo_width = 222 * theo_fraction
        self.theo_power.width = theo_width
        self.theo_power.x = 701 - theo_width

        tug_width = min(245.0, abs(self.meter) * 2.45)
        if self.meter >= 0:
            self.tug_fill.x = 400
            self.tug_fill.width = tug_width
            self.tug_fill.color = (77, 124, 212)
        else:
            self.tug_fill.x = 400 - tug_width
            self.tug_fill.width = tug_width
            self.tug_fill.color = (199, 86, 70)

        clasp_x = 400 + self.meter * 1.25
        kenny_forearm_width = max(32.0, clasp_x - 300)
        self.kenny_forearm.x = 300
        self.kenny_forearm.width = kenny_forearm_width
        self.kenny_fist.x = clasp_x - 15

        theo_forearm_width = max(32.0, 500 - clasp_x)
        self.theo_forearm.x = clasp_x
        self.theo_forearm.width = theo_forearm_width
        self.theo_fist.x = clasp_x + 15

        pulse = 4.0 * math.sin(self.theo_phase * 2.0)
        self.kenny_bicep.radius = max(52, 59 + (5 if self.c_press_flash > 0 else 0) + pulse)
        self.theo_bicep.radius = max(52, 59 + (6 if self.theo_burst > 0 else 0) - pulse)

    def _start_match(self):
        kenny = EngineGlobals.kenny
        self.state = self.COUNTDOWN
        self.countdown_frames = 150.0
        self.match_frames = 600.0
        self.meter = 0.0
        self.winner = None
        self.fish_progress = 0.0
        self.fish_loops = 0
        EngineGlobals.arm_wrestling_active = True
        EngineGlobals.on_sand = False
        kenny.x_speed = Decimal(0)
        kenny.y_speed = Decimal(0)
        kenny.x_position = self.table_x - Decimal(90)
        kenny.y_position = self.table_y
        self.prompt_label.text = ""
        self._build_match_overlay()

    def _finish_match(self, winner):
        self.state = self.RESULT
        self.winner = winner
        self.result_frames = 250.0
        self.fish_progress = 0.0
        self.fish_loops = 0
        EngineGlobals.arm_wrestling_active = True
        self.status_label.text = "KENNY WINS!" if winner == "kenny" else "THEO WINS!"
        self.timer_label.text = "Winner gets the fish. Loser gets the slap."
        self._create_fish()

    def _create_fish(self):
        for shape in self.fish_shapes:
            shape.delete()
        self.fish_shapes = []
        batch = EngineGlobals.main_batch
        front = EngineGlobals.editor_group_front
        body = pyglet.shapes.Rectangle(0, 0, 58, 24, color=(114, 166, 181), batch=batch, group=front)
        head = pyglet.shapes.Circle(0, 0, 16, color=(131, 183, 195), batch=batch, group=front)
        eye = pyglet.shapes.Circle(0, 0, 3, color=(10, 10, 10), batch=batch, group=front)
        tail_top = pyglet.shapes.Rectangle(0, 0, 19, 9, color=(85, 137, 153), batch=batch, group=front)
        tail_bottom = pyglet.shapes.Rectangle(0, 0, 19, 9, color=(85, 137, 153), batch=batch, group=front)
        self.fish_shapes = [body, head, eye, tail_top, tail_bottom]
        self._add_overlay_label(
            pyglet.text.Label("FISH SLAP!", x=400, y=390, anchor_x="center", font_size=30,
                              weight=pyglet.text.Weight.BOLD, color=(35, 25, 20, 255), batch=batch, group=front)
        )

    def _update_fish(self, dt):
        if not self.fish_shapes:
            return
        self.fish_progress += 0.045 * float(dt)
        if self.fish_progress >= 1.0:
            self.fish_progress = 0.0
            self.fish_loops += 1

        if self.winner == "kenny":
            start_x, end_x = 220.0, 625.0
        else:
            start_x, end_x = 580.0, 175.0
        x = start_x + (end_x - start_x) * self.fish_progress
        y = 305.0 + math.sin(self.fish_progress * math.pi) * 120.0

        body, head, eye, tail_top, tail_bottom = self.fish_shapes
        body.x = x - 29
        body.y = y - 12
        head.x = x + 29
        head.y = y
        eye.x = x + 35
        eye.y = y + 5
        tail_top.x = x - 47
        tail_top.y = y + 4
        tail_bottom.x = x - 47
        tail_bottom.y = y - 13

    def updateloop(self, dt):
        self._sync_world_scene()
        self._update_sand(dt)

        if self.state == self.IDLE:
            self.prompt_label.text = "Press D to arm wrestle Theo" if self._near_table() else "Walk up to Theo's table and press D"
            return

        if self.state == self.COUNTDOWN:
            self.countdown_frames -= float(dt)
            if self.countdown_frames > 100:
                self.status_label.text = "3"
            elif self.countdown_frames > 50:
                self.status_label.text = "2"
            elif self.countdown_frames > 0:
                self.status_label.text = "1"
            else:
                self.state = self.WRESTLING
                self.status_label.text = "MASH C!"
                self.timer_label.text = "10.0s"
            self._update_overlay_visuals()
            return

        if self.state == self.WRESTLING:
            frame_dt = float(dt)
            self.match_frames -= frame_dt
            self.theo_phase += 0.11 * frame_dt

            if self.theo_burst > 0:
                theo_force = 0.52
                self.theo_burst -= frame_dt
            else:
                theo_force = 0.18 + max(0.0, math.sin(self.theo_phase)) * 0.19
                if random.random() < 0.012 * max(1.0, frame_dt):
                    self.theo_burst = random.randint(18, 42)

            self.meter -= theo_force * frame_dt
            self.meter *= 0.998 ** frame_dt
            self.meter = max(-100.0, min(100.0, self.meter))
            self.c_press_flash = max(0.0, self.c_press_flash - frame_dt)
            self.status_label.text = "PUSH!" if self.c_press_flash > 0 else "MASH C!"
            self.timer_label.text = "{:.1f}s".format(max(0.0, self.match_frames / 60.0))
            self._update_overlay_visuals()

            if self.meter >= 100.0:
                self._finish_match("kenny")
            elif self.meter <= -100.0:
                self._finish_match("theo")
            elif self.match_frames <= 0:
                self._finish_match("kenny" if self.meter > 0 else "theo")
            return

        if self.state == self.RESULT:
            self.result_frames -= float(dt)
            self._update_fish(dt)
            self._update_overlay_visuals()
            if self.result_frames <= 0:
                self._end_match()

    def _end_match(self):
        EngineGlobals.arm_wrestling_active = False
        self.state = self.IDLE
        self.prompt_label.text = "Press D for a rematch"
        self._clear_match_overlay()
        kenny = getattr(EngineGlobals, "kenny", None)
        if kenny is not None:
            kenny.x_position = self.table_x - Decimal(115)
            kenny.y_position = self.table_y
            kenny.x_speed = Decimal(0)
            kenny.y_speed = Decimal(0)

    def on_key_press(self, symbol, modifiers):
        if self.state == self.IDLE:
            if symbol == pyglet.window.key.D and self._near_table():
                self._start_match()
                return pyglet.event.EVENT_HANDLED
            return pyglet.event.EVENT_UNHANDLED

        if self.state == self.WRESTLING and symbol == pyglet.window.key.C:
            self.meter = min(100.0, self.meter + 7.0)
            self.c_press_flash = 8.0
            self._update_overlay_visuals()
            if self.meter >= 100.0:
                self._finish_match("kenny")
            return pyglet.event.EVENT_HANDLED

        if self.state in (self.COUNTDOWN, self.WRESTLING, self.RESULT):
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def _cleanup_graphics(self):
        self._clear_match_overlay()
        for label, _, _ in self.world_labels:
            label.delete()
        self.world_labels = []
        for label in self.fixed_labels:
            label.delete()
        self.fixed_labels = []
        for shape, _, _ in self.world_shapes:
            shape.delete()
        self.world_shapes = []
        for shape in self.fixed_shapes:
            shape.delete()
        self.fixed_shapes = []

    def on_finalDeletion(self):
        EngineGlobals.arm_wrestling_active = False
        EngineGlobals.on_sand = False
        try:
            EngineGlobals.window.remove_handlers(self)
        except Exception:
            pass
        self._cleanup_graphics()
