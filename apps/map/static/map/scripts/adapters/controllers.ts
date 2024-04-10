import * as api from "./api.js";
import * as parsers from "./parsers.js";
import * as renderers from "./renderers.js";
import * as cases from "../core/cases.js";

export function drawMap(mapSurface: renderers.DOM.MapSurface): Promise<boolean> {
    return cases.drawMap(
        parsers.getCurrentMapId,
        api.client,
        new renderers.MessageShowingWithCachedSearching(alert),
        renderers.DOM.mapSurfacesOf(mapSurface),
        renderers.DOM.taskSurfaces,
        renderers.DOM.taskDrawing,
    );
}
