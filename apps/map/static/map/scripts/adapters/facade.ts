import * as apiClient from "./api-client.js";
import * as storages from "./storages.js";
import * as layout from "./layout.js";
import * as parsers from "./parsers.js";
import * as cases from "../core/cases.js";
import * as types from "../core/types.js";
import * as ports from "../core/ports.js";

export class Tasks {
    private _tasks: storages.MatchingByHTMLElement<types.Task>;
    private _mapAdapters: cases.maps.Ports<layout.MapSurface, layout.TaskSurface>;
    private _taskAdapters: cases.tasks.Ports<layout.MapSurface, layout.TaskSurface>;

    constructor(
        mapElement: layout.MapSurface,
        initTaskControllers: (s: layout.TaskSurface, tasks: Tasks) => any,
    ) {
        this._tasks = new storages.MatchingByHTMLElement<types.Task>();

        this._mapAdapters = {
            getCurrentMapId: parsers.getCurrentMapId,
            remoteTasks: apiClient.tasks,
            show: alert,
            mapSurfaces: layout.maps.surfacesOf(mapElement),
            taskSurfaces: layout.tasks.surfaces,
            drawing: layout.tasks.drawing,
            logError: console.error,
            tasks: this._tasks,
            hangControllersOn: surface => initTaskControllers(surface, this)
        }

        this._taskAdapters = {
            tasks: this._tasks,
            logError: console.error,
            drawing: layout.tasks.drawing,
        }
    }

    draw() {
        cases.maps.draw(this._mapAdapters)
    }

    changeMode(taskSurface: layout.TaskSurface) {
        cases.tasks.changeMode(this._taskAdapters, taskSurface);
    }

    movingFor(taskElement: layout.TaskSurface) {
        const cursor = layout.tasks.taskSurfaceCursorFor(taskElement);

        if (cursor === undefined)
            return;

        const adapters: cases.taskMoving.Ports<layout.MapSurface, layout.TaskSurface> = {
            referencePointContainer: new storages.StorageContainer(),
            activationContainer: new storages.StorageContainer(),
            remoteFixationTimeoutContainer: new storages.StorageContainer(),
            remoteTasks: apiClient.tasks,
            tasks: this._tasks,
            cursor: cursor,
            drawing: layout.tasks.drawing,
        }

        return {
            prepare: () => cases.taskMoving.prepare(adapters, taskElement),
            cancel: () => cases.taskMoving.cancel(adapters, taskElement),
            start(x: number, y: number) {
                cases.taskMoving.start(adapters, taskElement, x, y);
            },
            handle(x: number, y: number) {
                cases.taskMoving.handle(adapters, taskElement, x, y);
            },
        }
    }
}

export type TaskAddingStartingControllers = ports.Controllers<layout.Animation>;
export type TaskAddingContinuationControllers = ports.Controllers<layout.TaskPrototypeSurface>;

export type TaskAddingControllers = {
    startingControllersOf(t: TaskAdding): TaskAddingStartingControllers,
    continuationControllersOf(t: TaskAdding): TaskAddingContinuationControllers,
}

export class TaskAdding {
    private _readnessAnimation = layout.taskAdding.createReadinessAnimation();
    private _adapters: cases.taskAdding.Ports<
        layout.MapSurface,
        layout.Animation,
        layout.TaskPrototypeSurface,
        layout.TaskSurface
    >;

    constructor(
        mapElement: layout.MapSurface,
        descriptionInputElement: storages.StorageHTMLElement,
        controllers: TaskAddingControllers,
    ) {
        this._adapters = {
            mapSurface: mapElement,
            descriptionContainer: new storages.DescriptionAdapterContainer(
                new storages.HTMLElementValueContainer(descriptionInputElement)
            ),
            availabilityContainer: new storages.StorageContainer(),
            readinessAnimation: this._readnessAnimation,
            readinessAnimationDrawing: new layout.LazyStaticDrawing(),
            cursor: layout.globalCursor,
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
            startingControllers: controllers.startingControllersOf(this),
            continuationControllers: controllers.continuationControllersOf(this),
        };
    }

    handleAvailability(): void {
        cases.taskAdding.handleAvailability(this._adapters);
    }

    start(x: number, y: number): void {
        cases.taskAdding.start(x, y, this._adapters);
    }

    handle(x: number, y: number): void {
        cases.taskAdding.handle(x, y, this._adapters);
    }

    complete(): void {
        cases.taskAdding.complete(this._adapters);
    }
}
