import java.math.BigInteger;
import java.util.List;
import java.util.random.RandomGenerator;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.LongStream;
import java.util.stream.Stream;


/*
 * THIS FILE WAS UPDATED IN 29/05/23
 * DO NOT USE EARLIER VERSIONS
 */

public class HashingUtils {
    final private static int             a_ASCII = 97;
    final private static int             z_ASCII = 122;
    final private        RandomGenerator rand;

    public HashingUtils() {
        rand = RandomGenerator.of("L64X128MixRandom"); // Using Java 17 new API for number generation.
    }

    public static long mod(long x, long m) {
        long res = x % m;

        return (res < 0) ? res + m : res;
    }

    public static int mod(int x, int m) {
        int res = x % m;

        return (res < 0) ? res + m : res;
    }

    public long genLong(long lower, long higher) {
        return rand.nextLong(lower, higher);
    }

    public Integer[] genUniqueIntegers(int numOfItemsToGen) {
        return Stream.generate(() -> rand.ints(0, Integer.MAX_VALUE)).flatMap(IntStream::boxed).distinct().limit(
                numOfItemsToGen).toArray(Integer[]::new);
    }

    public Long[] genUniqueLong(int numOfItemsToGen) {
        return Stream.generate(() -> rand.longs(0, Long.MAX_VALUE)).flatMap(LongStream::boxed).distinct().limit(
                numOfItemsToGen).toArray(Long[]::new);
    }

    public List<String> genUniqueStrings(int numOfItemsToGen, int stringMinLength, int stringMaxLength) {
        return rand.ints(stringMinLength, stringMaxLength)
                   .limit(numOfItemsToGen)
                   .mapToObj(length -> rand.ints(a_ASCII,
                                                 z_ASCII
                                                 + 1)
                                           .limit(length)
                                           .distinct()
                                           .collect(StringBuilder::new,
                                                    StringBuilder::appendCodePoint,
                                                    StringBuilder::append)
                                           .toString())
                   .collect(Collectors.toList());
    }

    private static Pair<Integer, Long> calculateEvenDivisorSplit(long num) {
        int s = 0;
        while ((num & 1) == 0) {
            num >>>= 1;
            ++s;
        }

        return new Pair<>(s, num);
    }

    private static long multiplyMod(long a, long b, long mod) {
        final BigInteger aBig = BigInteger.valueOf(a);
        final BigInteger bBig = BigInteger.valueOf(b);
        final BigInteger multiplyRes = aBig.multiply(bBig);
        final BigInteger modBig = BigInteger.valueOf(mod);

        return multiplyRes.mod(modBig).longValue();
    }

    public static long modPow(long a, long b, long mod) {
        final BigInteger aBig = BigInteger.valueOf(a);
        final BigInteger bBig = BigInteger.valueOf(b);
        final BigInteger modBig = BigInteger.valueOf(mod);
        final BigInteger res = aBig.modPow(bBig, modBig);

        return res.longValue();
    }

    /**
     * An implementation of the Rabin-Miller probabilistic primality test as defined in the following link:
     * <a href="https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test#Miller%E2%80%93Rabin_test">...</a>
     * This process requires theta of (rounds * log(suspect) ^ 3)
     *
     * @param suspect - The number suspected of being prime, assuming suspect isn't even.
     * @param rounds  - The number of rounds to run the test. A good default value is 50.
     *
     * @return True if suspect is probably prime with a false positive probability of 4^(-rounds)
     */
    public boolean runMillerRabinTest(long suspect, int rounds) {
        Pair<Integer, Long> split = calculateEvenDivisorSplit(suspect - 1);
        final int s = split.first();
        final long d = split.second();

        long y = 1;

        for (int i = 0; i < rounds; ++i) {
            final long a = genLong(2L, suspect - 1);
            long x = modPow(a, d, suspect);

            for (int j = 0; j < s; ++j) {
                y = multiplyMod(x, x, suspect);

                if (y == 1 && x != 1 && x != suspect - 1) {
                    return false;
                }

                x = y;
            }
        }

        return (y == 1);
    }
}
