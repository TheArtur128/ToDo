import * as types from "./types.js";
import * as controllers from "./ports/controllers.js";
import * as messages from "./ports/messages.js";
import * as remoting from "./ports/remoting.js";
import * as repos from "./ports/repos.js";
import * as timeouts from "./ports/timeouts.js";
import * as views from "./ports/views.js";
import { bad, ok } from "../fp.js";

export async function drawnMapOf<RootView, MapView, TaskView>(
    rootView: RootView,
    mapDrawing: views.StaticDrawing<RootView, MapView>,
    getCurrentMapId: () => number,
    mapViewContainer: repos.Container<MapView>,
    mapViews: views.RootViews<MapView, TaskView, types.Task>,
    remoteTasks: remoting.RemoteTasks,
    notifications: messages.Notifications,
    taskViews: views.Views<TaskView>,
    taskDrawing: views.Drawing<MapView, TaskView, types.Task>,
    errorLogs: messages.Logs,
    taskMatching: repos.Matching<TaskView, types.Task>,
    withControllers: controllers.WithControllers<TaskView>,
) {
    const map: types.Map = {id: getCurrentMapId()};

    let mapView = repos.valueOf(mapViewContainer);

    if (mapView === undefined) {
        mapView = mapViews.emptyView;
        rootView = mapDrawing.withDrawn(mapView, rootView);
        mapViewContainer = repos.with_(mapView, mapViewContainer);
    }

    const tasks = await remoteTasks.tasksOn(map);

    if (tasks === undefined) {
        notifications = notifications.with(
            "All your tasks could not be displayed."
        );
        errorLogs = errorLogs.with(
            `Failed to get remote tasks on map with id = ${map.id}`
        );

        return bad({notifications: notifications, errorLogs: errorLogs});
    }

    let numberOfUndisplayedTasks = 0;

    for await (const task of tasks) {
        if (task === undefined) {
            numberOfUndisplayedTasks++;
            continue;
        }

        let taskView = mapViews.foundSubviewOn(mapView, task);

        if (taskView === undefined) {
            taskView = taskDrawing.redrawnBy(task, taskViews.emptyView);
            mapView = taskDrawing.withDrawn(taskView, mapView);
        }
        else {
            taskView = taskDrawing.redrawnBy(task, taskView);
        }

        taskMatching = taskMatching.withPair(withControllers(taskView), task);
    }

    let asResult = ok;

    if (numberOfUndisplayedTasks !== 0) {
        notifications = notifications.with(
            "Some of your tasks could not be displayed."
        );
        errorLogs = errorLogs.with(
            `Failed to get ${numberOfUndisplayedTasks} remote tasks from map with id = ${map.id}`
        );

        asResult = bad;
    }

    return asResult({
        rootView: rootView,
        mapViewContainer: mapViewContainer,
        taskMatching: taskMatching,
        notifications: notifications,
        errorLogs: errorLogs,
    });
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
