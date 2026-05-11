public interface HashFactory<K> {
    /**
     * @param capacity - The capacity of the hash table using the expected hash function.
     * @return A randomly chosen hash function wrapped in a HashFunctor class.
     */
    public HashFunctor<K> pickHash(int k);
}
