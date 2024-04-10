import * as ports from "./ports.js";
import * as services from "./services.js";
import { Task, TaskPrototype, Map } from "./types.js";

export async function drawMap<MapSurface, TaskSurface, TaskPrototypeSurface>(
    getCurrentMapId: () => number,
    remoteTasks: ports.RemoteTasks,
    messageShowing: ports.MessageShowing,
    mapSurfaces: ports.MapSurfaces<MapSurface>,
    taskSurfaces: ports.TaskSurfaces<MapSurface, TaskSurface>,
    drawing: ports.Drawing<MapSurface, TaskSurface, Task>,
): Promise<boolean> {
    let map: Map = {id: getCurrentMapId()};

    let tasks = await remoteTasks.tasksForMapWithId(map.id);
    let mapSurface = <MapSurface>mapSurfaces.mapSurfaceOf(map);

    if (mapSurface === undefined || tasks === undefined) {
        services.showErrorMessageOnce(
            "At the moment you are freed from any tasks!",
            messageShowing,
        );

        return false;
    }

    tasks.forEach(task => {
        let taskSurface = taskSurfaces.taskSurfaceOn(mapSurface, task.id);

        if (taskSurface !== undefined) {
            drawing.redraw(taskSurface, task);
            return;
        }

        taskSurface = taskSurfaces.getEmpty();
        drawing.redraw(taskSurface, task);
        drawing.drawOn(mapSurface, taskSurface);        
    });

    return true;
}


export const taskAdding = {
    _errorMessage: "Your task could not be added",

    start<MapSurface, TaskPrototypeSurface>(
        description: string,
        x: number,
        y: number,
        getCurrentMapId: () => number,
        messageShowing: ports.MessageShowing,
        mapSurfaces: ports.MapSurfaces<MapSurface>,
        taskPrototypeSurfaces: ports.TaskPrototypeSurfaces<TaskPrototypeSurface>,
        drawing: ports.Drawing<MapSurface, TaskPrototypeSurface, TaskPrototype>,
        singleTaskPrototypeContainer: ports.SingleValueContainer<TaskPrototype>,
        singleTaskPrototypeSurfaceContainer: ports.SingleValueContainer<TaskPrototypeSurface>,
    ): boolean {
        let map: Map = {id: getCurrentMapId()};
        let taskPrototype: TaskPrototype = {description: description, x: x, y: y}

        let mapSurface = mapSurfaces.mapSurfaceOf(map);

        if (mapSurface === undefined) {
            services.showErrorMessageOnce(this._errorMessage, messageShowing);
            return false;
        }

        let taskPrototypeSurface = taskPrototypeSurfaces.getEmpty();

        singleTaskPrototypeContainer.set(taskPrototype)
        singleTaskPrototypeSurfaceContainer.set(taskPrototypeSurface);

        drawing.redraw(taskPrototypeSurface, taskPrototype);
        drawing.drawOn(mapSurface, taskPrototypeSurface);

        return true;
    },

    handle<MapSurface, TaskPrototypeSurface>(
        x: number,
        y: number,
        messageShowing: ports.MessageShowing,
        taskPrototypeContainer: ports.SingleValueContainer<TaskPrototype>,
        taskPrototypeSurfaceContainer: ports.SingleValueContainer<TaskPrototypeSurface>,
        drawing: ports.Drawing<MapSurface, TaskPrototypeSurface, TaskPrototype>,
    ): boolean {
        let taskPrototype = taskPrototypeContainer.get();
        let taskPrototypeSurface = taskPrototypeSurfaceContainer.get();

        if (taskPrototype === undefined || taskPrototypeSurface === undefined) {
            services.showErrorMessageOnce(this._errorMessage, messageShowing);
            return false;
        }

        taskPrototype = {...taskPrototype, x: x, y: y};
        taskPrototypeContainer.set(taskPrototype);

        drawing.redraw(taskPrototypeSurface, taskPrototype);

        return true;
    },

    async complete<MapSurface, TaskPrototypeSurface, TaskSurface>(
        getCurrentMapId: () => number,
        messageShowing: ports.MessageShowing,
        taskPrototypeContainer: ports.SingleValueContainer<TaskPrototype>,
        taskPrototypeSurfaceContainer: ports.SingleValueContainer<TaskPrototypeSurface>,
        taskPrototypeDrawing: ports.Drawing<MapSurface, TaskPrototypeSurface, TaskPrototype>,
        taskDrawing: ports.Drawing<MapSurface, TaskSurface, Task>,
        mapSurfaces: ports.MapSurfaces<MapSurface>,
        taskSurfaces: ports.TaskSurfaces<MapSurface, TaskSurface>,
        remoteTasks: ports.RemoteTasks,
    ): Promise<boolean> {
        let taskPrototype = taskPrototypeContainer.get();
        let taskPrototypeSurface = taskPrototypeSurfaceContainer.get();

        if (taskPrototype === undefined || taskPrototypeSurface === undefined) {
            services.showErrorMessageOnce(this._errorMessage, messageShowing);
            return false;
        }

        let map: Map = {id: getCurrentMapId()};
        let mapSurface = mapSurfaces.mapSurfaceOf(map);

        if (mapSurface === undefined) {
            services.showErrorMessageOnce(this._errorMessage, messageShowing);
            return false;
        }

        taskPrototypeDrawing.eraseFrom(mapSurface, taskPrototypeSurface);

        let task = await remoteTasks.createdTaskFrom(taskPrototype, map.id);

        if (task === undefined) {
            services.showErrorMessageOnce(this._errorMessage, messageShowing);
            return false;
        }

        let taskSurface = taskSurfaces.getEmpty();
        taskDrawing.redraw(taskSurface, task);
        taskDrawing.drawOn(mapSurface, taskSurface);

        return true;
    }
}
