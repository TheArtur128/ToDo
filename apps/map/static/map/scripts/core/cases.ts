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
        descriptionContainer: ports.Container<Description>,
        descriptionUpdatingTimeout: ports.Container<number>,
        remoteTasks: ports.RemoteTasks,
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

    export function changeDescription<MapSurface, TaskSurface>(
        adapters: Ports<MapSurface, TaskSurface>,
        taskSurface: TaskSurface,
    ): void {
        const task = adapters.tasks.matchedWith(taskSurface);

        if (task === undefined) {
            adapters.logError("No matching between task and surface");
            return;
        }

        const newDescription = adapters.descriptionContainer.get();

        if (newDescription === undefined || task.description.value === newDescription.value)
            return;

        task.description = newDescription;
        adapters.drawing.redraw(taskSurface, task);

        services.updateRemoteFixationTimeout(adapters.descriptionUpdatingTimeout, () => {
            adapters.remoteTasks.updateDescription(task);
        });
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

        services.updateRemoteFixationTimeout(adapters.remoteFixationTimeoutContainer, () => {
            adapters.remoteTasks.updatePosition(task)
        });
    }
}

export namespace taskAdding {
    export type Ports<MapSurface, ReadinessAnimation, TaskPrototypeSurface, TaskSurface> = {
        mapSurface: MapSurface,
        descriptionContainer: ports.Container<Description>,
        availabilityContainer: ports.Container<boolean>,
        readinessAnimation: ReadinessAnimation,
        readinessAnimationDrawing: ports.StaticDrawing<MapSurface, ReadinessAnimation>,
        taskPrototypeSurfaces: ports.TaskPrototypeSurfaces<TaskPrototypeSurface>,
        taskPrototypeContainer: ports.Container<TaskPrototype>,
        taskPrototypeSurfaceContainer: ports.Container<TaskPrototypeSurface>,
        taskPrototypeDrawing: ports.Drawing<MapSurface, TaskPrototypeSurface, TaskPrototype>,
        logError: ports.Log,
        show: ports.Show,
        continuationControllers: ports.Controllers<TaskPrototypeSurface>,
        getCurrentMapId: () => number,
        remoteTasks: ports.RemoteTasks,
        taskSurfaces: ports.TaskSurfaces<MapSurface, TaskSurface>,
        taskDrawing: ports.Drawing<MapSurface, TaskSurface, Task>,
        startingControllers: ports.Controllers<ReadinessAnimation>,
        hangControllersOn: ports.HangControllers<TaskSurface>,
        tasks: ports.Matching<TaskSurface, Task>,
    }

    export function handleAvailability<MapSurface, ReadinessAnimation, TaskPrototypeSurface, TaskSurface>(
        adapters: taskAdding.Ports<MapSurface, ReadinessAnimation, TaskPrototypeSurface, TaskSurface>
    ): void {
        const available = adapters.descriptionContainer.get() !== undefined;
        let availableInPast = adapters.availabilityContainer.get();

        if (availableInPast === undefined)
            availableInPast = false;

        adapters.availabilityContainer.set(available);

        if (available && !availableInPast) {
            adapters.readinessAnimationDrawing.drawOn(
                adapters.mapSurface,
                adapters.readinessAnimation,
            );
            adapters.startingControllers.hangOn(adapters.readinessAnimation);
        }
        else if (!available && availableInPast) {
            adapters.readinessAnimationDrawing.eraseFrom(
                adapters.mapSurface,
                adapters.readinessAnimation,
            );
            adapters.startingControllers.removeFrom(adapters.readinessAnimation);
        }
    }

