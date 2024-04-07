import * as downloaders from "./downloaders.js";
import * as parsers from "./parsers.js";
import * as renderers from "./renderers.js";
import * as cases from "../core/cases.js";

export function drawMap(mapSurface: renderers.MapDOMSurface): void {
    let domRendering = new renderers.DOMRendering(mapSurface);

    cases.drawMap(
        parsers.getCurrentMapId,
        downloaders.tasksForMapWithId,
        new renderers.MessageShowingWithCachedSearching(alert),
        domRendering,
        domRendering,
    );
}
