from calcipy.cli import task


def test_task_decorator_without_parens():
    @task
    def my_task(ctx):
        pass

    assert callable(my_task)
    assert my_task.__wrapped__.__name__ == 'my_task'
