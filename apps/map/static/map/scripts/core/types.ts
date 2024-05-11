import * as errors from "./errors.js";
import { Maybe } from "../fp.js";

abstract class _ValueObject<Value> {
    constructor(readonly value: Value) {}

    mappedBy(tranformed: (value: Value) => Value): typeof this {
        return this.constructor(tranformed(this.value));
    }

    static of<Value>(value: Value): Maybe<typeof this> {
        try {
            return this.constructor(value);
        }
        catch (MapError) {
            return undefined;
        }
    }
}

abstract class _Entity {
    with(props: Partial<typeof this>): typeof this {
        return { ...this, ...props};
    }
}

export type Map = { id: number }

export enum InteractionMode { moving, editing }

export class Task extends _Entity {
    get mode() {
        return this._mode;
    }

    constructor(
        public id: number,
        public description: Description,
        public x: number,
        public y: number,
        private _mode: InteractionMode = InteractionMode.moving,
    ) {
        super();
    }

    withChangedMode(): Task {
        let changedMode = this._mode++;

        if (InteractionMode[this._mode] === undefined)
            changedMode = InteractionMode.moving;

        return { ...this, _mode: changedMode };
    }
}

export type TaskPrototype = {
    description: Description,
    x: number,
    y: number,
}

export class Description extends _ValueObject<string> {
    constructor(value: string) {
        super(value);

        if (value === '')
            throw new errors.EmptyDescriptionError();
    }
}

export class Vector {
    constructor(readonly x: number, readonly y: number) {}

    map(operation: (n: number) => number): Vector {
        return new Vector(operation(this.x), operation(this.y));
    }

    of(vector: Vector, operation: (a: number, b: number) => number): Vector {
        return new Vector(operation(this.x, vector.x), operation(this.y, vector.y));
    }
}
