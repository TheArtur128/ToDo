import * as types from "./types.js";
import * as controllers from "./ports/controllers.js";
import * as messages from "./ports/messages.js";
import * as remoteRepos from "./ports/remote-repos.js";
import * as repos from "./ports/repos.js";
import * as timeouts from "./ports/timeouts.js";
import * as views from "./ports/views.js";
import { Maybe } from "../sugar.js";

const fixationTime: timeouts.Milliseconds = 600;

export async function drawnMapOf<MapRootView, MapView, TaskView>(
    mapRootView: MapRootView,
    mapView: Maybe<MapView>,
    mapViews: views.Views<MapView>,
    mapDrawing: views.Drawing<MapRootView, MapView, types.Map>,
    remoteTasks: remoteRepos.RemoteTasks,
    taskViews: views.Subviews<MapView, TaskView, types.Task>,
    taskDrawing: views.Drawing<MapView, TaskView, types.Task>,
    taskMatching: repos.MaybeMatchingBy<TaskView, types.Task>,
    taskControllers: controllers.ControllersFor<TaskView, types.Task>,
    notify: messages.Notify,
    logError: messages.Log,
    mapId: number,
) {
    const map: types.Map = {id: mapId};

    if (mapView !== undefined)
        mapDrawing.redrawBy(map, mapView);
    else {
        mapView = mapViews.createEmptyView();
        mapDrawing.redrawBy(map, mapView);
        mapDrawing.drawOn(mapRootView, mapView);
    }

    const tasks = await remoteTasks.tasksOn(map);

    if (tasks === undefined) {
        notify("All your tasks could not be displayed.");
        logError(`Failed to get remote tasks on map with id = ${map.id}`);
        return;
    }

    let numberOfUndisplayedTasks = 0;

    for await (const task of tasks) {
        if (task === undefined) {
            numberOfUndisplayedTasks++;
            continue;
        }

        let taskView = taskViews.foundViewOn(mapView, task);

        if (taskView === undefined) {
            taskView = taskViews.createEmptyView();
            taskDrawing.redrawBy(task, taskView);
            taskDrawing.drawOn(mapView, taskView);
        }
        else {
            taskDrawing.redrawBy(task, taskView);
        }

        taskControllers.activeFor(taskView, task);
        taskMatching.match(taskView, task);
    }

    if (numberOfUndisplayedTasks !== 0) {
        notify("Some of your tasks could not be displayed.");
        logError(
            `Failed to get ${numberOfUndisplayedTasks} remote tasks from map with id = ${map.id}`
        );
    }
}

export function changedTaskModeOf<MapView, TaskView>(
    view: TaskView,
    controllers: controllers.ControllersFor<TaskView, types.Task>,
    matching: repos.MaybeMatchingBy<TaskView, types.Task>,
    logError: messages.Log,
    drawing: views.Drawing<MapView, TaskView, types.Task>
) {
    let task = matching.matchedWith(view);

    if (task === undefined) {
        logError("No matching between task and surface");
        return;
    }

    task.changeMode();

    drawing.redrawBy(task, view);
    controllers.updateFor(view, task);
}

export function changedTaskDescriptionOf<MapView, TaskView>(
    taskMatching: repos.MaybeMatchingBy<TaskView, types.Task>,
    drawing: views.Drawing<MapView, TaskView, types.Task>,
    controllers: controllers.ControllersFor<TaskView, types.Task>,
    logError: messages.Log,
    fixationTimeout: timeouts.Timeout,
    remoteTasks: remoteRepos.RemoteTasks,
    taskView: TaskView,
    descriptionValue: string,
) {
    let task = taskMatching.matchedWith(taskView);

    if (task === undefined) {
        logError("No matching between task and surface");
        return;
    }

    const newDescription = types.Description.of(descriptionValue);

    if (newDescription === undefined || task.description.value === newDescription.value)
        return;

    task.description = newDescription;
    drawing.redrawBy(task, taskView);
    controllers.updateFor(taskView, task);

    fixationTimeout.executeIn(fixationTime, async () => {
        const updatedTask = await remoteTasks.withUpToDateDescription(task);

        if (updatedTask === undefined)
            logError("The remote task description could not be updated");
    });
}

