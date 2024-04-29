import * as ports from "./ports.js";
import * as services from "./services.js";
import { Task, TaskPrototype, Map, Description } from "./types.js";

export namespace maps {
    export type Ports<MapSurface, TaskSurface> = {
        getCurrentMapId: () => number,
        remoteTasks: ports.RemoteTasks,
        show: ports.ShowMessage,
        mapSurfaces: ports.MapSurfaces<MapSurface>,
        taskSurfaces: ports.TaskSurfaces<MapSurface, TaskSurface>,
        drawing: ports.Drawing<MapSurface, TaskSurface, Task>,
        logError: ports.Log,
    }

    export async function draw<MapSurface, TaskSurface>(
        adapters: Ports<MapSurface, TaskSurface>,
    ): Promise<void> {
        let map: Map = {id: adapters.getCurrentMapId()};

        let mapSurface = adapters.mapSurfaces.mapSurfaceOf(map);

        if (mapSurface === undefined) {
            adapters.show("All your tasks could not be displayed.");
            adapters.logError(`Map surface with id = ${map.id} was not found`);
            return;
        }

        let tasks = await adapters.remoteTasks.tasksForMapWithId(map.id);

        if (tasks === undefined) {
            adapters.show("All your tasks could not be displayed.");
            adapters.logError(`Failed to get remote tasks on map with id = ${map.id}`);
            return;
        }

        let numberOfUndisplayedTasks = 0;

        for await (const task of tasks) {
            if (task === undefined) {
                numberOfUndisplayedTasks++;
                continue;
            }

            let taskSurface = adapters.taskSurfaces.taskSurfaceOn(mapSurface, task.id);

            if (taskSurface !== undefined) {
                adapters.drawing.redraw(taskSurface, task);
                continue;
            }

            taskSurface = adapters.taskSurfaces.getEmpty();
            adapters.drawing.redraw(taskSurface, task);
            adapters.drawing.drawOn(mapSurface, taskSurface);
        }

        if (numberOfUndisplayedTasks !== 0) {
            adapters.show("Some of your tasks could not be displayed.");
            adapters.logError(
                `Failed to get ${numberOfUndisplayedTasks} remote tasks`
                + ` from map with id = ${map.id}`
            );
            return;
        }

        return;
    }
}

export namespace taskAdding {
    export enum State { waiting, prepared, active, inCompleting, inPanic }

    export type Ports<MapSurface, TaskPrototypeSurface, TaskSurface> = {
        stateContainer: ports.Container<State>,
        descriptionContainer: ports.Container<Description>,
        taskPrototypeContainer: ports.Container<TaskPrototype>,
        taskPrototypeSurfaceContainer: ports.Container<TaskPrototypeSurface>,
        getCurrentMapId: () => number,
        show: ports.ShowMessage,
        mapSurfaces: ports.MapSurfaces<MapSurface>,
        taskPrototypeSurfaces: ports.TaskPrototypeSurfaces<TaskPrototypeSurface>,
        taskSurfaces: ports.TaskSurfaces<MapSurface, TaskSurface>,
        taskPrototypeDrawing: ports.Drawing<MapSurface, TaskPrototypeSurface, TaskPrototype>,
        taskDrawing: ports.Drawing<MapSurface, TaskSurface, Task>,
        remoteTasks: ports.RemoteTasks,
        logError: ports.Log,
        cursor: ports.Cursor,
    }

    function _panic<MapSurface, TaskPrototypeSurface, TaskSurface>(
        adapters: taskAdding.Ports<MapSurface, TaskPrototypeSurface, TaskSurface>
    ): void {
        adapters.stateContainer.set(State.inPanic);

        adapters.cursor.setDefault();
        adapters.show("Your task could not be added");
    }

    export function prepare<MapSurface, TaskPrototypeSurface, TaskSurface>(
        adapters: taskAdding.Ports<MapSurface, TaskPrototypeSurface, TaskSurface>
    ): void {
        const description = adapters.descriptionContainer.get();

        if (adapters.stateContainer.get() !== State.waiting || description === undefined)
            return;

        adapters.cursor.setGrabbed();
        adapters.stateContainer.set(State.prepared);
    }

    export function start<MapSurface, TaskPrototypeSurface, TaskSurface>(
        x: number,
        y: number,
        adapters: taskAdding.Ports<MapSurface, TaskPrototypeSurface, TaskSurface>
    ): void {
        if (adapters.stateContainer.get() !== State.prepared)
            return;

        let description = services.popFrom(adapters.descriptionContainer);

        if (description === undefined)
            return;

        let map: Map = {id: adapters.getCurrentMapId()};
        let taskPrototype: TaskPrototype = {description: description, x: x, y: y};

        let mapSurface = adapters.mapSurfaces.mapSurfaceOf(map);

        if (mapSurface === undefined) {
            adapters.logError("Map surface does not exist");
            _panic(adapters);
            return;
        }

        let taskPrototypeSurface = adapters.taskPrototypeSurfaces.getEmpty();

        adapters.taskPrototypeContainer.set(taskPrototype)
        adapters.taskPrototypeSurfaceContainer.set(taskPrototypeSurface);

        adapters.taskPrototypeDrawing.redraw(taskPrototypeSurface, taskPrototype);
        adapters.taskPrototypeDrawing.drawOn(mapSurface, taskPrototypeSurface);

        adapters.stateContainer.set(State.active);

        return;
    }

