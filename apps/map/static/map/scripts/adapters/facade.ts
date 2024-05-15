import * as apiClient from "./api-client.js";
import * as repos from "./repos.js";
import * as layout from "./layout.js";
import * as parsers from "./parsers.js";
import * as messages from "./messages.js";
import * as cases from "../core/cases.js";
import * as types from "../core/types.js";
import * as controllers from "../core/ports/controllers.js";
import { Maybe } from "../fp.js";

export type Map = {
    readonly mapElement: layout.MapView,
    readonly tasks: repos.MatchingByHTMLElement<types.Task>,
    
}

export async function drawMap(
    rootElement: layout.View,

    mapViews: views.Views<MapView>,
    mapDrawing: views.Drawing<MapRootView, MapView, types.Map>,
    remoteTasks: remoteRepos.RemoteTasks,
    taskViews: views.Subviews<MapView, TaskView, types.Task>,
    taskDrawing: views.Drawing<MapView, TaskView, types.Task>,
    taskMatching: EntityMatching<TaskView, types.Task>,
    taskControllerMatching: ControllerMatching<TaskView, types.Task>,
    notifications: messages.Notifications,
    errorLogs: messages.Logs,
    mapId: number,
) {
    cases.drawnMapOf(rootElement, )
}

// export async function drawnMapOf<MapRootView, MapView, TaskView>(
//     mapRootView: MapRootView,
//     mapView: Maybe<MapView>,
//     mapViews: views.Views<MapView>,
//     mapDrawing: views.Drawing<MapRootView, MapView, types.Map>,
//     remoteTasks: remoteRepos.RemoteTasks,
//     taskViews: views.Subviews<MapView, TaskView, types.Task>,
//     taskDrawing: views.Drawing<MapView, TaskView, types.Task>,
//     taskMatching: EntityMatching<TaskView, types.Task>,
//     taskControllerMatching: ControllerMatching<TaskView, types.Task>,
//     notifications: messages.Notifications,
//     errorLogs: messages.Logs,
//     mapId: number,
// ) {
// export function changedTaskModeOf<MapView, TaskView>(
//     taskView: TaskView,
//     taskControllerMatching: ControllerMatching<TaskView, types.Task>,
//     taskMatching: EntityMatching<TaskView, types.Task>,
//     errorLogs: messages.Logs,
//     drawing: views.Drawing<MapView, TaskView, types.Task>
// ) 
// export function changedTaskDescriptionOf<MapView, TaskView>(
//     taskMatching: EntityMatching<TaskView, types.Task>,
//     taskControllerMatching: ControllerMatching<TaskView, types.Task>,
//     drawing: views.Drawing<MapView, TaskView, types.Task>,
//     errorLogs: messages.Logs,
//     fixationTimeout: timeouts.Timeout,
//     remoteTasks: remoteRepos.RemoteTasks,
//     taskView: TaskView,
//     descriptionValue: string,
// ) 
// export function preparedTaskMovingOf<TaskView>(
//     taskMatching: EntityMatching<TaskView, types.Task>,
//     cursor: views.Cursor,
//     taskView: TaskView,
// ) 
// export function startedTaskMovingOf<TaskView>(
//     taskMatching: EntityMatching<TaskView, types.Task>,
//     cursor: views.Cursor,
//     taskView: TaskView,
//     x: number,
//     y: number,
// ) 
// export function canceledTaskMovingOf<TaskView>(
//     taskMatching: EntityMatching<TaskView, types.Task>,
//     cursor: views.Cursor,
//     taskView: TaskView,
// ) 
// export function movedTaskOf<MapView, TaskView>(
//     errorLogs: messages.Logs,
//     referencePoint: types.Vector,
//     fixationTimeout: timeouts.Timeout,
//     remoteTasks: remoteRepos.RemoteTasks,
//     taskMatching: EntityMatching<TaskView, types.Task>,
//     drawing: views.Drawing<MapView, TaskView, types.Task>,
//     taskView: TaskView,
//     taskControllerMatching: ControllerMatching<TaskView, types.Task>,
//     x: number,
//     y: number,
// ) 
// export function taskAddingAvailabilityOf<MapView, ReadinessAnimation>(
//     availableInPast: boolean,
//     mapView: MapView,
//     descriptionValue: string,
//     readinessAnimation: ReadinessAnimation,
//     readinessAnimationDrawing: views.StaticDrawing<MapView, ReadinessAnimation>,
//     startingControllers: controllers.StaticControllers<ReadinessAnimation>,
// ) 
// export function startedTaskAddingOf<MapView, ReadinessAnimation, TaskPrototypeView>(
//     mapView: MapView,
//     readinessAnimation: ReadinessAnimation,
//     readinessAnimationDrawing: views.StaticDrawing<MapView, ReadinessAnimation>,
//     taskPrototypeViews: views.Views<TaskPrototypeView>,
//     taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype>,
//     continuationControllers: controllers.Controllers<TaskPrototypeView, types.TaskPrototype>,
//     startingControllers: controllers.StaticControllers<ReadinessAnimation>,
//     descriptionValue: string,
//     x: number,
//     y: number,
// ) 
// export function continuedTaskAddingOf<MapView, TaskPrototypeView>(
//     taskPrototype: types.TaskPrototype,
//     taskPrototypeView: TaskPrototypeView,
//     continuationControllers: controllers.Controllers<TaskPrototypeView, types.TaskPrototype>,
//     taskPrototypeViews: views.Views<TaskPrototypeView>,
//     taskPrototypeDrawing: views.Drawing<MapView, TaskPrototypeView, types.TaskPrototype>,
//     x: number,
//     y: number,
// ) 
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
//     taskControllerMatching: ControllerMatching<TaskView, types.Task>,
//     taskMatching: EntityMatching<TaskView, types.Task>,
//     mapId: number,
// ) 