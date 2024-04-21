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

export const taskAdding = {
    _taskPrototypeContainer: new containers.StorageContainer<types.TaskPrototype>(),
    _taskPrototypeSurfaceContainer: new containers.StorageContainer<domServices.TaskPrototypeSurface>(),
    _descriptionTemporaryContainer: new containers.StorageContainer<string>(),

    start(
        mapElement: domServices.MapSurface,
        descriptionInputElement: containers.StorageHTMLElement,
        x: number,
        y: number,
    ): boolean {
        return cases.taskAdding.start(
            x,
            y,
            new containers.HTMLElementValueContainer(descriptionInputElement),
            this._descriptionTemporaryContainer,
            parsers.getCurrentMapId,
            showing.alertShowing,
            domServices.maps.surfacesOf(mapElement),
            domServices.taskPrototypes.surfaces,
            domServices.taskPrototypes.drawing,
            this._taskPrototypeContainer,
            this._taskPrototypeSurfaceContainer,
        );
    },

    cancel(
        mapElement: domServices.MapSurface,
        descriptionInputElement: containers.StorageHTMLElement
    ): void {
        cases.taskAdding.cancel(
            new containers.HTMLElementValueContainer(descriptionInputElement),
            this._descriptionTemporaryContainer,
            parsers.getCurrentMapId,
            this._taskPrototypeContainer,
            this._taskPrototypeSurfaceContainer,
            domServices.taskPrototypes.drawing,
            domServices.maps.surfacesOf(mapElement),
            loggers.consoleLogger,
        )
    },

    handle(x: number, y: number): boolean {
        return cases.taskAdding.handle(
            x,
            y,
            showing.alertShowing,
            this._taskPrototypeContainer,
            this._taskPrototypeSurfaceContainer,
            domServices.taskPrototypes.drawing,
        );
    },

    complete(mapElement: domServices.MapSurface): Promise<boolean> {
        return cases.taskAdding.complete(
            parsers.getCurrentMapId,
            showing.alertShowing,
            this._taskPrototypeContainer,
            this._taskPrototypeSurfaceContainer,
            domServices.taskPrototypes.drawing,
            domServices.tasks.drawing,
            domServices.maps.surfacesOf(mapElement),
            domServices.tasks.surfaces,
            apiClient.tasks,
        );
    },
}
