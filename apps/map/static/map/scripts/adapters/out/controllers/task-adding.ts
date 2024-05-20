import * as base from "./base.js";
import * as facade from "../facade.js";
import * as layout from "../../in/layout.js";
import * as tools from "../../../tools.js";

export class AvailabilityController extends base.StaticController<tools.StorageHTMLElement> {
    constructor(
        view: tools.StorageHTMLElement,
        private _readnessAnimationRootElement: layout.View,
    ) {
        super(view);
    }

    activate() {
        this._view.addEventListener("input", this._handler);
    }

    deactivate() {
        this._view.removeEventListener("input", this._handler);
    }

    private _handler(_: any) {
        facade.handleTaskAddingAvailability(
            (view: layout.Animation) => new StartingController(view, this._view),
            this._readnessAnimationRootElement,
            this._view.value,
        );
    }
}

export class StartingController extends base.StaticController<layout.Animation> {
    constructor(
        view: layout.Animation,
        private _inputDescriptionElement: tools.StorageHTMLElement,
    ) {
        super(view);
    }

    activate() {
        this._view.addEventListener("pointerdown", this._handler);
    }

    deactivate() {
        this._view.removeEventListener("pointerdown", this._handler);
    }

    private _handler(event: PointerEvent) {
        facade.startTaskAdding(
            (view: layout.Animation) => new StartingController(view, this._inputDescriptionElement),
            (view: layout.TaskPrototypeView) => new ContinuationController(view),
            this._view,
            this._inputDescriptionElement,
            event.clientX,
            event.clientY,
        );
    }
}

export class ContinuationController extends base.StaticController<layout.TaskPrototypeView> {
    activate() {
        this._view.addEventListener("pointermove", this._handler);
    }

    deactivate() {
        this._view.removeEventListener("pointermove", this._handler);
    }

    private _handler(event: PointerEvent) {
        facade.continueTaskAdding(event.clientX, event.clientY);
    }
}

export class CompletionController extends base.StaticController<layout.TaskPrototypeView> {
    activate() {
        this._view.addEventListener("pointermove", this._handler);
    }

    deactivate() {
        this._view.removeEventListener("pointermove", this._handler);
    }

    private _handler(event: PointerEvent) {
        facade.completeTaskAdding(event.clientX, event.clientY);
    }
}

