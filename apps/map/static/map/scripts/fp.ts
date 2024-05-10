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

export class Ok<Value> {
    constructor(readonly value: Value) {}
}

export class Bad<Value> {
    constructor(readonly value: Value) {}
}

export function ok<Value>(value: Value): Ok<Value> {
    return new Ok(value)
}

export function bad<Value>(value: Value): Bad<Value> {
    return new Bad(value)
}

export type Result<Value> = Ok<Value> | Bad<Value>

export function toMapOk<Value>(
    transformed: (value: Value) => Result<Value>
): (result: Result<Value>) => Result<Value> {
    return (result: Result<Value>) => {
        return result instanceof Ok ? transformed(result.value) : result;
    }
}

export function toMapBad<Value>(
    transformed: (value: Value) => Result<Value>
): (result: Result<Value>) => Result<Value> {
    return (result: Result<Value>) => {
        return result instanceof Bad ? transformed(result.value) : result;
    }
}