    export function stop<MapSurface, TaskPrototypeSurface, TaskSurface>(
        adapters: taskAdding.Ports<MapSurface, TaskPrototypeSurface, TaskSurface>
    ): void {
        if (adapters.stateContainer.get() !== State.active)
            return;

        let taskPrototype = services.popFrom(adapters.taskPrototypeContainer);
        let taskPrototypeSurface = services.popFrom(adapters.taskPrototypeSurfaceContainer);
        
        services.setDefaultAt(adapters.descriptionContainer, taskPrototype?.description);

        if (taskPrototypeSurface === undefined) {
            adapters.logError("Task prototype surface does not exist");
            _panic(adapters);
            return;
        }

        let map: Map = {id: adapters.getCurrentMapId()};
        let mapSurface = adapters.mapSurfaces.mapSurfaceOf(map);

        if (mapSurface === undefined) {
            adapters.logError(`Surface for map with id = ${map.id} do not exist`);
            _panic(adapters);
            return;
        }

        adapters.taskPrototypeDrawing.eraseFrom(mapSurface, taskPrototypeSurface);

        adapters.stateContainer.set(State.prepared);
    }

    export function cancel<MapSurface, TaskPrototypeSurface, TaskSurface>(
        adapters: taskAdding.Ports<MapSurface, TaskPrototypeSurface, TaskSurface>
    ): void {
        if (adapters.stateContainer.get() !== State.prepared)
            return;

        adapters.cursor.setDefault();
        adapters.stateContainer.set(State.waiting);
    }

    export function handle<MapSurface, TaskPrototypeSurface, TaskSurface>(
        x: number,
        y: number,
        adapters: taskAdding.Ports<MapSurface, TaskPrototypeSurface, TaskSurface>
    ): void {
        if (adapters.stateContainer.get() !== State.active)
            return;

        let taskPrototype = adapters.taskPrototypeContainer.get();
        let taskPrototypeSurface = adapters.taskPrototypeSurfaceContainer.get();

        if (taskPrototype === undefined)
            adapters.logError("Task prototype does not exist");

        if (taskPrototypeSurface === undefined)
            adapters.logError("Task prototype surface does not exist");

        if (taskPrototype === undefined || taskPrototypeSurface === undefined) {
            _panic(adapters);
            return;
        }

        taskPrototype = {...taskPrototype, x: x, y: y};
        adapters.taskPrototypeContainer.set(taskPrototype);

        adapters.taskPrototypeDrawing.redraw(taskPrototypeSurface, taskPrototype);
    }

    export async function complete<MapSurface, TaskPrototypeSurface, TaskSurface>(
        adapters: taskAdding.Ports<MapSurface, TaskPrototypeSurface, TaskSurface>
    ): Promise<void> {
        if (adapters.stateContainer.get() !== State.active)
            return;

        let taskPrototype = adapters.taskPrototypeContainer.get();
        let taskPrototypeSurface = adapters.taskPrototypeSurfaceContainer.get();

        if (taskPrototype === undefined)
            adapters.logError("Task prototype does not exist");

        if (taskPrototypeSurface === undefined)
            adapters.logError("Task prototype surface does not exist");

        if (taskPrototype === undefined || taskPrototypeSurface === undefined) {
            _panic(adapters);
            return;
        }

        let map: Map = {id: adapters.getCurrentMapId()};
        let mapSurface = adapters.mapSurfaces.mapSurfaceOf(map);

        if (mapSurface === undefined) {
            adapters.logError("Map surface does not exist");
            _panic(adapters);
            return;
        }

        adapters.taskPrototypeDrawing.eraseFrom(mapSurface, taskPrototypeSurface);

        let task = await adapters.remoteTasks.createdTaskFrom(taskPrototype, map.id);

        if (task === undefined) {
            adapters.logError(`A remote task on the map with id = ${map.id} could not be created`);
            _panic(adapters);
            return;
        }

        let taskSurface = adapters.taskSurfaces.getEmpty();
        adapters.taskDrawing.redraw(taskSurface, task);
        adapters.taskDrawing.drawOn(mapSurface, taskSurface);

        adapters.stateContainer.set(State.inCompleting);

        adapters.cursor.setToGrab();

        setTimeout(() => _finishCompletion(adapters), 3000);
    }

    function _finishCompletion<MapSurface, TaskPrototypeSurface, TaskSurface>(
        adapters: taskAdding.Ports<MapSurface, TaskPrototypeSurface, TaskSurface>
    ): void {
        if (adapters.stateContainer.get() !== State.inCompleting)
            return;

        adapters.cursor.setDefault();
        adapters.stateContainer.set(State.waiting);
    }
}
