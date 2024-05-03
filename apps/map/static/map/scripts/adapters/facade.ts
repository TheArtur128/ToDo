import * as apiClient from "./api-client.js";
import * as storages from "./storages.js";
import * as layout from "./layout.js";
import * as parsers from "./parsers.js";
import * as cases from "../core/cases.js";
import * as types from "../core/types.js";

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

export function taskAddingOf(
    mapElement: layout.MapSurface,
    descriptionInputElement: storages.StorageHTMLElement,
) {
    const adapters: cases.taskAdding.Ports<
        layout.MapSurface,
        layout.TaskPrototypeSurface,
        layout.TaskSurface
    > = {
        stateContainer: new storages.StorageContainer(cases.taskAdding.State.waiting),
        descriptionContainer: new storages.DescriptionAdapterContainer(
            new storages.HTMLElementValueContainer(descriptionInputElement)
        ),
        taskPrototypeContainer: new storages.StorageContainer<types.TaskPrototype>(),
        taskPrototypeSurfaceContainer: new storages.StorageContainer<layout.TaskPrototypeSurface>(),
        getCurrentMapId: parsers.getCurrentMapId,
        show: async (message: string) => await alert(message),
        mapSurfaces: layout.maps.surfacesOf(mapElement),
        taskPrototypeSurfaces: layout.taskPrototypes.surfaces,
        taskSurfaces: layout.tasks.surfaces,
        taskPrototypeDrawing: layout.taskPrototypes.drawing,
        taskDrawing: layout.tasks.drawing,
        remoteTasks: apiClient.tasks,
        logError: console.error,
        cursor: layout.globalCursor,
    };

    return {
        prepare: () => cases.taskAdding.prepare(adapters),
        start: (x: number, y: number) => cases.taskAdding.start(x, y, adapters),
        stop: () => cases.taskAdding.stop(adapters),
        cancel: () => cases.taskAdding.cancel(adapters),
        handle: (x: number, y: number) => cases.taskAdding.handle(x, y, adapters),
        complete: () => cases.taskAdding.complete(adapters),
    }
}
