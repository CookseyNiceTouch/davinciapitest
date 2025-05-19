# Davinci API Test

This project is a simple test of the Davinci API. It is currently set up to work with [UV](https://github.com/astral-sh/uv) and uses Python version 3.13.

## What does `davinciapitest.py` do?

- Checks that you are running 64-bit Python 3.13 or newer.
- Sets up the environment variables and paths required for the DaVinci Resolve scripting API, depending on your operating system (Windows, macOS, or Linux).
- Adds the DaVinci Resolve scripting modules to the Python path.
- Attempts to import the `DaVinciResolveScript` module and provides detailed error messages if it fails.
- Connects to a running instance of DaVinci Resolve and prints a success or failure message.
- If connected, prints the DaVinci Resolve version and the name of the currently open project (if any).

## Requirements

- DaVinci Resolve installed on your system.
- Python 3.13 (64-bit).
- [UV](https://github.com/astral-sh/uv) for dependency management (if needed).

## Usage

1. Make sure DaVinci Resolve is running.
2. Run the script:
   ```sh
   python davinciapitest.py
   ```
3. The script will print diagnostic information and details about your DaVinci Resolve installation and current project.
