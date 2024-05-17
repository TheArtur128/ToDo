import * as timeouts from "../../core/ports/timeouts";

export class Timeout implements timeouts.Timeout {
    constructor(private _id?: number) {}

    executeIn(milliseconds: timeouts.Milliseconds, callback: () => any): void {
        if (this._id !== undefined)
            clearTimeout(this._id);

        this._id = setTimeout(callback, milliseconds);
    }
}
