"""Automates common actions.

This module provides a set of functions to simplify repetitive operations in
various contexts, including data manipulation with pandas, etc.

Functions
---------
- ``add_row_dataframe(data, row) `` -- Appends ``row`` to ``data`` and returns a new
                                       DataFrame.

- ``fetch_html_content(url, timeout)`` -- Retrieve the html content from the ``url``.

- ``fetch_and_parse(url)`` -- Fetches HTML content from url and parses it.
"""

from typing import Optional

import requests
import pydantic
import bs4
import pandas as pd


from app.exception import MissingColumnsOrKeys
from app import types_

# pylint: disable=no-member


def append_row_dataframe(data: pd.DataFrame, row: dict) -> pd.DataFrame:
    """Append ``row`` in ``data``.

    Appends a new ``row`` to the end of the DataFrame ``data``.

    Parameters
    ----------
    data : DataFrame
        DataFrame in which to append ``row``.
    row : dict
        The ``row`` to be added.

    Returns
    -------
    DataFrame
        DataFrame with the new ``row`` appended.

    Raises
    ------
    TypeError
        If ``data`` is not a DataFrame or ``row`` a dict.
    MissingColumnsOrKeys
        If the columns of ``data`` or keys of ``row`` are missing.

    Notes
    ----
    The returned dataframe indexes are reset.

    Examples
    --------
    >>> import pandas as pd
    >>> data = pd.DataFrame()
    >>> row = {"col1": 8, "col2": 10}
    >>> append_row_dataframe(data, row)
       col1  col2
    0     8    10
    >>> data = pd.DataFrame({"col1": [1, 2], "col2": [4, 5]})
    >>> row = {"col1": 3, "col2": 6}
    >>> append_row_dataframe(data, row)
       col1  col2
    0     1     4
    1     2     5
    2     3     6
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a DataFrame")
    if not isinstance(row, dict):
        raise TypeError("row must be a dictionary")

    df_row = pd.DataFrame([row])
    if not data.empty:
        # Checking keys and columns
        extra_keys = set(row.keys()) - set(data.columns)
        missing_keys = set(data.columns) - set(row.keys())
        if extra_keys:
            raise MissingColumnsOrKeys(
                extra_keys, "These keys are not columns of the DataFrame"
            )
        if missing_keys:
            raise MissingColumnsOrKeys(
                missing_keys, "These columns are not dictionary keys"
            )

    return pd.concat([data, df_row], ignore_index=True)


def fetch_html_content(
    url: pydantic.HttpUrl, timeout: Optional[int] = 10
) -> types_.HTML:
    """Retrieve the html content from the ``url``.

    This function returns a HTML content or raises an exception
    if an error occurs (invalid URL, timeout, etc.).

    Parameters
    ----------
    url: pydantic.HttpUrl
        ``url`` of which we wish to retrieve html content.

    timeout: int, default=10
        Maximum waiting time in seconds before interruption.

    Returns
    -------
    types_.HTML
        An object containing the html content.

    Raises
    ------
    pydantic.ValidationError
       if ``url`` is invalid

    requests.ConnectionError
        If the service is unavailable (503 error).

    requests.Timeout
        If the request times out (408 error).

    requests.HTTPError
        If the request not found (404 error).
    """
    response = requests.get(url, timeout=timeout)  # type: ignore
    if response.status_code != requests.codes.OK:
        response.raise_for_status()

    return types_.HTML(response.text)


def fetch_and_parse(url: pydantic.HttpUrl):
    """Fetches HTML content and parses it with BeautifulSoup."""
    return bs4.BeautifulSoup(fetch_html_content(url), "lxml")
