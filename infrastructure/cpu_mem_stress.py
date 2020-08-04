from multiprocessing import Pool
from multiprocessing import cpu_count
import math
import sys

MB = 1024 * 1024


def main():
    cores = sys.argvs[0]
    mem_eat = "L" * MB * sys.argvs[1]
    if cores > cpu_count():
        print(
            "Too many threads running! You are only able to run"
            f" {cpu_count()} threads at a time!"
        )
        sys.exit(1)

    print(f"Stressing {cores} cores")
    pool = Pool(cores)
    pool.map(stress, range(cores))


def stress(x):
    while True:
        for i in range(1, int(math.sqrt(x)) + 1):
            if x % i == 0:
                x ** x
        x ** x


if __name__ == "__main__":
    main()
