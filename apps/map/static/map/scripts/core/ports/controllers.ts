// export type ControllersFor<View, Value> = {
//     activeFor(view: View, value: Value): void,
//     updateFor(view: View, value: Value): void,
//     removeFrom(view: View, value: Value): void,
// }

// export type ControllersForStatic<View> = {
//     activeFor(view: View): void,
//     updateFor(view: View): void,
//     removeFrom(view: View): void,
// }

export type Controller<Value> = {
    activate(): void;
    deactivate(): void;
    update(value: Value): void;
}

export type StaticController = {
    activate(): void;
    deactivate(): void;
}
