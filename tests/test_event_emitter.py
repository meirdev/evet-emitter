import functools
import time
from unittest.mock import Mock

import pytest

from event_emitter import EventEmitter, EventEmitterMaxListenerError


def test_add_listener():
    mock = Mock()

    event_emitter = EventEmitter()
    event_emitter.add_listener("test", mock)

    event_emitter.emit("test")
    event_emitter.emit("test")

    assert mock.call_count == 2


def test_prepend_listener():
    mock1 = Mock()
    mock2 = Mock()

    def set_time(m):
        m.return_value = time.time()

    event_emitter = EventEmitter()
    event_emitter.add_listener("test", functools.partial(set_time, mock1))
    event_emitter.prepend_listener("test", functools.partial(set_time, mock2))

    event_emitter.emit("test")

    assert mock1.return_value > mock2.return_value


def test_once_listener():
    mock1 = Mock()
    mock2 = Mock()

    event_emitter = EventEmitter()
    event_emitter.on("test", mock1)
    event_emitter.once("test", mock2)

    event_emitter.emit("test")
    event_emitter.emit("test")

    assert mock1.call_count == 2
    assert mock2.call_count == 1


def test_prepend_once_listener():
    mock1 = Mock()
    mock2 = Mock()

    def set_time(m):
        m()
        m.return_value = time.time()

    event_emitter = EventEmitter()
    event_emitter.add_listener("test", functools.partial(set_time, mock1))
    event_emitter.prepend_once_listener("test", functools.partial(set_time, mock2))

    event_emitter.emit("test")

    assert mock1.return_value > mock2.return_value

    event_emitter.emit("test")

    assert mock1.call_count == 2
    assert mock2.call_count == 1


def test_remove_listener():
    mock = Mock()

    event_emitter = EventEmitter()
    event_emitter.add_listener("test", mock)
    event_emitter.add_listener("test", mock)

    event_emitter.emit("test")

    assert mock.call_count == 2

    event_emitter.remove_listener("test", mock)

    event_emitter.emit("test")

    assert mock.call_count == 3


def test_event_names():
    mock = Mock()

    event_emitter = EventEmitter()
    event_emitter.on("test1", mock)
    event_emitter.on("test2", mock)

    assert event_emitter.event_names() == ["test1", "test2"]


def test_max_listeners():
    event_emitter = EventEmitter()

    assert event_emitter.max_listeners() == 10

    event_emitter.set_max_listeners(5)

    assert event_emitter.max_listeners() == 5


def test_listener_count():
    mock = Mock()

    event_emitter = EventEmitter()
    event_emitter.on("test1", mock)
    event_emitter.on("test1", mock)
    event_emitter.on("test2", mock)

    assert event_emitter.listener_count("test1") == 2


def test_max_listeners_error():
    mock = Mock()

    event_emitter = EventEmitter()

    for _ in range(10):
        event_emitter.on("test", mock)

    with pytest.raises(EventEmitterMaxListenerError):
        event_emitter.on("test", mock)


def test_remove_all_listeners():
    mock = Mock()

    event_emitter = EventEmitter()
    event_emitter.on("test", mock)
    event_emitter.on("test", mock)

    assert event_emitter.listener_count("test") == 2

    event_emitter.remove_all_listeners("test")

    assert event_emitter.listener_count("test") == 0


def test_listeners_and_raw_listeners():
    mock = Mock()

    event_emitter = EventEmitter()
    event_emitter.once("test", mock)
    event_emitter.on("test", mock)

    assert event_emitter.listeners("test") == [mock, mock]

    assert len(event_emitter.raw_listeners("test")) == 2

    assert getattr(event_emitter.raw_listeners("test")[0], "__once_wrapper__", False)
    assert not getattr(event_emitter.raw_listeners("test")[1], "__once_wrapper__", False)


def test_off():
    mock = Mock()

    event_emitter = EventEmitter()
    event_emitter.on("test", mock)
    event_emitter.on("test", mock)

    event_emitter.emit("test")

    assert mock.call_count == 2

    event_emitter.off("test", mock)

    event_emitter.emit("test")

    assert mock.call_count == 3
