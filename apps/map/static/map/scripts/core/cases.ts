import * as ports from "./ports.js";
import * as services from "./services.js";
import { Task, TaskPrototype, Map, Description, InteractionMode, Vector } from "./types.js";

export namespace maps {
    export type Ports<MapSurface, TaskSurface> = {
        getCurrentMapId: () => number,
        remoteTasks: ports.RemoteTasks,
        show: ports.ShowMessage,
        mapSurfaces: ports.MapSurfaces<MapSurface>,
        taskSurfaces: ports.TaskSurfaces<MapSurface, TaskSurface>,
        drawing: ports.Drawing<MapSurface, TaskSurface, Task>,
        logError: ports.Log,
        tasks: ports.Matching<TaskSurface, Task>,
        hangControllersOn: ports.HangControllers<TaskSurface>;
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
            taskSurface = services.renderOn(
                mapSurface, taskSurface, task, adapters.taskSurfaces, adapters.drawing
            );

            adapters.hangControllersOn(taskSurface);
            adapters.tasks.match(taskSurface, task);
        }

        if (numberOfUndisplayedTasks !== 0) {
            adapters.show("Some of your tasks could not be displayed.");
            adapters.logError(
                `Failed to get ${numberOfUndisplayedTasks} remote tasks`
                + ` from map with id = ${map.id}`
            );
        }
    }
}

export namespace tasks {
    export type Ports<MapSurface, TaskSurface> = {
        tasks: ports.Matching<TaskSurface, Task>,
        drawing: ports.Drawing<MapSurface, TaskSurface, Task>
        logError: ports.Log,
    }

    export function changeMode<MapSurface, TaskSurface>(
        adapters: Ports<MapSurface, TaskSurface>,
        taskSurface: TaskSurface,
    ): void {
        const task = adapters.tasks.matchedWith(taskSurface);

        if (task === undefined) {
            adapters.logError("No matching between task and surface");
            return;
        }

        task.changeMode();
        adapters.drawing.redraw(taskSurface, task);
    }
}

export namespace taskMoving {
    export type Ports<MapSurface, TaskSurface> = {
        referencePointContainer: ports.Container<Vector>,
        activationContainer: ports.Container<true>,
        remoteFixationTimeoutContainer: ports.Container<number>,
        remoteTasks: ports.RemoteTasks,
        tasks: ports.Matching<TaskSurface, Task>,
        cursor: ports.Cursor,
        drawing: ports.Drawing<MapSurface, TaskSurface, Task>,
    }

    export function prepare<MapSurface, TaskSurface>(
        adapters: Ports<MapSurface, TaskSurface>,
        taskSurface: TaskSurface,
    ) {
        const task = adapters.tasks.matchedWith(taskSurface);

        if (task?.mode !== InteractionMode.moving)
            return;

        adapters.cursor.setToGrab();
    }

    export function cancel<MapSurface, TaskSurface>(
        adapters: Ports<MapSurface, TaskSurface>,
        taskSurface: TaskSurface,
    ) {
        const task = adapters.tasks.matchedWith(taskSurface);

        if (task?.mode !== InteractionMode.moving)
            return;

        adapters.cursor.setDefault();
        adapters.activationContainer.set(undefined);
    }

    export function start<MapSurface, TaskSurface>(
        adapters: Ports<MapSurface, TaskSurface>,
        taskSurface: TaskSurface,
        x: number,
        y: number,
    ) {
        const task = adapters.tasks.matchedWith(taskSurface);

        if (task?.mode !== InteractionMode.moving)
            return;

        adapters.referencePointContainer.set(new Vector(x, y));
        adapters.cursor.setGrabbed();

        adapters.activationContainer.set(true);
    }

    export function handle<MapSurface, TaskSurface>(
        adapters: Ports<MapSurface, TaskSurface>,
        taskSurface: TaskSurface,
        x: number,
        y: number,
    ) {
        const task = adapters.tasks.matchedWith(taskSurface);
        const referencePoint = adapters.referencePointContainer.get();
        const isActive = adapters.activationContainer.get();

        if (!(task?.mode === InteractionMode.moving && isActive && referencePoint !== undefined))
            return;

        let taskPosition = new Vector(task.x, task.y);
        const newReferencePoint = new Vector(x, y);

        const taskPositionDifference = (
            newReferencePoint.of(referencePoint, (v1, v2) => v1 - v2)
        );

        taskPosition = taskPosition.of(taskPositionDifference, (v1, v2) => v1 + v2);

        task.x = taskPosition.x;
        task.y = taskPosition.y;

        adapters.referencePointContainer.set(newReferencePoint);

        adapters.drawing.redraw(taskSurface, task);

        const remoteFixationTimeout = adapters.remoteFixationTimeoutContainer.get();

        if (remoteFixationTimeout !== undefined)
            clearTimeout(remoteFixationTimeout);

        adapters.remoteFixationTimeoutContainer.set(setTimeout(
            () => adapters.remoteTasks.updatePosition(task),
            2000,
        ));
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
