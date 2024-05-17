import * as repos from "../../core/ports/repos.js";
import { Maybe } from "../../sugar.js";

export class WeakMapMatching<Key extends WeakKey, Value> implements repos.MaybeMatchingBy<Key, Value> {
    constructor(private _storage: WeakMap<Key, Value> = new WeakMap()) {}

    matchedWith(key: Key): Maybe<Value> {
        return this._storage.get(key);
    }

    match(key: Key, value: Value): void {
        this._storage.set(key, value);
    }

    dontMatchWith(key: Key): void {
        this._storage.delete(key);
    }
}

export class BooleanMatching<Key> implements repos.MatchingBy<Key, boolean> {
    constructor(private _keys: Set<Key> = new Set()) {}

    matchedWith(key: Key): boolean {
        return this._keys.has(key);
    }

    match(key: Key, value: boolean): void {
        if (value)
            this._keys.add(key);
        else
            this._keys.delete(key);
    }
}

export type StorageHTMLElement = HTMLElement & {value: string}

export class HTMLElementValueContainer implements repos.Container<string> {
    constructor(private _storageElement: StorageHTMLElement) {}

    set(value: string) {
        this._storageElement.value = value;
    }

    get(): string {
        return this._storageElement.value;
    }
}
