import * as errors from "./errors";

export type Map = {id: number}

export type Task = {
    id: number,
    description: Description,
    x: number,
    y: number,
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
