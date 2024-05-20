export type Milliseconds = number;

export type Timeout = {
    executeIn(milliseconds: Milliseconds, callback: () => any): any,
}
