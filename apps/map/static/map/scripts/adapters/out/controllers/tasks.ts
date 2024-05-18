import * as domain from "../../../core/domain.js";
import * as base from "./base.js";
import * as ports from "../../../core/ports/controllers.js";
import * as facade from "../facade.js";
import * as layout from "../../in/layout.js";
import * as tools from "../../../tools.js";

export class TaskModeChangingControllers extends base.EventListenerControllers<layout.TaskView, domain.Task> {
    root: ports.ControllersFor<layout.TaskView, domain.Task>

    constructor() {
        super();
        this.root = this;
    }

    activeFor(view: layout.TaskView, _: never): void {
        const buttonElement = view.querySelector(".task-interaction-mode");

        if (buttonElement instanceof HTMLElement)
            buttonElement.addEventListener("mouseup", this._handler);
    }

    removeFrom(view: layout.TaskView, _: never): void {
        const buttonElement = view.querySelector(".task-interaction-mode");

        if (buttonElement instanceof HTMLElement)
            buttonElement.removeEventListener("mouseup", this._handler);
    }

    private _handler(event: MouseEvent) {
        if (event.target instanceof HTMLDivElement)
            facade.changeTaskMode(event.target, this.root)
    }
}

export class TaskDescriptionChangingControllers extends base.EventListenerControllers<layout.TaskView, domain.Task> {
    root: ports.ControllersFor<layout.TaskView, domain.Task>

    constructor(private _handlers = new WeakSet()) {
        super();
        this.root = this;
    }

    activeFor(view: layout.TaskView, _: never): void {
        const descriptionView = view.querySelector(".task-description");

        if (!(descriptionView instanceof HTMLTextAreaElement))
            return;

        const handler = new _TaskDescriptionChangingHandler(this, view, descriptionView);

        descriptionView.addEventListener("input", this._handler);
    }

    removeFrom(view: layout.TaskView, _: never): void {
        const descriptionView = view.querySelector(".task-description");

        if (descriptionView instanceof HTMLTextAreaElement)
            descriptionView.removeEventListener("input", this._handler);
    }
}

class _TaskDescriptionChangingHandler {
    constructor(
        private _controllers: TaskDescriptionChangingControllers,
        private _taskView: layout.TaskView,
        private _descriptionView: layout.TaskDescriptionView,
    ) {}

    handle(event: Event) {
        facade.changeTaskDescription(
            this._controllers.root,
            this._taskView,
            this._descriptionView.value,
        );
    }
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
