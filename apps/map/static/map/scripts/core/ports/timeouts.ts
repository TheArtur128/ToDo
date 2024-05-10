import { Container, valueOf, with_ } from "./repos.ts";

type TimeoutId = number;

export function withUpdatedTimeoutIn(
    timeoutContainer: Container<TimeoutId>,
    milliseconds: number,
    callback: () => any,
): Container<TimeoutId> {
    const timeout = valueOf(timeoutContainer);

    if (timeout !== undefined)
        clearTimeout(timeout);

    const newTimeoutId = setTimeout(callback, milliseconds);
    return with_(newTimeoutId, timeoutContainer);
}

export function withUpdatedRemoteFixationTimeoutIn(
    timeoutContainer: Container<number>,
    callback: () => any,
): Container<TimeoutId> {
    return withUpdatedTimeoutIn(timeoutContainer, 600, callback);
}
