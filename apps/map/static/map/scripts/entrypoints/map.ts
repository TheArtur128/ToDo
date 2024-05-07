import * as facade from "../adapters/facade.js";
import * as taskControllers from "../controllers/tasks.js";
import * as taskAddingControllers from "../controllers/task-adding.js";

const taskListElement = <HTMLDivElement>document.querySelector("#tasks");
const descriptionInputElement = <HTMLTextAreaElement>document.querySelector("#new-task-description");

const facade_ = new facade.Facade(
    taskControllers.initAllControllers,
    taskListElement,
    descriptionInputElement,
    taskAddingControllers.dynamicControllers,
);

facade_.taskGroups.draw();
taskAddingControllers.initAvailabilityControllers(facade_, descriptionInputElement);
