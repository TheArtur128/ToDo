import * as types from "./types.js";
import * as controllers from "./ports/controllers.js";
import * as messages from "./ports/messages.js";
import * as remoteRepos from "./ports/remote-repos.js";
import * as repos from "./ports/repos.js";
import * as timeouts from "./ports/timeouts.js";
import * as views from "./ports/views.js";
import { bad, ok, valueOf } from "../fp.js";

const waitingForFix: timeouts.Waiting = 600;

export async function drawnMapOf<RootView, MapView, TaskView>(
    rootView: RootView,
    mapDrawing: views.StaticDrawing<RootView, MapView>,
    getCurrentMapId: () => number,
    mapViewContainer: repos.Container<MapView>,
    mapViews: views.Views<MapView>,
    remoteTasks: remoteRepos.RemoteTasks,
    notifications: messages.Notifications,
    taskViews: views.Subviews<MapView, TaskView, types.Task>,
    taskDrawing: views.Drawing<MapView, TaskView, types.Task>,
    errorLogs: messages.Logs,
    taskMatching: repos.Matching<TaskView, types.Task>,
    withControllers: controllers.WithControllers<TaskView>,
) {
    const map: types.Map = {id: getCurrentMapId()};

    let mapView = mapViewContainer.value;

    if (mapView === undefined) {
        mapView = mapViews.emptyView;
        rootView = mapDrawing.withDrawn(mapView, rootView);
        mapViewContainer = mapViewContainer.with(mapView);
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

        let taskView = taskViews.foundViewOn(mapView, task);

        if (taskView === undefined) {
            taskView = taskDrawing.redrawnBy(task, taskViews.emptyView).value;
            mapView = taskDrawing.withDrawn(taskView, mapView);
        }
        else {
            taskView = taskDrawing.redrawnBy(task, taskView).value;
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

export function changedTaskModeOf<MapView, TaskView>(
    taskView: TaskView,
    taskMatching: repos.Matching<TaskView, types.Task>,
    errorLogs: messages.Logs,
    drawing: views.Drawing<MapView, TaskView, types.Task>
) {
    let task = taskMatching.matchedWith(taskView);

    if (task === undefined) {
        errorLogs = errorLogs.with("No matching between task and surface");
        return bad({errorLogs: errorLogs});
    }

    task = task.withChangedMode();
    taskView = drawing.redrawnBy(task, taskView).value;

    return ok({taskMatching: taskMatching.withPair(taskView, task)});
}

export function changeTaskDescription<MapView, TaskView>(
    taskMatching: repos.Matching<TaskView, types.Task>,
    drawing: views.Drawing<MapView, TaskView, types.Task>,
    errorLogs: messages.Logs,
    timeout: timeouts.Timeout,
    remoteTasks: remoteRepos.RemoteTasks,
    taskView: TaskView,
    descriptionValue: string,
) {
    let task = taskMatching.matchedWith(taskView);

    if (task === undefined) {
        return bad({
            errorLogs: errorLogs.with("No matching between task and surface"),
        });
    }

    const newDescription = descriptionContainer.value;

    if (newDescription === undefined || task.description.value === newDescription.value)
        return ok();

    task = task.with({description: newDescription});
    taskView = drawing.redrawnBy(task, taskView).value;

    taskMatching = taskMatching.withPair(taskView, task);

    const timeoutId = valueOf(timeouts.updated(timeout, waitingForFix, async () => {
        const updatedTask = await remoteTasks.withUpToDateDescription(task);

        if (updatedTask !== undefined)
            return ok();

        const errorLog = "The remote task description could not be updated";
        return bad({errorLogs: errorLogs.with(errorLog)});
    }));

    return ok({taskMatching: taskMatching, timeoutId: timeoutId});
}

export function preparedTaskMovingOf<TaskView>(
    taskMatching: repos.Matching<TaskView, types.Task>,
    cursor: views.Cursor,
    taskView: TaskView,
) {
    const task = taskMatching.matchedWith(taskView);

    const isMoving = task?.mode === types.InteractionMode.moving;
    return isMoving ? ok({cursor: cursor.toGrab()}) : bad();
}

export function startedTaskMovingOf<TaskView>(
    taskMatching: repos.Matching<TaskView, types.Task>,
    cursor: views.Cursor,
    taskView: TaskView,
    x: number,
    y: number,
) {
    const task = taskMatching.matchedWith(taskView);

    if (task?.mode !== types.InteractionMode.moving)
        return bad();

    return ok({
        referencePoint: new types.Vector(x, y),
        cursor: cursor.asGrabbed(),
    })
}

export function canceledTaskMovingOf<TaskView>(
    taskMatching: repos.Matching<TaskView, types.Task>,
    cursor: views.Cursor,
    taskView: TaskView,
) {
    const task = taskMatching.matchedWith(taskView);

    if (task?.mode === types.InteractionMode.moving)
        return bad();

    return ok({cursor: cursor.asDefault()});
}

export function movedTaskOf<MapView, TaskView>(
    errorLogs: messages.Logs,
    referencePoint: types.Vector,
    fixationTimeout: timeouts.Timeout,
    remoteTasks: remoteRepos.RemoteTasks,
    taskMatching: repos.Matching<TaskView, types.Task>,
    drawing: views.Drawing<MapView, TaskView, types.Task>,
    taskView: TaskView,
    x: number,
    y: number,
) {
    let task = taskMatching.matchedWith(taskView);

    if (task?.mode !== types.InteractionMode.moving)
        return;

    let taskPosition = new types.Vector(task.x, task.y);
    const newReferencePoint = new types.Vector(x, y);

    const taskPositionDifference = (
        newReferencePoint.of(referencePoint, (v1, v2) => v1 - v2)
    );
    taskPosition = taskPosition.of(taskPositionDifference, (v1, v2) => v1 + v2);

    task = task.with({x: taskPosition.x, y: taskPosition.y});
    taskView = drawing.redrawnBy(task, taskView).value;

    taskMatching = taskMatching.withPair(taskView, task);

    fixationTimeout = valueOf(timeouts.updated(fixationTimeout, waitingForFix, async () => {
        const updatedTask = await remoteTasks.withUpToDatePosition(task);

        if (updatedTask !== undefined)
            return;

        const errorLog = "The remote task position could not be updated";
        return {errorLogs: errorLogs.with(errorLog)};
    }));

    return {
        taskMatching: taskMatching,
        fixationTimeout: fixationTimeout,
    }
}

export function taskAddingAvailabilityOf<MapView, ReadinessAnimation, TaskPrototypeView, TaskView>(
    mapView: MapView,
    descriptionContainer: repos.Container<types.Description>,
    readinessAnimation: ReadinessAnimation,
    readinessAnimationDrawing: views.StaticDrawing<MapView, ReadinessAnimation>,
    taskPrototypeViews: views.Views<TaskPrototypeView>,
    taskPrototype: types.TaskPrototype,
    taskPrototypeView: TaskPrototypeView,
    taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype>,
    errorLogs: messages.Logs,
    notifications: messages.Notifications,
    continuationControllers: controllers.Controllers<TaskPrototypeView>,
    getCurrentMapId: () => number,
    remoteTasks: remoteRepos.RemoteTasks,
    taskViews: views.Views<TaskView>,
    taskDrawing: views.Drawing<MapView, TaskView, types.Task>,
    startingControllers: controllers.Controllers<ReadinessAnimation>,
    hangControllersOn: controllers.WithControllers<TaskView>,
    taskMatching: repos.Matching<TaskView, types.Task>,
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

// export type Ports<MapView, ReadinessAnimation, TaskPrototypeView, TaskView> = {
//     mapView: MapView,
//     descriptionContainer: repos.Container<types.Description>,
//     readinessAnimation: ReadinessAnimation,
//     readinessAnimationDrawing: views.StaticDrawing<MapView, ReadinessAnimation>,
//     taskPrototypeViews: views.Views<TaskPrototypeView>,
//     taskPrototype: types.TaskPrototype,
//     taskPrototypeView: TaskPrototypeView,
//     taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype>,
//     errorLogs: messages.Logs,
//     notifications: messages.Notifications,
//     continuationControllers: controllers.Controllers<TaskPrototypeView>,
//     getCurrentMapId: () => number,
//     remoteTasks: remoteRepos.RemoteTasks,
//     taskViews: views.Views<TaskView>,
//     taskDrawing: views.Drawing<MapView, TaskView, types.Task>,
//     startingControllers: controllers.Controllers<ReadinessAnimation>,
//     hangControllersOn: controllers.WithControllers<TaskView>,
//     taskMatching: repos.Matching<TaskView, types.Task>,
// }

export namespace taskAdding {
    export function handleAvailability<MapView, ReadinessAnimation, TaskPrototypeSurface, TaskSurface>(
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
