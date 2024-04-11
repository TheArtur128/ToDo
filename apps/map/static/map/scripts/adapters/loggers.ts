import * as types from "../core/types.js";

export const consoleLogger = {
    logMapHasNoSurface(map: types.Map): any {
        console.error(`Surface for map with id = ${map.id} do not exist`);
    },
};
