import * as types from "../core/types.js";

export async function tasksForMapWithId(
  mapId: number,
): Promise<types.Task[] | undefined> {
  return _tasksFrom(`/api/0.1v/map/top-maps/${mapId}/tasks/`);
}

async function _tasksFrom(url: string): Promise<types.Task[] | undefined> {
  let response = await fetch(url);

  if (!response.ok)
    return undefined;

  let tasks: types.Task[] = [];

  let responseData = await response.json();

  tasks = tasks.concat(responseData.results);

  if (responseData.next === null)
    return tasks;

  let nextTasks = await _tasksFrom(responseData.next);
  if (nextTasks === undefined)
    return tasks;

  return tasks.concat(nextTasks);
}
