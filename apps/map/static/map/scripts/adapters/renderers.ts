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

export type MapDOMSurface = HTMLDivElement;
export type TaskDOMSurface = HTMLDivElement;

type TaskDescriptionDOMSurface = HTMLTextAreaElement;

export class DOMRendering {
    mapSurface: MapDOMSurface;
    taskDescriptionSurfaceClassName = "task-description";

    constructor(mapSurface: MapDOMSurface) {
        this.mapSurface = mapSurface;
    }

    mapSurfaceOf(_: any): MapDOMSurface {
        return this.mapSurface;
    }

    taskSurfaceOn(mapSurface: MapDOMSurface, task_id: number): TaskDOMSurface | undefined {
        let taskSurface = mapSurface.querySelector(`#${this._taskSurfaceIdOf(task_id)}`);

        return taskSurface instanceof HTMLDivElement ? taskSurface : undefined
    }

    getEmptyTaskSurface(): TaskDOMSurface {
        let surface = document.createElement('div');
        surface.appendChild(this._getEmptyTaskDescriptionSurface());

        surface.className = "block";
        surface.style.position = "absolute";

        return surface;
    }

    redraw(surface: TaskDOMSurface, task: types.Task): void {
        surface.id = this._taskSurfaceIdOf(task.id);
        surface.style.left = this._taskSurfacePositionCoordinateOf(task.x);
        surface.style.top = this._taskSurfacePositionCoordinateOf(task.y);

        let query = `.${this.taskDescriptionSurfaceClassName}`;
        let descriptionSurface = surface.querySelector(query);

        if (descriptionSurface instanceof HTMLTextAreaElement)
            descriptionSurface.value = task.description;
    }

    drawOn(mapSurface: MapDOMSurface, taskSurface: TaskDOMSurface): void {
        mapSurface.appendChild(taskSurface);
    }

    _taskSurfaceIdOf(id: number): string {
        return `task-${id}`;
    }

    _taskSurfacePositionCoordinateOf(coordinate: number): string {
        return `${coordinate}px`;
    }

    _getEmptyTaskDescriptionSurface(): HTMLTextAreaElement {
        let descriptionSurface = document.createElement("textarea");

        descriptionSurface.className = this.taskDescriptionSurfaceClassName;
        descriptionSurface.disabled = true;
        descriptionSurface.maxLength = 128;
        descriptionSurface.rows = 4;
        descriptionSurface.cols = 32;

        return descriptionSurface;
    }
}
