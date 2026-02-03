import asyncio
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


def is_within_time_range(config):
    """Check if current time is within run_time_start and run_time_end range."""
    run_time_start = config.get("run_time_start", "")
    run_time_end = config.get("run_time_end", "")

    if not run_time_start or not run_time_end:
        raise ValueError(
            "run_time_start and run_time_end must be configured in config.json"
        )

    try:
        now = datetime.datetime.now().time()
        start_time = datetime.datetime.strptime(run_time_start, "%H:%M").time()
        end_time = datetime.datetime.strptime(run_time_end, "%H:%M").time()

        # Validate that end_time is greater than start_time (same day)
        if end_time <= start_time:
            raise ValueError(
                f"run_time_end ({run_time_end}) must be greater than run_time_start ({run_time_start})"
            )

        # Check if current time is within the range
        return start_time <= now <= end_time
    except ValueError as e:
        # Re-raise if it's our validation error, otherwise it's a format error
        if "must be greater" in str(e):
            raise
        raise ValueError(
            f"Invalid time format in config. Expected HH:MM format. Error: {e}"
        )


def job_sync():
    """
    Checks the configuration date and frequency to determine if a print job
    should be executed today. This is the synchronous job function.
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


async def main():
    """Main async function that runs the print job in a loop."""
    # Print sys._MEIPASS contents at startup for debugging
    print_meipass_contents()

    while True:
        config = load_config()
        if config:
            try:
                # Check if we're within the allowed time range
                if is_within_time_range(config):
                    # Run the job asynchronously without blocking the event loop
                    await asyncio.to_thread(job_sync)
                else:
                    # Skip execution if outside time range
                    now = datetime.datetime.now().strftime("%H:%M")
                    print(
                        f"Current time {now} is outside allowed range. Skipping execution."
                    )
            except ValueError as e:
                print(f"ERROR: {e}")
                print("Please configure run_time_start and run_time_end in config.json")
                # Wait before retrying
                await asyncio.sleep(60)
                continue

        # Wait 10 minutes (600 seconds) between executions
        await asyncio.sleep(600)


if __name__ == "__main__":
    asyncio.run(main())
