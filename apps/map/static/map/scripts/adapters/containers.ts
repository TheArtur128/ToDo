export class SingleValueContainer<Value> {
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
