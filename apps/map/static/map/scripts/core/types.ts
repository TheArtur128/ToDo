import * as errors from "./errors.js";

export type Map = { id: number }

export enum InteractionMode { moving, editing }

export class Task {
    get mode() {
        return this._mode;
    }

    constructor(
        public id: number,
        public description: Description,
        public x: number,
        public y: number,
        private _mode: InteractionMode = InteractionMode.moving,
    ) {}

    changeMode(): void {
        this._mode++;

        if (InteractionMode[this._mode] === undefined)
            this._mode = InteractionMode.moving;
    }
}

export type TaskPrototype = {
    description: Description,
    x: number,
    y: number,
}

export class Description {
    constructor(readonly value: string) {
        if (value === '')
            throw new errors.EmptyDescriptionError();
    }
}
