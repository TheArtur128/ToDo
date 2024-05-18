import * as ports from "../../../core/ports/controllers.js";
import * as layout from "../../in/layout.js";

export abstract class EventListenerControllersForStatic<View extends layout.View = layout.View> implements ports.ControllersForStatic<View> {
    updateFor(_: View): void {}
    abstract activeFor(view: View): void;
    abstract removeFrom(view: View): void;
}

export abstract class EventListenerControllers<View extends layout.View, Value> implements ports.ControllersFor<layout.View, Value> {
    updateFor(_: View, __: never): void {}
    abstract activeFor(view: View, value: Value): void;
    abstract removeFrom(view: View, value: Value): void;
}

export class asForDynamic<View> implements ports.ControllersFor<View, never> {
    constructor(private _controllersForStatic: ports.ControllersForStatic<View>) {}

    activeFor(view: View, _: never): void {
        this._controllersForStatic.activeFor(view);
    }

    updateFor(view: View, _: never): void {
        this._controllersForStatic.updateFor(view);
    }
    
    removeFrom(view: View, _: never): void {
        this._controllersForStatic.removeFrom(view);
    }
}

export type WithRoot<Value> = {
    root: ports.ControllersFor<layout.View, Value>
} 

export class And<View extends layout.View, Value> implements ports.ControllersFor<View, Value> {
    constructor(private _controllers: Array<ports.ControllersFor<View, Value> & WithRoot<Value>>) {
        _controllers.forEach(c => {
            if (c.root !== c)
                throw new Error("Controllers has root");

            c.root = this;
        })
    }

    activeFor(view: View, value: Value): void {
        this._controllers.forEach(c => c.activeFor(view, value));
    }

    updateFor(view: View, value: Value): void {
        this._controllers.forEach(c => c.updateFor(view, value));
    }
    
    removeFrom(view: View, value: Value): void {
        this._controllers.forEach(c => c.removeFrom(view, value));
    }
}
