import * as apiClient from "./api-client.js";
import * as containers from "./containers.js";
import * as domServices from "./dom-services.js";
import * as loggers from "./loggers.js";
import * as parsers from "./parsers.js";
import * as showing from "./showing.js";
import * as cases from "../core/cases.js";
import * as types from "../core/types.js";

export function drawMap(mapElement: domServices.MapSurface): Promise<boolean> {
    return cases.drawMap(
        parsers.getCurrentMapId,
        apiClient.tasks,
        showing.alertShowing,
        domServices.maps.surfacesOf(mapElement),
        domServices.tasks.surfaces,
        domServices.tasks.drawing,
    );
}

export type TaskAdding = cases.TaskAdding<
    domServices.MapSurface,
    domServices.TaskPrototypeSurface,
    domServices.TaskSurface
>;

export function taskAddingOf(
    mapElement: domServices.MapSurface,
    descriptionInputElement: containers.StorageHTMLElement,
): TaskAdding {
    return new cases.TaskAdding(
        new containers.HTMLElementValueContainer(descriptionInputElement),
        new containers.StorageContainer<string>(),
        new containers.StorageContainer<types.TaskPrototype>(),
        new containers.StorageContainer<domServices.TaskPrototypeSurface>(),
        parsers.getCurrentMapId,
        showing.alertShowing,
        domServices.maps.surfacesOf(mapElement),
        domServices.taskPrototypes.surfaces,
        domServices.tasks.surfaces,
        domServices.taskPrototypes.drawing,
        domServices.tasks.drawing,
        apiClient.tasks,
        loggers.consoleLogger,
        domServices.cursor,
    );
}
