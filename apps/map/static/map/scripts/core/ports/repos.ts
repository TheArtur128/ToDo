import { Maybe } from "../../sugar.js";

export type MatchingBy<Key, Value> = {
    matchedWith(key: Key): Value;
    match(key: Key, value: Value): void;
}

export type MaybeMatchingBy<Key, Value> = {
    matchedWith(key: Key): Maybe<Value>;
    match(key: Key, value: Value): void;
    dontMatchWith(key: Key): void;
}

export type Container<Value> = {
    set(value: Value): any,
    get(): Value,
}
