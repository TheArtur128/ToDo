export function initTaskAddingView(centerElement: HTMLElement): void {
    var isAdding = false;

    centerElement.addEventListener("mousedown", () => {
        isAdding = true;

        document.querySelectorAll('*').forEach(element => {
            if (!(element instanceof HTMLElement))
                return;

            element.style.setProperty("cursor", "grabbing", "important");
        })
    });

    document.addEventListener("mouseup", (event: MouseEvent) => {
        if (!isAdding)
            return;

        document.querySelectorAll('*').forEach(element => {
            if (!(element instanceof HTMLElement))
                return;

            element.style.setProperty("cursor", '', '');
        })
    });
}
