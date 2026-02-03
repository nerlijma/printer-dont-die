# Printer Don't Die

Automated photo printing system that periodically prints photos to keep your printer from drying out or getting clogged.

## Configuration

Edit `config.json` in the project root:

```json
{
  "print_frequency_days": 7,
  "printer_name_or_ip": "YOUR_PRINTER_NAME_HERE",
  "printer_tool_exe": "SumatraPDF-3.5.2-64.exe",
  "last_printed_date": "",
  "dry_run": false
}
```

**Configuration Options:**
- `print_frequency_days`: How often to print (in days). Default: 7
- `printer_name_or_ip`: Exact name of your printer (must match exactly as shown in system settings)
- `printer_tool_exe`: (Windows only) Path to PDF printer tool executable (e.g., SumatraPDF). Required for PDF printing on Windows. Leave empty to use default Windows print command.
- `last_printed_date`: Last print date (ISO format: YYYY-MM-DD). Leave empty for first run
- `dry_run`: Set to `true` to test without actually printing. Set to `false` for normal operation

**Note:** The application always uses `app/resources/test_photo.pdf` for printing.

## Running

**From Python:**
```bash
python app/main.py
```

**Or use the scripts:**
- macOS: `./gen_macos.sh` to build, then run from `dist/`
- Windows: `gen_win.bat` to build, then run from `dist/`

## Build

### Build in Windows

```cmd
pip install pyinstaller
gen_win.bat
```

The `.exe` file will be in `dist/printer-dont-die.exe`

### Build in macOS

```bash
brew install pyinstaller
./gen_macos.sh
```

The executable will be in `dist/printer-dont-die`

**To run the executable:**
```bash
cd dist
./printer-dont-die
```

**Note:** If macOS blocks the executable (Gatekeeper), run:
```bash
xattr -cr dist/printer-dont-die
```
