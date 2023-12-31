from apps.confirmation import config, services, views


__all__ = ("subjects", "via", "register_for", "open_port_of", "OpeningView")


subjects = config.subjects
activity_minutes = config.activity_minutes

via = services.sendings
register_for = services.endpoint.register_handler_for
open_port_of = services.endpoint.open_for

OpeningView = views.OpeningView
