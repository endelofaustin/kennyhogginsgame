"""Small explicit state machine used by players, enemies, and game flow."""


class State:
    name = "state"

    def enter(self, owner, previous=None):
        pass

    def exit(self, owner, next_state=None):
        pass

    def update(self, owner, dt):
        pass


class StateMachine:
    def __init__(self, owner, states, initial):
        self.owner = owner
        self.states = {state.name: state for state in states}
        self.current = None
        self.change(initial)

    @property
    def name(self):
        return self.current.name if self.current else None

    def change(self, name):
        if name not in self.states:
            raise KeyError("Unknown state: {}".format(name))
        if self.current and self.current.name == name:
            return
        previous = self.current
        next_state = self.states[name]
        if previous:
            previous.exit(self.owner, next_state)
        self.current = next_state
        self.current.enter(self.owner, previous)

    def update(self, dt):
        if self.current:
            self.current.update(self.owner, dt)
