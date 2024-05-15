import { results } from "../../fp";

export type InactiveControllers<View, Value> = {
    activeControllersFor(view: View, value: Value): ActiveControllers<View, Value>,
}

export type ActiveControllers<View, Value> = {
    updatedControllersFor(view: View, value: Value): ActiveControllers<View, Value>,
    readonly inactiveControllers: InactiveControllers<View, Value>,
}

export type Controllers<View, Value> = (
    results.Ok<ActiveControllers<View, Value>>
    | results.Bad<InactiveControllers<View, Value>>
)

export function asActiveFor<View, Value>(
    view: View,
    value: Value,
    controllers: Controllers<View, Value>
): results.Ok<ActiveControllers<View, Value>> {
    return controllers
        .mapOk(c => c.updatedControllersFor(view, value))
        .mapBad(c => c.activeControllersFor(view, value))
        .asOk
}

export type StaticInactiveControllers<View> = {
    activeControllersFor(view: View): StaticActiveControllers<View>,
}

export type StaticActiveControllers<View> = {
    updatedControllersFor(view: View): StaticActiveControllers<View>,
    readonly inactiveControllers: StaticInactiveControllers<View>,
}

export type StaticControllers<View> = (
    results.Ok<StaticActiveControllers<View>>
    | results.Bad<StaticInactiveControllers<View>>
)

export function asStaticActiveFor<View>(
    view: View,
    controllers: StaticControllers<View>
): results.Ok<StaticActiveControllers<View>> {
    return controllers
        .mapOk(c => c.updatedControllersFor(view))
        .mapBad(c => c.activeControllersFor(view))
        .asOk
}
