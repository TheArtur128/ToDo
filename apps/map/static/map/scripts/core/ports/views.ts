export type StaticDrawing<RootView, Subview> = {
    withDrawn(subview: Subview, rootView: RootView): RootView,
    withErased(subview: Subview, rootView: RootView): RootView,
}

export type Drawing<RootView, Subview, Value> = StaticDrawing<RootView, Subview> & {
    redrawnBy(value: Value, subview: Subview): Subview,
}

export type Views<View> = {
    readonly emptyView: View,
    sizeOf(view: View): Vector,
}

export type RootViews<RootView, Subview, SubViewValue> = Views<RootView> & {
    foundSubviewOn(rootView: RootView, value: SubViewValue): Maybe<Subview>
}

export type Cursor = {
    asDefault(): Cursor;
    toGrab(): Cursor;
    asGrabbed(): Cursor;
}
