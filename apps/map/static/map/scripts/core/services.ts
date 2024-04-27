import { Container } from "./ports.js";

export function popFrom<Value>(container: Container<Value>): Value | undefined {
    let value = container.get();

    if (value !== undefined)
        container.set(undefined);

    return value;
}

export function setDefaultAt<Value>(
    container: Container<Value>,
    defaultValue: Value,
): void {
    let storedValue = container.get();

    if (storedValue === undefined)
        container.set(defaultValue);
}
