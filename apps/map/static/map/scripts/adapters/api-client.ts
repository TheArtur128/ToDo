import * as types from "../core/types.js";

export const tasks = {
    async createdTaskFrom(
        taskPrototype: types.TaskPrototype,
        mapId: number,
    ): Promise<types.Task | undefined> {
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

        const responseData = await response.json();

        return <types.Task>{
            id: responseData.id,
            description: responseData.description,
            x: responseData.x,
            y: responseData.y,
        }
    },

    tasksForMapWithId(mapId: number): AsyncGenerator<types.Task | undefined> {
        return this._tasksFrom(this._topMapTaskEndpointURLWith(mapId));
    },

    async *_tasksFrom(url: string): AsyncGenerator<types.Task | undefined> {
        let response = await fetch(url);

        if (!response.ok) {
            yield undefined;
            return;
        }

        let responseData = await response.json();

        yield* responseData.results;

        if (responseData.next !== null)
            yield* this._tasksFrom(responseData.next);
    },

    _topMapTaskEndpointURLWith(mapId: number): string {
        return `/api/0.1v/map/top-maps/${mapId}/tasks/`;
    },
}
