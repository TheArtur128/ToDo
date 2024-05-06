import * as facade from "../adapters/facade.js";

export function initAvailabilityControllers(
    taskAdding: facade.TaskAdding,
    activatingElement: HTMLElement,
): void {
    activatingElement.addEventListener("input", () => {
        taskAdding.handleAvailability();
    });
}

export const dynamicTaskAddingControllers: facade.TaskAddingControllers = {
    startingControllersOf(taskAdding: facade.TaskAdding): facade.TaskAddingStartingControllers {
        const start = (event: PointerEvent) => {
            taskAdding.start(event.clientX, event.clientY);
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

    continuationControllersOf(
        taskAdding: facade.TaskAdding,
    ): facade.TaskAddingContinuationControllers {
        const handle = (event: PointerEvent) => taskAdding.handle(event.clientX, event.clientY);
        const complete = () => taskAdding.complete();

        return {
            hangOn(activatingElement: HTMLElement): void {
                activatingElement.addEventListener("pointermove", handle);
                activatingElement.addEventListener("pointerup", complete);
            },

            removeFrom(activatingElement: HTMLElement): void {
                activatingElement.removeEventListener("pointermove", handle);
                activatingElement.removeEventListener("pointerup", complete);
            },
        }
    },
}
