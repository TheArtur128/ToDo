from act import val
from event_bus import EventBus

from apps.shared import event_bus, mixins


event_bus: EventBus = event_bus.event_bus


mixins = val(Visualizable=mixins.Visualizable)
