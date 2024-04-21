import * as ports from "./ports.js";
import * as services from "./services.js";
import { Task, TaskPrototype, Map } from "./types.js";

export async function drawMap<MapSurface, TaskSurface>(
    getCurrentMapId: () => number,
    remoteTasks: ports.RemoteTasks,
    messageShowing: ports.MessageShowing,
    mapSurfaces: ports.MapSurfaces<MapSurface>,
    taskSurfaces: ports.TaskSurfaces<MapSurface, TaskSurface>,
    drawing: ports.Drawing<MapSurface, TaskSurface, Task>,
): Promise<boolean> {
    let map: Map = {id: getCurrentMapId()};

    let mapSurface = <MapSurface>mapSurfaces.mapSurfaceOf(map);

    if (mapSurface === undefined) {
        messageShowing.show("All your tasks could not be displayed.");
        return false;
    }

    let taskResults = remoteTasks.tasksForMapWithId(map.id);

    let wereTasksLost = false;

    for await (const taskResult of taskResults) {
        if (taskResult === undefined) {
            wereTasksLost = true;
            continue;
        }

        let task = taskResult;

        let taskSurface = taskSurfaces.taskSurfaceOn(mapSurface, task.id);

        if (taskSurface !== undefined) {
            drawing.redraw(taskSurface, task);
            continue;
        }

        taskSurface = taskSurfaces.getEmpty();
        drawing.redraw(taskSurface, task);
        drawing.drawOn(mapSurface, taskSurface);        
    }

    if (wereTasksLost) {
        messageShowing.show("Some of your tasks could not be displayed.");
        return false;
    }

    return true;
}


export const taskAdding = {
    _errorMessage: "Your task could not be added",

    start<MapSurface, TaskPrototypeSurface>(
        x: number,
        y: number,
        originalDescriptionContainer: ports.Container<string>,
        descriptionTemporaryContainer: ports.Container<string>,
        getCurrentMapId: () => number,
        messageShowing: ports.MessageShowing,
        mapSurfaces: ports.MapSurfaces<MapSurface>,
        taskPrototypeSurfaces: ports.TaskPrototypeSurfaces<TaskPrototypeSurface>,
        drawing: ports.Drawing<MapSurface, TaskPrototypeSurface, TaskPrototype>,
        taskPrototypeContainer: ports.Container<TaskPrototype>,
        taskPrototypeSurfaceContainer: ports.Container<TaskPrototypeSurface>,
    ): boolean {
        var description = services.popFrom(originalDescriptionContainer);

        if (description === undefined) {
            services.showErrorMessageOnce(this._errorMessage, messageShowing);
            return false;
        }

        descriptionTemporaryContainer.set(description);

        let map: Map = {id: getCurrentMapId()};
        let taskPrototype: TaskPrototype = {description: description, x: x, y: y}

        let mapSurface = mapSurfaces.mapSurfaceOf(map);

        if (mapSurface === undefined) {
            services.showErrorMessageOnce(this._errorMessage, messageShowing);
            return false;
        }

        let taskPrototypeSurface = taskPrototypeSurfaces.getEmpty();

        taskPrototypeContainer.set(taskPrototype)
        taskPrototypeSurfaceContainer.set(taskPrototypeSurface);

        drawing.redraw(taskPrototypeSurface, taskPrototype);
        drawing.drawOn(mapSurface, taskPrototypeSurface);

        return true;
    },

    cancel<MapSurface, TaskPrototypeSurface, TaskPrototype>(
        originalDescriptionContainer: ports.Container<string>,
        descriptionTemporaryContainer: ports.Container<string>,
        getCurrentMapId: () => number,
        taskPrototypeContainer: ports.Container<TaskPrototype>,
        taskPrototypeSurfaceContainer: ports.Container<TaskPrototypeSurface>,
        drawing: ports.Drawing<MapSurface, TaskPrototypeSurface, TaskPrototype>,
        mapSurfaces: ports.MapSurfaces<MapSurface>,
        logger: ports.Logger,
    ): void {
        let originalDescription = descriptionTemporaryContainer.get();
        services.setDefaultAt(originalDescriptionContainer, originalDescription);

        taskPrototypeContainer.set(undefined);
        let taskPrototypeSurface = services.popFrom(taskPrototypeSurfaceContainer);

        if (taskPrototypeSurface === undefined)
            return;

        let map: Map = {id: getCurrentMapId()};
        let mapSurface = mapSurfaces.mapSurfaceOf(map);

        if (mapSurface === undefined) {
            logger.logMapHasNoSurface(map);
            return;
        }

        drawing.eraseFrom(mapSurface, taskPrototypeSurface);
    },

    handle<MapSurface, TaskPrototypeSurface>(
        x: number,
        y: number,
        messageShowing: ports.MessageShowing,
        taskPrototypeContainer: ports.Container<TaskPrototype>,
        taskPrototypeSurfaceContainer: ports.Container<TaskPrototypeSurface>,
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
        taskPrototypeContainer: ports.Container<TaskPrototype>,
        taskPrototypeSurfaceContainer: ports.Container<TaskPrototypeSurface>,
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
    },
}
