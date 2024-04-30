import * as ports from "../core/ports.js";
import * as types from "../core/types.js";

export type MapSurface = HTMLDivElement;
export type TaskSurface = HTMLDivElement;
export type TaskPrototypeSurface = HTMLDivElement;

export type TaskDescriptionSurface = HTMLTextAreaElement;
export type InteractionModeSurface = HTMLDivElement;

const _drawingBase = {
    drawOn(mapSurface: MapSurface, surface: HTMLElement) {
        mapSurface.appendChild(surface);
    },

    eraseFrom(mapSurface: MapSurface, surface: HTMLElement) {
        try {
            mapSurface.removeChild(surface);
        }
        catch (NotFoundError) {} 
    },
}

export namespace tasks {
    const _descriptionSurfaceClassName = "task-description";
    const _interactionModeSurfaceClassName = "task-interaction-mode";

    export const surfaces = {
        taskSurfaceOn(mapSurface: MapSurface, task_id: number): TaskSurface | undefined {
            let taskSurface = mapSurface.querySelector(`#${_surfaceIdOf(task_id)}`);

            return taskSurface instanceof HTMLDivElement ? taskSurface : undefined
        },

        getEmpty(): TaskSurface {
            let surface = document.createElement('div');
            surface.appendChild(this._getEmptyTaskDescriptionSurface());
            surface.appendChild(this._getEmptyInteractionModeSurface());

            surface.className = "block";
            surface.style.position = "absolute";

            return surface;
        },

        _getEmptyTaskDescriptionSurface(): TaskDescriptionSurface {
            let descriptionSurface = document.createElement("textarea");

            descriptionSurface.className = _descriptionSurfaceClassName;
            descriptionSurface.disabled = true;
            descriptionSurface.maxLength = 128;
            descriptionSurface.rows = 4;
            descriptionSurface.cols = 32;

            return descriptionSurface;
        },

        _getEmptyInteractionModeSurface(): InteractionModeSurface {
            const interactionModeSurface = document.createElement("div");

            interactionModeSurface.className = _interactionModeSurfaceClassName;

            return interactionModeSurface;
        },
    }

    export const drawing: ports.Drawing<MapSurface, TaskSurface, types.Task> = {
        ..._drawingBase,

        redraw(surface: TaskSurface, task: types.Task) {
            surface.id = _surfaceIdOf(task.id);
            surface.style.left = _surfacePositionCoordinateOf(task.x);
            surface.style.top = _surfacePositionCoordinateOf(task.y);

            const descriptionSurface = surface.querySelector(
                `.${_descriptionSurfaceClassName}`
            );

            const interactionModeSurface = surface.querySelector(
                `.${_interactionModeSurfaceClassName}`
            );

            if (descriptionSurface instanceof HTMLTextAreaElement)
                descriptionSurface.value = task.description.value;

            if (interactionModeSurface instanceof HTMLDivElement)
                interactionModeSurface.replaceChildren(_imageElementOf(task.mode));
        }
    }

    function _surfaceIdOf(id: number): string {
        return `task-${id}`;
    }

    function _imageElementOf(mode: types.InteractionMode): HTMLImageElement {
        const element = document.createElement("img");

        if (mode === types.InteractionMode.editing) {
            element.src = "/static/map/images/editing-mode.png";
            element.width = 10;
            element.height = 10;
        }
        else if (mode === types.InteractionMode.moving) {
            element.src = "/static/map/images/moving-mode.png";
            element.width = 12;
            element.height = 12;
        }

        return element
    }
}

export const taskPrototypes = {
    surfaces: <ports.TaskPrototypeSurfaces<TaskPrototypeSurface>>{
        getEmpty(): TaskPrototypeSurface {
            let surface = document.createElement('div');

            surface.className = "task-prototype";
            surface.style.position = "absolute";

            return surface;
        }
    },

    drawing: <ports.Drawing<MapSurface, TaskPrototypeSurface, types.TaskPrototype>>{
        ..._drawingBase,

        redraw(surface: TaskPrototypeSurface, taskPrototype: types.TaskPrototype) {
            surface.style.left = _surfacePositionCoordinateOf(taskPrototype.x);
            surface.style.top = _surfacePositionCoordinateOf(taskPrototype.y);
        },
    },
}

export const maps = {
    surfacesOf(mapSurface: MapSurface): ports.MapSurfaces<MapSurface> {
        return {mapSurfaceOf: _ => mapSurface};
    },
}

export const cursor: ports.Cursor = {
    setDefault(): void {
        _setGlobalStyleProperty("cursor", '', '');
    },

    setToGrab(): void {
        _setGlobalStyleProperty("cursor", "grab", "important");
    },

    setGrabbed(): void {
        _setGlobalStyleProperty("cursor", "grabbing", "important");
    },
}

function _setGlobalStyleProperty(property: string, value: string | null, priority?: string): void {
    document.querySelectorAll('*').forEach(element => {
        if (!(element instanceof HTMLElement))
            return;

        element.style.setProperty(property, value, priority);
    })
}

function _surfacePositionCoordinateOf(coordinate: number): string {
    return `${coordinate}px`;
}
