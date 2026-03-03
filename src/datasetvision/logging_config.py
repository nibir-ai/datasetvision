"""
Central logging configuration for datasetvision.
"""

import logging


def configure_logging(verbose: bool = False) -> None:
    """
    Configure application-wide logging.
    """

    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
