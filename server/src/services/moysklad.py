from moysklad_api import MoySklad
from src.core.config import settings


def get_ms1_client() -> MoySklad:
    """
    Get a MoySklad client for MS1.
    """
    if not settings.MS1_TOKEN:
        raise ValueError("MS1_TOKEN is not set in the environment")

    return MoySklad(
        token=settings.MS1_TOKEN,
        debug=True  # Set to True for debugging
    )


def get_ms2_client() -> MoySklad:
    """
    Get a MoySklad client for MS2.
    """
    if not settings.MS2_TOKEN:
        raise ValueError("MS2_TOKEN is not set in the environment")

    return MoySklad(
        token=settings.MS2_TOKEN,
        debug=True  # Set to True for debugging
    )