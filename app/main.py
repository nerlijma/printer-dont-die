import datetime
import os

from config import load_config, update_config
from google import get_random_photo_and_download
from printer import print_photo


def check_and_run_print_job():
    """
    Checks the configuration date and frequency to determine if a print job
    should be executed today.
    """
    config = load_config()
    if not config:
        return

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
            print("Configuration error: 'last_printed_date' is invalid. Printing now.")
            should_print = True

    else:
        # First execution, no date recorded
        should_print = True
        print("First time run. Printing photo.")

    # Execute the job if scheduled
    if should_print:
        # STEP 1: Download the photo (REPLACE with actual Google Photos code)
        temp_photo_path = get_random_photo_and_download()

        if temp_photo_path and os.path.exists(temp_photo_path):
            # STEP 2: Print
            exit_code = print_photo(temp_photo_path)
            if exit_code != 0:
                print(f"ERROR: Failed to send print job. Exit code: {exit_code}")
                return
            else:
                print("Print job successfully sent to the system queue.")
                update_config("last_printed_date", datetime.date.today().isoformat())

            # Cleanup the temporary file (optional but recommended)
            try:
                os.remove(temp_photo_path)
            except Exception as e:
                print(f"Warning: Could not delete temp file: {e}")
        else:
            print("ERROR: Could not download or find the photo file. Aborting print.")


if __name__ == "__main__":
    check_and_run_print_job()
