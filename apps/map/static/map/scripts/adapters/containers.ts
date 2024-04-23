import * as ports from "../core/ports.js";

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
        return this._outerValueOf(this.inputElement.value);
    }

    private _storedValueOf(outerValue: string | undefined): string {
        return outerValue === undefined ? '' : outerValue;
    }

    private _outerValueOf(storedValue: string): string | undefined {
        return storedValue === '' ? undefined : storedValue;
    }
}
