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
    mapOf: (m: Map) => MapSurfaceT | undefined,
    taskOn: (s: MapSurfaceT, task_id: number) => TaskSurfaceT | undefined,
    getEmptyTask: () => TaskSurfaceT,
}
