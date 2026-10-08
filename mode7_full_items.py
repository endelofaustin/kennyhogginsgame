"""Items, hazards, collisions, and AI item behavior for 3D Reaching."""

from mode7_full_content import (
    ITEM_BOMB, ITEM_BUMPER, ITEM_COIN, ITEM_FEATHER, ITEM_LIGHTNING,
    ITEM_OIL, ITEM_SHIELD, ITEM_STAR, ITEM_TURBO,
)

class FullMode7ItemsMixin:
    def _weighted_item(self):
        place = self._place() if self.rivals else 1
        if place <= 2:
            bag = (
                [ITEM_COIN] * 4 + [ITEM_OIL] * 3 + [ITEM_BUMPER] * 2
                + [ITEM_TURBO] * 2 + [ITEM_SHIELD] + [ITEM_FEATHER]
            )
        elif place <= 5:
            bag = (
                [ITEM_TURBO] * 4 + [ITEM_BUMPER] * 4 + [ITEM_OIL] * 2
                + [ITEM_SHIELD] * 2 + [ITEM_FEATHER] * 2 + [ITEM_BOMB]
                + [ITEM_COIN] * 2 + [ITEM_STAR]
            )
        else:
            bag = (
                [ITEM_TURBO] * 5 + [ITEM_BUMPER] * 5 + [ITEM_LIGHTNING] * 2
                + [ITEM_STAR] * 3 + [ITEM_BOMB] * 2 + [ITEM_SHIELD] * 2
                + [ITEM_FEATHER] * 2 + [ITEM_COIN]
            )
        return self.rng.choice(bag)

    def _give_item(self):
        if self.play_mode == "TIME TRIAL" or self.held_item is not None:
            return
        self.held_item = self._weighted_item()
        self.item_label.text = "ITEM: {}".format(self.held_item)
        self._show_mechanic("ITEM BOX: {}".format(self.held_item), 45.0)

    def _consume_protection(self, message="BLOCKED!"):
        if self.invincible_timer > 0:
            self._show_mechanic("STAR {}".format(message), 38.0)
            return True
        if self.shield_timer > 0:
            self.shield_timer = 0.0
            self._show_mechanic("BAT SHIELD {}".format(message), 48.0)
            return True
        return False

    def _hit_player(self, message, speed_factor=0.60, lane_kick=0.34):
        if self._consume_protection("SAVE!"):
            return
        self.speed *= speed_factor
        self.player_lane += self.rng.choice((-lane_kick, lane_kick))
        self.hit_timer = max(self.hit_timer, 55.0)
        self.coin_count = max(0, self.coin_count - 2)
        self._show_mechanic(message, 62.0)

    def _nearest_rival_ahead(self):
        if not self.rivals:
            return None
        player_progress = self.lap * self.track_length + self.distance
        candidates = []
        for rival in self.rivals:
            progress = rival.finished_laps * self.track_length + rival.distance
            gap = progress - player_progress
            if 0 < gap < self.track_length * 0.70:
                candidates.append((gap, rival))
        return min(candidates, key=lambda pair: pair[0])[1] if candidates else None

    def _use_item(self):
        item = self.held_item
        if item is None or self.state != self.STATE_RACE:
            return
        self.held_item = None
        self.item_label.text = "ITEM: —"
        physics = self._physics()
        if item == ITEM_TURBO:
            self.boost_timer = max(self.boost_timer, 105.0)
            self.speed = max(self.speed, physics["max_speed"] + 1.25)
            self._show_mechanic("TURBO!", 55.0)
        elif item == ITEM_BUMPER:
            rival = self._nearest_rival_ahead()
            if rival is not None:
                rival.speed *= 0.45
                rival.hit_timer = 85.0
                rival.lane += self.rng.choice((-0.30, 0.30))
                self._show_mechanic("BUMPER HIT {}!".format(rival.name.upper()), 65.0)
            else:
                self.boost_timer = max(self.boost_timer, 35.0)
                self._show_mechanic("NO TARGET — SMALL BOOST", 45.0)
        elif item == ITEM_OIL:
            progress = self.lap * self.track_length + self.distance - 25.0
            self.player_traps.append({"progress": max(0.0, progress), "lane": self.player_lane})
            self._show_mechanic("OIL DROPPED!", 42.0)
        elif item == ITEM_SHIELD:
            self.shield_timer = 360.0
            self._show_mechanic("BAT SHIELD ACTIVE!", 55.0)
        elif item == ITEM_FEATHER:
            self.hop_total = 68.0
            self.hop_timer = self.hop_total
            self.was_airborne = True
            self.air_trick_armed = True
            self._show_mechanic("SUPER HOP!", 50.0)
        elif item == ITEM_LIGHTNING:
            for rival in self.rivals:
                rival.speed *= 0.56
                rival.hit_timer = max(rival.hit_timer, 135.0)
            self._show_mechanic("LIGHTNING! THE FIELD SHRINKS BACK!", 80.0)
        elif item == ITEM_STAR:
            self.invincible_timer = 260.0
            self.boost_timer = max(self.boost_timer, 220.0)
            self.speed = max(self.speed, physics["max_speed"] + 1.3)
            self._show_mechanic("STAR POWER!", 75.0)
        elif item == ITEM_COIN:
            self.coin_count = min(10, self.coin_count + 2)
            self._show_mechanic("+2 COINS!", 38.0)
        elif item == ITEM_BOMB:
            player_progress = self.lap * self.track_length + self.distance
            hits = 0
            for rival in self.rivals:
                rival_progress = rival.finished_laps * self.track_length + rival.distance
                if abs(rival_progress - player_progress) < 620.0:
                    rival.speed *= 0.42
                    rival.hit_timer = 95.0
                    hits += 1
            self._show_mechanic("BOMB BLAST! {} RIVALS HIT".format(hits), 72.0)

    def _track_interactions(self):
        segment = self._segment_at(self.distance + 12.0)
        physics = self._physics()
        seg_index = self._segment_index(self.distance + 12.0)
        key = (self.lap, seg_index)
        if segment["boost"] and abs(self.player_lane) < 0.78 and self.hit_timer <= 0:
            self.boost_timer = max(self.boost_timer, 38.0 + physics["boost"] * 3.0)
            self.speed = max(self.speed, physics["max_speed"] + 0.7)
            self._show_mechanic("BOOST STRIP!", 30.0)
        if segment["oil"] and abs(self.player_lane - 0.18) < 0.29 and self.hit_timer <= 0:
            if not self._consume_protection("BLOCKED OIL!"):
                self.speed *= 0.54 + physics["weight"] * 0.018
                self.player_lane += self.rng.choice((-0.40, 0.40))
                self.hit_timer = 58.0
                self.coin_count = max(0, self.coin_count - 1)
                self._show_mechanic("OIL SPIN!", 58.0)
        if segment["mud"] and abs(self.player_lane + 0.12) < 0.44 and self.invincible_timer <= 0:
            self.speed *= (0.89 + physics["grip"] * 0.006) ** 0.75
            self._show_mechanic("ROUGH GROUND", 8.0)
        if segment["ramp"] and abs(self.player_lane) < 0.86 and self.hop_timer <= 0:
            self.hop_total = 42.0
            self.hop_timer = self.hop_total
            self.was_airborne = True
            self.air_trick_armed = False
            self._show_mechanic("RAMP! TAP SPACE FOR A TRICK", 45.0)
        if segment.get("item") and abs(self.player_lane) < 0.80:
            if key != self.last_item_key and self.item_box_cooldown <= 0:
                self._give_item()
                self.last_item_key = key
                self.item_box_cooldown = 35.0
        if segment.get("coin") and abs(self.player_lane + 0.18) < 0.34:
            if key != self.last_coin_key and self.coin_cooldown <= 0:
                self.coin_count = min(10, self.coin_count + 1)
                self.last_coin_key = key
                self.coin_cooldown = 25.0
                self._show_mechanic("COIN! {} / 10".format(self.coin_count), 24.0)

    def _check_rival_collision(self):
        if self.hit_timer > 0 or self.invincible_timer > 0:
            return
        physics = self._physics()
        for rival in self.rivals:
            relative = (rival.distance - self.distance) % self.track_length
            if relative < 38.0 and abs(rival.lane - self.player_lane) < 0.27:
                if self.shield_timer > 0:
                    self.shield_timer = 0.0
                    rival.speed *= 0.70
                    rival.hit_timer = 35.0
                    self._show_mechanic("BAT SHIELD BUMP!", 42.0)
                    return
                weight_ratio = physics["weight"] / max(1.0, float(rival.weight))
                if weight_ratio >= 1.0:
                    self.speed *= max(0.86, 0.95 - 0.025 / weight_ratio)
                    rival.speed *= 0.76
                    rival.hit_timer = 30.0
                    rival.lane += 0.19 if rival.lane > self.player_lane else -0.19
                else:
                    self.speed *= max(0.62, 0.79 * weight_ratio)
                    self.player_lane += -0.20 if rival.lane > self.player_lane else 0.20
                self.hit_timer = 22.0
                self._show_mechanic("KART BUMP!", 24.0)
                return

    def _update_rivals(self, dt):
        super()._update_rivals(dt)
        if self.play_mode == "TIME TRIAL":
            return
        player_progress = self.lap * self.track_length + self.distance
        remaining_traps = []
        for trap in self.player_traps:
            hit = False
            for rival in self.rivals:
                rival_progress = rival.finished_laps * self.track_length + rival.distance
                if abs(rival_progress - trap["progress"]) < 34.0 and abs(rival.lane - trap["lane"]) < 0.30:
                    rival.speed *= 0.48
                    rival.hit_timer = 80.0
                    hit = True
                    break
            if not hit and player_progress - trap["progress"] < self.track_length * 1.2:
                remaining_traps.append(trap)
        self.player_traps = remaining_traps
        for rival in self.rivals:
            rival.item_cooldown = max(0.0, getattr(rival, "item_cooldown", 0.0) - dt)
            segment = self._segment_at(rival.distance)
            if not segment.get("item") or rival.item_cooldown > 0:
                continue
            rival.item_cooldown = 380.0 + self.rng.random() * 220.0
            rival_progress = rival.finished_laps * self.track_length + rival.distance
            gap = player_progress - rival_progress
            roll = self.rng.random()
            if roll < 0.42:
                rival.boost_timer = max(rival.boost_timer, 70.0)
                rival.speed += 0.8
            elif roll < 0.68 and 30.0 < gap < 750.0:
                self._hit_player("RIVAL BUMPER HIT!", 0.64, 0.30)
            elif roll < 0.82 and -190.0 < gap < -25.0:
                self._hit_player("RIVAL OIL!", 0.68, 0.26)
            elif roll < 0.90 and self._class_def()["name"] == "150cc":
                self._hit_player("RIVAL LIGHTNING!", 0.72, 0.20)

    def _update_player(self, dt):
        previous_lap = self.lap
        super()._update_player(dt)
        self.item_box_cooldown = max(0.0, self.item_box_cooldown - dt)
        self.coin_cooldown = max(0.0, self.coin_cooldown - dt)
        self.shield_timer = max(0.0, self.shield_timer - dt)
        self.invincible_timer = max(0.0, self.invincible_timer - dt)
        self.coin_label.text = "COINS {}".format(self.coin_count)
        if self.shield_timer > 0:
            self.item_label.text = "SHIELD ACTIVE"
        elif self.invincible_timer > 0:
            self.item_label.text = "STAR ACTIVE"
        elif self.held_item is None:
            self.item_label.text = "ITEM: —"
        else:
            self.item_label.text = "ITEM: {}".format(self.held_item)
        if self.lap > previous_lap:
            lap_time = max(0.0, self.race_time - self.lap_started_at)
            self.lap_started_at = self.race_time
            if lap_time > 0:
                if self.current_best_lap is None or lap_time < self.current_best_lap:
                    self.current_best_lap = lap_time
                key = (self.selected_track, self.selected_class, self.selected_character)
                old = self.best_laps.get(key)
                if old is None or lap_time < old:
                    self.best_laps[key] = lap_time

    def _update_progress_bar(self):
        if not self.progress_dots:
            return
        total_length = self.TOTAL_LAPS * self.track_length
        player_progress = min(total_length, self.lap * self.track_length + self.distance)
        self.progress_dots[0].x = 270 + 260 * max(0.0, min(1.0, player_progress / total_length))
        for dot, rival in zip(self.progress_dots[1:], self.rivals):
            progress = min(total_length, rival.finished_laps * self.track_length + rival.distance)
            dot.x = 270 + 260 * max(0.0, min(1.0, progress / total_length))
