import * as facade from "../adapters/facade.js";
import * as taskControllers from "../controllers/tasks.js";
import * as taskAddingControllers from "../controllers/task-adding.js";

const taskListElement = <HTMLDivElement>document.querySelector("#tasks");
const descriptionInputElement = <HTMLTextAreaElement>document.querySelector("#new-task-description");

new facade.Tasks(taskListElement, taskControllers.initAllControllers).draw();

const tasksAdding = new facade.TaskAdding(
    taskListElement,
    descriptionInputElement,
    taskAddingControllers.dynamicTaskAddingControllers
);

taskAddingControllers.initAvailabilityControllers(tasksAdding, descriptionInputElement);
