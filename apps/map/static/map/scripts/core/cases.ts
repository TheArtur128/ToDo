import * as types from "./types.js";
import * as controllers from "./ports/controllers.js";
import * as messages from "./ports/messages.js";
import * as remoteRepos from "./ports/remote-repos.js";
import * as repos from "./ports/repos.js";
import * as timeouts from "./ports/timeouts.js";
import * as views from "./ports/views.js";
import { Maybe, bad, ok } from "../fp.js";

const waitingForFix: timeouts.Waiting = 600;

export async function drawnMapOf<MapRootView, MapView, TaskView>(
    mapRootView: MapRootView,
    mapView: Maybe<MapView>,
    mapViews: views.Views<MapView>,
    mapDrawing: views.Drawing<MapRootView, MapView, types.Map>,
    remoteTasks: remoteRepos.RemoteTasks,
    taskViews: views.Subviews<MapView, TaskView, types.Task>,
    taskDrawing: views.Drawing<MapView, TaskView, types.Task>,
    taskControllers: controllers.Controllers<TaskView>,
    taskMatching: repos.MatchingBy<TaskView, types.Task>,
    notifications: messages.Notifications,
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
        return bad({
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

        taskControllers = taskControllers.for(taskView);
        taskMatching = taskMatching.withPair(taskView, task);
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
        mapRootView: mapRootView,
        mapView: mapView,
        taskMatching: taskMatching,
        taskControllers: taskControllers,
        notifications: notifications,
        errorLogs: errorLogs,
    });
}

export function changedTaskModeOf<MapView, TaskView>(
    taskView: TaskView,
    taskControllers: controllers.Controllers<TaskView>,
    taskMatching: repos.MatchingBy<TaskView, types.Task>,
    errorLogs: messages.Logs,
    drawing: views.Drawing<MapView, TaskView, types.Task>
) {
    let task = taskMatching.matchedWith(taskView);

    if (task === undefined) {
        errorLogs = errorLogs.with("No matching between task and surface");
        return bad({errorLogs: errorLogs});
    }

    task = task.withChangedMode();

    taskView = drawing.redrawnBy(task, taskView);
    taskControllers = taskControllers.updatedFor(taskView);

    taskMatching = taskMatching.withPair(taskView, task);

    return ok({taskMatching: taskMatching, taskControllers: taskControllers});
}

export function changeTaskDescription<MapView, TaskView>(
    taskMatching: repos.MatchingBy<TaskView, types.Task>,
    drawing: views.Drawing<MapView, TaskView, types.Task>,
    errorLogs: messages.Logs,
    fixationTimeout: timeouts.Timeout,
    remoteTasks: remoteRepos.RemoteTasks,
    taskView: TaskView,
    taskControllers: controllers.Controllers<TaskView>,
    descriptionValue: string,
) {
    let task = taskMatching.matchedWith(taskView);

    if (task === undefined) {
        return bad({
            errorLogs: errorLogs.with("No matching between task and surface"),
        });
    }

    const newDescription = types.Description.of(descriptionValue);

    if (newDescription === undefined || task.description.value === newDescription.value)
        return ok();

    task = task.with({description: newDescription});
    taskView = drawing.redrawnBy(task, taskView);
    taskControllers = taskControllers.updatedFor(taskView);

    taskMatching = taskMatching.withPair(taskView, task);

    fixationTimeout = timeouts.updated(fixationTimeout, waitingForFix, async () => {
        const updatedTask = await remoteTasks.withUpToDateDescription(task);

        if (updatedTask !== undefined)
            return ok();

        const errorLog = "The remote task description could not be updated";
        return bad({errorLogs: errorLogs.with(errorLog)});
    });

    return ok({
        taskMatching: taskMatching,
        taskControllers: taskControllers,
        fixationTimeout: fixationTimeout,
    });
}

export function preparedTaskMovingOf<TaskView>(
    taskMatching: repos.MatchingBy<TaskView, types.Task>,
    cursor: views.Cursor,
    taskView: TaskView,
) {
    const task = taskMatching.matchedWith(taskView);

    const isMoving = task?.mode === types.InteractionMode.moving;
    return isMoving ? ok({cursor: cursor.toGrab()}) : bad();
}

