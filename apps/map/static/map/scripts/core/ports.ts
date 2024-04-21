import { Task, TaskPrototype, Map } from "./types.js";

export type AsyncIterable<Value> = {
    [Symbol.asyncIterator](): AsyncIterator<Value>;
}

export type MessageShowing = {
    show(message: string): any;
    setWasShown(message: string): any,
    isWasShown(message: string): boolean;
}

export type Drawing<MapSurface, Surface, Value> = {
    drawOn(m: MapSurface, t: Surface): any,
    eraseFrom(m: MapSurface, s: Surface): any
    redraw(s: Surface, t: Value): any,
}

export type MapSurfaces<MapSurface> = {
    mapSurfaceOf(m: Map): MapSurface | undefined,
}

export type TaskSurfaces<MapSurface, TaskSurface> = {
    taskSurfaceOn(s: MapSurface, task_id: number): TaskSurface | undefined,
    getEmpty(): TaskSurface,
}

export type TaskPrototypeSurfaces<TaskPrototypeSurface> = {
    getEmpty(): TaskPrototypeSurface,
}

export type Container<Value> = {
    set(v: Value | undefined): any,
    get(): Value | undefined,
}

export type RemoteTasks = {
    tasksForMapWithId(id: number): AsyncIterable<Task | undefined>,
    createdTaskFrom(p: TaskPrototype, mapId: number): Promise<Task | undefined>,
}

export type Logger = {
    logMapHasNoSurface(m: Map): any;
}
