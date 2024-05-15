import * as repos from "../core/ports/repos.js";
import { Maybe } from "../fp.js";

export class MatchingByHTMLElement<Value> implements repos.MatchingBy<HTMLElement, Value> {
    private constructor(private _storage: Record<string, Value>) {}

    static get empty(): MatchingByHTMLElement<undefined> {
        return new MatchingByHTMLElement({});
    }

    matchedWith(element: HTMLElement): Maybe<Value> {
        return this._storage[element.id];
    }

    matchingBetween<NewValue>(element: HTMLElement, value: NewValue): MatchingByHTMLElement<Value | NewValue> {
        const storageWithPair = {...this._storage, [element.id]: value}

        return new MatchingByHTMLElement(storageWithPair);
    }
}
