import collections
import functools
from typing import Any, Callable, DefaultDict


class EventEmitterMaxListenerError(Exception):
    pass


Listener = Callable[..., Any]


class EventEmitter:
    DEFAULT_MAX_LISTENERS = 10

    def __init__(self, max_listener: int = DEFAULT_MAX_LISTENERS) -> None:
        self._max_listeners = max_listener
        self._events: DefaultDict[str, list[Listener]] = collections.defaultdict(list)

    def _check_max_listeners(self, event_name: str) -> None:
        if len(self._events.get(event_name, [])) == self._max_listeners:
            raise EventEmitterMaxListenerError

    def _once_wrapper(self, event_name: str, listener: Listener) -> Callable[[], Any]:
        @functools.wraps(listener)
        def wrapper(*args, **kwargs):
            self._remove_listener(event_name, wrapper)
            return listener(*args, **kwargs)

        wrapper.__once_wrapper__ = True

        return wrapper

    def _insert_listener(
        self,
        event_name: str,
        listener: Listener,
        index: int | None = None,
        once: bool = False,
    ) -> None:
        self._check_max_listeners(event_name)

        if once:
            listener = self._once_wrapper(event_name, listener)

        self.emit("new_listener", event_name, listener)

        if index is not None:
            self._events[event_name].insert(index, listener)
        else:
            self._events[event_name].append(listener)

    def _remove_listener(self, event_name: str, listener: Listener) -> None:
        self._events[event_name].remove(listener)

        self.emit("remove_listener", event_name, listener)

    def add_listener(self, event_name: str, listener: Listener) -> "EventEmitter":
        self._insert_listener(event_name, listener)
        return self

    def prepend_listener(self, event_name: str, listener: Listener) -> "EventEmitter":
        self._insert_listener(event_name, listener, 0)
        return self

    def prepend_once_listener(
        self, event_name: str, listener: Listener
    ) -> "EventEmitter":
        self._insert_listener(event_name, listener, 0, once=True)
        return self

    def remove_listener(self, event_name: str, listener: Listener) -> "EventEmitter":
        if event := self._events.get(event_name):
            if listener in event:
                self._remove_listener(event_name, listener)
        return self

    def remove_all_listeners(self, event_name: str | None = None) -> "EventEmitter":
        for event in list(self._events):
            if event_name is None or event_name == event:
                for listener in list(self._events[event]):
                    self._remove_listener(event, listener)
                self._events.pop(event)
        return self

    def on(self, event_name: str, listener: Listener) -> "EventEmitter":
        return self.add_listener(event_name, listener)

    def once(self, event_name: str, listener: Listener) -> "EventEmitter":
        self._insert_listener(event_name, listener, once=True)
        return self

    def off(self, event_name: str, listener: Listener) -> "EventEmitter":
        return self.remove_listener(event_name, listener)

    def emit(self, __event_name: str, *args: Any, **kwargs: Any) -> None:
        for listener in self._events.get(__event_name, []).copy():
            listener(*args, **kwargs)

    def event_names(self) -> list[str]:
        return list(self._events)

    def max_listeners(self) -> int | None:
        return self._max_listeners

    def set_max_listeners(self, value: int) -> "EventEmitter":
        self._max_listeners = value
        return self

    def listeners(self, event_name: str) -> list[Listener]:
        # __wrapped__ added by functools.wraps
        return [
            getattr(func, "__wrapped__", func)
            for func in self.raw_listeners(event_name)
        ]

    def raw_listeners(self, event_name: str) -> list[Listener]:
        return self._events.get(event_name, [])

    def listener_count(self, event_name: str) -> int:
        return len(self._events.get(event_name, []))
