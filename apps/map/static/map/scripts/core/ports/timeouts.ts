export type Milliseconds = number;

export type Timeout = {
    executingIn(milliseconds: Milliseconds, callback: () => any): Timeout,
}
