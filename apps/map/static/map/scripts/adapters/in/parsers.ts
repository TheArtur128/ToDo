import * as domain from "../../core/domain.js";

const mapId = Number(window.location.pathname.split('/')[2]);
const currentMap: domain.Map = {id: mapId};

export function getCurrentMap(): domain.Map {
    return currentMap;
}
