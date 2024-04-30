import * as apiClient from "./api-client.js";
import * as storages from "./storages.js";
import * as domServices from "./dom-services.js";
import * as parsers from "./parsers.js";
import * as cases from "../core/cases.js";
import * as types from "../core/types.js";


export class Tasks {
    _mapAdapters: cases.maps.Ports<domServices.MapSurface, domServices.TaskSurface>;
    _taskAdaperts: cases.tasks.Ports<domServices.MapSurface, domServices.TaskSurface>;

    constructor(
        mapElement: domServices.MapSurface,
        initTaskControllers: (s: domServices.TaskSurface, tasks: Tasks) => any,
    ) {
        const tasks = new storages.MatchingByHTMLElement<types.Task>();

        this._mapAdapters = {
            getCurrentMapId: parsers.getCurrentMapId,
            remoteTasks: apiClient.tasks,
            show: alert,
            mapSurfaces: domServices.maps.surfacesOf(mapElement),
            taskSurfaces: domServices.tasks.surfaces,
            drawing: domServices.tasks.drawing,
            logError: console.error,
            tasks: tasks,
            hangControllersOn: surface => initTaskControllers(surface, this)
        }

        this._taskAdaperts = {
            tasks: tasks,
            logError: console.error,
            drawing: domServices.tasks.drawing,
        }
    }

    draw() {
        cases.maps.draw(this._mapAdapters)
    }

    changeMode(taskSurface: domServices.TaskSurface) {
        cases.tasks.changeMode(this._taskAdaperts, taskSurface);
    }
}

export function taskAddingOf(
    mapElement: domServices.MapSurface,
    descriptionInputElement: storages.StorageHTMLElement,
) {
    const adapters: cases.taskAdding.Ports<
        domServices.MapSurface,
        domServices.TaskPrototypeSurface,
        domServices.TaskSurface
    > = {
        stateContainer: new storages.StorageContainer(cases.taskAdding.State.waiting),
        descriptionContainer: new storages.DescriptionAdapterContainer(
            new storages.HTMLElementValueContainer(descriptionInputElement)
        ),
        taskPrototypeContainer: new storages.StorageContainer<types.TaskPrototype>(),
        taskPrototypeSurfaceContainer: new storages.StorageContainer<domServices.TaskPrototypeSurface>(),
        getCurrentMapId: parsers.getCurrentMapId,
        show: async (message: string) => await alert(message),
        mapSurfaces: domServices.maps.surfacesOf(mapElement),
        taskPrototypeSurfaces: domServices.taskPrototypes.surfaces,
        taskSurfaces: domServices.tasks.surfaces,
        taskPrototypeDrawing: domServices.taskPrototypes.drawing,
        taskDrawing: domServices.tasks.drawing,
        remoteTasks: apiClient.tasks,
        logError: console.error,
        cursor: domServices.cursor,
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
