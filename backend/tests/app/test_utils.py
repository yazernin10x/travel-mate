""" Define useful test

This module defines several tests for the ``utils.py`` module in the ``backend/app/ ``
package.
"""

import re
from unittest.mock import MagicMock, Mock

import pytest
import requests
import pydantic
import pandas as pd
from pytest_mock.plugin import MockerFixture

import config
from app import utils
from app import exception

# pylint: disable=no-member


class TestAppendRowToDataFrame:
    """Test class for the `append_row_dataframe` function."""

    @pytest.mark.parametrize(
        "data, row, error_msg",
        [
            ([1, 2], {"col1": 3, "col2": 4}, "data must be a DataFrame"),
            (
                pd.DataFrame([{"col1": 1, "col2": 2}]),
                {43, 547, 1},
                "row must be a dictionary",
            ),
        ],
    )
    def test_type_error(self, data: pd.DataFrame, row: dict, error_msg: str) -> None:
        """Test the raising of the TypeError exception.

        This parametric test ensures that the arguments ``data`` and ``row`` are of the
        correct types. An exception is raised if either argument is of an unexpected
        type.

        Parameters
        ----------
        data : DataFrame
            The DataFrame to which a row is being appended.
        row : iterable
            The ``row`` of data being appended to the DataFrame.
        error_msg : str
            The expected error message for the TypeError.

        Raises
        ------
        TypeError
            If data is not a DataFrame or if row is not a dictionary.
        """
        with pytest.raises(TypeError) as excinfo:
            utils.append_row_dataframe(data, row)
        assert str(excinfo.value) == error_msg

    @pytest.mark.parametrize(
        "data, row, error_msg",
        [
            (
                pd.DataFrame([{"col1": 1, "col2": 2, "col3": 5}]),
                {"col1": 3, "col2": 4},
                "These columns are not dictionary keys: col3.",
            ),
            (
                pd.DataFrame([{"col1": 1, "col2": 2}]),
                {"col1": 3, "col3": 4},
                "These keys are not columns of the DataFrame: col3.",
            ),
        ],
    )
    def test_missing_columns_or_keys(
        self, data: pd.DataFrame, row: dict, error_msg: str
    ) -> None:
        """Test the raising of the ``MissingColumnsOrKeys`` exception.

        This test verifies that the names and number of columns in ``data`` correspond
        exactly to the keys in ``row``. If a discrepancy is detected (missing column or
        key, different number), a 'MissingColumnsOrKeys' exception is raised.

        Parameters
        ----------
        data : DataFrame
            The DataFrame to which a row is being appended.
        row : dict
            The row of data being appended to the DataFrame.
        error_msg : str
            The expected error message for the ``MissingColumnsOrKeys``.

        Raises
        ------
        MissingColumnsOrKeys
            If columns are missing in ``data`` or keys are missing in row.
        """
        assert data.empty is False
        with pytest.raises(exception.MissingColumnsOrKeys) as excinfo:
            utils.append_row_dataframe(data, row)

        value = re.sub(r"\{|\}|'", "", str(excinfo.value))
        assert value == error_msg

    @pytest.mark.parametrize(
        "data, row, expected_value",
        [
            (
                pd.DataFrame(),
                {"col1": 8, "col2": 10},
                pd.DataFrame({"col1": [8], "col2": [10]}),
            ),
            (
                pd.DataFrame({"col1": [1, 2], "col2": [4, 5]}),
                {"col1": 3, "col2": 6},
                pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]}),
            ),
        ],
    )
    def test_succed(
        self, data: pd.DataFrame, row: dict, expected_value: pd.DataFrame
    ) -> None:
        """Test append of row to data.

        Parameters
        ----------
        data : DataFrame
            The DataFrame to which a row is being appended.
        row : iterable
            The row of data being appended to the DataFrame.
        expected_value : DataFrame
            The expected result after the append of the ``row`` in ``data``.
        """
        assert utils.append_row_dataframe(data, row).equals(expected_value)


