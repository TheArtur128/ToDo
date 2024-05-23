import * as domain from "../../core/domain.js";
import * as cases from "../../core/cases.js";
import * as controllers from "../../core/ports/controllers.js";
import * as apiClient from "../in/api-client.js";
import * as repos from "../in/repos.js";
import * as layout from "../in/layout.js";
import * as parsers from "../in/parsers.js";
import * as messages from "../in/messages.js";
import * as timeouts from "../in/timeouts.js";
import * as controllerBase from "./controllers/base.js";
import * as tools from "../../tools.js";

const _taskControllerMatching = new repos.MatchingFromMap<layout.TaskView, controllers.Controller[]>();
const _taskAddingAvailabilityControllerMatching = new repos.MatchingFromMap<
    layout.MapView,
    controllers.Controller
>();

const _mapViewMatching = new repos.MatchingFromMap<domain.Map, layout.MapView>();
const _taskMatching = new repos.MatchingFromMap<layout.TaskView, domain.Task>();

export function drawMap<TaskAddingElement extends layout.View>(
    mapRootElement: layout.View,
    taskAddingElement: TaskAddingElement,
    taskAddingAvailabilityControllerFor: controllers.StaticControllerFor<TaskAddingElement>,
    taskControllerFactories: controllers.ControllerFor<layout.TaskView, domain.Task>[],
): void {
    cases.drawMap(
        mapRootElement,
        _mapViewMatching,
        _taskControllerMatching,
        _taskAddingAvailabilityControllerMatching,
        layout.maps.views,
        layout.maps.presenter,
        apiClient.tasks,
        layout.tasks.views,
        layout.tasks.presenter,
        _taskMatching,
        taskControllerFactories,
        messages.asyncAlert,
        console.error,
        parsers.getCurrentMap,
        taskAddingElement,
        taskAddingAvailabilityControllerFor,
    )
}

export function changeTaskMode(taskElement: layout.TaskView): void {
    cases.changeTaskMode(
        taskElement,
        _taskMatching,
        console.error,
        layout.tasks.modeChangingPresenter,
    )
}

const _taskDescriptionTimeout = new timeouts.Timeout();

export function changeTaskDescription(taskElement: layout.TaskView, description: string): void {
    cases.changeTaskDescription(
        _taskMatching,
        layout.tasks.presenter,
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
        layout.tasks.readyToMovePresenter,
        taskElement,
    )
}

const _movingReferencePointMatching = new repos.MatchingFromMap<layout.TaskView, domain.Vector>();
const _movingControllerMatching = new repos.MatchingFromMap<
    layout.TaskView,
    controllers.Controller
>()

export function startTaskMoving(
    taskElement: layout.TaskView,
    taskMovingControllerFor: (view: layout.TaskView) => controllers.Controller,
    x: number,
    y: number,
): void {
    cases.startTaskMoving(
        _taskMatching,
        _movingReferencePointMatching,
        layout.tasks.movementPresenter,
        taskElement,
        new controllerBase.StaticControllerMatching(
            taskMovingControllerFor,
            _movingControllerMatching,
        ),
        x,
        y,
    )
}

export function cancelTaskMoving(taskElement: layout.TaskView): void {
    cases.cancelTaskMoving(_taskMatching, layout.tasks.staticPresenter, taskElement);
}

export function stopTaskMoving(
    taskElement: layout.TaskView,
    taskMovingControllerFor: controllers.StaticControllerFor<layout.TaskView>,
): void {
    cases.stopTaskMoving(
        _taskMatching,
        _movingReferencePointMatching,
        new controllerBase.StaticControllerMatching(
            taskMovingControllerFor,
            _movingControllerMatching,
        ),
        layout.tasks.readyToMovePresenter,
        taskElement,
    )
}

const _taskMovingTimeout = new timeouts.Timeout();

export function moveTask(taskElement: layout.TaskView, x: number, y: number): void {
    cases.moveTask(
        _taskMatching,
        _movingReferencePointMatching,
        console.error,
        _taskMovingTimeout,
        apiClient.tasks,
        layout.tasks.presenter,
        taskElement,
        x,
        y,
    )
}

