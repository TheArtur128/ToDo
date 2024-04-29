import * as ports from "../core/ports.js";
import * as types from "../core/types.js";

export const tasks = {
    async createdTaskFrom(
        taskPrototype: types.TaskPrototype,
        mapId: number,
    ): ports.Remote<types.Task> {
        const url = this._topMapTaskEndpointURLWith(mapId);

        const response = await fetch(url, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
                description: taskPrototype.description,
                status_code: 1,
                x: taskPrototype.x,
                y: taskPrototype.y,
            })
        })

        if (!response.ok)
            return undefined;

        return this._taskOf(await response.json());
    },

    tasksForMapWithId(mapId: number): ports.RemoteIterable<types.Task> {
        return this._tasksFrom(this._topMapTaskEndpointURLWith(mapId));
    },

    async _tasksFrom(url: string): ports.RemoteIterable<types.Task> {
        const response = await fetch(url);
        const responseData = await response.json();

        if (!(response.ok && responseData?.results instanceof Array))
            return undefined;

        return this._parsedTasksFrom(responseData?.results, responseData?.next);
    },

    async *_parsedTasksFrom(results: any[], next: any): AsyncGenerator<types.Task | undefined> {
        for (const taskData of results)
            yield this._taskOf(taskData);

        if (typeof next === "string") {
            const tasks = await this._tasksFrom(next);

            if (tasks !== undefined)
                yield* tasks;
        }
    },

    _topMapTaskEndpointURLWith(mapId: number): string {
        return `/api/0.1v/map/top-maps/${mapId}/tasks/`;
    },

    _taskOf(taskData: any): types.Task | undefined {
        const id = taskData?.id;
        let description = taskData?.description;
        const x = taskData?.x;
        const y = taskData?.y;

        if (typeof id !== "number" || typeof x !== "number" || typeof y !== "number")
            return undefined;

        if (typeof description === "string")
            try {
                description = new types.Description(description);
            }
            catch (MapError) {
                return undefined;
            }

        if (!(description instanceof types.Description))
            return undefined;

        return <types.Task>{id: id, description: description, x: x, y: y}
    },
}
