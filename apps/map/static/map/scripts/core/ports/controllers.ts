export type Controller = {
    activate(): void;
    deactivate(): void;
}

export type ControllerFor<View, Value> = (view: View, value: Value) => Controller;
export type StaticControllerFor<View> = (view: View) => Controller;
