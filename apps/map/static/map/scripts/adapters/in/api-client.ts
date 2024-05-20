import * as remoteRepos from "../../core/ports/remote-repos.js";
import * as domain from "../../core/domain.js";
import * as tools from "../../tools.js";
import { Maybe } from "../../sugar.js";

const _urls = {
    topMapTaskEndpointURLWith(mapId: number): string {
        return `/api/0.1v/map/top-maps/${mapId}/tasks/`;
    },

    taskEndpointURLFor(task: domain.Task): string {
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
        taskPrototype: domain.TaskPrototype,
        map: domain.Map,
    ): remoteRepos.Remote<domain.Task> {
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
            return;

        return this._sculptureTaskOf(await response.json());
    },

    tasksOn(map: domain.Map): remoteRepos.RemoteIterable<domain.Task> {
        return this._tasksFrom(_urls.topMapTaskEndpointURLWith(map.id));
    },

    async withUpToDatePosition(task: domain.Task): remoteRepos.Remote<domain.Task> {
        const response = await fetch(_urls.taskEndpointURLFor(task), {
            method: 'PATCH',
            headers: _headers.dispatchHeaders,
            body: JSON.stringify({x: Math.round(task.x), y: Math.round(task.y)})
        })

        if (response.ok)
            return task;
    },

    async withUpToDateDescription(task: domain.Task): remoteRepos.Remote<domain.Task> {
        const response = await fetch(_urls.taskEndpointURLFor(task), {
            method: 'PATCH',
            headers: _headers.dispatchHeaders,
            body: JSON.stringify({description: task.description.value})
        })

        if (response.ok)
            return task;
    },

    async _tasksFrom(url: string): remoteRepos.RemoteIterable<domain.Task> {
        const response = await fetch(url);
        const responseData = await response.json();

        if (!(response.ok && responseData?.results instanceof Array))
            return;

        return this._parsedTasksFrom(responseData?.results, responseData?.next);
    },

    async *_parsedTasksFrom(results: any[], next: any): AsyncGenerator<Maybe<domain.Task>> {
        for (const taskData of results)
            yield this._sculptureTaskOf(taskData);

        if (typeof next === "string") {
            const tasks = await this._tasksFrom(next);

            if (tasks !== undefined)
                yield* tasks;
        }
    },

    _sculptureTaskOf(taskData: any): Maybe<domain.Task> {
        const id = taskData?.id;
        let description = taskData?.description;
        const x = taskData?.x;
        const y = taskData?.y;

        if (typeof id !== "number" || typeof x !== "number" || typeof y !== "number")
            return;

        if (typeof description === "string")
            description = domain.Description.of(description);

            if (description === undefined)
                return

        if (!(description instanceof domain.Description))
            return;

        return new domain.Task(id, description, x, y);
    },
}
