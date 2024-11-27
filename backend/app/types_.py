"""Define useful types

This module provides new types for representing certain types of information, such as
HTML text, which is represented by the HTML type to indicate that the text is in HTML
format.

Types
-----
- ``HTML`` -- Type to represent HTML format.
"""

from typing import NewType


HTML = NewType("HTML", str)
