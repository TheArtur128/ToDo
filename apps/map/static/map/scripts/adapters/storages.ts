import { MapError } from "../core/errors.js";
import * as ports from "../core/ports.js";
import { Description } from "../core/types.js";

export class StorageContainer<Value> implements ports.Container<Value> {
    constructor(private value: Value | undefined = undefined) {}

    set(newValue: Value | undefined) {
        this.value = newValue;
    }

    get(): Value | undefined {
        return this.value;
    }
}

export type StorageHTMLElement = HTMLElement & {value: string}

export class HTMLElementValueContainer implements ports.Container<string> {
    constructor(private inputElement: StorageHTMLElement) {}

    set(outerValue: string | undefined) {
        this.inputElement.value = this._storedValueOf(outerValue);
    }

    get(): string | undefined {
        return this.inputElement.value;
    }

    private _storedValueOf(outerValue: string | undefined): string {
        return outerValue === undefined ? '' : outerValue;
    }
}

export class DescriptionAdapterContainer implements ports.Container<Description> {
    constructor(private _valueContainer: ports.Container<string>) {}

    set(description: Description | undefined) {
        this._valueContainer.set(
            description === undefined ? undefined : description.value
        );
    }

    get(): Description | undefined {
        const value = this._valueContainer.get();

        if (value === undefined)
            return undefined;

        try {
            return new Description(value);
        }
        catch (MapError) {
            return undefined;
        }
    }
}

export class MatchingByHTMLElement<Value> implements ports.Matching<HTMLElement, Value> {
    private _storage: Record<string, Value>;

    constructor() {
        this._storage = {};
    }

    matchedWith(element: HTMLElement): Value | undefined {
        return this._storage[element.id];
    }

    match(element: HTMLElement, value: Value): void {
        this._storage[element.id] = value;
    }
}
