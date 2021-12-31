"""Test the Cement CLI Application."""

from calcipy.cli.main import CLIAppTest


def test_calcipy_cli():
    """Test calcipy without any subcommands or arguments."""
    with CLIAppTest() as app:
        app.run()
        assert app.exit_code == 0


def test_calcipy_debug_cli():
    """Test that debug mode is functional."""
    argv = ['--debug']
    with CLIAppTest(argv=argv) as app:
        app.run()
        assert app.debug is True
        assert app.exit_code == 0


# PLANNED: Not yet used. From cement boilerplate

# def test_echo():
#     """Test echo without arguments."""
#     argv = ['echo']
#     with CLIAppTest(argv=argv) as app:
#         app.run()
#         data,output = app.last_rendered
#         assert data['foo'] == 'bar'
#         assert output.find('Foo => bar')
#
#
# def test_echo_args():
#     """Test echo with arguments."""
#     argv = ['echo', '--foo', 'not-bar']
#     with CLIAppTest(argv=argv) as app:
#         app.run()
#         data,output = app.last_rendered
#         assert data['foo'] == 'not-bar'
#         assert output.find('Foo => not-bar')
