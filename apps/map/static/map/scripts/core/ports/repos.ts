export type MatchingBy<Key, Value> = {
    matchedWith(key: Key): Value;
    matchingBetween(key: Key, value: Value): MatchingBy<Key, Value>;
}

export function map<Key, Value>(
    matching: MatchingBy<Key, Value>,
    key: Key,
    action: (value: Value) => Value,
): MatchingBy<Key, Value> {
    const value = matching.matchedWith(key);
    return matching.matchingBetween(key, action(value));
}
