import os
import sys

from config import get_resource_path
from loguru import logger


def get_random_photo():
    """
    Gets a photo to print. Always uses test_photo.pdf from resources.
    Returns the absolute path to the photo file.
    """
    # Always use test_photo.pdf from resources
    photo_path = get_resource_path("app/resources/test_photo.pdf")

    # If that doesn't work, try alternative path
    if not os.path.exists(photo_path):
        # Try without app/ prefix (in case PyInstaller structure is different)
        if getattr(sys, "frozen", False):
            alt_path = os.path.join(sys._MEIPASS, "resources", "test_photo.pdf")
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            alt_path = os.path.join(current_dir, "resources", "test_photo.pdf")

        if os.path.exists(alt_path):
            photo_path = alt_path

    if os.path.exists(photo_path):
        logger.info(f"Using test photo: {photo_path}")
        return os.path.abspath(photo_path)
    else:
        logger.error(f"test_photo.pdf not found at: {photo_path}")
        if getattr(sys, "frozen", False):
            logger.debug(f"sys._MEIPASS = {sys._MEIPASS}")
            logger.debug(
                f"Looking in: {os.path.join(sys._MEIPASS, 'app', 'resources')}"
            )
            if os.path.exists(os.path.join(sys._MEIPASS, "app")):
                logger.debug(
                    f"Contents of {os.path.join(sys._MEIPASS, 'app')}: {os.listdir(os.path.join(sys._MEIPASS, 'app'))}"
                )
        return None
