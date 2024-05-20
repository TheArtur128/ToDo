import * as base from "./base.js";
import * as domain from "../../../core/domain.js";
import * as facade from "../facade.js";
import * as layout from "../../in/layout.js";
import * as tools from "../../../tools.js";
import { Maybe } from "../../../sugar.js";

export class PreparationController extends base.Controller<layout.TaskView, domain.Task> {
    activate(): void {
        this._view.addEventListener("pointerenter", this._handler);
    }

    deactivate(): void {
        this._view.removeEventListener("pointerenter", this._handler);
    }

    private _handler(_: any) {
        facade.prepareTaskMoving(this._view);
    }

    static get factory(): (view: layout.TaskView, value: domain.Task) => PreparationController {
        return (view: layout.TaskView, value: domain.Task) => new PreparationController(
            view,
            value,
        );
    }
}

export class ContinuationController extends base.StaticController<layout.TaskView> {
    activate(): void {
        this._view.addEventListener("pointermove", this._handler);
    }

    deactivate(): void {
        this._view.removeEventListener("pointermove", this._handler);
    }

    private _handler(event: PointerEvent) {
        facade.moveTask(this._view, event.clientX, event.clientY);
    }
}

export class StartingController extends base.Controller<layout.TaskView, domain.Task> {
    private _interactionModeView: Maybe<layout.InteractionModeView> = undefined;

    constructor(view: layout.TaskView, value: domain.Task) {
        super(view, value);

        const _interactionModeView = this._view.querySelector(".task-description");

        if (_interactionModeView instanceof HTMLDivElement)
            this._interactionModeView = _interactionModeView;
    }

    activate(): void {
        this._view.addEventListener("pointerdown", this._handler);
    }

    deactivate(): void {
        this._view.removeEventListener("pointerdown", this._handler);
    }

    private _handler(event: PointerEvent) {
        const isInInteractionModeView = (
            this._interactionModeView !== undefined
            && tools.isInDOMOf(this._interactionModeView, event.target)
        );
        if (isInInteractionModeView)
            return;

        facade.startTaskMoving(
            this._view,
            (view) => new ContinuationController(view),
            event.clientX,
            event.clientY,
        );
    }

    static get factory(): (view: layout.TaskView, value: domain.Task) => StartingController {
        return (view: layout.TaskView, value: domain.Task) => (
            new StartingController(view, value)
        );
    }
}

export class CancellationController extends base.Controller<layout.TaskView, domain.Task> {
    activate(): void {
        this._view.addEventListener("pointerup", this._handler);
        this._view.addEventListener("pointerleave", this._handler);
    }

    deactivate(): void {
        this._view.removeEventListener("pointerup", this._handler);
        this._view.removeEventListener("pointerleave", this._handler);
    }

    private _handler(_: any) {
        facade.cancelTaskMoving(
            this._view,
            (view) => new ContinuationController(view),
        );
    }

    static get factory(): (view: layout.TaskView, value: domain.Task) => CancellationController {
        return (view: layout.TaskView, value: domain.Task) => (
            new CancellationController(view, value)
        );
    }
}
