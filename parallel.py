from multiprocessing import Pool
import time
from functools import partial


def evaluate_next_batch(ix: int, data: list[int]) -> None:
    for value in data:
        print(ix, value)
        time.sleep(10)


def run():
    # num_cpus = psutil.cpu_count(logical=False)
    num_cpus = 4
    pool = Pool(num_cpus)
    res: list[None] = pool.map(
        partial(evaluate_next_batch, data=[1, 3, 5, 7, 9]),
        iterable=range(num_cpus),
        chunksize=1,
    )
    print(res)


if __name__ == '__main__':
    run()
