# Event Emitter

Event emitter for Python. Inspired by https://nodejs.org/dist/latest-v19.x/docs/api/events.html#class-eventemitter.

## Example

```python
from event_emitter import EventEmitter

emitter = EventEmitter()

emitter.on("event", lambda: print("event emitted"))

emitter.emit("event")

# Output: event emitted
```
