import * as facade from "../adapters/facade.js";

export function initAvailabilityControllers(
    facade: facade.Facade,
    activatingElement: HTMLElement,
): void {
    activatingElement.addEventListener("input", () => {
        facade.taskAdding.handleAvailability();
    });
}

export const dynamicControllers: facade.TaskAddingControllers = {
    startingControllersOf(facade: facade.Facade): facade.TaskAddingStartingControllers {
        const start = (event: PointerEvent) => {
            facade.taskAdding.start(event.clientX, event.clientY);
        }

        return {
            hangOn(activatingElement: HTMLElement): void {
                activatingElement.addEventListener("pointerdown", start);
            },

            removeFrom(activatingElement: HTMLElement): void {
                activatingElement.removeEventListener("pointerdown", start);
            },
        }
    },

    continuationControllersOf(facade: facade.Facade): facade.TaskAddingContinuationControllers {
        const handle = (event: PointerEvent) => {
            facade.taskAdding.handle(event.clientX, event.clientY);
        }
        const complete = () => facade.taskAdding.complete();

        return {
            hangOn(activatingElement: HTMLElement): void {
                document.addEventListener("pointermove", handle);
                activatingElement.addEventListener("pointerup", complete);
            },

            removeFrom(activatingElement: HTMLElement): void {
                document.removeEventListener("pointermove", handle);
                activatingElement.removeEventListener("pointerup", complete);
            },
        }
    },
}
