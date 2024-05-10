import { Maybe, on } from "../../fp.js";

export type Iterable<Value> = {
    [Symbol.iterator](): Iterator<Value>;
}

export type AsyncIterable<Value> = {
    [Symbol.asyncIterator](): AsyncIterator<Value>;
}

export type Matching<Key, Value> = {
    matchedWith(key: Key): Maybe<Value>;
    withPair(key: Key, value: Value): Matching<Key, Value>;
}

export type Container<Value> = {
    _with(value: Maybe<Value>): Container<Value>,
    _get(): Maybe<Value>,
}

export function valueOf<Value>(container: Container<Value>): Maybe<Value> {
    return container._get();
}

export function with_<Value>(
    value: Maybe<Value>,
    container: Container<Value>,
): Container<Value> {
    return container._with(value);
}

export function mapped<Value>(
    container: Container<Value>,
    transformed: (v: Maybe<Value>) => Maybe<Value>
): Container<Value> {
    return with_(transformed(valueOf(container)), container);
}

export function withDefault<Value>(
    defaultValue: Maybe<Value>,
    container: Container<Value>,
): Container<Value> {
    return mapped(container, on(undefined, defaultValue));
}

export function popFrom<Value>(container: Container<Value>): [Maybe<Value>, Container<Value>] {
    const value = valueOf(container);

    if (value !== undefined)
        container = with_(undefined, container);

    return [value, container];
}
