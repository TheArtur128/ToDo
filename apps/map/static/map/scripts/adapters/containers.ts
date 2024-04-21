import * as ports from "../core/ports.js";

export class StorageContainer<Value> implements ports.Container<Value> {
    #value: Value | undefined;

    constructor(value: Value | undefined = undefined) {
        this.#value = value;
    }

    set(newValue: Value | undefined) {
        this.#value = newValue;
    }

    get(): Value | undefined {
        return this.#value;
    }
}

export type StorageHTMLElement = HTMLElement & {value: string}

export class HTMLElementValueContainer implements ports.Container<string> {
    #inputElement: StorageHTMLElement;

    constructor(inputElement: StorageHTMLElement) {
        this.#inputElement = inputElement
    }

    set(newValue: string | undefined) {
        this.#inputElement.value = this.#storedValueOf(newValue);
    }

    get(): string | undefined {
        return this.#inputValueOf(this.#inputElement.value);
    }

    #storedValueOf(value: string | undefined): string {
        return value === undefined ? '' : value;
    }

    #inputValueOf(storedValue: string): string | undefined {
        return storedValue === '' ? undefined : storedValue;
    }
}
