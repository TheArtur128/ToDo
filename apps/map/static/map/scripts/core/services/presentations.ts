import * as repos from "../ports/repos.js";
import * as controllers from "../ports/controllers.js";
import * as views from "../ports/views";
import { Maybe } from "../../fp";

export type EntityMatching<View, Entity> = repos.MatchingBy<View, Maybe<Entity>>;
export type ControllerMatching<View, Entity> = repos.MatchingBy<
    View, controllers.Controllers<View, Entity>
>;

export type EntityPresentation<View, Entity> = [
    EntityMatching<View, Entity>,
    ControllerMatching<View, Entity>
];

export function updatedPresentationOf<RootView, View, Entity>(
    entity: Entity,
    view: View,
    drawing: views.Drawing<RootView, View, Entity>,
    entityMatching: EntityMatching<View, Entity>,
    controllerMatching: ControllerMatching<View, Entity>,
): EntityPresentation<View, Entity> {
    drawing.redrawBy(entity, view);

    return [
        entityMatching.matchingBetween(view, entity),
        repos.map(
            controllerMatching,
            view,
            m => m.mapOk(c => c.updatedControllersFor(view, entity))
        ),
    ]
}
