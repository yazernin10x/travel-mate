"""Define global fixtures
"""

from unittest.mock import Mock, MagicMock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture(name="mock_requests_get")
def mock_requests_method_get(mocker: MockerFixture) -> tuple[MagicMock, Mock]:
    """Create Mock of ``requests.get``

    Fixture to replace the requests.get function with a mocked version returning a
    custom response.

    Parameters
    ----------
    mocker: MockerFixture
        The ``pytest-mock`` fixture for mocking objects.

    Returns
    -------
    tuple[MagicMock, Mock]
        Two mock objects are returned: the object replacing requests.get and associated
        the object response.

    """
    mock_get = mocker.patch("requests.get")
    mock_response = mocker.Mock()
    mock_get.return_value = mock_response
    return mock_get, mock_response
