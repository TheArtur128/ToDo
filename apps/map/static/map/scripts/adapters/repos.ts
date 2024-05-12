import * as repos from "../core/ports/repos.js";
import { Dirty, Maybe } from "../fp.js";

export class MatchingByHTMLElement<Value> implements repos.MatchingBy<HTMLElement, Value> {
    private _storage: Record<string, Value>;

    constructor() {
        this._storage = {};
    }

    matchedWith(element: HTMLElement): Maybe<Value> {
        return this._storage[element.id];
    }

    withPair(element: HTMLElement, value: Value): Dirty<MatchingByHTMLElement<Value>> {
        this._storage[element.id] = value;
        return this;
    }
}