export function startedTaskMovingOf<TaskView>(
    taskMatching: repos.MatchingBy<TaskView, types.Task>,
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
    taskMatching: repos.MatchingBy<TaskView, types.Task>,
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
    taskMatching: repos.MatchingBy<TaskView, types.Task>,
    drawing: views.Drawing<MapView, TaskView, types.Task>,
    taskView: TaskView,
    taskControllers: controllers.Controllers<TaskView>,
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
    taskView = drawing.redrawnBy(task, taskView);
    taskControllers = taskControllers.updatedFor(taskView);

    taskMatching = taskMatching.withPair(taskView, task);

    fixationTimeout = timeouts.updated(fixationTimeout, waitingForFix, async () => {
        const updatedTask = await remoteTasks.withUpToDatePosition(task);

        if (updatedTask !== undefined)
            return;

        const errorLog = "The remote task position could not be updated";
        return {errorLogs: errorLogs.with(errorLog)};
    });

    return {
        taskMatching: taskMatching,
        taskControllers: taskControllers,
        fixationTimeout: fixationTimeout,
    }
}

export function taskAddingAvailabilityOf<MapView, ReadinessAnimation>(
    availableInPast: boolean,
    mapView: MapView,
    descriptionValue: string,
    readinessAnimation: ReadinessAnimation,
    readinessAnimationDrawing: views.StaticDrawing<MapView, ReadinessAnimation>,
    startingControllers: controllers.Controllers<ReadinessAnimation>,
) {
    const description = types.Description.of(descriptionValue);
    const available = description !== undefined;

    if (available && !availableInPast) {
        mapView = readinessAnimationDrawing.withDrawn(readinessAnimation, mapView);
        startingControllers = startingControllers.for(readinessAnimation);
    }
    else if (!available && availableInPast) {
        mapView = readinessAnimationDrawing.withErased(readinessAnimation, mapView);
        startingControllers = startingControllers.notFor(readinessAnimation);
    }

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
    continuationControllers: controllers.Controllers<TaskPrototypeView>,
    startingControllers: controllers.Controllers<ReadinessAnimation>,
    descriptionValue: string,
    x: number,
    y: number,
) {
    const description = types.Description.of(descriptionValue);

    if (description === undefined)
        return;

    mapView = readinessAnimationDrawing.withErased(readinessAnimation, mapView);
    startingControllers = startingControllers.notFor(readinessAnimation);

    const taskPrototype: types.TaskPrototype = {description: description, x: x, y: y};
    const taskPrototypeView = taskPrototypeDrawing.redrawnBy(
        taskPrototype,
        taskPrototypeViews.emptyView
    );

    continuationControllers = continuationControllers.for(taskPrototypeView);
    mapView = taskPrototypeDrawing.withDrawn(taskPrototypeView, mapView);

    return {
        availableInPast: false,
        mapView: mapView,
        continuationControllers: continuationControllers,
        taskPrototype: taskPrototype,
        taskPrototypeView: taskPrototypeView,
    }
}

export function continuedTaskAddingOf<MapView, TaskPrototypeView>(
    taskPrototypeViews: views.Views<TaskPrototypeView>,
    taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype>,
    taskPrototype: types.TaskPrototype,
    taskPrototypeView: TaskPrototypeView,
    continuationControllers: controllers.Controllers<TaskPrototypeView>,
    x: number,
    y: number,
) {
    taskPrototype = {...taskPrototype, x: x, y: y};

    const size = taskPrototypeViews.sizeOf(taskPrototypeView);

    taskPrototypeView = taskPrototypeDrawing.redrawnBy(
        {...taskPrototype, x: x - size.x / 2, y: y - size.y / 2},
        taskPrototypeView,
    );
    continuationControllers = continuationControllers.updatedFor(taskPrototypeView);

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
    taskControllers: controllers.Controllers<TaskView>,
    taskMatching: repos.MatchingBy<TaskView, types.Task>,
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

        return bad({
            errorLogs: errorLogs.with(log),
            notifications: notifications.with("Try adding your task later"),
        });
    }

    taskView = taskDrawing.redrawnBy(task, taskView);
    mapView = taskDrawing.withDrawn(taskView, mapView);

    taskControllers = taskControllers.for(taskView);
    taskMatching = taskMatching.withPair(taskView, task);

    return ok({
        taskMatching: taskMatching,
        mapView: mapView,
        taskView: taskView,
        taskControllers: taskControllers,
    })
}
