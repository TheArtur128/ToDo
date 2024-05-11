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
    readonly value: Maybe<Value>,
    with(value: Maybe<Value>): Container<Value>,
}

export function mapped<Value>(
    container: Container<Value>,
    transformed: (v: Maybe<Value>) => Maybe<Value>
): Container<Value> {
    return container.with(transformed(container.value));
}

export function withDefault<Value>(
    defaultValue: Maybe<Value>,
    container: Container<Value>,
): Container<Value> {
    return mapped(container, on(undefined, defaultValue));
}

export function popFrom<Value>(container: Container<Value>): [Maybe<Value>, Container<Value>] {
    const value = container.value;

    if (value !== undefined)
        container = container.with(value);

    return [value, container];
}
