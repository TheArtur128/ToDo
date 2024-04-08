import { MessageShowing, Surfaces, Drawing } from "./ports.js";
import { Task, Map } from "./types.js";

export async function drawMap<MapSurfaceT, TaskSurfaceT>(
    getCurrentMapId: () => number,
    tasksForMapWithId: (id: number) => Promise<Task[] | undefined>,
    messageShowing: MessageShowing,
    surfaces: Surfaces<MapSurfaceT, TaskSurfaceT>,
    drawing: Drawing<MapSurfaceT, TaskSurfaceT>
): Promise<boolean> {
    let map: Map = {id: getCurrentMapId()};

    const exitOf = (value: any): value is undefined => {
        const errorMessage = "At the moment you are freed from any tasks!";

        if (value !== undefined)
            return false;

        if (!messageShowing.isWasShown(errorMessage)) {
            messageShowing.show(errorMessage);
            messageShowing.setWasShown(errorMessage);
        }

        return true;
    }

    let tasks = await tasksForMapWithId(map.id);
    if (exitOf(tasks))
        return false;

    let mapSurface = <MapSurfaceT>surfaces.mapOf(map);
    if (exitOf(mapSurface))
        return false;

    tasks.forEach(task => {
        let taskSurface = surfaces.taskSurfaceOn(mapSurface, task.id);

        if (taskSurface !== undefined) {
            drawing.redraw(taskSurface, task);
            return;
        }

        taskSurface = surfaces.getEmptyTaskSurface();
        drawing.redraw(taskSurface, task);
        drawing.drawOn(mapSurface, taskSurface);        
    });

    return true;
}
