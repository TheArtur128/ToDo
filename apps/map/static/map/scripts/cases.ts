import { Task, MapSize } from "./types.js";

export function initTaskListView(
    getCurrentMapId: () => number,
    tasksForMapWithId: (id: number) => Task[] | undefined,
    show: (m: string) => any,
    getCurrentMapSize: () => MapSize,
) {
    let tasks = tasksForMapWithId(getCurrentMapId());

    if (tasks === undefined) {
        show("At the moment you are freed from any tasks!");
        return;
    }
}
