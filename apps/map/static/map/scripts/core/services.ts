import { MessageShowing } from "./ports.js";


export function showErrorMessageOnce(
    errorMessage: string,
    messageShowing: MessageShowing,
): void {
    if (messageShowing.isWasShown(errorMessage))
        return;

    messageShowing.show(errorMessage);
    messageShowing.setWasShown(errorMessage);
}