class TestFetcHtmlContent:
    """Test class for the `fetch_html_content` function."""

    def test_get_200_ok(self, mock_requests_get: tuple[MagicMock, Mock]) -> None:
        """Test the 200 (OK) response.

        This test ensures that the ``scrape_tourism_sites`` function correctly
        collects and processes data from the Ivorian tourism website.

        Parameters
        ----------
        mock_requests_get: tuple[MagicMock, Mock]
            A pytest fixture that mocks the requests.get method for testing purposes.
        """
        url = pydantic.HttpUrl("https://www.mock-adress.org")
        expected_value = """
            <html>
                <body>
                    <h1>Title</h1>
                    <p>Test `requests.get` succed</p>
                </body>
            </html>
        """

        mock_get, mock_response = mock_requests_get
        mock_response.status_code = requests.codes.ok
        mock_response.text = expected_value

        result = utils.fetch_html_content(url)
        mock_get.assert_called_once()
        assert result == expected_value

    def test_get_404_not_found(self, mock_requests_get: tuple[MagicMock, Mock]) -> None:
        """Test the 404 (Not Found) response.

        This test simulates a scenario where a request to the target URL
        returns a 404 status code. It verifies that the scrape_tourism_sites
        function raises a requests.HTTPError with the message "404 Not Found"
        when a 404 error occurs.

        Parameters
        ----------
        mock_requests_get: tuple[MagicMock, Mock]
            A pytest fixture that mocks the requests.get method for testing purposes.

        Raises
        ------
        requests.HTTPError
            If the request not found (404 error).
        """
        mock_get, mock_response = mock_requests_get
        mock_response.status_code = requests.codes.not_found
        http_error = requests.HTTPError("404 Not Found")
        mock_response.raise_for_status.side_effect = http_error

        with pytest.raises(requests.HTTPError, match="404 Not Found"):
            utils.fetch_html_content(config.IVORY_COAST_URL)

        mock_get.assert_called_once_with(config.IVORY_COAST_URL, timeout=10)

    def test_get_503_service_unavailable(
        self, mocker: MockerFixture, mock_requests_get: tuple[MagicMock, Mock]
    ) -> None:
        """Test the 503 (Service Unavailable ) response.

        This test simulates service unavailability by mocking requests.get to
        return a 503 status code and raise a ConnectionError with the message
        "503 Service Unavailable".

        Parameters
        ----------
        mocker: MockerFixture
            Fixture to mock the behavior of external dependencies.
            The ``pytest-mock`` fixture for mocking objects.
        mock_requests_get: tuple[MagicMock, Mock]
            A pytest fixture that mocks the requests.get method for testing purposes.

        Raises
        ------
            requests.ConnectionError: If the service is unavailable
                                      (503 error).
        """
        mock_get, mock_response = mock_requests_get
        mock_response.status_code = requests.codes.service_unavailable
        connection_error = requests.ConnectionError("503 Service Unavailable")
        mock_response.raise_for_status.side_effect = connection_error
        mocker.patch.object(
            config,
            "IVORY_COAST_URL",
            "https://www.missing-adress.org",
        )

        with pytest.raises(
            requests.ConnectionError,
            match="503 Service Unavailable",
        ):
            utils.fetch_html_content(config.IVORY_COAST_URL)

        mock_get.assert_called_once_with(config.IVORY_COAST_URL, timeout=10)

    def test_get_408_request_timeout(
        self, mock_requests_get: tuple[MagicMock, Mock]
    ) -> None:
        """Test the 408 (Request Timeout) response.

        This test simulates a timeout scenario by mocking the `requests.get`
        method to return a 408 status code and raising a `Timeout` exception
        with the message "408 Request Timeout".

        Parameters
        ----------
        mock_requests_get: tuple[MagicMock, Mock]
            A pytest fixture that mocks the requests.get method for testing purposes.

        Raises
        ------
        requests.Timeout
            If the request times out (408 error).
        """
        mock_get, mock_response = mock_requests_get
        mock_response.status_code = requests.codes.request_timeout
        connection_error = requests.Timeout("408 Request Timeout")
        mock_response.raise_for_status.side_effect = connection_error

        with pytest.raises(requests.Timeout, match="408 Request Timeout"):
            utils.fetch_html_content(config.IVORY_COAST_URL)

        mock_get.assert_called_once_with(config.IVORY_COAST_URL, timeout=10)
