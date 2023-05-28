public interface HashFunctor<K> {
    /***
     * @param key - A valid key of type K
     * @return A hash mapping into [m], where m is a parameter of the HashFunctor
     */
    public int hash(K key);
}
