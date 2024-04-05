from act import val
from event_bus import EventBus

from apps.shared import event_bus, mixins, validation, ui, renders


event_bus: EventBus = event_bus.event_bus


mixins = val(Visualizable=mixins.Visualizable)


to_raise_multiple_errors = validation.to_raise_multiple_errors

raise_ = validation.raise_

last = validation.last
latest = validation.latest

same = validation.same
exists = validation.exists


ui = ui
renders = renders
