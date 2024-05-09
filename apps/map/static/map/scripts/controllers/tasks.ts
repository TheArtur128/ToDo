import * as facade from "../adapters/facade.js";
import * as tools from "../tools.js";

export function initModeChangingControllers(
    taskElement: HTMLDivElement,
    facade: facade.Facade,
): void {
    const buttonElement = taskElement.querySelector(".task-interaction-mode");

    if (buttonElement instanceof HTMLElement)
        buttonElement.addEventListener("mouseup", () => {
            facade.tasks.changeMode(taskElement);
        })
}

export function initDescriptionChangingControllers(
    taskElement: HTMLDivElement,
    facade: facade.Facade,
): void {
    const descriptionInputElement = taskElement.querySelector(".task-description");

    if (descriptionInputElement instanceof HTMLElement)
        descriptionInputElement.addEventListener("input", () => {
            facade.tasks.changeDescription(taskElement);
        })
}

export function initMovingControllers(
    taskElement: HTMLDivElement,
    facade: facade.Facade,
): void {
    const buttonElement = taskElement.querySelector(".task-interaction-mode");
    const moving = facade.taskMovingFor(taskElement);

    if (!(moving !== undefined && buttonElement instanceof HTMLElement))
        return;

    taskElement.addEventListener("pointerenter", () => {
        moving.prepare();
    });

    taskElement.addEventListener("pointerdown", event => {
        if (!tools.isInDOMOf(buttonElement, event.target))
            moving.start(event.clientX, event.clientY);
    });

    taskElement.addEventListener("pointerup", () => {
        moving.cancel();
    });

    taskElement.addEventListener("pointerleave", () => {
        moving.cancel();
    });

    taskElement.addEventListener("pointermove", event => {
        moving.handle(event.clientX, event.clientY);
    });
}

export function initAllControllers(
    taskElement: HTMLDivElement,
    facade: facade.Facade,
) {
    initModeChangingControllers(taskElement, facade);
    initDescriptionChangingControllers(taskElement, facade);
    initMovingControllers(taskElement, facade);
}
