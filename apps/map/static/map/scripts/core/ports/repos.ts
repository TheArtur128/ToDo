import { Maybe } from "../../fp";

export type MatchingBy<Key, Value> = {
    matchedWith(key: Key): Maybe<Value>;
    matchingBetween(key: Key, value: Value): MatchingBy<Key, Value>;
}
