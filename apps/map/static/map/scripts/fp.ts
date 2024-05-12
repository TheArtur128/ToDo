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

class _Context<Value> {
    constructor(readonly value: Value) {}
}

export class Ok<Value> extends _Context<Value> {}
export class Bad<Value> extends _Context<Value> {}
export type Result<Value> = Ok<Value> | Bad<Value>

export type Dirty<Value> = Value;

export function ok<Value>(value?: undefined): Ok<undefined>
export function ok<Value>(value?: Value): Ok<Value>
export function ok<Value>(value?: Maybe<Value>): Ok<Maybe<Value>> {
    return new Ok(value);
}

export function bad<Value>(value?: undefined): Bad<undefined>
export function bad<Value>(value?: Value): Bad<Value>
export function bad<Value>(value?: Maybe<Value>): Bad<Maybe<Value>> {
    return new Bad(value);
}

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

export function valueOf<Value>(container: {readonly value: Value}): Value {
    return container.value;
}
