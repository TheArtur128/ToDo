import * as base from "./base.js";
import * as domain from "../../../core/domain.js";
import * as facade from "../facade.js";
import * as layout from "../../in/layout.js";
import { Maybe } from "../../../sugar.js";

export class TaskModeChangingController extends base.Controller<layout.TaskView, domain.Task> {
    private _interactionModeView: Maybe<layout.InteractionModeView> = undefined;

    constructor(view: layout.TaskView, value: domain.Task) {
        super(view, value);

        const _interactionModeView = this._view.querySelector(".task-description");

        if (_interactionModeView instanceof HTMLDivElement)
            this._interactionModeView = _interactionModeView;
    }

    activate(): void {
        this._interactionModeView?.addEventListener("mouseup", this._handler);
    }

    deactivate(): void {
        this._interactionModeView?.removeEventListener("mouseup", this._handler);
    }

    private _handler(_: MouseEvent) {
        facade.changeTaskMode(this._view);
    }

    static get factory(): (view: layout.TaskView, value: domain.Task) => TaskModeChangingController {
        return (view: layout.TaskView, value: domain.Task) => (
            new TaskModeChangingController(view, value)
        );
    }
}

export class TaskDescriptionChangingController extends base.Controller<layout.TaskView, domain.Task> {
    private _descriptionView: Maybe<layout.TaskDescriptionView> = undefined;

    constructor(view: layout.TaskView, value: domain.Task) {
        super(view, value);

        const descriptionView = this._view.querySelector(".task-description");

        if (descriptionView instanceof HTMLTextAreaElement)
            this._descriptionView = descriptionView;
    }

    activate(): void {
        this._descriptionView?.addEventListener("input", this._handler);
    }

    deactivate(): void {
        this._descriptionView?.removeEventListener("input", this._handler);
    }

    private _handler(_: Event) {
        if (this._descriptionView === undefined)
            return;

        facade.changeTaskDescription(this._view, this._descriptionView.value);
    }

    static get factory(): (view: layout.TaskView, value: domain.Task) => TaskDescriptionChangingController {
        return (view: layout.TaskView, value: domain.Task) => (
            new TaskDescriptionChangingController(view, value)
        );
    }
}
