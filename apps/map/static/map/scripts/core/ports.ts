import { Task, TaskPrototype, Map } from "./types.js";

export type Iterable<Value> = {
    [Symbol.iterator](): Iterator<Value>;
}

export type AsyncIterable<Value> = {
    [Symbol.asyncIterator](): AsyncIterator<Value>;
}

export type ShowMessage = (m: string) => any;

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

export type Remote<Value> = Promise<Value | undefined>
export type RemoteIterable<Value> = Promise<AsyncGenerator<Value | undefined> | undefined>

export type RemoteTasks = {
    tasksForMapWithId(id: number): RemoteIterable<Task>,
    createdTaskFrom(p: TaskPrototype, mapId: number): Remote<Task>,
}

export type Log = (m: string) => any;

export type Cursor = {
    setDefault(): void;
    setToGrab(): void;
    setGrabbed(): void;
}
