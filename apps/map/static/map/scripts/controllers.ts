import * as facade from "./adapters/facade.js";
import * as tools from "./tools.js";

export function initTaskAddingView(
    centerElement: HTMLElement,
    mapElement: HTMLDivElement,
    descriptionInputElement: HTMLInputElement | HTMLTextAreaElement,
): void {
    const taskAdding = facade.taskAddingOf(mapElement, descriptionInputElement);

    centerElement.addEventListener("mousedown", taskAdding.prepare);

    centerElement.addEventListener("mouseleave", event => {
        taskAdding.start(event.clientX, event.clientY);
    });

    centerElement.addEventListener("mouseenter", event => {
        if (event.target === centerElement)
            taskAdding.stop();
    });

    document.addEventListener("mousemove", event => {
        if (!tools.isInDOMOf(centerElement, event.target))
            taskAdding.handle(event.clientX, event.clientY);
    });

    document.addEventListener("mouseup", event => {
        if (tools.isInDOMOf(centerElement, event.target))
            taskAdding.cancel();
        else
            taskAdding.complete();
    });
}
