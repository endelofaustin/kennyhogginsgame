"""Finish flow, controls, and update loop for the full 3D Reaching game."""

import pyglet

import mode7_racing as base
from mode7_full_content import CUPS, FULL_TRACKS, MODES, POINTS, SPEED_CLASSES

class FullMode7FlowMixin:
    def _finish_race(self):
        self.state = self.STATE_FINISH
        self.speed = 0.0
        self.finish_place = self._place() if self.rivals else 1
        self.finish_panel.visible = True
        self.finish_title.text = "FINISH!"
        key = (self.selected_track, self.selected_class, self.selected_character)
        if self.play_mode == "TIME TRIAL":
            previous = self.best_times.get(key)
            is_best = previous is None or self.race_time < previous
            if is_best:
                self.best_times[key] = self.race_time
            self.finish_result.text = "{}  •  {:.2f}s{}".format(
                self._selected_profile()["name"], self.race_time / 60.0,
                "  NEW BEST!" if is_best else "",
            )
            self.finish_prompt.text = "ENTER retry   •   ESC main menu"
            return
        if self.play_mode == "GRAND PRIX":
            order = self._award_gp_points()
            place = order.index(self._selected_profile()["name"]) + 1
            self.finish_place = place
            points = POINTS[place - 1]
            self.finish_result.text = "RACE {}/5 • PLACE {}/8 • +{} PTS".format(
                self.gp_race + 1, place, points
            )
            self.finish_prompt.text = "ENTER championship standings"
            return
        self.finish_result.text = "{} finished {} of 8".format(
            self._selected_profile()["name"], self.finish_place
        )
        self.finish_prompt.text = "ENTER rematch   •   ESC main menu"

    def start(self):
        self.active = True
        self.keys.clear()
        self.selected_mode = 0
        self.selected_class = 1
        self.selected_character = 0
        self.selected_cup = 0
        self.selected_track = 0
        self.gp_roster = []
        self.gp_points = {}
        self._clear_race()
        self._build_mode_select()

    def on_key_press(self, symbol, modifiers):
        if not self.active:
            return pyglet.event.EVENT_UNHANDLED
        enter = symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN)
        if self.state == self.STATE_MODE:
            if symbol == pyglet.window.key.ESCAPE:
                self.stop()
                if self.on_exit_to_menu:
                    self.on_exit_to_menu()
            elif symbol in (pyglet.window.key.UP, pyglet.window.key.LEFT):
                self.selected_mode = (self.selected_mode - 1) % len(MODES)
                self._refresh_mode_select()
            elif symbol in (pyglet.window.key.DOWN, pyglet.window.key.RIGHT):
                self.selected_mode = (self.selected_mode + 1) % len(MODES)
                self._refresh_mode_select()
            elif enter:
                self.play_mode = MODES[self.selected_mode][0]
                self._build_class_select()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_CLASS:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_mode_select()
            elif symbol in (pyglet.window.key.LEFT, pyglet.window.key.UP):
                self.selected_class = (self.selected_class - 1) % len(SPEED_CLASSES)
                self._refresh_class_select()
            elif symbol in (pyglet.window.key.RIGHT, pyglet.window.key.DOWN):
                self.selected_class = (self.selected_class + 1) % len(SPEED_CLASSES)
                self._refresh_class_select()
            elif enter:
                self._build_character_select()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_CHARACTER:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_class_select()
            elif symbol == pyglet.window.key.LEFT:
                self.selected_character = (self.selected_character - 1) % len(base.CHARACTERS)
                self._refresh_character_select()
            elif symbol == pyglet.window.key.RIGHT:
                self.selected_character = (self.selected_character + 1) % len(base.CHARACTERS)
                self._refresh_character_select()
            elif symbol == pyglet.window.key.UP:
                self.selected_character = (self.selected_character - 5) % len(base.CHARACTERS)
                self._refresh_character_select()
            elif symbol == pyglet.window.key.DOWN:
                self.selected_character = (self.selected_character + 5) % len(base.CHARACTERS)
                self._refresh_character_select()
            elif enter:
                if self.play_mode == "GRAND PRIX":
                    self._build_cup_select()
                else:
                    self._build_track_select()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_CUP:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_character_select()
            elif symbol == pyglet.window.key.LEFT:
                self.selected_cup = (self.selected_cup - 1) % len(CUPS)
                self._refresh_cup_select()
            elif symbol == pyglet.window.key.RIGHT:
                self.selected_cup = (self.selected_cup + 1) % len(CUPS)
                self._refresh_cup_select()
            elif symbol == pyglet.window.key.UP:
                self.selected_cup = (self.selected_cup - 2) % len(CUPS)
                self._refresh_cup_select()
            elif symbol == pyglet.window.key.DOWN:
                self.selected_cup = (self.selected_cup + 2) % len(CUPS)
                self._refresh_cup_select()
            elif enter:
                self._begin_cup()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_TRACK:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_character_select()
            elif symbol == pyglet.window.key.LEFT:
                self.selected_track = (self.selected_track - 1) % len(FULL_TRACKS)
                self._refresh_track_select()
            elif symbol == pyglet.window.key.RIGHT:
                self.selected_track = (self.selected_track + 1) % len(FULL_TRACKS)
                self._refresh_track_select()
            elif symbol == pyglet.window.key.UP:
                self.selected_track = (self.selected_track - 4) % len(FULL_TRACKS)
                self._refresh_track_select()
            elif symbol == pyglet.window.key.DOWN:
                self.selected_track = (self.selected_track + 4) % len(FULL_TRACKS)
                self._refresh_track_select()
            elif enter:
                self._start_race()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_STANDINGS:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_mode_select()
            elif enter:
                self._advance_gp()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_CUP_DONE:
            if symbol == pyglet.window.key.ESCAPE:
                self.stop()
                if self.on_exit_to_menu:
                    self.on_exit_to_menu()
            elif enter:
                self.gp_roster = []
                self.gp_points = {}
                self._build_mode_select()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_FINISH:
            if symbol == pyglet.window.key.ESCAPE:
                self.stop()
                if self.on_exit_to_menu:
                    self.on_exit_to_menu()
            elif enter:
                if self.play_mode == "GRAND PRIX":
                    self._build_standings(final=self.gp_race >= 4)
                else:
                    self._start_race()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_RACE and symbol == pyglet.window.key.D:
            self._use_item()
            return pyglet.event.EVENT_HANDLED
        return super().on_key_press(symbol, modifiers)

    def update(self, dt):
        super().update(dt)
        if not self.active:
            return
        if self.state in (self.STATE_COUNTDOWN, self.STATE_RACE, self.STATE_FINISH):
            self._update_progress_bar()
            if hasattr(self, "best_label"):
                if self.current_best_lap:
                    self.best_label.text = "BEST LAP {:.2f}s".format(self.current_best_lap / 60.0)
                elif self.play_mode == "TIME TRIAL":
                    key = (self.selected_track, self.selected_class, self.selected_character)
                    best = self.best_times.get(key)
                    self.best_label.text = "BEST {:.2f}s".format(best / 60.0) if best else "NO BEST YET"
                else:
                    self.best_label.text = ""
            if hasattr(self, "place_label") and self.play_mode == "TIME TRIAL":
                self.place_label.text = "TIME TRIAL"
