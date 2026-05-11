/**
 * This class represents an immutable pair of values of different types.
 * @param <T> First value
 * @param <U> Second value
 */
public class Pair<T, U> {
    final private T first;
    final private U second;

    public Pair(T first, U second) {
        this.first = first;
        this.second = second;
    }

    public T first() {
        return first;
    }

    public U second() {
        return second;
    }
}
