import * as views from "../../core/ports/views.js";
import * as domain from "../../core/domain.js";
import { Maybe } from "../../sugar.js";

export type View = HTMLElement;
export type MapView = HTMLDivElement;
export type TaskView = HTMLDivElement;
export type TaskPrototypeView = HTMLDivElement;

export type TaskDescriptionView = HTMLTextAreaElement;
export type InteractionModeView = HTMLDivElement;
export type Animation = HTMLImageElement;

export const staticPresenter = {
    drawOn<RootView extends View>(rootView: RootView, view: View): void {
        rootView.appendChild(view);
    },

    eraseFrom<RootView extends View>(rootView: RootView, view: View): void {
        try {
            rootView.removeChild(view);
        }
        catch (NotFoundError) {}
    },
}
const _staticPresenter = staticPresenter;

export class LazyStaticPresenter implements views.StaticPresenter<View, View> {
    private _drawnViewsInDOM: Set<View>;

    constructor() {
        this._drawnViewsInDOM = new Set();
    }

    drawOn(rootView: View, view: View): void {
        if (this._drawnViewsInDOM.has(view))
            view.hidden = false;
        else {
            rootView.appendChild(view);
            this._drawnViewsInDOM.add(view);
        }
    }

    eraseFrom(_: View, view: View): void {
        view.hidden = true;
    }
}

const _baseOfVisibleViews = {
    sizeOf(view: View): domain.Vector {
        const rect = view.getBoundingClientRect()

        return new domain.Vector(rect.width, rect.height);
    }
}

export namespace taskAdding {
    export function createReadinessAnimation(): Animation {
        const element = document.createElement("img");
        element.id = "readiness-animation-of-task-adding";
        element.src = "/static/map/animations/ready-to-add.gif";

        element.addEventListener('dragstart', event => event.preventDefault());

        return element;
    }
}

export namespace tasks {
    const _descriptionViewClassName = "task-description";
    const _interactionModeViewClassName = "task-interaction-mode";

    export const views = {
        sizeOf(_: any): domain.Vector {
            return new domain.Vector(255, 124);
        },

        foundViewOn(mapView: MapView, task: domain.Task): Maybe<TaskView> {
            const view = mapView.querySelector(`#${_viewIdOf(task.id)}`);

            return view instanceof HTMLDivElement ? view : undefined
        },

        createEmptyView(): TaskView {
            let view = document.createElement('div');
            view.appendChild(this._getEmptyTaskDescriptionView());
            view.appendChild(this._getEmptyInteractionModeView());

            view.className = "task";
            view.style.position = "absolute";

            return view;
        },

        _getEmptyTaskDescriptionView(): TaskDescriptionView {
            let descriptionView = document.createElement("textarea");

            descriptionView.className = _descriptionViewClassName;
            descriptionView.maxLength = 128;
            descriptionView.rows = 4;
            descriptionView.cols = 32;

            return descriptionView;
        },

        _getEmptyInteractionModeView(): InteractionModeView {
            const view = document.createElement("div");
            view.className = _interactionModeViewClassName;

            view.appendChild(document.createElement("img"));

            return view;
        },
    }

    export const presenter = {
        ..._staticPresenter,

        redrawBy(task: domain.Task, view: TaskView): void {
            view.id = _viewIdOf(task.id);
            view.style.left = _inStyleUnits(task.x);
            view.style.top = _inStyleUnits(task.y);

            const descriptionView = view.querySelector(
                `.${_descriptionViewClassName}`
            );

            const interactionModeView = view.querySelector(
                `.${_interactionModeViewClassName}`
            );

            if (descriptionView instanceof HTMLTextAreaElement)
                this._redrawDescriptionView(descriptionView, task);

            if (interactionModeView instanceof HTMLDivElement)
                this._redrawInteractionModeView(interactionModeView, task);
        },

        _redrawDescriptionView(
            descriptionView: HTMLTextAreaElement,
            task: domain.Task,
        ): void {
            descriptionView.value = task.description.value;
            descriptionView.disabled = task.mode !== domain.InteractionMode.editing;
        },

        _redrawInteractionModeView(
            interactionModeView: InteractionModeView,
            task: domain.Task,
        ): void {
            const imageElement = interactionModeView.querySelector("img");

            if (imageElement === null)
                return;

            if (task.mode === domain.InteractionMode.editing) {
                imageElement.src = "/static/map/images/editing-mode.png";
                imageElement.width = 10;
                imageElement.height = 10;
            }
            else if (task.mode === domain.InteractionMode.moving) {
                imageElement.src = "/static/map/images/moving-mode.png";
                imageElement.width = 12;
                imageElement.height = 12;
            }
        }
    }

    export const modeChangingPresenter = {
        ...presenter,

        redrawBy(task: domain.Task, view: TaskView): void {
            presenter.redrawBy(task, view);
            _cursorFor(view).setDefault();
        }
    }

    export const movementPresenter = {
        redrawBy(_: domain.Task, view: TaskView): void {
            _cursorFor(view).setGrabbed();
        },
    }

    export const readyToMovePresenter = {
        redrawBy(_: domain.Task, view: TaskView): void {
            _cursorFor(view).setToGrab();
        },
    }

    export const staticPresenter = {
        redrawBy(_: domain.Task, view: TaskView): void {
            _cursorFor(view).setDefault();
        },
    }

    function _cursorFor(taskView: TaskView): _LocalCursor {
        let query = `.${_descriptionViewClassName}`;
        const descriptionView = taskView.querySelector(query);

        if (descriptionView instanceof HTMLElement)
            return new _LocalCursor(taskView, descriptionView);
        else
            return new _LocalCursor(taskView);
    }

    function _viewIdOf(id: number): string {
        return `task-${id}`;
    }
}

export namespace taskPrototypes {
    export const views: views.Views<TaskPrototypeView> = {
        ..._baseOfVisibleViews,

        createEmptyView(): TaskPrototypeView {
            const view = document.createElement('div');
            view.className = "task-prototype";

            return view;
        },
    }

    export const presenter: views.Presenter<MapView, TaskPrototypeView, domain.TaskPrototype> = {
        ...staticPresenter,

        redrawBy(taskPrototype: domain.TaskPrototype, view: TaskPrototypeView): void {
            view.style.left = _inStyleUnits(taskPrototype.x);
            view.style.top = _inStyleUnits(taskPrototype.y);
        },
    }
}

export namespace maps {
    export const views: views.Views<MapView> = {
        ..._baseOfVisibleViews,

        createEmptyView(): MapView {
            const view = document.createElement('div');
            view.id = "tasks";

            return view;
        },
    }

    export const presenter = {
        ...staticPresenter,

        drawOn<RootView extends View>(rootView: RootView, view: MapView): void {
            rootView.insertBefore(view, rootView.firstChild);
        },

        redrawBy(_: domain.Map, __: MapView): void {}
    }
}

class _LocalCursor {
    private _elements: HTMLElement[];

    constructor(...elements: HTMLElement[]) {
        this._elements = elements;
    }

    setDefault(): void {
        this._elements.forEach(element => {
            element.style.setProperty("cursor", '', '');
        });
    }

    setToGrab(): void {
        this._elements.forEach(element => {
            element.style.setProperty("cursor", "grab", "important");
        });
    }

    setGrabbed(): void {
        this._elements.forEach(element => {
            element.style.setProperty("cursor", "grabbing", "important");
        });
    }
}

function _inStyleUnits(coordinate: number): string {
    return `${coordinate}px`;
}
