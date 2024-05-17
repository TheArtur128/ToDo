import * as domain from "../../core/domain.js";
import { Maybe } from "../../sugar.js";

class _MemorizedMapProvider {
    private _map: Maybe<domain.Map> = undefined;

    getCurrentMap() {
        if (this._map !== undefined)
            return this._map;

        const mapId = Number(window.location.pathname.split('/')[2]);

        return <domain.Map>{id: mapId};
    }
}

export const getCurrentMap = new _MemorizedMapProvider().getCurrentMap;
