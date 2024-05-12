import * as remoteRepos from "../core/ports/remote-repos.js";
import * as types from "../core/types.js";
import * as tools from "../tools.js";

const _urls = {
    topMapTaskEndpointURLWith(mapId: number): string {
        return `/api/0.1v/map/top-maps/${mapId}/tasks/`;
    },

    taskEndpointURLFor(task: types.Task): string {
        return `/api/0.1v/map/tasks/${task.id}/`
    }
}

namespace _headers {
    export const csrfProtectionHeaders = {"X-Csrftoken": tools.originalCookies["csrftoken"]}

    export const receivingHeaders = {'Content-Type': 'application/json'}
    export const dispatchHeaders = {...receivingHeaders, ...csrfProtectionHeaders}
}

export const tasks = {
    async createdTaskFrom(
        taskPrototype: types.TaskPrototype,
        map: types.Map,
    ): remoteRepos.Remote<types.Task> {
        const url = _urls.topMapTaskEndpointURLWith(map.id);

        const response = await fetch(url, {
          method: 'POST',
          headers: _headers.dispatchHeaders,
          body: JSON.stringify({
                description: taskPrototype.description.value,
                x: Math.round(taskPrototype.x),
                y: Math.round(taskPrototype.y),
            })
        })

        if (!response.ok)
            return undefined;

        return this._taskOf(await response.json());
    },

    tasksOn(map: types.Map): remoteRepos.RemoteIterable<types.Task> {
        return this._tasksFrom(_urls.topMapTaskEndpointURLWith(map.id));
    },

    async withUpToDatePosition(task: types.Task): remoteRepos.Remote<types.Task> {
        const response = await fetch(_urls.taskEndpointURLFor(task), {
            method: 'PATCH',
            headers: _headers.dispatchHeaders,
            body: JSON.stringify({x: Math.round(task.x), y: Math.round(task.y)})
        })

        return response.ok ? task : undefined;
    },

    async withUpToDateDescription(task: types.Task): remoteRepos.Remote<types.Task> {
        const response = await fetch(_urls.taskEndpointURLFor(task), {
            method: 'PATCH',
            headers: _headers.dispatchHeaders,
            body: JSON.stringify({description: task.description.value})
        })

        return response.ok ? task : undefined;
    },

    async _tasksFrom(url: string): remoteRepos.RemoteIterable<types.Task> {
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

        return new types.Task(id, description, x, y);
    },
}
