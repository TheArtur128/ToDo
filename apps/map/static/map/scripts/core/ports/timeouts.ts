import { Maybe, Dirty, dirty } from "../../fp.js";
import { Container } from "./repos.js";

export type Waiting = number;
export type TimeoutId = number;
export type Timeout = Maybe<TimeoutId>;

export function updated(
    timeout: Timeout,
    waiting: Waiting,
    callback: () => any,
): Dirty<TimeoutId> {
    if (timeout !== undefined)
        clearTimeout(timeout);

    const timeoutId = setTimeout(callback, waiting);
    return dirty(timeoutId);
}

