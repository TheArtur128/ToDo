import * as controllers from "../../../core/ports/controllers.js";
import * as repos from "../../../core/ports/repos.js";

export abstract class Controller<View, Value> implements controllers.Controller {
    constructor(protected _view: View, protected _value: Value) {}
    abstract activate(): void;
    abstract deactivate(): void;
}

export abstract class StaticController<View> implements controllers.Controller {
    constructor(protected _view: View) {}
    abstract activate(): void;
    abstract deactivate(): void;
}

export class StaticControllerMatching<View> implements repos.MatchingBy<View, controllers.Controller> {
    constructor(
        private _controllerFor: (view: View) => controllers.Controller,
        private _maybeMatching: repos.MaybeMatchingBy<View, controllers.Controller>
    ) {}

    matchedWith(view: View): controllers.Controller {
        let controller = this._maybeMatching.matchedWith(view);

        if (controller !== undefined)
            return controller;

        controller = this._controllerFor(view);
        this._maybeMatching.match(view, controller);

        return controller;
    }

    match(view: View, controller: controllers.Controller): void {
        this._maybeMatching.match(view, controller);
    }
}
