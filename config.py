"""Define the app's configurations

Constants
---------
- ``ROOT_DIR``: The absolute path to the project's root directory.
- ``IVORY_COAST_URL``: URL of tourists websites of the ivory coast
"""

from pathlib import Path

import pydantic

ROOT_DIR = Path(__file__).resolve()

# URL
IVORY_COAST_URL = pydantic.HttpUrl("https://tourisme.gouv.ci/accueil/sitetouristique")
