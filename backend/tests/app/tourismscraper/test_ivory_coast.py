"""Define the unit tests to retrieve data from the tourist site of Ivory Coast."""

import bs4
import pytest
import pandas as pd
from pytest_mock.plugin import MockerFixture

from app.tourismscraper import ivory_coast
from app import types_

# pylint: disable=no-member


@pytest.mark.parametrize(
    "first_response, detail_response",
    [
        ("<html><body></body></html>", ""),
        ('<a href="https://tourist_site.com/1">Lire plus</a>', ""),
    ],
)
def test_empty_response(
    mocker: MockerFixture, first_response: types_.HTML, detail_response: types_.HTML
) -> None:
    """Test the response of the tourist site's URL.

    This parameterized test evaluates how the function handles the content of the main
    page and the detail pages of tourist sites.

    The goal is to verify two cases:
    1. When the main page, supposed to contain all the tourist site URLs, contains no
        links.
    2. For each valid URL on the page, if the linked tourist site contains no valid data.

    Parameters
    ----------
    mocker: MockerFixture
        Fixture to mock the behavior of external dependencies.
    first_response: str
        Simulated HTML content of the initial page response.
    detail_response: str
        Simulated HTML content of the detail page response.
    """
    mock = mocker.patch("app.utils.fetch_and_parse")
    mock.side_effect = [
        bs4.BeautifulSoup(first_response, "lxml"),
        bs4.BeautifulSoup(detail_response, "lxml"),
    ]
    result = ivory_coast.scrape_tourism_sites()
    mock.assert_called()
    assert isinstance(result, pd.DataFrame)
    assert result.empty is True
    assert len(result) == 0


@pytest.mark.parametrize(
    "first_response, detail_frist_response, detail_seconde_response",
    [
        (
            """<a href="https://tourist_site.com/1">Lire plus</a>
                <a href="https://tourist_site.com/2"">Lire plus</a>""",
            """<div class="news_content">
                    <a href="#">Titre du site 1</a>
                    <img src="https://tourist_site.com/1/detail/image_site.jpg" />
                    <p>Description du site touristique 1.</p>
                </div>""",
            """<div class="news_content">
                    <a href="#">Titre du site 2</a>
                    <img src="https://tourist_site.com/2/detail/image_site.jpg" />
                    <p>Description du site touristique 2.</p>
                </div>""",
        ),
        (
            """<a href="https://tourist_site.com/1">Lire plus</a>
               <a href="https://tourist_site.com/2">Lire plus</a>""",
            """<div class="news_content"></div>""",
            """<div class="news_content"></div>""",
        ),
        (
            """<a href="https://tourist_site.com/1">Lire plus</a>
               <a href="https://tourist_site.com/2">Lire plus</a>""",
            """<div class="news_content"><a href="#">Titre du site 1</a></div>""",
            """<div class="news_content"><a href="#">Titre du site 2</a></div>""",
        ),
        (
            """<a href="https://tourist_site.com/1">Lire plus</a>
               <a href="https://tourist_site.com/2">Lire plus</a>""",
            """<div class="news_content"></div>""",
            """<div class="news_content"><img src="https://tourist_site.com/2/detail/image_site.jpg"/></div>""",
        ),
        (
            """<a href="https://tourist_site.com/1">Lire plus</a>
               <a href="https://tourist_site.com/2">Lire plus</a>""",
            """<div class="news_content"><p>Description du site touristique 1.</p></div>""",
            """<div class="news_content"></div>""",
        ),
    ],
)
def test_non_empty_response(
    mocker: MockerFixture,
    first_response: types_.HTML,
    detail_frist_response: types_.HTML,
    detail_seconde_response: types_.HTML,
) -> None:
    """Test the response of the tourist site's URL.

    This parameterized test evaluates how the function handles the content of the main
    page and the detail pages of tourist sites.

    In this test, we assume that the main page contains valid URLs of tourist sites,
    and that the detail page may or may not contain data such as the title,
    description, etc.

    The goal is to verify several cases:
    1. all data such as title are present in tourist site page.
    2. Nothing data are not present in tourist site page.
    3. Only tourist site title is available in tourist site page.
    3. Etc.

    Parameters
    ----------
    mocker: MockerFixture
        Fixture to mock the behavior of external dependencies.
    first_response: str
        Simulated HTML content of the main page response containing all url
        tourist sites.
    detail_frist_response: str
        Simulated HTML content of the detail page response tourist site.
    detail_seconde_response: str
        Simulated HTML content of the detail page response tourist site.
    """
    mock = mocker.patch("app.utils.fetch_and_parse")
    mock.side_effect = [
        bs4.BeautifulSoup(first_response, "lxml"),
        bs4.BeautifulSoup(detail_frist_response, "lxml"),
        bs4.BeautifulSoup(detail_seconde_response, "lxml"),
    ]
    result = ivory_coast.scrape_tourism_sites()
    url = result["url"].iloc[0]
    title = result["title"].iloc[0]
    picture = result["picture"].iloc[0]
    description = result["description"].iloc[0]

    mock.assert_called()
    assert isinstance(result, pd.DataFrame)
    assert len(result) in [1, 2]
    assert url == "https://tourist_site.com/1"
    assert title in [None, "Titre du site 1"], f"Unexpected title: {title}"
    assert picture in [None, "https://tourist_site.com/1/detail/image_site.jpg"]
    assert description in [None, "Description du site touristique 1."]
