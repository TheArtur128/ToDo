export type WithControllers<View> = (view: View) => View;

export type Controllers<View> = {
    withControllers: WithControllers<View>,
    withoutControllers(view: View): View,
}
