import logging
from time import perf_counter
from multiprocessing import Pool, cpu_count


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


def _divisors(n: int) -> list[int]:

    if n <= 0:
        raise ValueError("All numbers must be positive integers")

    result: list[int] = []
    for i in range(1, n + 1):
        if n % i == 0:
            result.append(i)
    return result


def factorize_sync(*numbers: int) -> tuple[list[int], ...]:

    return tuple(_divisors(n) for n in numbers)


def factorize_parallel(*numbers: int) -> tuple[list[int], ...]:

    with Pool(processes=cpu_count()) as pool:
        return tuple(pool.map(_divisors, numbers))


def main() -> None:
    nums = (128, 255, 99999, 10651060)


    t0 = perf_counter()
    a, b, c, d = factorize_sync(*nums)
    t1 = perf_counter()
    logger.info("[sync] time: %.4f s", t1 - t0)


    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [
        1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316,
        380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060
    ]


    t2 = perf_counter()
    a2, b2, c2, d2 = factorize_parallel(*nums)
    t3 = perf_counter()
    logger.info("[parallel] time: %.4f s (cpu cores: %s)", t3 - t2, cpu_count())

    assert (a2, b2, c2, d2) == (a, b, c, d)
    logger.info("OK, results match")


if __name__ == "__main__":
    main()

