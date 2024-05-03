import * as facade from "./adapters/facade.js";
import * as tools from "./tools.js";

export function initTaskAddingControllers(
    taskAdding: ReturnType<typeof facade.taskAddingOf>,
    centerElement: HTMLElement,
): void {
    centerElement.addEventListener("mousedown", () => {
        taskAdding.prepare();
    });

    centerElement.addEventListener("mouseleave", event => {
        taskAdding.start(event.clientX, event.clientY);
    });

    centerElement.addEventListener("mouseenter", event => {
        if (event.target === centerElement)
            taskAdding.stop();
    });

    document.addEventListener("mousemove", event => {
        if (!tools.isInDOMOf(centerElement, event.target))
            taskAdding.handle(event.clientX, event.clientY);
    });

    document.addEventListener("mouseup", event => {
        if (tools.isInDOMOf(centerElement, event.target))
            taskAdding.cancel();
        else
            taskAdding.complete();
    });
}

export function initTaskModeChangingControllers(
    taskElement: HTMLDivElement,
    tasks: facade.Tasks,
): void {
    const buttonElement = taskElement.querySelector(".task-interaction-mode");

    if (buttonElement instanceof HTMLElement)
        buttonElement.addEventListener("mouseup", () => {
            tasks.changeMode(taskElement);
        })
}

export function initTaskMovingControllers(
    taskElement: HTMLDivElement,
    tasks: facade.Tasks,
): void {
    const buttonElement = taskElement.querySelector(".task-interaction-mode");
    const moving = tasks.movingFor(taskElement);

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

export function initAllTaskControllers(
    taskElement: HTMLDivElement,
    tasks: facade.Tasks,
) {
    initTaskModeChangingControllers(taskElement, tasks);
    initTaskMovingControllers(taskElement, tasks);
}
