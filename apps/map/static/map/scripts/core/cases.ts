import * as types from "./types.js";
import * as controllers from "./ports/controllers.js";
import * as messages from "./ports/messages.js";
import * as remoteRepos from "./ports/remote-repos.js";
import * as timeouts from "./ports/timeouts.js";
import * as views from "./ports/views.js";
import { EntityMatching, ControllerMatching, updatedPresentationOf } from "./services/presentations.js";
import { Maybe, results } from "../fp.js";

const fixationTime: timeouts.Milliseconds = 600;

export async function drawnMapOf<MapRootView, MapView, TaskView>(
    mapRootView: MapRootView,
    mapView: Maybe<MapView>,
    mapViews: views.Views<MapView>,
    mapDrawing: views.Drawing<MapRootView, MapView, types.Map>,
    remoteTasks: remoteRepos.RemoteTasks,
    taskViews: views.Subviews<MapView, TaskView, types.Task>,
    taskDrawing: views.Drawing<MapView, TaskView, types.Task>,
    taskMatching: EntityMatching<TaskView, types.Task>,
    taskControllerMatching: ControllerMatching<TaskView, types.Task>,
    notifications: messages.Notify,
    errorLogs: messages.Logs,
    mapId: number,
) {
    const map: types.Map = {id: mapId};

    if (mapView !== undefined)
        mapView = mapDrawing.redrawnBy(map, mapView);
    else {
        mapView = mapDrawing.redrawnBy(map, mapViews.emptyView);
        mapRootView =  mapDrawing.withDrawn(mapView, mapRootView);
    }

    const tasks = await remoteTasks.tasksOn(map);

    if (tasks === undefined) {
        return results.bad({
            mapRootView: mapRootView,
            mapView: mapView,
            notifications: notifications.with(
                "All your tasks could not be displayed."
            ),
            errorLogs: errorLogs.with(
                `Failed to get remote tasks on map with id = ${map.id}`
            ),
        });
    }

    let numberOfUndisplayedTasks = 0;

    for await (const task of tasks) {
        if (task === undefined) {
            numberOfUndisplayedTasks++;
            continue;
        }

        let taskView = taskViews.foundViewOn(mapView, task);

        if (taskView === undefined) {
            taskView = taskDrawing.redrawnBy(task, taskViews.emptyView);
            mapView = taskDrawing.withDrawn(taskView, mapView);
        }
        else {
            taskView = taskDrawing.redrawnBy(task, taskView);
        }

        const taskControllers = taskControllerMatching
            .matchedWith(taskView)
            .mapOk(c => c.updatedControllersFor(taskView, task))
            .mapBad(c => c.activeControllersFor(taskView, task))
            .asOk;

        taskMatching = taskMatching.matchingBetween(taskView, task);
        taskControllerMatching = taskControllerMatching.matchingBetween(taskView, taskControllers);
    }

    if (numberOfUndisplayedTasks !== 0) {
        notifications = notifications.with(
            "Some of your tasks could not be displayed."
        );
        errorLogs = errorLogs.with(
            `Failed to get ${numberOfUndisplayedTasks} remote tasks from map with id = ${map.id}`
        );
    }

    return results.ok({
        mapRootView: mapRootView,
        taskControllerMatching: taskControllerMatching,
        mapView: mapView,
        taskMatching: taskMatching,
        notifications: notifications,
        errorLogs: errorLogs,
    });
}

export function changedTaskModeOf<MapView, TaskView>(
    taskView: TaskView,
    taskControllerMatching: ControllerMatching<TaskView, types.Task>,
    taskMatching: EntityMatching<TaskView, types.Task>,
    errorLogs: messages.Logs,
    drawing: views.Drawing<MapView, TaskView, types.Task>
) {
    let task = taskMatching.matchedWith(taskView);

    if (task === undefined) {
        errorLogs = errorLogs.with("No matching between task and surface");
        return results.bad({errorLogs: errorLogs});
    }

    task = task.withChangedMode();

    [taskMatching, taskControllerMatching] = updatedPresentationOf(
        task, taskView, drawing, taskMatching, taskControllerMatching
    )

    return results.ok({
        taskMatching: taskMatching,
        taskControllerMatching: taskControllerMatching,
    });
}

