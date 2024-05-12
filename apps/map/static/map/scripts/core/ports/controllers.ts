export type Controllers<View> = {
    for(view: View): Controllers<View>,
    updatedFor(view: View): Controllers<View>,
    notFor(view: View): Controllers<View>,
}
