import { MessageShowing, Socket } from "./ports.js";

export function showErrorMessageOnce(
    errorMessage: string,
    messageShowing: MessageShowing,
): void {
    if (messageShowing.isWasShown(errorMessage))
        return;

    messageShowing.show(errorMessage);
    messageShowing.setWasShown(errorMessage);
}

export function popFrom<Value>(socket: Socket<Value>): Value | undefined {
    let value = socket.get();

    if (value !== undefined)
        socket.set(undefined);

    return value;
}

export function setDefaultAt<Value>(
    socket: Socket<Value>,
    defaultValue: Value,
): void {
    let storedValue = socket.get();

    if (storedValue === undefined)
        socket.set(defaultValue);
}
