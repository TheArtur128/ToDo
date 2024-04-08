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


export class DOMRendering {
    mapSurface: MapDOMSurface;

    constructor(mapSurface: MapDOMSurface) {
        this.mapSurface = mapSurface;
    }

    mapOf(_: any): MapDOMSurface {
        return this.mapSurface;
    }

    taskSurfaceOn(mapSurface: MapDOMSurface, task_id: number): TaskDOMSurface | undefined {
        let taskSurface = mapSurface.querySelector(`#${this._taskSurfaceIdOf(task_id)}`);

        return taskSurface instanceof HTMLDivElement ? taskSurface : undefined
    }

    getEmptyTaskSurface(): TaskDOMSurface {
        return document.createElement('div');
    }

    redraw(surface: TaskDOMSurface, task: types.Task): void {
        surface.id = this._taskSurfaceIdOf(task.id);
        surface.className = "task";
        surface.innerText = task.description;

        surface.style.position = "absolute";
        surface.style.left = this._taskSurfacePositionCoordinateOf(task.x);
        surface.style.top = this._taskSurfacePositionCoordinateOf(task.y);
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
}
