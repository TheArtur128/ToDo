import * as ports from "../core/ports.js";

export class SocketContainer<Value> implements ports.Socket<Value> {
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

export type HTMLElementContainer = HTMLElement & {value: string}

export class HTMLElementSocket implements ports.Socket<string> {
    #inputElement: HTMLElementContainer;

    constructor(inputElement: HTMLElementContainer) {
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
