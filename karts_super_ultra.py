"""Bridge the legacy KARTS menu slot to standalone Super Ultra Kenny Kart.

The legacy KartsMode object is retained only as the host expected by main.py.
All gameplay/render/input is delegated to the standalone SuperUltraKart engine.
No Mode 7/N64 classes are imported or modified.
"""

import karts_mode as km
from super_ultra_kart import SuperUltraKart
from super_ultra_visuals import install_super_ultra_visuals


_INSTALLED = False


def _delegate(self):
    return self._super_ultra


def _init(self, on_exit_to_menu=None):
    self.on_exit_to_menu = on_exit_to_menu
    self._super_ultra = SuperUltraKart(on_exit_to_menu=on_exit_to_menu)


def _start(self):
    game = _delegate(self)
    # Embedded mode: main.py already owns the update/draw/input loop, so do
    # SuperUltraKart.start's setup without installing a second window clock.
    game.active = True
    game.keys.clear()
    game.buttons.clear()
    game.attach_controllers()
    game._clear_race()
    game._build_home()


def _stop(self):
    game = _delegate(self)
    game.active = False
    game.keys.clear()
    game.buttons.clear()
    game._clear_menu()
    game._clear_race()


def _update(self, dt):
    _delegate(self).update(dt)


def _draw(self):
    _delegate(self).draw()


def _on_key_press(self, symbol, modifiers):
    return _delegate(self).on_key_press(symbol, modifiers)


def _on_key_release(self, symbol, modifiers):
    return _delegate(self).on_key_release(symbol, modifiers)


def install_super_ultra():
    """Route only the old KARTS slot to the standalone Super Ultra game."""
    global _INSTALLED
    if _INSTALLED:
        return

    install_super_ultra_visuals()

    cls = km.KartsMode
    cls.__init__ = _init
    cls.start = _start
    cls.stop = _stop
    cls.update = _update
    cls.draw = _draw
    cls.on_key_press = _on_key_press
    cls.on_key_release = _on_key_release

    _INSTALLED = True
