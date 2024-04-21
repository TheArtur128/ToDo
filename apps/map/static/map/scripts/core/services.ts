import { MessageShowing, Container } from "./ports.js";

export function showErrorMessageOnce(
    errorMessage: string,
    messageShowing: MessageShowing,
): void {
    if (messageShowing.isWasShown(errorMessage))
        return;

    messageShowing.show(errorMessage);
    messageShowing.setWasShown(errorMessage);
}

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