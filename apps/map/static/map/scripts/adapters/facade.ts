import * as apiClient from "./api-client.js";
import * as repos from "./repos.js";
import * as layout from "./layout.js";
import * as parsers from "./parsers.js";
import * as messages from "./messages.js";
import * as cases from "../core/cases.js";
import * as types from "../core/types.js";
import * as controllers from "../core/ports/controllers.js";
import { Maybe } from "../fp.js";

export type TaskControllers = controllers.Controllers<layout.TaskView>;

export function createEmptyTasks() {
    return new repos.MatchingByHTMLElement();
}

export async function drawnMapOf<RootView, MapView, TaskView>(
    mapView?: Maybe<MapView>,
    mapId: number,
    taskControllers: TaskControllers,
    tasks: repos.MatchingByHTMLElement,
) {
    return cases.drawnMapOf(
        mapView,
        layout.maps.views,
        layout.maps.drawing,
        apiClient.tasks,
        layout.tasks.views,
        layout.tasks.drawing,
        taskControllers,
        tasks,
        messages.alertNotifications,
        messages.consoleErrorLogs,
        parsers.getCurrentMapId(),
    );
}

// export function changedTaskModeOf<MapView, TaskView>(
//     taskView: TaskView,
//     taskControllers: controllers.Controllers<TaskView>,
//     taskMatching: repos.MatchingBy<TaskView, types.Task>,
//     errorLogs: messages.Logs,
//     drawing: views.Drawing<MapView, TaskView, types.Task>

// export function changeTaskDescription<MapView, TaskView>(
//     taskMatching: repos.MatchingBy<TaskView, types.Task>,
//     drawing: views.Drawing<MapView, TaskView, types.Task>,
//     errorLogs: messages.Logs,
//     fixationTimeout: timeouts.Timeout,
//     remoteTasks: remoteRepos.RemoteTasks,
//     taskView: TaskView,
//     taskControllers: controllers.Controllers<TaskView>,
//     descriptionValue: string,
// ) {
//     let task = taskMatching.matchedWith(taskView);

//     if (task === undefined) {
//         return bad({
//             errorLogs: errorLogs.with("No matching between task and surface"),
//         });
//     }

//     const newDescription = types.Description.of(descriptionValue);

//     if (newDescription === undefined || task.description.value === newDescription.value)
//         return ok();

//     task = task.with({description: newDescription});
//     taskView = drawing.redrawnBy(task, taskView);
//     taskControllers = taskControllers.updatedFor(taskView);

//     taskMatching = taskMatching.withPair(taskView, task);

//     fixationTimeout = timeouts.updated(fixationTimeout, waitingForFix, async () => {
//         const updatedTask = await remoteTasks.withUpToDateDescription(task);

//         if (updatedTask !== undefined)
//             return ok();

//         const errorLog = "The remote task description could not be updated";
//         return bad({errorLogs: errorLogs.with(errorLog)});
//     });

//     return ok({
//         taskMatching: taskMatching,
//         taskControllers: taskControllers,
//         fixationTimeout: fixationTimeout,
//     });

// export function preparedTaskMovingOf<TaskView>(
//     taskMatching: repos.MatchingBy<TaskView, types.Task>,
//     cursor: views.Cursor,
//     taskView: TaskView,

// export function startedTaskMovingOf<TaskView>(
//     taskMatching: repos.MatchingBy<TaskView, types.Task>,
//     cursor: views.Cursor,
//     taskView: TaskView,
//     x: number,
//     y: number,

// export function canceledTaskMovingOf<TaskView>(
//     taskMatching: repos.MatchingBy<TaskView, types.Task>,
//     cursor: views.Cursor,
//     taskView: TaskView,

// export function movedTaskOf<MapView, TaskView>(
//     errorLogs: messages.Logs,
//     referencePoint: types.Vector,
//     fixationTimeout: timeouts.Timeout,
//     remoteTasks: remoteRepos.RemoteTasks,
//     taskMatching: repos.MatchingBy<TaskView, types.Task>,
//     drawing: views.Drawing<MapView, TaskView, types.Task>,
//     taskView: TaskView,
//     taskControllers: controllers.Controllers<TaskView>,
//     x: number,
//     y: number,

// export function taskAddingAvailabilityOf<MapView, ReadinessAnimation>(
//     availableInPast: boolean,
//     mapView: MapView,
//     descriptionValue: string,
//     readinessAnimation: ReadinessAnimation,
//     readinessAnimationDrawing: views.StaticDrawing<MapView, ReadinessAnimation>,
//     startingControllers: controllers.Controllers<ReadinessAnimation>,

// export function startedTaskAddingOf<MapView, ReadinessAnimation, TaskPrototypeView>(
//     mapView: MapView,
//     readinessAnimation: ReadinessAnimation,
//     readinessAnimationDrawing: views.StaticDrawing<MapView, ReadinessAnimation>,
//     taskPrototypeViews: views.Views<TaskPrototypeView>,
//     taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype>,
//     continuationControllers: controllers.Controllers<TaskPrototypeView>,
//     startingControllers: controllers.Controllers<ReadinessAnimation>,
//     descriptionValue: string,
//     x: number,
//     y: number,

// export function continuedTaskAddingOf<MapView, TaskPrototypeView>(
//     taskPrototypeViews: views.Views<TaskPrototypeView>,
//     taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype>,
//     taskPrototype: types.TaskPrototype,
//     taskPrototypeView: TaskPrototypeView,
//     continuationControllers: controllers.Controllers<TaskPrototypeView>,
//     x: number,
//     y: number,

// export async function completedTaskAddingOf<RootView, MapView, TaskPrototypeView, TaskView>(
//     mapView: MapView,
//     mapDrawing: views.Drawing<RootView, MapView, types.Map>,
//     taskPrototype: types.TaskPrototype,
//     taskPrototypeView: TaskPrototypeView,
//     taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype>,
//     errorLogs: messages.Logs,
//     notifications: messages.Notifications,
//     remoteTasks: remoteRepos.RemoteTasks,
//     taskViews: views.Views<TaskView>,
//     taskDrawing: views.Drawing<MapView, TaskView, types.Task>,
//     taskControllers: controllers.Controllers<TaskView>,
//     taskMatching: repos.MatchingBy<TaskView, types.Task>,
//     mapId: number,
