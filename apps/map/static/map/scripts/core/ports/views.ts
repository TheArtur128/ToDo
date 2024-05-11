import * as types from "../types.js";
import { Maybe, Dirty } from "../../fp";

export type StaticDrawing<Rootview, Subview> = {
    withDrawn(subview: Subview, rootview: Rootview): Rootview,
    withErased(subview: Subview, rootview: Rootview): Rootview,
}

export type Drawing<Rootview, Subview, Value> = StaticDrawing<Rootview, Subview> & {
    redrawnBy(value: Value, subview: Subview): Dirty<Subview>,
}

export type Views<View> = {
    readonly emptyView: View,
    sizeOf(view: View): types.Vector,
}

export type Subviews<Rootview, View, Value> = Views<View> & {
    foundViewOn(rootview: Rootview, value: Value): Maybe<View>,
}

export type Cursor = {
    asDefault(): Cursor;
    toGrab(): Cursor;
    asGrabbed(): Cursor;
}
