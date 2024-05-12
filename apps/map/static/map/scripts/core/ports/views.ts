import * as types from "../types.js";
import { Maybe, Dirty } from "../../fp";

export type StaticDrawing<RootView, View> = {
    withDrawn(view: View, rootView: RootView): Dirty<RootView>,
    withErased(view: View, rootView: RootView): Dirty<RootView>,
}

export type Drawing<RootView, View, Value> = (
    StaticDrawing<RootView, View> & {
        redrawnBy(value: Value, view: View): Dirty<View>,
    }
)

export type Views<View> = {
    readonly emptyView: View,
    sizeOf(view: View): types.Vector,
}

export type Subviews<RootView, View, Value> = Views<View> & {
    foundViewOn(rootView: RootView, value: Value): Maybe<View>,
}

export type Cursor = {
    asDefault(): Cursor;
    toGrab(): Cursor;
    asGrabbed(): Cursor;
}
