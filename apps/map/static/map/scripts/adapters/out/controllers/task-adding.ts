import * as base from "./base.js";
import * as facade from "../facade.js";
import * as layout from "../../in/layout.js";

export class AvailabilityControllers extends base.EventListenerControllersForStatic<layout.View> {
    activeFor(view: layout.View) {
        view.addEventListener("input", this._handler);
    }

    removeFrom(view: layout.View) {
        view.removeEventListener("input", this._handler);
    }

    private _handler() {
        facade.handleTaskAddingAvailability();
    }
}

export class StartingControllers extends base.EventListenerControllersForStatic<layout.View> {
    activeFor(view: layout.View) {
        view.addEventListener("pointerdown", this._handler);
    }

    removeFrom(view: layout.View) {
        view.removeEventListener("pointerdown", this._handler);
    }

    private _handler() {
        facade.startTaskAdding(event.clientX, event.clientY);
    }
}

export class ContinuationControllers extends base.EventListenerControllersForStatic<layout.View> {
    activeFor(view: layout.View) {
        document.addEventListener("pointermove", this._handleContinuation);
        view.addEventListener("pointerup", this._handleCompletion);
    }

    removeFrom(view: layout.View) {
        document.removeEventListener("pointermove", this._handleContinuation);
        view.removeEventListener("pointerup", this._handleCompletion);
    }

    private _handleCompletion() {
        facade.completeTaskAdding();
    }

    private handleContinuation(event: PointerEvent) {
        facade.continueTaskAdding(event.clientX, event.clientY);
    }
}
