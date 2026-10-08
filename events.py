"""Tiny publish/subscribe event bus used by gameplay systems."""

from collections import defaultdict


class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_name, callback):
        if callback not in self._subscribers[event_name]:
            self._subscribers[event_name].append(callback)
        return callback

    def unsubscribe(self, event_name, callback):
        if callback in self._subscribers.get(event_name, []):
            self._subscribers[event_name].remove(callback)

    def publish(self, event_name, **payload):
        for callback in tuple(self._subscribers.get(event_name, ())):
            callback(**payload)


BUS = EventBus()