export function preparedTaskMovingOf<TaskView>(
    taskMatching: repos.MaybeMatchingBy<TaskView, types.Task>,
    cursor: views.Cursor,
    taskView: TaskView,
) {
    const task = taskMatching.matchedWith(taskView);

    if (task?.mode === types.InteractionMode.moving)
        cursor.setToGrab();
}

export function startedTaskMovingOf<TaskView>(
    taskMatching: repos.MaybeMatchingBy<TaskView, types.Task>,
    referencePointMatching: repos.MaybeMatchingBy<TaskView, types.Vector>,
    cursor: views.Cursor,
    taskView: TaskView,
    taskMovingControllers: controllers.ControllersFor<TaskView, types.Task>,
    x: number,
    y: number,
) {
    const task = taskMatching.matchedWith(taskView);

    if (task?.mode !== types.InteractionMode.moving)
        return;

    referencePointMatching.match(taskView, new types.Vector(x, y));

    cursor.setGrabbed();
    taskMovingControllers.activeFor(taskView, task);
}

export function canceledTaskMovingOf<TaskView>(
    taskMatching: repos.MaybeMatchingBy<TaskView, types.Task>,
    referencePointMatching: repos.MaybeMatchingBy<TaskView, types.Vector>,
    cursor: views.Cursor,
    taskMovingControllers: controllers.ControllersFor<TaskView, types.Task>,
    taskView: TaskView,
) {
    const task = taskMatching.matchedWith(taskView);

    if (task?.mode !== types.InteractionMode.moving)
        return;

    referencePointMatching.dontMatchWith(taskView);

    taskMovingControllers.removeFrom(taskView, task);
    cursor.setDefault();
}

export function movedTaskOf<MapView, TaskView>(
    taskMatching: repos.MaybeMatchingBy<TaskView, types.Task>,
    referencePointMatching: repos.MaybeMatchingBy<TaskView, types.Vector>,
    logError: messages.Log,
    fixationTimeout: timeouts.Timeout,
    remoteTasks: remoteRepos.RemoteTasks,
    drawing: views.Drawing<MapView, TaskView, types.Task>,
    taskView: TaskView,
    taskControllers: controllers.ControllersFor<TaskView, types.Task>,
    taskMovingControllers: controllers.ControllersFor<TaskView, types.Task>,
    x: number,
    y: number,
) {
    const task = taskMatching.matchedWith(taskView);
    const referencePoint = referencePointMatching.matchedWith(taskView);

    if (task?.mode !== types.InteractionMode.moving)
        return;

    if (referencePoint === undefined) {
        logError(`the moving of task with id = ${task.id} was not started`);
        return;
    }

    let taskPosition = new types.Vector(task.x, task.y);
    const newReferencePoint = new types.Vector(x, y);

    const taskPositionDifference = (
        newReferencePoint.of(referencePoint, (v1, v2) => v1 - v2)
    );
    taskPosition = taskPosition.of(taskPositionDifference, (v1, v2) => v1 + v2);

    task.x = taskPosition.x;
    task.y = taskPosition.y;

    drawing.redrawBy(task, taskView);
    taskControllers.updateFor(taskView, task);
    taskMovingControllers.updateFor(taskView, task);

    fixationTimeout.executeIn(fixationTime, async () => {
        const updatedTask = await remoteTasks.withUpToDatePosition(task);

        if (updatedTask === undefined)
            logError("The remote task position could not be updated");
    });
}

export function taskAddingAvailabilityOf<ReadinessAnimationRoot, ReadinessAnimation>(
    pastAvailabilityMatching: repos.MatchingBy<ReadinessAnimation, boolean>,
    descriptionValue: string,
    readinessAnimationRoot: ReadinessAnimationRoot,
    readinessAnimation: ReadinessAnimation,
    readinessAnimationDrawing: views.StaticDrawing<ReadinessAnimationRoot, ReadinessAnimation>,
    startingControllers: controllers.ControllersForStatic<ReadinessAnimation>,
): void {
    const description = types.Description.of(descriptionValue);

    const available = description !== undefined;
    const availableInPast = pastAvailabilityMatching.matchedWith(readinessAnimation);

    if (available && !availableInPast) {
        readinessAnimationDrawing.drawOn(readinessAnimationRoot, readinessAnimation);
        startingControllers.activeFor(readinessAnimation);
    }
    else if (!available && availableInPast) {
        readinessAnimationDrawing.eraseFrom(readinessAnimationRoot, readinessAnimation);
        startingControllers.removeFrom(readinessAnimation);
    }

    pastAvailabilityMatching.match(readinessAnimation, available);
}

