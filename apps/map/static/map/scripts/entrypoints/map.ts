import * as facade from "../adapters/out/facade.js";
import * as taskAddingControllers from "../adapters/out/controllers/task-adding.js";
import * as taskMovingControllers from "../adapters/out/controllers/task-moving.js";
import * as taskControllers from "../adapters/out/controllers/tasks.js";

const taskControllerFactories = [
    taskControllers.TaskModeChangingController.factory,
    taskControllers.TaskDescriptionChangingController.factory,
    taskMovingControllers.PreparationController.factory,
    taskMovingControllers.StartingController.factory,
    taskMovingControllers.StoppingController.factory,
    taskMovingControllers.CancellationController.factory,
];

facade.drawMap(
    document.body,
    <HTMLTextAreaElement>document.querySelector("#new-task-description"),
    view => new taskAddingControllers.AvailabilityController(
        view,
        document.body,
        taskControllerFactories,
    ),
    taskControllerFactories,
);
