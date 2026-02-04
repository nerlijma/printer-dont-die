import os
import platform

from loguru import logger

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
        # Check if file is PDF or image
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == ".pdf":
            # For PDFs, use the configured printer tool (e.g., SumatraPDF)
            printer_tool = config.get("printer_tool_exe", "")
            if printer_tool and printer_tool.strip():
                # Use the specified printer tool with -print-to option
                # Format: {printer_tool_exe} -print-to "{printer_name}" "{file_path}"
                # Assume both executables are in the same directory (where config.json is)
                from config import get_base_path

                base_path = get_base_path()
                printer_tool = os.path.join(base_path, printer_tool)
                # Don't quote the executable path, only quote arguments that might have spaces
                command = f'{printer_tool} -print-to "{printer_target}" "{file_path}"'
            else:
                # Fallback: use Windows print command if no tool specified
                command = f'print /D:"{printer_target}" "{file_path}"'
        else:
            # For images, use the reliable rundll32 trick to leverage the native Windows photo viewer print function.
            # This requires the image file path and the EXACT printer name to be in quotes.
            dll_path = r"C:\WINDOWS\system32\shimgvw.dll"
            function_name = "ImageView_PrintTo"
            # Command format: rundll32 <dll_path>,<function_name> "file_path" "printer_name"
            command = f'rundll32 "{dll_path}",{function_name} "{file_path}" "{printer_target}"'

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
        logger.error(f"Operating system '{current_os}' is not supported for printing.")
        return

    # 2. Check if dry_run is enabled
    dry_run = config.get("dry_run", False)
    if dry_run:
        logger.info("DRY RUN MODE: Skipping actual print command execution.")
        return 0

    # 3. Execute the command
    logger.info(f"Executing print command ({current_os}): {command}")
    exit_code = os.system(command)
    if exit_code == 0:
        logger.info("Print job successfully sent to the system queue.")
    else:
        logger.error(f"Failed to send print job. Exit code: {exit_code}")
    return exit_code
