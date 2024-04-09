import { Task, Map } from "./types.js";

export type MessageShowing = {
    show: (message: string) => any;
    setWasShown: (message: string) => any,
    isWasShown: (message: string) => boolean;
}

export type Drawing<MapSurfaceT, TaskSurfaceT> = {
    drawOn: (m: MapSurfaceT, t: TaskSurfaceT) => any,
    redraw: (s: TaskSurfaceT, t: Task) => any,
}

export type Surfaces<MapSurfaceT, TaskSurfaceT> = {
    mapSurfaceOf: (m: Map) => MapSurfaceT | undefined,
    taskSurfaceOn: (s: MapSurfaceT, task_id: number) => TaskSurfaceT | undefined,
    getEmptyTaskSurface: () => TaskSurfaceT,
}
