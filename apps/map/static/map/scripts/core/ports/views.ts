import { Maybe } from "../../sugar.js";

export type StaticPresenter<RootView, View> = {
    drawOn(rootView: RootView, view: View): void,
    eraseFrom(rootView: RootView, view: View): void,
}

export type DynamicPresenter<View, Value> = {
    redrawBy(value: Value, view: View): void;
}

export type Presenter<RootView, View, Value> = (
    StaticPresenter<RootView, View>
    & DynamicPresenter<View, Value>
)

export type Views<View> = {
    createEmptyView(): View,
}

export type Subviews<RootView, View, Value> = Views<View> & {
    foundViewOn(rootView: RootView, value: Value): Maybe<View>,
}