export function changedTaskDescriptionOf<MapView, TaskView>(
    taskMatching: EntityMatching<TaskView, types.Task>,
    taskControllerMatching: ControllerMatching<TaskView, types.Task>,
    drawing: views.Drawing<MapView, TaskView, types.Task>,
    errorLogs: messages.Logs,
    fixationTimeout: timeouts.Timeout,
    remoteTasks: remoteRepos.RemoteTasks,
    taskView: TaskView,
    descriptionValue: string,
) {
    let task = taskMatching.matchedWith(taskView);

    if (task === undefined) {
        return results.bad({
            errorLogs: errorLogs.with("No matching between task and surface"),
        });
    }

    const newDescription = types.Description.of(descriptionValue);

    if (newDescription === undefined || task.description.value === newDescription.value)
        return results.ok();

    task = task.with({description: newDescription});

    [taskMatching, taskControllerMatching] = updatedPresentationOf(
        task, taskView, drawing, taskMatching, taskControllerMatching
    )

    fixationTimeout = fixationTimeout.executingIn(fixationTime, async () => {
        const updatedTask = await remoteTasks.withUpToDateDescription(task);

        if (updatedTask !== undefined)
            return results.ok();

        const errorLog = "The remote task description could not be updated";
        return results.bad({errorLogs: errorLogs.with(errorLog)});
    });

    return results.ok({
        taskMatching: taskMatching,
        taskControllerMatching: taskControllerMatching,
        fixationTimeout: fixationTimeout,
    });
}

export function preparedTaskMovingOf<TaskView>(
    taskMatching: EntityMatching<TaskView, types.Task>,
    cursor: views.Cursor,
    taskView: TaskView,
) {
    const task = taskMatching.matchedWith(taskView);

    const isMoving = task?.mode === types.InteractionMode.moving;
    return isMoving ? results.ok({cursor: cursor.toGrab()}) : results.bad();
}

export function startedTaskMovingOf<TaskView>(
    taskMatching: EntityMatching<TaskView, types.Task>,
    cursor: views.Cursor,
    taskView: TaskView,
    x: number,
    y: number,
) {
    const task = taskMatching.matchedWith(taskView);

    if (task?.mode !== types.InteractionMode.moving)
        return results.bad();

    return results.ok({
        referencePoint: new types.Vector(x, y),
        cursor: cursor.asGrabbed(),
    })
}

export function canceledTaskMovingOf<TaskView>(
    taskMatching: EntityMatching<TaskView, types.Task>,
    cursor: views.Cursor,
    taskView: TaskView,
) {
    const task = taskMatching.matchedWith(taskView);

    if (task?.mode === types.InteractionMode.moving)
        return results.bad();

    return results.ok({cursor: cursor.asDefault()});
}

export function movedTaskOf<MapView, TaskView>(
    errorLogs: messages.Logs,
    referencePoint: types.Vector,
    fixationTimeout: timeouts.Timeout,
    remoteTasks: remoteRepos.RemoteTasks,
    taskMatching: EntityMatching<TaskView, types.Task>,
    drawing: views.Drawing<MapView, TaskView, types.Task>,
    taskView: TaskView,
    taskControllerMatching: ControllerMatching<TaskView, types.Task>,
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

    [taskMatching, taskControllerMatching] = updatedPresentationOf(
        task, taskView, drawing, taskMatching, taskControllerMatching
    )

    fixationTimeout = fixationTimeout.executingIn(fixationTime, async () => {
        const updatedTask = await remoteTasks.withUpToDatePosition(task);

        if (updatedTask !== undefined)
            return;

        const errorLog = "The remote task position could not be updated";
        return {errorLogs: errorLogs.with(errorLog)};
    });

    return {
        taskMatching: taskMatching,
        taskControllerMatching: taskControllerMatching,
        fixationTimeout: fixationTimeout,
    }
}

export function taskAddingAvailabilityOf<MapView, ReadinessAnimation>(
    availableInPast: boolean,
    mapView: MapView,
    descriptionValue: string,
    readinessAnimation: ReadinessAnimation,
    readinessAnimationDrawing: views.StaticDrawing<MapView, ReadinessAnimation>,
    startingControllers: controllers.StaticControllers<ReadinessAnimation>,
) {
    const description = types.Description.of(descriptionValue);
    const available = description !== undefined;

    if (available && !availableInPast)
        mapView = readinessAnimationDrawing.withDrawn(readinessAnimation, mapView);
    else if (!available && availableInPast)
        mapView = readinessAnimationDrawing.withErased(readinessAnimation, mapView);

    startingControllers = startingControllers
        .mapBad(c => c.activeControllersFor(readinessAnimation))
        .asOk;

    return {
        availableInPast: available,
        mapView: mapView,
        startingControllers:startingControllers,
    }
}

