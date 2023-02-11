import multiprocessing
import random
from concurrent.futures import ProcessPoolExecutor
from time import sleep

from rich import progress


def long_running_fn(progress, task_id):
    len_of_task = random.randint(3, 20)  # take some random length of time
    for n in range(0, len_of_task):
        sleep(1)  # sleep for a bit to simulate work
        progress[task_id] = {'progress': n + 1, 'total': len_of_task}


if __name__ == '__main__':
    n_workers = 8  # set this to the number of cores you have on your machine

    with progress.Progress(
        '[progress.description]{task.description}',
        progress.BarColumn(),
        '[progress.percentage]{task.percentage:>3.0f}%',
        progress.TimeRemainingColumn(),
        progress.TimeElapsedColumn(),
        refresh_per_second=1,  # bit slower updates
    ) as progress:
        futures = []  # keep track of the jobs
        with multiprocessing.Manager() as manager:
            # this is the key - we share some state between our
            # main process and our worker functions
            _progress = manager.dict()
            overall_progress_task = progress.add_task('[green]All jobs progress:')

            with ProcessPoolExecutor(max_workers=n_workers) as executor:
                for n in range(0, 20):  # iterate over the jobs we need to run
                    # set visible false so we don't have a lot of bars all at once:
                    task_id = progress.add_task(f'task {n}', visible=False)
                    futures.append(executor.submit(long_running_fn, _progress, task_id))

                # monitor the progress:
                while (n_finished := sum([future.done() for future in futures])) < len(
                    futures
                ):
                    progress.update(
                        overall_progress_task, completed=n_finished, total=len(futures)
                    )
                    for task_id, update_data in _progress.items():
                        latest = update_data['progress']
                        total = update_data['total']
                        # update the progress bar for this task:
                        progress.update(
                            task_id,
                            completed=latest,
                            total=total,
                            visible=latest < total,
                        )

                # raise any errors:
                for future in futures:
                    future.result()
