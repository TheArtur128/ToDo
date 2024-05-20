import * as domain from "../../../core/domain.js";
import * as controllers from "../../../core/ports/controllers.js";
import * as base from "./base.js";
import * as facade from "../facade.js";
import * as layout from "../../in/layout.js";
import * as tools from "../../../tools.js";

export class AvailabilityController extends base.StaticController<tools.StorageHTMLElement> {
    constructor(
        view: tools.StorageHTMLElement,
        private _readnessAnimationRootElement: layout.View,
        private _taskControllerFactories: controllers.ControllerFor<layout.TaskView, domain.Task>[],
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
            (animation: layout.Animation) => new StartingController(
                animation,
                this._view,
                this._taskControllerFactories,
            ),
            this._readnessAnimationRootElement,
            this._view.value,
        );
    }
}

export class StartingController extends base.StaticController<layout.Animation> {
    constructor(
        view: layout.Animation,
        private _inputDescriptionElement: tools.StorageHTMLElement,
        private _taskControllerFactories: controllers.ControllerFor<layout.TaskView, domain.Task>[],
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
            (animation: layout.Animation) => new StartingController(
                animation,
                this._inputDescriptionElement,
                this._taskControllerFactories,
            ),
            (view: layout.TaskPrototypeView) => new ContinuationController(view),
            (view: layout.TaskPrototypeView) => new CompletionController(
                view,
                this._taskControllerFactories
            ),
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
    constructor(
        view: layout.TaskPrototypeView,
        private _taskControllerFactories: controllers.ControllerFor<layout.TaskView, domain.Task>[]
    ) {
        super(view);
    }

    activate() {
        this._view.addEventListener("pointermove", this._handler);
    }

    deactivate() {
        this._view.removeEventListener("pointermove", this._handler);
    }

    private _handler(_: any) {
        facade.completeTaskAdding(
            (view: layout.TaskPrototypeView) => new ContinuationController(view),
            this._taskControllerFactories,
        );
    }
}
