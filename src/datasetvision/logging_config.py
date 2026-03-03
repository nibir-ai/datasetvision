"""
Central logging configuration for datasetvision.
"""

import logging


def configure_logging(verbose: bool = False) -> None:
    """
    Configure logging behavior.
    """

    root = logging.getLogger()

    # Clear existing handlers
    if root.hasHandlers():
        root.handlers.clear()

    if verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
    else:
        logging.basicConfig(
            level=logging.WARNING,
        )
