import * as domain from "../../core/domain.js";
import { Maybe } from "../../sugar.js";

class _MemorizedMapProvider {
    private _memorizedMap: Maybe<domain.Map> = undefined;

    getCurrentMap() {
        if (this._memorizedMap !== undefined)
            return this._memorizedMap;

        const mapId = Number(window.location.pathname.split('/')[2]);
        const map: domain.Map = {id: mapId};

        this._memorizedMap = map;

        return map;
    }
}

export const getCurrentMap = new _MemorizedMapProvider().getCurrentMap;
