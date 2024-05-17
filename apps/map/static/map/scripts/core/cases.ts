import * as domain from "./domain.js";
import * as controllers from "./ports/controllers.js";
import * as messages from "./ports/messages.js";
import * as remoteRepos from "./ports/remote-repos.js";
import * as repos from "./ports/repos.js";
import * as timeouts from "./ports/timeouts.js";
import * as views from "./ports/views.js";

const fixationTime: timeouts.Milliseconds = 600;

export async function drawMap<MapRootView, MapView, TaskView, TaskAddingView>(
    mapRootView: MapRootView,
    mapViewMatching: repos.MaybeMatchingBy<domain.Map, MapView>,
    mapViews: views.Views<MapView>,
    mapDrawing: views.Drawing<MapRootView, MapView, domain.Map>,
    remoteTasks: remoteRepos.RemoteTasks,
    taskViews: views.Subviews<MapView, TaskView, domain.Task>,
    taskDrawing: views.Drawing<MapView, TaskView, domain.Task>,
    taskMatching: repos.MaybeMatchingBy<TaskView, domain.Task>,
    taskControllers: controllers.ControllersFor<TaskView, domain.Task>,
    notify: messages.Notify,
    logError: messages.Log,
    getCurrentMap: () => domain.Map,
    matchingForMapViewHasTaskAdding: repos.MatchingBy<MapView, boolean>,
    taskAddingView: TaskAddingView,
    taskAddingAvailabilityControllers: controllers.ControllersForStatic<TaskAddingView>,
): Promise<void> {
    const map: domain.Map = getCurrentMap();
    let mapView = mapViewMatching.matchedWith(map);

    if (mapView !== undefined)
        mapDrawing.redrawBy(map, mapView);
    else {
        mapView = mapViews.createEmptyView();
        mapDrawing.redrawBy(map, mapView);
        mapDrawing.drawOn(mapRootView, mapView);

        mapViewMatching.match(map, mapView);
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

    if (matchingForMapViewHasTaskAdding.matchedWith(mapView))
        taskAddingAvailabilityControllers.updateFor(taskAddingView);
    else {
        taskAddingAvailabilityControllers.activeFor(taskAddingView);
        matchingForMapViewHasTaskAdding.match(mapView, true);
    }
}

export function changeTaskMode<MapView, TaskView>(
    view: TaskView,
    controllers: controllers.ControllersFor<TaskView, domain.Task>,
    matching: repos.MaybeMatchingBy<TaskView, domain.Task>,
    logError: messages.Log,
    drawing: views.Drawing<MapView, TaskView, domain.Task>
): void {
    let task = matching.matchedWith(view);

    if (task === undefined) {
        logError("No matching between task and view");
        return;
    }

    task.changeMode();

    drawing.redrawBy(task, view);
    controllers.updateFor(view, task);
}

export function changeTaskDescription<MapView, TaskView>(
    taskMatching: repos.MaybeMatchingBy<TaskView, domain.Task>,
    drawing: views.Drawing<MapView, TaskView, domain.Task>,
    controllers: controllers.ControllersFor<TaskView, domain.Task>,
    logError: messages.Log,
    fixationTimeout: timeouts.Timeout,
    remoteTasks: remoteRepos.RemoteTasks,
    taskView: TaskView,
    descriptionValue: string,
): void {
    let task = taskMatching.matchedWith(taskView);

    if (task === undefined) {
        logError("No matching between task and view");
        return;
    }

    const newDescription = domain.Description.of(descriptionValue);

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

export function prepareTaskMoving<TaskView>(
    taskMatching: repos.MaybeMatchingBy<TaskView, domain.Task>,
    cursor: views.Cursor,
    taskView: TaskView,
): void {
    const task = taskMatching.matchedWith(taskView);

    if (task?.mode === domain.InteractionMode.moving)
        cursor.setToGrab();
}

export function startTaskMoving<TaskView>(
    taskMatching: repos.MaybeMatchingBy<TaskView, domain.Task>,
    referencePointMatching: repos.MaybeMatchingBy<TaskView, domain.Vector>,
    cursor: views.Cursor,
    taskView: TaskView,
    taskMovingControllers: controllers.ControllersFor<TaskView, domain.Task>,
    x: number,
    y: number,
): void {
    const task = taskMatching.matchedWith(taskView);

    if (task?.mode !== domain.InteractionMode.moving)
        return;

    referencePointMatching.match(taskView, new domain.Vector(x, y));

    cursor.setGrabbed();
    taskMovingControllers.activeFor(taskView, task);
}

export function cancelTaskMoving<TaskView>(
    taskMatching: repos.MaybeMatchingBy<TaskView, domain.Task>,
    referencePointMatching: repos.MaybeMatchingBy<TaskView, domain.Vector>,
    cursor: views.Cursor,
    taskMovingControllers: controllers.ControllersFor<TaskView, domain.Task>,
    taskView: TaskView,
): void {
    const task = taskMatching.matchedWith(taskView);

    if (task?.mode !== domain.InteractionMode.moving)
        return;

    referencePointMatching.dontMatchWith(taskView);

    taskMovingControllers.removeFrom(taskView, task);
    cursor.setDefault();
}

export function moveTask<MapView, TaskView>(
    taskMatching: repos.MaybeMatchingBy<TaskView, domain.Task>,
    referencePointMatching: repos.MaybeMatchingBy<TaskView, domain.Vector>,
    logError: messages.Log,
    fixationTimeout: timeouts.Timeout,
    remoteTasks: remoteRepos.RemoteTasks,
    drawing: views.Drawing<MapView, TaskView, domain.Task>,
    taskView: TaskView,
    taskControllers: controllers.ControllersFor<TaskView, domain.Task>,
    taskMovingControllers: controllers.ControllersFor<TaskView, domain.Task>,
    x: number,
    y: number,
): void {
    const task = taskMatching.matchedWith(taskView);
    const referencePoint = referencePointMatching.matchedWith(taskView);

    if (task?.mode !== domain.InteractionMode.moving)
        return;

    if (referencePoint === undefined) {
        logError(`the moving of task with id = ${task.id} was not started`);
        return;
    }

    let taskPosition = new domain.Vector(task.x, task.y);
    const newReferencePoint = new domain.Vector(x, y);

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

export function handleTaskAddingAvailability<ReadinessAnimationRoot, ReadinessAnimation>(
    pastAvailabilityMatching: repos.MatchingBy<ReadinessAnimation, boolean>,
    descriptionValue: string,
    readinessAnimationRoot: ReadinessAnimationRoot,
    readinessAnimation: ReadinessAnimation,
    readinessAnimationDrawing: views.StaticDrawing<ReadinessAnimationRoot, ReadinessAnimation>,
    startingControllers: controllers.ControllersForStatic<ReadinessAnimation>,
): void {
    const description = domain.Description.of(descriptionValue);

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

export function startTaskAdding<MapView, ReadinessAnimation, ReadinessAnimationRoot, TaskPrototypeView>(
    pastAvailabilityMatching: repos.MatchingBy<ReadinessAnimation, boolean>,
    mapViewMatching: repos.MaybeMatchingBy<domain.Map, MapView>,
    readinessAnimationRoot: ReadinessAnimationRoot,
    readinessAnimation: ReadinessAnimation,
    readinessAnimationDrawing: views.StaticDrawing<ReadinessAnimationRoot, ReadinessAnimation>,
    taskPrototypeViews: views.Views<TaskPrototypeView>,
    taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, domain.TaskPrototype>,
    continuationControllers: controllers.ControllersFor<TaskPrototypeView, domain.TaskPrototype>,
    startingControllers: controllers.ControllersForStatic<ReadinessAnimation>,
    descriptionValueContainer: repos.Container<string>,
    getCurrentMap: () => domain.Map,
    x: number,
    y: number,
): void {
    const mapView = mapViewMatching.matchedWith(getCurrentMap());
    const description = domain.Description.of(descriptionValueContainer.get());

    if (description === undefined || mapView === undefined)
        return;

    descriptionValueContainer.set('');

    pastAvailabilityMatching.match(readinessAnimation, false);
    readinessAnimationDrawing.eraseFrom(readinessAnimationRoot, readinessAnimation);
    startingControllers.removeFrom(readinessAnimation);

    const taskPrototype: domain.TaskPrototype = {description: description, x: x, y: y};

    const taskPrototypeView = taskPrototypeViews.createEmptyView();
    taskPrototypeDrawing.redrawBy(taskPrototype, taskPrototypeView);
    taskPrototypeDrawing.drawOn(mapView, taskPrototypeView);

    continuationControllers.activeFor(taskPrototypeView, taskPrototype);
}

export function continueTaskAdding<MapView, TaskPrototypeView>(
    continuationControllers: controllers.ControllersFor<TaskPrototypeView, domain.TaskPrototype>,
    taskPrototypeViews: views.Views<TaskPrototypeView>,
    taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, domain.TaskPrototype>,
    taskPrototype: domain.TaskPrototype,
    taskPrototypeView: TaskPrototypeView,
    x: number,
    y: number,
): void {
    taskPrototype = {...taskPrototype, x: x, y: y};

    const size = taskPrototypeViews.sizeOf(taskPrototypeView);
    const taskPrototypeToPresent = {
        ...taskPrototype, x: x - size.x / 2, y: y - size.y / 2
    };

    taskPrototypeDrawing.redrawBy(taskPrototypeToPresent, taskPrototypeView);
    continuationControllers.updateFor(taskPrototypeView, taskPrototype);
}

export async function completeTaskAdding<RootView, MapView, TaskPrototypeView, TaskView>(
    mapViewMatching: repos.MaybeMatchingBy<domain.Map, MapView>,
    taskPrototype: domain.TaskPrototype,
    taskPrototypeView: TaskPrototypeView,
    taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, domain.TaskPrototype>,
    logError: messages.Log,
    notify: messages.Notify,
    remoteTasks: remoteRepos.RemoteTasks,
    taskViews: views.Views<TaskView>,
    taskDrawing: views.Drawing<MapView, TaskView, domain.Task>,
    taskControllers: controllers.ControllersFor<TaskView, domain.Task>,
    taskMatching: repos.MaybeMatchingBy<TaskView, domain.Task>,
    getCurrentMap: () => domain.Map,
): Promise<void> {
    const map: domain.Map = getCurrentMap();
    const mapView = mapViewMatching.matchedWith(map);

    if (mapView === undefined)
        return;

    const taskView = taskViews.createEmptyView();
    const size = taskViews.sizeOf(taskView);

    const taskPrototypeToCreateTask = {
        ...taskPrototype,
        x: taskPrototype.x - size.x / 2,
        y: taskPrototype.y - size.y / 2,
    }

    const task = await remoteTasks.createdTaskFrom(taskPrototypeToCreateTask, map);

    taskPrototypeDrawing.eraseFrom(mapView, taskPrototypeView);

    if (task === undefined) {
        logError(`A remote task on the map with id = ${map.id} could not be created`);
        notify("Try adding your task later");
        return;
    }

    taskDrawing.redrawBy(task, taskView);
    taskDrawing.drawOn(mapView, taskView);
    taskControllers.activeFor(taskView, task);

    taskMatching.match(taskView, task);
}
