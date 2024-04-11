import * as apiClient from "./api-client.js";
import * as sockets from "./sockets.js";
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
    _taskPrototypeSocket: new sockets.SocketContainer<types.TaskPrototype>(),
    _taskPrototypeSurfaceSocket: new sockets.SocketContainer<domServices.TaskPrototypeSurface>(),
    _descriptionTemporarySocket: new sockets.SocketContainer<string>(),

    start(
        mapElement: domServices.MapSurface,
        descriptionInputElement: sockets.HTMLElementContainer,
        x: number,
        y: number,
    ): boolean {
        return cases.taskAdding.start(
            x,
            y,
            new sockets.HTMLElementSocket(descriptionInputElement),
            this._descriptionTemporarySocket,
            parsers.getCurrentMapId,
            showing.alertShowing,
            domServices.maps.surfacesOf(mapElement),
            domServices.taskPrototypes.surfaces,
            domServices.taskPrototypes.drawing,
            this._taskPrototypeSocket,
            this._taskPrototypeSurfaceSocket,
        );
    },

    cancel(
        mapElement: domServices.MapSurface,
        descriptionInputElement: sockets.HTMLElementContainer
    ): void {
        cases.taskAdding.cancel(
            new sockets.HTMLElementSocket(descriptionInputElement),
            this._descriptionTemporarySocket,
            parsers.getCurrentMapId,
            this._taskPrototypeSocket,
            this._taskPrototypeSurfaceSocket,
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
            this._taskPrototypeSocket,
            this._taskPrototypeSurfaceSocket,
            domServices.taskPrototypes.drawing,
        );
    },

    complete(mapElement: domServices.MapSurface): Promise<boolean> {
        return cases.taskAdding.complete(
            parsers.getCurrentMapId,
            showing.alertShowing,
            this._taskPrototypeSocket,
            this._taskPrototypeSurfaceSocket,
            domServices.taskPrototypes.drawing,
            domServices.tasks.drawing,
            domServices.maps.surfacesOf(mapElement),
            domServices.tasks.surfaces,
            apiClient.tasks,
        );
    },
}
