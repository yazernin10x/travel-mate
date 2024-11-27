"""Define useful exceptions

CLASS
-----
- ``MissingColumnsOrKeys`` -- Indicate missing columns or keys in ``data`` or ``row``.
"""

from typing import Iterable, Optional


class MissingColumnsOrKeys(Exception):
    """Indicate missing columns or keys in ``data`` or ``row``.

    Methods
    -----
    - __init__(missing_items, message=None) -- Initialize exception
    """

    def __init__(
        self, missing_items: Iterable[str], message: Optional[str] = None
    ) -> None:
        """Initialize exception.

        Parameters
        ----------
        missing_items : Iterable[str]
            An iterable of strings of missing columns or keys.

        message : str, optional
            A custom error message. If not provided, a default message is generated.
        """
        self.missing_items = ", ".join(map(str, missing_items))
        self.message = message
        if self.message is None:
            self.message = "Missing columns or keys"
        super().__init__(f"{self.message}: {self.missing_items}.")
