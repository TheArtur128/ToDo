from act import val
from event_bus import EventBus

from apps.shared import event_bus, mixins, validation


event_bus: EventBus = event_bus.event_bus


mixins = val(Visualizable=mixins.Visualizable)


to_raise_multiple_errors = validation.to_raise_multiple_errors
last = validation.last
latest = validation.latest

same = validation.same
exists = validation.exists
