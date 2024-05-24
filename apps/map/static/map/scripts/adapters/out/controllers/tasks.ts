import * as domain from "../../../core/domain.js";
import * as controllers from "../../../core/ports/controllers.js";
import * as facade from "../facade.js";
import * as layout from "../../in/layout.js";

export function modeChangingControllerFor(
    view: layout.TaskView,
    _: domain.Task,
): controllers.Controller {
    const handler = () => facade.changeTaskMode(view);

    let interactionModeView = view.querySelector(".task-interaction-mode");

    if (!(interactionModeView instanceof HTMLDivElement))
        interactionModeView = null;

    return {
        activate: () => interactionModeView?.addEventListener("mouseup", handler),
        deactivate: () => interactionModeView?.removeEventListener("mouseup", handler),
    }
}

export function descriptionChangingControllerFor(
    view: layout.TaskView,
    _: domain.Task,
): controllers.Controller {
    const handler = () => {
        if (!(descriptionView instanceof HTMLTextAreaElement))
            return;

        facade.changeTaskDescription(view, descriptionView.value);
    };

    const descriptionView = view.querySelector(".task-description");

    return {
        activate: () => descriptionView?.addEventListener("input", handler),
        deactivate: () => descriptionView?.removeEventListener("input", handler),
    }
}
