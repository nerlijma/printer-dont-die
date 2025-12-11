import os
import platform

from config import load_config


# --- Print Function ---
def print_photo(file_path):
    """
    Prints the file using the appropriate system command for Windows, Linux, or macOS.
    """
    config = load_config()
    if not config:
        return

    printer_target = config.get("printer_name_or_ip")
    current_os = platform.system()
    command = ""

    # 1. Select the appropriate command
    if current_os == "Windows":
        # Using the reliable rundll32 trick to leverage the native Windows photo viewer print function.
        # This requires the image file path and the EXACT printer name to be in quotes.
        dll_path = r"C:\WINDOWS\system32\shimgvw.dll"
        function_name = "ImageView_PrintTo"
        # Command format: rundll32 <dll_path>,<function_name> "file_path" "printer_name"
        command = (
            f'rundll32 "{dll_path}",{function_name} "{file_path}" "{printer_target}"'
        )

    elif current_os == "Linux":
        # Using LPR, the standard command-line print utility for CUPS (Common Unix Printing System).
        # -P specifies the printer name/queue.
        command = f'lpr -P "{printer_target}" "{file_path}"'

    elif current_os == "Darwin":  # macOS
        # Using LP, the standard command-line print utility for CUPS on macOS.
        # -d specifies the printer name/queue.
        # If printer_target is empty, use default printer
        if printer_target:
            command = f'lp -d "{printer_target}" "{file_path}"'
        else:
            # Use default printer if no printer specified
            command = f'lp "{file_path}"'

    else:
        print(f"Operating system '{current_os}' is not supported for printing.")
        return

    print(f"Executing print command ({current_os}): {command}")

    # 2. Execute the command
    return os.system(command)