export function startedTaskAddingOf<MapView, ReadinessAnimation, TaskPrototypeView>(
    mapView: MapView,
    readinessAnimation: ReadinessAnimation,
    readinessAnimationDrawing: views.StaticDrawing<MapView, ReadinessAnimation>,
    taskPrototypeViews: views.Views<TaskPrototypeView>,
    taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype>,
    continuationControllers: controllers.Controllers<TaskPrototypeView, types.TaskPrototype>,
    startingControllers: controllers.StaticControllers<ReadinessAnimation>,
    descriptionValue: string,
    x: number,
    y: number,
) {
    const description = types.Description.of(descriptionValue);

    if (description === undefined)
        return;

    mapView = readinessAnimationDrawing.withErased(readinessAnimation, mapView);
    startingControllers = startingControllers.mapOk(c => c.inactiveControllers).asBad;

    const taskPrototype: types.TaskPrototype = {description: description, x: x, y: y};

    const taskPrototypeView = taskPrototypeDrawing.redrawnBy(
        taskPrototype,
        taskPrototypeViews.emptyView
    );

    mapView = taskPrototypeDrawing.withDrawn(taskPrototypeView, mapView);
    continuationControllers = controllers.asActiveFor(
        taskPrototypeView, taskPrototype, continuationControllers
    );

    return {
        availableInPast: false,
        mapView: mapView,
        continuationControllers: continuationControllers,
        startingControllers: startingControllers,
        taskPrototype: taskPrototype,
        taskPrototypeView: taskPrototypeView,
    }
}

export function continuedTaskAddingOf<MapView, TaskPrototypeView>(
    taskPrototype: types.TaskPrototype,
    taskPrototypeView: TaskPrototypeView,
    continuationControllers: controllers.Controllers<TaskPrototypeView, types.TaskPrototype>,
    taskPrototypeViews: views.Views<TaskPrototypeView>,
    taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype>,
    x: number,
    y: number,
) {
    taskPrototype = {...taskPrototype, x: x, y: y};

    const size = taskPrototypeViews.sizeOf(taskPrototypeView);
    const taskPrototypeToPresent = {
        ...taskPrototype, x: x - size.x / 2, y: y - size.y / 2
    };

    taskPrototypeView = taskPrototypeDrawing.redrawnBy(
        taskPrototypeToPresent, taskPrototypeView
    );
    continuationControllers = controllers.asActiveFor(
        taskPrototypeView, taskPrototypeToPresent, continuationControllers
    )

    return {
        taskPrototype: taskPrototype,
        taskPrototypeView: taskPrototypeView,
        continuationControllers: continuationControllers,
    }
}

export async function completedTaskAddingOf<RootView, MapView, TaskPrototypeView, TaskView>(
    mapView: MapView,
    mapDrawing: views.Drawing<RootView, MapView, types.Map>,
    taskPrototype: types.TaskPrototype,
    taskPrototypeView: TaskPrototypeView,
    taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype>,
    errorLogs: messages.Logs,
    notifications: messages.Notifications,
    remoteTasks: remoteRepos.RemoteTasks,
    taskViews: views.Views<TaskView>,
    taskDrawing: views.Drawing<MapView, TaskView, types.Task>,
    taskControllerMatching: ControllerMatching<TaskView, types.Task>,
    taskMatching: EntityMatching<TaskView, types.Task>,
    mapId: number,
) {
    let taskView = taskViews.emptyView;
    const size = taskViews.sizeOf(taskView);

    const taskPrototypeToCreateTask = {
        ...taskPrototype,
        x: taskPrototype.x - size.x / 2,
        y: taskPrototype.y - size.y / 2,
    }

    const map: types.Map = {id: mapId};
    mapView = mapDrawing.redrawnBy(map, mapView);

    const task = await remoteTasks.createdTaskFrom(taskPrototypeToCreateTask, map);

    mapView = taskPrototypeDrawing.withErased(taskPrototypeView, mapView);

    if (task === undefined) {
        const log = `A remote task on the map with id = ${mapId} could not be created`;

        return results.bad({
            errorLogs: errorLogs.with(log),
            notifications: notifications.with("Try adding your task later"),
        });
    }

    taskView = taskDrawing.redrawnBy(task, taskView);
    mapView = taskDrawing.withDrawn(taskView, mapView);

    const taskControllers = taskControllerMatching
        .matchedWith(taskView)
        .mapBad(c => c.activeControllersFor(taskView, task))
        .asOk;

    taskControllerMatching = taskControllerMatching.matchingBetween(taskView, taskControllers);
    taskMatching = taskMatching.matchingBetween(taskView, task);

    return results.ok({
        taskMatching: taskMatching,
        taskControllerMatching: taskControllerMatching,
        mapView: mapView,
        taskView: taskView,
    })
}
