import { Maybe, Impure } from "../../fp.js";

export type Waiting = number;
export type TimeoutId = number;
export type Timeout = Maybe<TimeoutId>;

export function updated(
    timeout: Timeout,
    waiting: Waiting,
    callback: () => any,
): Impure<TimeoutId> {
    if (timeout !== undefined)
        clearTimeout(timeout);

    const timeoutId = setTimeout(callback, waiting);
    return timeoutId;
}
