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
        x: number,
        y: number,
        originalDescriptionSocket: ports.Socket<string>,
        descriptionTemporarySocket: ports.Socket<string>,
        getCurrentMapId: () => number,
        messageShowing: ports.MessageShowing,
        mapSurfaces: ports.MapSurfaces<MapSurface>,
        taskPrototypeSurfaces: ports.TaskPrototypeSurfaces<TaskPrototypeSurface>,
        drawing: ports.Drawing<MapSurface, TaskPrototypeSurface, TaskPrototype>,
        taskPrototypeSocket: ports.Socket<TaskPrototype>,
        taskPrototypeSurfaceSocket: ports.Socket<TaskPrototypeSurface>,
    ): boolean {
        var description = services.popFrom(originalDescriptionSocket);

        if (description === undefined) {
            services.showErrorMessageOnce(this._errorMessage, messageShowing);
            return false;
        }

        descriptionTemporarySocket.set(description);

        let map: Map = {id: getCurrentMapId()};
        let taskPrototype: TaskPrototype = {description: description, x: x, y: y}

        let mapSurface = mapSurfaces.mapSurfaceOf(map);

        if (mapSurface === undefined) {
            services.showErrorMessageOnce(this._errorMessage, messageShowing);
            return false;
        }

        let taskPrototypeSurface = taskPrototypeSurfaces.getEmpty();

        taskPrototypeSocket.set(taskPrototype)
        taskPrototypeSurfaceSocket.set(taskPrototypeSurface);

        drawing.redraw(taskPrototypeSurface, taskPrototype);
        drawing.drawOn(mapSurface, taskPrototypeSurface);

        return true;
    },

    cancel<MapSurface, TaskPrototypeSurface, TaskPrototype>(
        originalDescriptionSocket: ports.Socket<string>,
        descriptionTemporarySocket: ports.Socket<string>,
        getCurrentMapId: () => number,
        taskPrototypeSocket: ports.Socket<TaskPrototype>,
        taskPrototypeSurfaceSocket: ports.Socket<TaskPrototypeSurface>,
        drawing: ports.Drawing<MapSurface, TaskPrototypeSurface, TaskPrototype>,
        mapSurfaces: ports.MapSurfaces<MapSurface>,
        logger: ports.Logger,
    ): void {
        let originalDescription = descriptionTemporarySocket.get();
        services.setDefaultAt(originalDescriptionSocket, originalDescription);

        taskPrototypeSocket.set(undefined);
        let taskPrototypeSurface = services.popFrom(taskPrototypeSurfaceSocket);

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
        taskPrototypeSocket: ports.Socket<TaskPrototype>,
        taskPrototypeSurfaceSocket: ports.Socket<TaskPrototypeSurface>,
        drawing: ports.Drawing<MapSurface, TaskPrototypeSurface, TaskPrototype>,
    ): boolean {
        let taskPrototype = taskPrototypeSocket.get();
        let taskPrototypeSurface = taskPrototypeSurfaceSocket.get();

        if (taskPrototype === undefined || taskPrototypeSurface === undefined) {
            services.showErrorMessageOnce(this._errorMessage, messageShowing);
            return false;
        }

        taskPrototype = {...taskPrototype, x: x, y: y};
        taskPrototypeSocket.set(taskPrototype);

        drawing.redraw(taskPrototypeSurface, taskPrototype);

        return true;
    },

    async complete<MapSurface, TaskPrototypeSurface, TaskSurface>(
        getCurrentMapId: () => number,
        messageShowing: ports.MessageShowing,
        taskPrototypeSocket: ports.Socket<TaskPrototype>,
        taskPrototypeSurfaceSocket: ports.Socket<TaskPrototypeSurface>,
        taskPrototypeDrawing: ports.Drawing<MapSurface, TaskPrototypeSurface, TaskPrototype>,
        taskDrawing: ports.Drawing<MapSurface, TaskSurface, Task>,
        mapSurfaces: ports.MapSurfaces<MapSurface>,
        taskSurfaces: ports.TaskSurfaces<MapSurface, TaskSurface>,
        remoteTasks: ports.RemoteTasks,
    ): Promise<boolean> {
        let taskPrototype = taskPrototypeSocket.get();
        let taskPrototypeSurface = taskPrototypeSurfaceSocket.get();

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
