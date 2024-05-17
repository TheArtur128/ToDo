import { Maybe } from "../../sugar.js";
import * as domain from "../domain.js";

export type Remote<Value> = Promise<Maybe<Value>>
export type RemoteIterable<Value> = Promise<Maybe<AsyncGenerator<Maybe<Value>>>>

export type RemoteTasks = {
    tasksOn(map: domain.Map): RemoteIterable<domain.Task>,
    createdTaskFrom(prototype: domain.TaskPrototype, map: domain.Map): Remote<domain.Task>,
    withUpToDatePosition(task: domain.Task): Remote<domain.Task>,
    withUpToDateDescription(task: domain.Task): Remote<domain.Task>,
}
