import { Task, TaskPrototype, Map, Vector } from "./types.js";

export type Iterable<Value> = {
    [Symbol.iterator](): Iterator<Value>;
}

export type AsyncIterable<Value> = {
    [Symbol.asyncIterator](): AsyncIterator<Value>;
}

export type Matching<Key, Value> = {
    matchedWith(key: Key): Value | undefined;
    match(key: Key, value: Value): any;
}

export type ShowMessage = (m: string) => any;

export type StaticDrawing<MapSurface, Surface> = {
    drawOn(m: MapSurface, t: Surface): any,
    eraseFrom(m: MapSurface, s: Surface): any
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
    sizeOf(s: TaskSurface): Vector,
}

export type TaskPrototypeSurfaces<TaskPrototypeSurface> = {
    getEmpty(): TaskPrototypeSurface,
    sizeOf(s: TaskPrototypeSurface): Vector,
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
    updatePosition(task: Task): Promise<boolean>,
    updateDescription(task: Task): Promise<boolean>,
}

export type Log = (m: string) => any;

export type Show = (m: string) => any;

export type HangControllers<Surface> = (s: Surface) => any;

export type Controllers<Surface> = {
    hangOn: HangControllers<Surface>,
    removeFrom: (s: Surface) => any,
}

export type Cursor = {
    setDefault(): any;
    setToGrab(): any;
    setGrabbed(): any;
}
