import * as facade from "../adapters/facade.js";
import * as controllers from "../controllers.js";

const taskListElement = <HTMLDivElement>document.querySelector("#tasks");
const creationPanelElement = <HTMLDivElement>document.querySelector("#creation-panel");
const descriptionInputElement = <HTMLTextAreaElement>document.querySelector("#new-task-description");

new facade.Tasks(taskListElement, controllers.initTaskControllers).draw();

const tasksAdding = facade.taskAddingOf(taskListElement, descriptionInputElement);
controllers.initTaskAddingControllers(tasksAdding, creationPanelElement);
