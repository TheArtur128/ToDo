import * as domain from "../../core/domain.js";
import * as cases from "../../core/cases.js";
import * as controllers from "../../core/ports/controllers.js";
import * as apiClient from "../in/api-client.js";
import * as repos from "../in/repos.js";
import * as layout from "../in/layout.js";
import * as parsers from "../in/parsers.js";
import * as messages from "../in/messages.js";
import * as timeouts from "../in/timeouts.js";

const _mapViewMatching = new repos.WeakMapMatching<domain.Map, layout.MapView>();
const _taskMatching = new repos.WeakMapMatching<layout.TaskView, domain.Task>();
const _matchingForMapViewHasTaskAdding = new repos.BooleanMatching<layout.MapView>();

export function drawMap<TaskAddingElement extends layout.View>(
    taskControllers: controllers.ControllersFor<layout.TaskView, domain.Task>,
    taskAddingAvailabilityControllers: controllers.ControllersForStatic<TaskAddingElement>,
    taskAddingElement: TaskAddingElement,
    mapRootElement: layout.View,
): void {
    cases.drawMap(
        mapRootElement,
        _mapViewMatching,
        layout.maps.views,
        layout.maps.drawing,
        apiClient.tasks,
        layout.tasks.views,
        layout.tasks.drawing,
        _taskMatching,
        taskControllers,
        messages.asyncAlert,
        console.error,
        parsers.getCurrentMap,
        _matchingForMapViewHasTaskAdding,
        taskAddingElement,
        taskAddingAvailabilityControllers,
    )
}

export function changeTaskMode(
    taskElement: layout.TaskView,
    taskControllers: controllers.ControllersFor<layout.TaskView, domain.Task>,
): void {
    cases.changeTaskMode(
        taskElement,
        taskControllers,
        _taskMatching,
        console.error,
        layout.tasks.drawing,
    )
}

const _taskDescriptionTimeout = new timeouts.Timeout();

export function changeTaskDescription(
    taskControllers: controllers.ControllersFor<layout.TaskView, domain.Task>,
    taskElement: layout.TaskView,
    description: string,
): void {
    cases.changeTaskDescription(
        _taskMatching,
        layout.tasks.drawing,
        taskControllers,
        console.error,
        _taskDescriptionTimeout,
        apiClient.tasks,
        taskElement,
        description,
    )
}

export function prepareTaskMoving(taskElement: layout.TaskView): void {
    cases.prepareTaskMoving(
        _taskMatching,
        layout.tasks.cursorFor(taskElement),
        taskElement,
    )
}

const _movingReferencePointMatching = new repos.WeakMapMatching<layout.TaskView, domain.Vector>();

export function startTaskMoving(
    taskElement: layout.TaskView,
    taskMovingControllers: controllers.ControllersFor<layout.TaskView, domain.Task>,
    x: number,
    y: number,
): void {
    cases.startTaskMoving(
        _taskMatching,
        _movingReferencePointMatching,
        layout.tasks.cursorFor(taskElement),
        taskElement,
        taskMovingControllers,
        x,
        y,
    )
}

export function cancelTaskMoving(
    taskMovingControllers: controllers.ControllersFor<layout.TaskView, domain.Task>,
    taskElement: layout.TaskView,
): void {
    cases.cancelTaskMoving(
        _taskMatching,
        _movingReferencePointMatching,
        layout.tasks.cursorFor(taskElement),
        taskMovingControllers,
        taskElement,
    )
}

const _taskMovingTimeout = new timeouts.Timeout();

export function moveTask(
    taskElement: layout.TaskView,
    taskControllers: controllers.ControllersFor<layout.TaskView, domain.Task>,
    taskMovingControllers: controllers.ControllersFor<layout.TaskView, domain.Task>,
    x: number,
    y: number,
): void {
    cases.moveTask(
        _taskMatching,
        _movingReferencePointMatching,
        console.error,
        _taskMovingTimeout,
        apiClient.tasks,
        layout.tasks.drawing,
        taskElement,
        taskControllers,
        taskMovingControllers,
        x,
        y,
    )
}

const _pastTaskAddingAvailabilityMatching = new repos.BooleanMatching<layout.Animation>();
const _taskAddingReadinessAnimation = layout.taskAdding.createReadinessAnimation();
const _taskAddingReadinessAnimationDrawing = new layout.LazyStaticDrawing();

export function handleTaskAddingAvailability(
    readinessAnimationRootElement: layout.View,
    description: string,
    startingControllers: controllers.ControllersForStatic<layout.Animation>,
): void {
    cases.handleTaskAddingAvailability(
        _pastTaskAddingAvailabilityMatching,
        description,
        readinessAnimationRootElement,
        _taskAddingReadinessAnimation,
        _taskAddingReadinessAnimationDrawing,
        startingControllers,
    )
}

export function startTaskAdding(
    continuationControllers: controllers.ControllersFor<layout.TaskPrototypeView, domain.TaskPrototype>,
    startingControllers: controllers.ControllersForStatic<layout.Animation>,
    readinessAnimationRootElement: layout.View,
    descriptionInputElement: repos.StorageHTMLElement,
    x: number,
    y: number,
): void {
    cases.startTaskAdding(
        _pastTaskAddingAvailabilityMatching,
        _mapViewMatching,
        readinessAnimationRootElement,
        _taskAddingReadinessAnimation,
        _taskAddingReadinessAnimationDrawing,
        layout.taskPrototypes.views,
        layout.taskPrototypes.drawing,
        continuationControllers,
        startingControllers,
        new repos.HTMLElementValueContainer(descriptionInputElement),
        parsers.getCurrentMap,
        x,
        y,
    )
}

export function continueTaskAdding(
    continuationControllers: controllers.ControllersFor<layout.TaskPrototypeView, domain.TaskPrototype>,
    taskPrototypeElement: layout.TaskPrototypeView,
    taskPrototype: domain.TaskPrototype,
    x: number,
    y: number,
): void {
    cases.continueTaskAdding(
        continuationControllers,
        layout.taskPrototypes.views,
        layout.taskPrototypes.drawing,
        taskPrototype,
        taskPrototypeElement,
        x,
        y,
    )
}

export async function completeTaskAdding(
    taskPrototype: domain.TaskPrototype,
    taskPrototypeElement: layout.TaskPrototypeView,
    taskControllers: controllers.ControllersFor<layout.TaskPrototypeView, domain.Task>,
): Promise<void> {
    cases.completeTaskAdding(
        _mapViewMatching,
        taskPrototype,
        taskPrototypeElement,
        layout.taskPrototypes.drawing,
        console.error,
        messages.asyncAlert,
        apiClient.tasks,
        layout.tasks.views,
        layout.tasks.drawing,
        taskControllers,
        _taskMatching,
        parsers.getCurrentMap,
    )
}
