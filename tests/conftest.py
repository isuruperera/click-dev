import pytest

from click.testing import CliRunner

collect_ignore = ["test_utils"]


@pytest.fixture(scope="function")
def runner(request):
    return CliRunner()
