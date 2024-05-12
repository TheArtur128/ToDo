import { Maybe } from "../../fp.js";

export type MatchingBy<Key, Value> = {
    matchedWith(key: Key): Maybe<Value>;
    withPair(key: Key, value: Value): MatchingBy<Key, Value>;
}
