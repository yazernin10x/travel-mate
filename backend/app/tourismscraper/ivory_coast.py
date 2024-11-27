""""Define the useful functions to scrape ivory coast tourism website

FUNCTIONS
---------
- ``scrape_tourism_website()`` -- Scrape ivory coast tourism website
"""

import re

import bs4
import config
import pandas as pd

from app import utils

# pylint: disable=no-member


def scrape_tourism_sites() -> pd.DataFrame:
    """Scrape ivory coast tourism website

    This function scrapes Ivory Coast tourism website to extract data such as titles, image URLs, and descriptions of tourist sites.

    Returns
    -------
    pandas.DataFrame
        DataFrame which contains the scraped data
    """
    tourist_sites = pd.DataFrame()
    soup = utils.fetch_and_parse(config.IVORY_COAST_URL)
    links = soup.find_all("a", string=re.compile("lire plus", re.IGNORECASE))
    for link in links:
        soup = utils.fetch_and_parse(link["href"])
        tourist_site = soup.find("div", class_="news_content")
        if isinstance(tourist_site, bs4.element.Tag):
            title, picture, description = None, None, None

            a = tourist_site.find("a")
            if isinstance(a, bs4.element.Tag):
                title = a.string

            img = tourist_site.find("img")
            if isinstance(img, bs4.element.Tag):
                picture = img["src"]

            try:
                describe_content = tourist_site.contents[-2]
            except IndexError:
                pass
            else:
                description = describe_content.get_text()

            tourist_sites = utils.append_row_dataframe(
                tourist_sites,
                {
                    "url": link["href"],
                    "title": title,
                    "picture": picture,
                    "description": description,
                },
            )
    return tourist_sites
