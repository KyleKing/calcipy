from calcipy.tasks.executable_utils import _EXECUTABLE_CACHE, check_installed


def test_check_installed_cache_hit(ctx):
    _EXECUTABLE_CACHE['test_exec'] = ctx.run('which test_exec', warn=True, hide=True)

    check_installed(ctx, executable='test_exec', message='missing')

    del _EXECUTABLE_CACHE['test_exec']
