import * as ports from "../core/ports.js";
import * as types from "../core/types.js";

export type MapSurface = HTMLDivElement;
export type TaskSurface = HTMLDivElement;
export type TaskPrototypeSurface = HTMLDivElement;

export type TaskDescriptionSurface = HTMLTextAreaElement;

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

export const tasks = {
    _taskDescriptionSurfaceClassName: "task-description",

    surfaces: {
        taskSurfaceOn(mapSurface: MapSurface, task_id: number): TaskSurface | undefined {
            let taskSurface = mapSurface.querySelector(`#${tasks._surfaceIdOf(task_id)}`);

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

            descriptionSurface.className = tasks._taskDescriptionSurfaceClassName;
            descriptionSurface.disabled = true;
            descriptionSurface.maxLength = 128;
            descriptionSurface.rows = 4;
            descriptionSurface.cols = 32;

            return descriptionSurface;
        },
    },

    drawing: <ports.Drawing<MapSurface, TaskSurface, types.Task>>{
        ..._drawingBase,

        redraw(surface: TaskSurface, task: types.Task) {
            surface.id = tasks._surfaceIdOf(task.id);
            surface.style.left = _surfacePositionCoordinateOf(task.x);
            surface.style.top = _surfacePositionCoordinateOf(task.y);

            let query = `.${tasks._taskDescriptionSurfaceClassName}`;
            let descriptionSurface = surface.querySelector(query);

            if (descriptionSurface instanceof HTMLTextAreaElement)
                descriptionSurface.value = task.description;
        }
    },

    _surfaceIdOf(id: number): string {
        return `task-${id}`;
    },
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
