import * as ports from "../core/ports.js";
import * as types from "../core/types.js";

export class MessageShowingWithCachedSearching {
    show: (message: string) => any;
    shownMessages: Set<string>;

    constructor(show: (message: string) => any) {
        this.show = show;
        this.shownMessages = new Set();
    }

    setWasShown(message: string): void {
        this.shownMessages.add(message);
    }

    isWasShown(message: string): boolean {
        return this.shownMessages.has(message);
    }
}

export namespace DOM {
    export type MapSurface = HTMLDivElement;
    export type TaskSurface = HTMLDivElement;
    export type TaskPrototypeSurface = HTMLDivElement;

    export type TaskDescriptionSurface = HTMLTextAreaElement;

    export const taskDescriptionSurfaceClassName = "task-description";

    const _drawingBase = {
        drawOn(mapSurface: MapSurface, surface: HTMLElement) {
            mapSurface.appendChild(surface);
        },

        eraseFrom(mapSurface: MapSurface, surface: TaskPrototypeSurface) {
            try {
                mapSurface.removeChild(surface);
            }
            catch (NotFoundError) {} 
        },
    }

    export const taskDrawing: ports.Drawing<MapSurface, TaskSurface, types.Task> = {
        ..._drawingBase,

        redraw(surface: TaskSurface, task: types.Task) {
            surface.id = DOM._taskSurfaceIdOf(task.id);
            surface.style.left = DOM._taskSurfacePositionCoordinateOf(task.x);
            surface.style.top = DOM._taskSurfacePositionCoordinateOf(task.y);

            let query = `.${DOM.taskDescriptionSurfaceClassName}`;
            let descriptionSurface = surface.querySelector(query);

            if (descriptionSurface instanceof HTMLTextAreaElement)
                descriptionSurface.value = task.description;
        }
    }

    export const taskPrototypeDrawing: ports.Drawing<
        MapSurface,
        TaskPrototypeSurface,
        types.TaskPrototype
    > = {
        ..._drawingBase,

        redraw(surface: TaskPrototypeSurface, taskPrototype: types.TaskPrototype) {
            surface.style.left = DOM._taskSurfacePositionCoordinateOf(taskPrototype.x);
            surface.style.top = DOM._taskSurfacePositionCoordinateOf(taskPrototype.y);
        },
    }

    export const mapSurfacesOf = (mapSurface: MapSurface): ports.MapSurfaces<MapSurface> => {
        return {mapSurfaceOf: _ => mapSurface};
    }

    type TaskSurfaces = (
        ports.TaskSurfaces<MapSurface, TaskSurface>
        & {_getEmptyTaskDescriptionSurface: () => TaskDescriptionSurface}
    )
    export const taskSurfaces: TaskSurfaces = {
        taskSurfaceOn(mapSurface: MapSurface, task_id: number): TaskSurface | undefined {
            let taskSurface = mapSurface.querySelector(`#${DOM._taskSurfaceIdOf(task_id)}`);

            return taskSurface instanceof HTMLDivElement ? taskSurface : undefined
        },

        getEmpty(): TaskSurface {
            let surface = document.createElement('div');
            surface.appendChild(this._getEmptyTaskDescriptionSurface());

            surface.className = "block";
            surface.style.position = "absolute";

            return surface;
        },

        _getEmptyTaskDescriptionSurface(): TaskDescriptionSurface {
            let descriptionSurface = document.createElement("textarea");

            descriptionSurface.className = DOM.taskDescriptionSurfaceClassName;
            descriptionSurface.disabled = true;
            descriptionSurface.maxLength = 128;
            descriptionSurface.rows = 4;
            descriptionSurface.cols = 32;

            return descriptionSurface;
        },
    }

    export const taskPrototypeSurfaces: ports.TaskPrototypeSurfaces<TaskPrototypeSurface> = {
        getEmpty(): TaskPrototypeSurface {
            let surface = document.createElement('div');

            surface.className = "task-prototype";
            surface.style.position = "absolute";

            return surface;
        }
    }

    export class SingleValueContainer<Value> {
        #value: Value | undefined;

        constructor(value: Value | undefined = undefined) {
            this.#value = value;
        }

        set(newValue: Value | undefined) {
            this.#value = newValue;
        }

        get(): Value | undefined {
            return this.#value;
        }
    }

    export const _taskSurfaceIdOf = (id: number): string => {
        return `task-${id}`;
    }

    export const _taskSurfacePositionCoordinateOf = (coordinate: number): string => {
        return `${coordinate}px`;
    }
}
