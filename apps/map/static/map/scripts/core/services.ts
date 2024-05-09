import { Container, Drawing } from "./ports.js";

export function popFrom<Value>(container: Container<Value>): Value | undefined {
    let value = container.get();

    if (value !== undefined)
        container.set(undefined);

    return value;
}

export function setDefaultAt<Value>(
    container: Container<Value>,
    defaultValue: Value,
): void {
    let storedValue = container.get();

    if (storedValue === undefined)
        container.set(defaultValue);
}

export function renderOn<MapSurface, Surface, Value>(
    mapSurface: MapSurface,
    surface: Surface | undefined,
    value: Value,
    surfaces: {getEmpty(): Surface},
    drawing: Drawing<MapSurface, Surface, Value>,
): Surface {
    if (surface === undefined) {
        surface = surfaces.getEmpty();
        drawing.redraw(surface, value);
        drawing.drawOn(mapSurface, surface);
    }
    else
        drawing.redraw(surface, value);

    return surface;
}

export function updateTimeout(timeoutContainer: Container<number>, milliseconds: number, callback: () => any) {
    const timeout = timeoutContainer.get();

    if (timeout !== undefined)
        clearTimeout(timeout);

    timeoutContainer.set(setTimeout(callback, milliseconds));
}

export function updateRemoteFixationTimeout(timeoutContainer: Container<number>, callback: () => any) {
    updateTimeout(timeoutContainer, 600, callback);
}
