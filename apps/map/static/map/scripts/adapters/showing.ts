export class MessageShowingWithCachedSearching {
    show: (message: string) => any;
    shownMessages: Set<string>;

    constructor(show: (message: string) => any) {
        this.show = show;
        this.shownMessages = new Set();
    }

    setWasShown(message: string): void {
        this.shownMessages.add(message);
    }

    isWasShown(message: string): boolean {
        return this.shownMessages.has(message);
    }
}

export const alertShowing = {
    show: alert,

    setWasShown(_: string): void {},

    isWasShown(_: string): boolean {
        return false;
    },
}
