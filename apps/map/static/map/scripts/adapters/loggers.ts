import * as ports from "../core/ports.js";

export const consoleLogger: ports.Logger = {
    log(message: string): any {
        console.error(message);
    },
};
