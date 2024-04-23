import * as facade from "./adapters/facade.js";

export function initTaskAddingView(
    centerElement: HTMLElement,
    mapElement: HTMLDivElement,
    descriptionInputElement: HTMLInputElement | HTMLTextAreaElement,
): void {
    const taskAdding = facade.taskAddingOf(mapElement, descriptionInputElement);

    centerElement.addEventListener("mousedown", taskAdding.prepare);

    centerElement.addEventListener("mouseout", event => {
        taskAdding.start(event.clientX, event.clientY);
    });

    centerElement.addEventListener("mouseover", taskAdding.stop);

    document.addEventListener("mousemove", event => {
        if (event.target !== centerElement)
            taskAdding.handle(event.clientX, event.clientY);
    });

    document.addEventListener("mouseup", event => {
        if (event.target === centerElement)
            taskAdding.cancel();
        else
            taskAdding.complete();
    });
}
