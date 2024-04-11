import * as apiClient from "./api-client.js";
import * as parsers from "./parsers.js";
import * as renderers from "./renderers.js";
import * as cases from "../core/cases.js";

export function drawMap(mapSurface: renderers.MapSurface): Promise<boolean> {
    return cases.drawMap(
        parsers.getCurrentMapId,
        apiClient.tasks,
        new renderers.MessageShowingWithCachedSearching(alert),
        renderers.maps.surfacesOf(mapSurface),
        renderers.tasks.surfaces,
        renderers.tasks.drawing,
    );
}
