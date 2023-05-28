import java.util.List;
import java.util.Random;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.LongStream;
import java.util.stream.Stream;

public class HashingUtils {
    final private static int a_ASCII = 97;
    final private static int z_ASCII = 122;
    final private Random rand;

    public HashingUtils() {
        rand = new Random(System.currentTimeMillis()); // Using current time as the random seed
    }

    /***
     * Evaluates the power of x at y, done at modulo mod in an efficient matter,
     * using the characteristics of modulo: (x * y) mod n = ((x mod n) * (y mod n)) mod n
     * @param x - The basis
     * @param y - The power
     * @param mod - The intended modulo of the value
     * @return (x ^ y) % mod
     */
    public static long fastModularPower(long x, long y, long mod) {
        long result = 1;
        while (y > 0) {
            if ((y & 1) == 0) {
                x *= x;
                x %= mod;
                y >>>= 1;
            } else {
                result *= x;
                result %= mod;
                --y;
            }
        }

        return result;
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
        return lower + (long) (rand.nextFloat() * (higher - lower));
    }

    public Integer[] genUniqueIntegers(int numOfItemsToGen) {
        return Stream.generate(() -> rand.ints(0, Integer.MAX_VALUE))
                .flatMap(IntStream::boxed)
                .distinct()
                .limit(numOfItemsToGen)
                .toArray(Integer[]::new);
    }

    public Long[] genUniqueLong(int numOfItemsToGen) {
        return Stream.generate(() -> rand.longs(0, Long.MAX_VALUE))
                     .flatMap(LongStream::boxed)
                     .distinct()
                     .limit(numOfItemsToGen)
                     .toArray(Long[]::new);
    }

    public List<String> genUniqueStrings(int numOfItemsToGen, int stringMinLength, int stringMaxLength) {
        return rand.ints(stringMinLength, stringMaxLength)
                .limit(numOfItemsToGen)
                .mapToObj(length -> rand.ints(a_ASCII, z_ASCII + 1)
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

    /**
     * An implementation of the Rabin-Miller probabilistic primality test as defined in the following link:
     * <a href="https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test#Miller%E2%80%93Rabin_test">...</a>
     * This process requires theta of (rounds * log(suspect) ^ 3)
     * @param suspect - The number suspected of being prime, assuming suspect isn't even.
     * @param rounds - The number of rounds to run the test. A good default value is 50.
     * @return True if suspect is probably prime with a false positive probability of 4^(-rounds)
     */
    public boolean runMillerRabinTest(long suspect, int rounds) {
        Pair<Integer, Long> split = calculateEvenDivisorSplit(suspect - 1);
        final int s = split.first();
        final long d = split.second();

        long y = 1;

        for (int i = 0; i < rounds; ++i) {
            final long a = genLong(2L, suspect - 1);
            long x = fastModularPower(a, d, suspect);

            for (int j = 0; j < s; ++j) {
                y = (x * x) % suspect;

                if (y == 1 && x != 1 && x != suspect - 1) {
                    return false;
                }

                x = y;
            }
        }

        return (y == 1);
    }
}
