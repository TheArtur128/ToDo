import * as apiClient from "./api-client.js";
import * as storages from "./storages.js";
import * as layout from "./layout.js";
import * as parsers from "./parsers.js";
import * as cases from "../core/cases.js";
import * as types from "../core/types.js";
import * as ports from "../core/ports.js";

export type InitTaskControllers = (s: layout.TaskSurface, facade: Facade) => any;
type _ShorterInitTaskControllers = (s: layout.TaskSurface) => any;

type _Tasks = storages.MatchingByHTMLElement<types.Task>;

export type TaskAddingControllers = {
    startingControllersOf(f: Facade): TaskAddingStartingControllers,
    continuationControllersOf(f: Facade): TaskAddingContinuationControllers,
}

export class Facade{
    private _taskGroup: storages.MatchingByHTMLElement<types.Task>;

    readonly taskGroups: ReturnType<typeof _taskGroupsOf>;
    readonly tasks: ReturnType<typeof _tasksOf>;
    readonly taskAdding: ReturnType<typeof _taskAddingOf>;

    constructor(
        initTaskControllers: InitTaskControllers,
        mapElement: layout.MapSurface,
        descriptionInputElement: storages.StorageHTMLElement,
        taskAddingControllers: TaskAddingControllers,
    ) {
        const shorterInitTaskControllers: _ShorterInitTaskControllers = (
            (s) => initTaskControllers(s, this)
        );
        this._taskGroup = new storages.MatchingByHTMLElement();

        this.taskGroups = _taskGroupsOf(mapElement, this._taskGroup, shorterInitTaskControllers);
        this.tasks = _tasksOf(this._taskGroup);
        this.taskAdding = _taskAddingOf(
            this._taskGroup,
            mapElement,
            descriptionInputElement,
            {
                initTaskControllers: shorterInitTaskControllers,
                startingControllers: taskAddingControllers.startingControllersOf(this),
                continuationControllers: taskAddingControllers.continuationControllersOf(this),
            },
        );
    }

    taskMovingFor(taskElement: layout.TaskSurface) {
        return _taskMovingOf(this._taskGroup, taskElement);
    }
}

function _taskGroupsOf(
    mapElement: layout.MapSurface,
    tasks: _Tasks,
    initTaskControllers: _ShorterInitTaskControllers,
) {
    const adapters: cases.maps.Ports<layout.MapSurface, layout.TaskSurface> = {
        getCurrentMapId: parsers.getCurrentMapId,
        remoteTasks: apiClient.tasks,
        show: alert,
        mapSurfaces: layout.maps.surfacesOf(mapElement),
        taskSurfaces: layout.tasks.surfaces,
        drawing: layout.tasks.drawing,
        logError: console.error,
        tasks: tasks,
        hangControllersOn: initTaskControllers,
    }

    return {
        draw: () => cases.maps.draw(adapters),
    }
}

function _tasksOf(tasks: _Tasks) {
    const adapters: cases.tasks.Ports<layout.MapSurface, layout.TaskSurface> = {
        tasks: tasks,
        logError: console.error,
        drawing: layout.tasks.drawing,
    }

    return {
        changeMode(taskSurface: layout.TaskSurface) {
            cases.tasks.changeMode(adapters, taskSurface);
        }
    }
}

function _taskMovingOf(
    tasks: _Tasks,
    taskElement: layout.TaskSurface,
) {
    const cursor = layout.tasks.taskSurfaceCursorFor(taskElement);

    if (cursor === undefined)
        return;

    const adapters: cases.taskMoving.Ports<layout.MapSurface, layout.TaskSurface> = {
        referencePointContainer: new storages.StorageContainer(),
        activationContainer: new storages.StorageContainer(),
        remoteFixationTimeoutContainer: new storages.StorageContainer(),
        remoteTasks: apiClient.tasks,
        tasks: tasks,
        cursor: cursor,
        drawing: layout.tasks.drawing,
    }

    return {
        prepare: () => cases.taskMoving.prepare(adapters, taskElement),
        cancel: () => cases.taskMoving.cancel(adapters, taskElement),
        start: (x: number, y: number) => cases.taskMoving.start(adapters, taskElement, x, y),
        handle: (x: number, y: number) => cases.taskMoving.handle(adapters, taskElement, x, y),
    }
}

export type TaskAddingStartingControllers = ports.Controllers<layout.Animation>;
export type TaskAddingContinuationControllers = ports.Controllers<layout.TaskPrototypeSurface>;

type _TaskAddingController = {
    initTaskControllers: _ShorterInitTaskControllers;
    startingControllers: TaskAddingStartingControllers,
    continuationControllers: TaskAddingContinuationControllers,
}

function _taskAddingOf(
    tasks: _Tasks,
    mapElement: layout.MapSurface,
    descriptionInputElement: storages.StorageHTMLElement,
    controllers: _TaskAddingController,
) {
    const adapters: cases.taskAdding.Ports<
        layout.MapSurface,
        layout.Animation,
        layout.TaskPrototypeSurface,
        layout.TaskSurface
    > = {
        mapSurface: mapElement,
        descriptionContainer: new storages.DescriptionAdapterContainer(
            new storages.HTMLElementValueContainer(descriptionInputElement)
        ),
        availabilityContainer: new storages.StorageContainer(),
        readinessAnimation: layout.taskAdding.createReadinessAnimation(),
        readinessAnimationDrawing: new layout.LazyStaticDrawing(),
        taskPrototypeSurfaces: layout.taskPrototypes.surfaces,
        taskPrototypeContainer: new storages.StorageContainer(),
        taskPrototypeSurfaceContainer: new storages.StorageContainer(),
        taskPrototypeDrawing: layout.taskPrototypes.drawing,
        logError: console.error,
        show: async (m: string) => await alert(m),
        getCurrentMapId: parsers.getCurrentMapId,
        remoteTasks: apiClient.tasks,
        taskSurfaces: layout.tasks.surfaces,
        taskDrawing: layout.tasks.drawing,
        startingControllers: controllers.startingControllers,
        continuationControllers: controllers.continuationControllers,
        tasks: tasks,
        hangControllersOn: controllers.initTaskControllers,
    }

    return {
        handleAvailability: () => cases.taskAdding.handleAvailability(adapters),
        start: (x: number, y: number) => cases.taskAdding.start(x, y, adapters),
        handle: (x: number, y: number) => cases.taskAdding.handle(x, y, adapters),
        complete: () => cases.taskAdding.complete(adapters),
    }
}
