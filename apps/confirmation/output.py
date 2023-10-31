from apps.confirmation import config, input, services, views


__all__ = ("subjects", "via", "register_for", "open_port_of", "OpeningView")


subjects = config.subjects
activity_minutes = input.activity_minutes

via = services.via
register_for = services.register_for
open_port_of = services.open_port_of

OpeningView = views.OpeningView