const _pastTaskAddingAvailabilityMatching = new repos.BooleanMatching<layout.Animation>();
const _taskAddingReadinessAnimation = layout.taskAdding.createReadinessAnimation();
const _taskAddingReadinessAnimationPresenter = new layout.LazyStaticPresenter();
const _startingControllerMatching = new repos.MatchingFromMap<layout.Animation, controllers.Controller>();

export function handleTaskAddingAvailability(
    startingControllerFor: controllers.StaticControllerFor<layout.Animation>,
    readinessAnimationRootElement: layout.View,
    description: string,
): void {
    cases.handleTaskAddingAvailability(
        _pastTaskAddingAvailabilityMatching,
        description,
        readinessAnimationRootElement,
        _taskAddingReadinessAnimation,
        _taskAddingReadinessAnimationPresenter,
        new controllerBase.StaticControllerMatching(
            startingControllerFor,
            _startingControllerMatching,
        ),
    )
}

const _taskPrototypeViewMatching = new repos.MatchingFromMap<layout.MapView, layout.TaskPrototypeView>();
const _taskPrototypeMatching = new repos.MatchingFromMap<layout.TaskPrototypeView, domain.TaskPrototype>();
const _continuationControllerMatching = new repos.MatchingFromMap<
    layout.TaskPrototypeView,
    controllers.Controller
>();
const _completionControllerMatching = new repos.MatchingFromMap<
    layout.TaskPrototypeView,
    controllers.Controller
>();

export function startTaskAdding(
    startingControllerFor: controllers.StaticControllerFor<layout.Animation>,
    continuationControllerFor: controllers.StaticControllerFor<layout.TaskPrototypeView>,
    completionControllerFor: controllers.StaticControllerFor<layout.TaskPrototypeView>,
    readinessAnimationRootElement: layout.View,
    descriptionInputElement: tools.StorageHTMLElement,
    x: number,
    y: number,
): void {
    cases.startTaskAdding(
        _pastTaskAddingAvailabilityMatching,
        _mapViewMatching,
        readinessAnimationRootElement,
        _taskAddingReadinessAnimation,
        _taskAddingReadinessAnimationPresenter,
        layout.taskPrototypes.views,
        layout.taskPrototypes.presenter,
        new controllerBase.StaticControllerMatching(
            continuationControllerFor,
            _continuationControllerMatching,
        ),
        new controllerBase.StaticControllerMatching(
            startingControllerFor,
            _startingControllerMatching,
        ),
        new controllerBase.StaticControllerMatching(
            completionControllerFor,
            _completionControllerMatching,
        ),
        new repos.HTMLElementValueContainer(descriptionInputElement),
        parsers.getCurrentMap,
        _taskPrototypeViewMatching,
        _taskPrototypeMatching,
        x,
        y,
    )
}

export function continueTaskAdding(x: number, y: number): void {
    cases.continueTaskAdding(
        parsers.getCurrentMap,
        _mapViewMatching,
        _taskPrototypeViewMatching,
        _taskPrototypeMatching,
        layout.taskPrototypes.views,
        layout.taskPrototypes.presenter,
        x,
        y,
    )
}

export async function completeTaskAdding(
    continuationControllerFor: controllers.StaticControllerFor<layout.TaskPrototypeView>,
    taskControllerFactories: controllers.ControllerFor<layout.TaskView, domain.Task>[],
): Promise<void> {
    cases.completeTaskAdding(
        _mapViewMatching,
        _taskPrototypeViewMatching,
        _taskPrototypeMatching,
        layout.taskPrototypes.presenter,
        console.error,
        messages.asyncAlert,
        apiClient.tasks,
        layout.tasks.views,
        layout.tasks.presenter,
        _taskMatching,
        parsers.getCurrentMap,
        new controllerBase.StaticControllerMatching(
            continuationControllerFor,
            _continuationControllerMatching,
        ),
        _taskControllerMatching,
        taskControllerFactories,
    )
}