export function startedTaskAddingOf<MapView, ReadinessAnimation, ReadinessAnimationRoot, TaskPrototypeView>(
    pastAvailabilityMatching: repos.MatchingBy<ReadinessAnimation, boolean>,
    mapView: MapView,
    readinessAnimationRoot: ReadinessAnimationRoot,
    readinessAnimation: ReadinessAnimation,
    readinessAnimationDrawing: views.StaticDrawing<ReadinessAnimationRoot, ReadinessAnimation>,
    taskPrototypeViews: views.Views<TaskPrototypeView>,
    taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype>,
    continuationControllers: controllers.ControllersFor<TaskPrototypeView, types.TaskPrototype>,
    startingControllers: controllers.ControllersForStatic<ReadinessAnimation>,
    descriptionValueContainer: repos.Container<string>,
    x: number,
    y: number,
) {
    const description = types.Description.of(descriptionValueContainer.get());

    if (description === undefined)
        return;

    descriptionValueContainer.set('');

    pastAvailabilityMatching.match(readinessAnimation, false);
    readinessAnimationDrawing.eraseFrom(readinessAnimationRoot, readinessAnimation);
    startingControllers.removeFrom(readinessAnimation);

    const taskPrototype: types.TaskPrototype = {description: description, x: x, y: y};

    const taskPrototypeView = taskPrototypeViews.createEmptyView();
    taskPrototypeDrawing.redrawBy(taskPrototype, taskPrototypeView);
    taskPrototypeDrawing.drawOn(mapView, taskPrototypeView);

    continuationControllers.activeFor(taskPrototypeView, taskPrototype);
}

export function continuedTaskAddingOf<MapView, TaskPrototypeView>(
    continuationControllers: controllers.ControllersFor<TaskPrototypeView, types.TaskPrototype>,
    taskPrototypeViews: views.Views<TaskPrototypeView>,
    taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype>,
    taskPrototype: types.TaskPrototype,
    taskPrototypeView: TaskPrototypeView,
    x: number,
    y: number,
) {
    taskPrototype = {...taskPrototype, x: x, y: y};

    const size = taskPrototypeViews.sizeOf(taskPrototypeView);
    const taskPrototypeToPresent = {
        ...taskPrototype, x: x - size.x / 2, y: y - size.y / 2
    };

    taskPrototypeDrawing.redrawBy(taskPrototypeToPresent, taskPrototypeView);
    continuationControllers.updateFor(taskPrototypeView, taskPrototype);
}

export async function completedTaskAddingOf<RootView, MapView, TaskPrototypeView, TaskView>(
    mapView: MapView,
    taskPrototype: types.TaskPrototype,
    taskPrototypeView: TaskPrototypeView,
    taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype>,
    logError: messages.Log,
    notify: messages.Notify,
    remoteTasks: remoteRepos.RemoteTasks,
    taskViews: views.Views<TaskView>,
    taskDrawing: views.Drawing<MapView, TaskView, types.Task>,
    taskControllers: controllers.ControllersFor<TaskView, types.Task>,
    taskMatching: repos.MaybeMatchingBy<TaskView, types.Task>,
    mapId: number,
) {
    const taskView = taskViews.createEmptyView();
    const size = taskViews.sizeOf(taskView);

    const taskPrototypeToCreateTask = {
        ...taskPrototype,
        x: taskPrototype.x - size.x / 2,
        y: taskPrototype.y - size.y / 2,
    }

    const map: types.Map = {id: mapId};
    const task = await remoteTasks.createdTaskFrom(taskPrototypeToCreateTask, map);

    taskPrototypeDrawing.eraseFrom(mapView, taskPrototypeView);

    if (task === undefined) {
        logError(`A remote task on the map with id = ${mapId} could not be created`);
        notify("Try adding your task later");
        return;
    }

    taskDrawing.redrawBy(task, taskView);
    taskDrawing.drawOn(mapView, taskView);
    taskControllers.activeFor(taskView, task);

    taskMatching.match(taskView, task);
}
