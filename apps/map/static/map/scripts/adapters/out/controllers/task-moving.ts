import * as controllers from "../../../core/ports/controllers.js";
import * as facade from "../facade.js";
import * as layout from "../../in/layout.js";
import * as tools from "../../../tools.js";

export function preparationControllerFor(view: layout.TaskView, _: any): controllers.Controller {
    const handler = () => facade.prepareTaskMoving(view);

    let interactionModeView = view.querySelector(".task-interaction-mode");

    return {
        activate() {
            view.addEventListener("pointerenter", handler);
            interactionModeView?.addEventListener("pointerleave", handler);
        },
        deactivate() {
            view.removeEventListener("pointerenter", handler);
            interactionModeView?.removeEventListener("pointerleave", handler);
        },
    }
}

export function continuationControllerFor(view: layout.TaskView): controllers.Controller {
    const handler = (event: PointerEvent) => facade.moveTask(view, event.clientX, event.clientY);

    return {
        activate: () => view.addEventListener("pointermove", handler),
        deactivate: () => view.removeEventListener("pointermove", handler),
    }
}

export function startingControllerFor(view: layout.TaskView, _: any): controllers.Controller {
    const interactionModeView = view.querySelector(".task-interaction-mode");

    const handler = (event: PointerEvent) => {
        const isInInteractionModeView = (
            interactionModeView instanceof HTMLElement
            && tools.isInDOMOf(interactionModeView, event.target)
        );
        if (isInInteractionModeView)
            return;

        facade.startTaskMoving(
            view,
            continuationControllerFor,
            event.clientX,
            event.clientY,
        );
    }

    return {
        activate: () => view.addEventListener("pointerdown", handler),
        deactivate: () => view.removeEventListener("pointerdown", handler),
    }
}

export function cancellationControllerFor(
    view: layout.TaskView,
    _: any,
): controllers.Controller {
    const handler = () => facade.cancelTaskMoving(view);

    return {
        activate: () => view.addEventListener("pointerleave", handler),
        deactivate: () => view.removeEventListener("pointerleave", handler),
    }
}

export function stoppingControllerFor(
    view: layout.TaskView,
    _: any,
): controllers.Controller {
    const handler = () => facade.stopTaskMoving(view, continuationControllerFor);

    return {
        activate: () => view.addEventListener("pointerup", handler),
        deactivate: () => view.removeEventListener("pointerup", handler),
    }
}
