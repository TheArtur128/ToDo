export type ValueThat<T> = T extends (...args: any[]) => infer R ? R : any;

export type Maybe<Value> = Value | undefined;

export function maybe<Value>(
    transformed: (value: Value) => Maybe<Value>,
): (value: Maybe<Value>) => Maybe<Value> {
    return (value) => value === undefined ? value : transformed(value);
}

export function on<Determinant, Rigth, Left=undefined>(
    determinant: Determinant,
    right: Rigth,
    left?: Left,
) {
    return (value: any) => value === determinant ? right : left
}

class _ResultBase<Value> {
    constructor(readonly value: Value) {}

    get asOk(): _Ok<Value> {
        return new _Ok(this.value);
    }

    get asBad(): _Bad<Value> {
        return new _Bad(this.value);
    }
}

class _Ok<Value> extends _ResultBase<Value> {
    mapOk<NextValue>(next: (value: Value) => NextValue): _Ok<NextValue> {
        return new _Ok(next(this.value));
    }

    mapBad(_: (value: never) => any): _Ok<Value> {
        return this;
    }
}

class _Bad<Value> extends _ResultBase<Value> {
    mapBad<NextValue>(next: (value: Value) => NextValue): _Bad<NextValue> {
        return new _Bad(next(this.value));
    }

    mapOk(_: (value: never) => any): _Bad<Value> {
        return this;
    }
}

export namespace results {
    export type Ok<Value> = _Ok<Value>;
    export type Bad<Value> = _Bad<Value>;
    export type Result<Value> = Ok<Value> | Bad<Value>

    export function ok<Value>(): _Ok<undefined>
    export function ok<Value>(value: Value): _Ok<Value>
    export function ok<Value>(value?: Value): _Ok<Maybe<Value>> {
        return new _Ok(value);
    }

    export function bad<Value>(): _Bad<undefined>
    export function bad<Value>(value: Value): _Bad<Value>
    export function bad<Value>(value?: Value): _Bad<Maybe<Value>> {
        return new _Bad(value);
    }
}

export type Dirty<Value> = Value;
