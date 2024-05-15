import * as types from "../types.js";
import { Maybe } from "../../fp";

export type StaticDrawing<RootView, View> = {
    drawOn(rootView: RootView, view: View): void,
    eraseFrom(rootView: RootView, view: View): void,
}

export type Drawing<RootView, View, Value> = (
    StaticDrawing<RootView, View> & {
        redrawBy(value: Value, view: View): void,
    }
)

export type Views<View> = {
    createEmptyView(): View,
    sizeOf(view: View): types.Vector,
}

export type Subviews<RootView, View, Value> = Views<View> & {
    foundViewOn(rootView: RootView, value: Value): Maybe<View>,
}

export type Cursor = {
    setDefault(): void;
    setToGrab(): void;
    setGrabbed(): void;
}
