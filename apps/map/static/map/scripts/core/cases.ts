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

enum _TaskAddingState { waiting, prepared, active, inCompleting, inPanic }

export class TaskAdding<MapSurface, TaskPrototypeSurface, TaskSurface> {
    private _state = _TaskAddingState.waiting;

    constructor(
        private _originalDescriptionContainer: ports.Container<string>,
        private _descriptionTemporaryContainer: ports.Container<string>,
        private _taskPrototypeContainer: ports.Container<TaskPrototype>,
        private _taskPrototypeSurfaceContainer: ports.Container<TaskPrototypeSurface>,
        private _getCurrentMapId: () => number,
        private _messageShowing: ports.MessageShowing,
        private _mapSurfaces: ports.MapSurfaces<MapSurface>,
        private _taskPrototypeSurfaces: ports.TaskPrototypeSurfaces<TaskPrototypeSurface>,
        private _taskSurfaces: ports.TaskSurfaces<MapSurface, TaskSurface>,
        private _taskPrototypeDrawing: ports.Drawing<MapSurface, TaskPrototypeSurface, TaskPrototype>,
        private _taskDrawing: ports.Drawing<MapSurface, TaskSurface, Task>,
        private _remoteTasks: ports.RemoteTasks,
        private _errorLogger: ports.Logger,
        private _cursor: ports.Cursor,
    ) {}

    private _panic(): void {
        this._state = _TaskAddingState.inPanic;

        this._cursor.setDefault();
        services.showErrorMessageOnce("Your task could not be added", this._messageShowing);
    }

    prepare(): void {
        if (this._state !== _TaskAddingState.waiting)
            return;

        this._cursor.setGrabbed();
        this._state = _TaskAddingState.prepared;
    }

    start(x: number, y: number): void {
        if (this._state !== _TaskAddingState.prepared)
            return;

        var description = services.popFrom(this._originalDescriptionContainer);

        if (description === undefined)
            return;

        this._descriptionTemporaryContainer.set(description);

        let map: Map = {id: this._getCurrentMapId()};
        let taskPrototype: TaskPrototype = {description: description, x: x, y: y};

        let mapSurface = this._mapSurfaces.mapSurfaceOf(map);

        if (mapSurface === undefined) {
            this._errorLogger.log("Map surface does not exist");
            this._panic();
            return;
        }

        let taskPrototypeSurface = this._taskPrototypeSurfaces.getEmpty();

        this._taskPrototypeContainer.set(taskPrototype)
        this._taskPrototypeSurfaceContainer.set(taskPrototypeSurface);

        this._taskPrototypeDrawing.redraw(taskPrototypeSurface, taskPrototype);
        this._taskPrototypeDrawing.drawOn(mapSurface, taskPrototypeSurface);

        this._state = _TaskAddingState.active;

        return;
    }

    stop(): void {
        if (this._state !== _TaskAddingState.active)
            return;

        let originalDescription = this._descriptionTemporaryContainer.get();
        services.setDefaultAt(this._originalDescriptionContainer, originalDescription);

        this._taskPrototypeContainer.set(undefined);
        let taskPrototypeSurface = services.popFrom(this._taskPrototypeSurfaceContainer);

        if (taskPrototypeSurface === undefined) {
            this._errorLogger.log("Task prototype surface does not exist");
            this._panic();
            return;
        }

        let map: Map = {id: this._getCurrentMapId()};
        let mapSurface = this._mapSurfaces.mapSurfaceOf(map);

        if (mapSurface === undefined) {
            this._errorLogger.log(`Surface for map with id = ${map.id} do not exist`);
            this._panic();
            return;
        }

        this._taskPrototypeDrawing.eraseFrom(mapSurface, taskPrototypeSurface);

        this._state = _TaskAddingState.prepared;
    }

    cancel(): void {
        if (this._state !== _TaskAddingState.prepared)
            return;

        this._cursor.setDefault();
        this._state = _TaskAddingState.waiting;
    }

    handle(x: number, y: number): void {
        if (this._state !== _TaskAddingState.active)
            return;

        let taskPrototype = this._taskPrototypeContainer.get();
        let taskPrototypeSurface = this._taskPrototypeSurfaceContainer.get();

        if (taskPrototype === undefined)
            this._errorLogger.log("Task prototype does not exist");

        if (taskPrototypeSurface === undefined)
            this._errorLogger.log("Task prototype surface does not exist");

        if (taskPrototype === undefined || taskPrototypeSurface === undefined) {
            this._panic();
            return;
        }

        taskPrototype = {...taskPrototype, x: x, y: y};
        this._taskPrototypeContainer.set(taskPrototype);

        this._taskPrototypeDrawing.redraw(taskPrototypeSurface, taskPrototype);
    }

    async complete(): Promise<void> {
        if (this._state !== _TaskAddingState.active)
            return;

        let taskPrototype = this._taskPrototypeContainer.get();
        let taskPrototypeSurface = this._taskPrototypeSurfaceContainer.get();

        if (taskPrototype === undefined)
            this._errorLogger.log("Task prototype does not exist");

        if (taskPrototypeSurface === undefined)
            this._errorLogger.log("Task prototype surface does not exist");

        if (taskPrototype === undefined || taskPrototypeSurface === undefined) {
            this._panic();
            return;
        }

        let map: Map = {id: this._getCurrentMapId()};
        let mapSurface = this._mapSurfaces.mapSurfaceOf(map);

        if (mapSurface === undefined) {
            this._errorLogger.log("Map surface does not exist");
            this._panic();
            return;
        }

        this._taskPrototypeDrawing.eraseFrom(mapSurface, taskPrototypeSurface);

        let task = await this._remoteTasks.createdTaskFrom(taskPrototype, map.id);

        if (task === undefined) {
            this._errorLogger.log(`A remote task on the map with id = ${map.id} could not be created`);
            this._panic();
            return;
        }

        let taskSurface = this._taskSurfaces.getEmpty();
        this._taskDrawing.redraw(taskSurface, task);
        this._taskDrawing.drawOn(mapSurface, taskSurface);

        this._state = _TaskAddingState.inCompleting;

        this._cursor.setToGrab();

        setTimeout(this._finishCompletion, 3000);
    }

    private _finishCompletion(): void {
        if (this._state !== _TaskAddingState.inCompleting)
            return;

        this._cursor.setDefault();
        this._state = _TaskAddingState.waiting;
    }
}
