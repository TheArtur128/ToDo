import * as ports from "../../../core/ports/controllers.js";
import * as layout from "../../in/layout.js";

export abstract class EventListenerControllers implements ports.ControllersForStatic<layout.View> {
    updateFor(view: HTMLElement): void {}
    abstract activeFor(view: HTMLElement): void;
    abstract removeFrom(view: HTMLElement): void;
}
