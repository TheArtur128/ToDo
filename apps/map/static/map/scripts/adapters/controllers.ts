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
