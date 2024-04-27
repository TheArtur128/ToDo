import * as apiClient from "./api-client.js";
import * as containers from "./containers.js";
import * as domServices from "./dom-services.js";
import * as parsers from "./parsers.js";
import * as cases from "../core/cases.js";
import * as types from "../core/types.js";

export function tasksOf(mapElement: domServices.MapSurface) {
    const adapters: cases.maps.Ports<domServices.MapSurface, domServices.TaskSurface> = {
        getCurrentMapId: parsers.getCurrentMapId,
        remoteTasks: apiClient.tasks,
        show: alert,
        mapSurfaces: domServices.maps.surfacesOf(mapElement),
        taskSurfaces: domServices.tasks.surfaces,
        drawing: domServices.tasks.drawing,
    }

    return {
        draw: () => cases.maps.draw(adapters),
    }
}

export function taskAddingOf(
    mapElement: domServices.MapSurface,
    descriptionInputElement: containers.StorageHTMLElement,
) {
    const adapters: cases.taskAdding.Ports<
        domServices.MapSurface,
        domServices.TaskPrototypeSurface,
        domServices.TaskSurface
    > = {
        stateContainer: new containers.StorageContainer(cases.taskAdding.State.waiting),
        descriptionContainer: new containers.DescriptionAdapterContainer(
            new containers.HTMLElementValueContainer(descriptionInputElement)
        ),
        taskPrototypeContainer: new containers.StorageContainer<types.TaskPrototype>(),
        taskPrototypeSurfaceContainer: new containers.StorageContainer<domServices.TaskPrototypeSurface>(),
        getCurrentMapId: parsers.getCurrentMapId,
        show: alert,
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
