import * as controllers from "../adapters/controllers.js";


const taskListElement = <HTMLDivElement>document.querySelector("#tasks");
const creationPanelElement = <HTMLDivElement>document.querySelector("#creation-panel");

controllers.drawMap(taskListElement);
