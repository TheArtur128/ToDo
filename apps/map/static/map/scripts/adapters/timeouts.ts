import * as timeouts from "../core/ports/timeouts";
import { Maybe, Dirty } from "../fp";

export class Timeout {
    constructor(private _id: Maybe<number> = undefined) {}

    executingIn(milliseconds: timeouts.Milliseconds, callback: () => any): Dirty<Timeout> {
        if (this._id !== undefined)
            clearTimeout(this._id);

        const timeoutId = setTimeout(callback, milliseconds);
        return new Timeout(timeoutId);
    }
}
