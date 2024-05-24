import * as domain from "../../../core/domain.js";
import * as controllers from "../../../core/ports/controllers.js";
import * as facade from "../facade.js";
import * as layout from "../../in/layout.js";
import * as tools from "../../../tools.js";

export function availabilityControllerFor(
    storageElement: tools.StorageHTMLElement,
    readnessAnimationRootElement: layout.View,
    taskControllerFactories: controllers.ControllerFor<layout.TaskView, domain.Task>[],
): controllers.Controller {
    const handler = () => {
        facade.handleTaskAddingAvailability(
            (animation: layout.Animation) => startingControllerFor(
                animation,
                storageElement,
                taskControllerFactories,
            ),
            readnessAnimationRootElement,
            storageElement.value,
        );
    }

    return {
        activate: () => storageElement.addEventListener("input", handler),
        deactivate: () => storageElement.removeEventListener("input", handler),
    }
}

export function startingControllerFor(
    animation: layout.Animation,
    inputDescriptionElement: tools.StorageHTMLElement,
    taskControllerFactories: controllers.ControllerFor<layout.TaskView, domain.Task>[],
): controllers.Controller {
    const handler = (event: PointerEvent) => facade.startTaskAdding(
        (animation: layout.Animation) => startingControllerFor(
            animation,
            inputDescriptionElement,
            taskControllerFactories,
        ),
        continuationControllerFor,
        (view: layout.TaskPrototypeView) => completionControllerFor(
            view,
            taskControllerFactories
        ),
        animation,
        inputDescriptionElement,
        event.clientX,
        event.clientY,
    );

    return {
        activate: () => animation.addEventListener("pointerdown", handler),
        deactivate: () => animation.removeEventListener("pointerdown", handler),
    }
}

export function continuationControllerFor(
    _: layout.TaskPrototypeView,
): controllers.Controller {
    const handler = (event: PointerEvent) => facade.continueTaskAdding(event.clientX, event.clientY);

    return {
        activate: () => document.addEventListener("pointermove", handler),
        deactivate: () => document.removeEventListener("pointermove", handler),
    }
}

export function completionControllerFor(
    _: layout.TaskPrototypeView,
    taskControllerFactories: controllers.ControllerFor<layout.TaskView, domain.Task>[],
): controllers.Controller {
    const handler = () => facade.completeTaskAdding(
        continuationControllerFor,
        (view: layout.TaskPrototypeView) => completionControllerFor(
            view,
            taskControllerFactories,
        ),
        taskControllerFactories,
    );

    return {
        activate: () => document.addEventListener("pointerup", handler),
        deactivate: () => document.removeEventListener("pointerup", handler),
    }
}
