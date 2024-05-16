import { Maybe } from "../../sugar.js";
import * as types from "../types.js";

export type Remote<Value> = Promise<Maybe<Value>>
export type RemoteIterable<Value> = Promise<Maybe<AsyncGenerator<Maybe<Value>>>>

export type RemoteTasks = {
    tasksOn(map: types.Map): RemoteIterable<types.Task>,
    createdTaskFrom(prototype: types.TaskPrototype, map: types.Map): Remote<types.Task>,
    withUpToDatePosition(task: types.Task): Remote<types.Task>,
    withUpToDateDescription(task: types.Task): Remote<types.Task>,
}