    export function start<MapSurface, ReadinessAnimation, TaskPrototypeSurface, TaskSurface>(
        x: number,
        y: number,
        adapters: taskAdding.Ports<MapSurface, ReadinessAnimation, TaskPrototypeSurface, TaskSurface>
    ): void {
        const description = services.popFrom(adapters.descriptionContainer);

        if (description === undefined)
            return;

        adapters.availabilityContainer.set(false);
        adapters.readinessAnimationDrawing.eraseFrom(adapters.mapSurface, adapters.readinessAnimation);
        adapters.startingControllers.removeFrom(adapters.readinessAnimation);

        const taskPrototype: TaskPrototype = {description: description, x: x, y: y};
        const taskPrototypeSurface = adapters.taskPrototypeSurfaces.getEmpty();

        adapters.taskPrototypeContainer.set(taskPrototype);
        adapters.taskPrototypeSurfaceContainer.set(taskPrototypeSurface);

        adapters.taskPrototypeDrawing.redraw(taskPrototypeSurface, taskPrototype);
        adapters.taskPrototypeDrawing.drawOn(adapters.mapSurface, taskPrototypeSurface);

        adapters.continuationControllers.hangOn(taskPrototypeSurface);
    }

    export function handle<MapSurface, ReadinessAnimation, TaskPrototypeSurface, TaskSurface>(
        x: number,
        y: number,
        adapters: taskAdding.Ports<MapSurface, ReadinessAnimation, TaskPrototypeSurface, TaskSurface>
    ): void {
        let taskPrototype = adapters.taskPrototypeContainer.get();
        const taskPrototypeSurface = adapters.taskPrototypeSurfaceContainer.get();

        if (taskPrototype === undefined)
            adapters.logError("Task prototype does not exist");

        if (taskPrototypeSurface === undefined)
            adapters.logError("Task prototype surface does not exist");

        if (taskPrototype === undefined || taskPrototypeSurface === undefined) {
            adapters.show("Adding your task was aborted");
            return;
        }

        taskPrototype.x = x;
        taskPrototype.y = y;

        const size = adapters.taskPrototypeSurfaces.sizeOf(taskPrototypeSurface);

        adapters.taskPrototypeDrawing.redraw(
            taskPrototypeSurface,
            {...taskPrototype, x: x - size.x / 2, y: y - size.y / 2},
        );
    }

    export async function complete<MapSurface, ReadinessAnimation, TaskPrototypeSurface, TaskSurface>(
        adapters: taskAdding.Ports<MapSurface, ReadinessAnimation, TaskPrototypeSurface, TaskSurface>
    ): Promise<void> {
        const taskPrototype = adapters.taskPrototypeContainer.get();
        const taskPrototypeSurface = adapters.taskPrototypeSurfaceContainer.get();

        if (taskPrototype === undefined)
            adapters.logError("Task prototype does not exist");

        if (taskPrototypeSurface === undefined)
            adapters.logError("Task prototype surface does not exist");
        else
            adapters.continuationControllers.removeFrom(taskPrototypeSurface);

        if (taskPrototype === undefined || taskPrototypeSurface === undefined) {
            adapters.show("Failed to add your task");
            return;
        }

        const taskSurface = adapters.taskSurfaces.getEmpty();
        const size = adapters.taskSurfaces.sizeOf(taskSurface);

        const taskPrototypeToCreateTask = {
            ...taskPrototype,
            x: taskPrototype.x - size.x / 2,
            y: taskPrototype.y - size.y / 2,
        }

        const mapId = adapters.getCurrentMapId();

        const task = await adapters.remoteTasks.createdTaskFrom(
            taskPrototypeToCreateTask, mapId
        );

        adapters.taskPrototypeDrawing.eraseFrom(adapters.mapSurface, taskPrototypeSurface);

        if (task === undefined) {
            adapters.logError(`A remote task on the map with id = ${mapId} could not be created`);
            adapters.show("Try adding your task later");
            return;
        }

        adapters.taskDrawing.redraw(taskSurface, task);
        adapters.taskDrawing.drawOn(adapters.mapSurface, taskSurface);

        adapters.hangControllersOn(taskSurface);
        adapters.tasks.match(taskSurface, task);
    }
}
