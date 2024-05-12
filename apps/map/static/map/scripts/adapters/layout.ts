import * as views from "../core/ports/views.js";
import * as types from "../core/types.js";
import { Maybe, Dirty } from "../fp.js";

export type View = HTMLElement;
export type MapView = HTMLDivElement;
export type TaskView = HTMLDivElement;
export type TaskPrototypeView = HTMLDivElement;

export type TaskDescriptionView = HTMLTextAreaElement;
export type InteractionModeView = HTMLDivElement;
export type Animation = HTMLImageElement;

export const staticDrawing = {
    withDrawn<RootView extends View>(view: View, rootView: RootView): RootView {
        rootView.appendChild(view);
        return rootView;
    },

    withErased<RootView extends View>(view: View, rootView: RootView): RootView {
        try {
            rootView.removeChild(view);
        }
        catch (NotFoundError) {}

        return rootView;
    },
}

export class LazyStaticDrawing implements views.StaticDrawing<MapView, HTMLElement> {
    private _drawnViewsInDOM: Set<HTMLElement>;

    constructor() {
        this._drawnViewsInDOM = new Set();
    }

    withDrawn<RootView extends View>(view: View, rootView: RootView): Dirty<RootView> {
        if (this._drawnViewsInDOM.has(view))
            view.hidden = false;
        else {
            rootView.appendChild(view);
            this._drawnViewsInDOM.add(view);
        }

        return rootView;
    }

    withErased<RootView extends View>(view: View, rootView: RootView): Dirty<RootView> {
        view.hidden = true;
        return rootView;
    }
}

const _baseVisibleViews = {
    sizeOf(view: View): types.Vector {
        const rect = view.getBoundingClientRect()

        return new types.Vector(rect.width, rect.height);
    }
}

export namespace taskAdding {
    export function createReadinessAnimation(): Dirty<Animation> {
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
        sizeOf(_: any): types.Vector {
            return new types.Vector(255, 124);
        },

        foundViewOn(mapView: MapView, task: types.Task): Dirty<Maybe<TaskView>> {
            const view = mapView.querySelector(`#${_viewIdOf(task.id)}`);

            return view instanceof HTMLDivElement ? view : undefined
        },

        get emptyView(): TaskView {
            let view = document.createElement('div');
            view.appendChild(this._getEmptyTaskDescriptionView());
            view.appendChild(this._getEmptyInteractionModeView());

            view.className = "block";
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

    export const drawing = {
        ...staticDrawing,

        redrawnBy(task: types.Task, view: TaskView): Dirty<TaskView> {
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

            return view;
        },

        _redrawDescriptionView(
            descriptionView: HTMLTextAreaElement,
            task: types.Task,
        ): void {
            descriptionView.value = task.description.value;
            descriptionView.disabled = task.mode !== types.InteractionMode.editing;
        },

        _redrawInteractionModeView(
            interactionModeView: InteractionModeView,
            task: types.Task,
        ): void {
            const imageElement = interactionModeView.querySelector("img");

            if (imageElement === null)
                return;

            if (task.mode === types.InteractionMode.editing) {
                imageElement.src = "/static/map/images/editing-mode.png";
                imageElement.width = 10;
                imageElement.height = 10;
            }
            else if (task.mode === types.InteractionMode.moving) {
                imageElement.src = "/static/map/images/moving-mode.png";
                imageElement.width = 12;
                imageElement.height = 12;
            }
        }
    }

    export function cursorFor(taskView: TaskView): Dirty<Maybe<LocalCursor>> {
        let query = `.${_descriptionViewClassName}`;
        const descriptionView = taskView.querySelector(query);

        if (descriptionView instanceof HTMLElement)
            return new LocalCursor(taskView, descriptionView);
    }

    function _viewIdOf(id: number): string {
        return `task-${id}`;
    }
}

export namespace taskPrototypes {
    export const views: views.Views<TaskPrototypeView> = {
        ..._baseVisibleViews,

        get emptyView(): TaskPrototypeView {
            const view = document.createElement('div');
            view.className = "task-prototype";

            return view;
        },
    }

    export const drawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype> = {
        ...staticDrawing,

        redrawnBy(
            taskPrototype: types.TaskPrototype,
            view: TaskPrototypeView,
        ): Dirty<TaskPrototypeView> {
            view.style.left = _inStyleUnits(taskPrototype.x);
            view.style.top = _inStyleUnits(taskPrototype.y);

            return view;
        },
    }
}

export namespace maps {
    export const views: views.Views<MapView> = {
        ..._baseVisibleViews,

        get emptyView(): MapView {
            const view = document.createElement('div');
            view.id = "tasks";

            return view;
        },
    }

    export const drawing = {
        ...staticDrawing,

        withDrawn<RootView extends View>(view: MapView, rootView: RootView): RootView {
            rootView.insertBefore(view, rootView.firstChild);
            return rootView;
        },

        redrawnBy(_: types.Map, view: MapView): MapView {
            return view;
        }
    }
}

export const globalCursor: views.Cursor = {
    asDefault(): Dirty<typeof this> {
        _setGlobalStyleProperty("cursor", '', '');
        return this;
    },

    toGrab(): Dirty<typeof this> {
        _setGlobalStyleProperty("cursor", "grab", "important");
        return this;
    },

    asGrabbed(): Dirty<typeof this> {
        _setGlobalStyleProperty("cursor", "grabbing", "important");
        return this;
    },
}

export class LocalCursor implements views.Cursor {
    private _elements: HTMLElement[];

    constructor(...elements: HTMLElement[]) {
        this._elements = elements;
    }

    asDefault(): Dirty<typeof this> {
        this._elements.forEach(element => {
            element.style.setProperty("cursor", '', '');
        });
        return this;
    }

    toGrab(): Dirty<typeof this> {
        this._elements.forEach(element => {
            element.style.setProperty("cursor", "grab", "important");
        });
        return this;
    }

    asGrabbed(): Dirty<typeof this> {
        this._elements.forEach(element => {
            element.style.setProperty("cursor", "grabbing", "important");
        });
        return this;
    }
}

function _setGlobalStyleProperty(property: string, value: string | null, priority?: string): void {
    document.querySelectorAll('*').forEach(element => {
        if (!(element instanceof HTMLElement))
            return;

        element.style.setProperty(property, value, priority);
    })
}

function _inStyleUnits(coordinate: number): string {
    return `${coordinate}px`;
}
