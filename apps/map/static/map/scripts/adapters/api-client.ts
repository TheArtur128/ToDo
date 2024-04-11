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

    async tasksForMapWithId(
      mapId: number,
    ): Promise<types.Task[] | undefined> {
      return this._tasksFrom(this._topMapTaskEndpointURLWith(mapId));
    },

    async _tasksFrom(url: string): Promise<types.Task[] | undefined> {
      let response = await fetch(url);

      if (!response.ok)
        return undefined;

      let tasks: types.Task[] = [];

      let responseData = await response.json();

      tasks = tasks.concat(responseData.results);

      if (responseData.next === null)
        return tasks;

      let nextTasks = await this._tasksFrom(responseData.next);
      if (nextTasks === undefined)
        return tasks;

      return tasks.concat(nextTasks);
    },

    _topMapTaskEndpointURLWith(mapId: number): string {
        return `/api/0.1v/map/top-maps/${mapId}/tasks/`;
    },
}
