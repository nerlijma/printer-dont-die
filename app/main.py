import datetime
import os
import sys

from config import load_config, update_config
from photos import get_random_photo
from printer import print_photo


def print_meipass_contents():
    """Print contents of app/ folder in sys._MEIPASS if running from PyInstaller executable."""
    if getattr(sys, "frozen", False):
        app_path = os.path.join(sys._MEIPASS, "app")
        if os.path.exists(app_path):
            print("Contents of app/ in sys._MEIPASS:")
            try:
                for root, dirs, files in os.walk(app_path):
                    level = root.replace(app_path, "").count(os.sep)
                    indent = " " * 2 * level
                    print(f"{indent}{os.path.basename(root)}/")
                    subindent = " " * 2 * (level + 1)
                    for file in files:
                        print(f"{subindent}{file}")
            except Exception as e:
                print(f"  Error listing contents: {e}")
        else:
            print(f"app/ folder not found in sys._MEIPASS: {sys._MEIPASS}")


def check_and_run_print_job():
    """
    Checks the configuration date and frequency to determine if a print job
    should be executed today.
    """
    config = load_config()
    if not config:
        return

    # Check if dry_run is enabled
    dry_run = config.get("dry_run", False)

    # If dry_run is true, always run and skip date checking
    if dry_run:
        print("DRY RUN MODE: Skipping date check, will always run.")
        should_print = True
    else:
        frequency_days = config.get("print_frequency_days", 7)
        last_date_str = config.get("last_printed_date")
        today = datetime.date.today()

        should_print = False

        # Check if a last print date exists
        if last_date_str:
            try:
                last_date = datetime.date.fromisoformat(last_date_str)
                days_passed = (today - last_date).days

                if days_passed >= frequency_days:
                    should_print = True
                    print(f"It has been {days_passed} days. Time to print!")
                else:
                    print(
                        f"Last print was {days_passed} days ago. Waiting for {frequency_days} days."
                    )

            except ValueError:
                print(
                    "Configuration error: 'last_printed_date' is invalid. Printing now."
                )
                should_print = True

        else:
            # First execution, no date recorded
            should_print = True
            print("First time run. Printing photo.")

    # Execute the job if scheduled
    if should_print:
        # STEP 1: Get photo
        temp_photo_path = get_random_photo()

        if temp_photo_path and os.path.exists(temp_photo_path):
            # STEP 2: Print
            exit_code = print_photo(temp_photo_path)
            if exit_code != 0:
                print(f"ERROR: Failed to send print job. Exit code: {exit_code}")
                return
            else:
                update_config("last_printed_date", datetime.date.today().isoformat())

            # Note: test_photo.pdf is never deleted as it's part of the resources
        else:
            print("ERROR: Could not download or find the photo file. Aborting print.")


if __name__ == "__main__":
    # Print sys._MEIPASS contents at startup for debugging
    print_meipass_contents()
    check_and_run_print_job()
