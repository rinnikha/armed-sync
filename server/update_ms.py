#!/usr/bin/env python3
"""
update_ms.py - Simple script to reinstall a local package.

This script reinstalls a local package (specified in .env file) in the current project.
Run this script whenever you want to update the package after making changes to it.
"""

import os
import subprocess
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get package path from environment variable
PACKAGE_PATH = os.getenv('MS_LOCAL_PACKAGE_PATH')


def get_package_name(package_path):
    """Determine the package name from the package path."""
    # For Node.js packages, try to read from package.json
    package_json_path = os.path.join(package_path, 'package.json')
    if os.path.exists(package_json_path):
        try:
            import json
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
                if 'name' in package_data:
                    return package_data['name']
        except Exception as e:
            print(f"Warning: Couldn't read package name from package.json: {e}")

    # Fall back to directory name
    return os.path.basename(os.path.normpath(package_path))


def install_package(package_path):
    """Install the package in the current project."""
    package_name = get_package_name(package_path)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"[{current_time}] Installing {package_name}...")

    try:
        # Determine if it's a Node.js or Python package
        if os.path.exists(os.path.join(package_path, 'package.json')):
            # For Node.js packages
            cmd = ["npm", "install", package_path]
        else:
            # For Python packages (running in the project's venv)
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--no-deps", package_path]

        subprocess.run(cmd, check=True)
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing {package_name}: {e}")
        return False


def main():
    """Main function to update the package on demand."""
    if not PACKAGE_PATH:
        print("Error: MS_LOCAL_PACKAGE_PATH not set in .env file")
        sys.exit(1)

    if not os.path.isdir(PACKAGE_PATH):
        print(f"Error: Package path '{PACKAGE_PATH}' is not a valid directory")
        sys.exit(1)

    package_name = get_package_name(PACKAGE_PATH)
    print(f"Reinstalling package {package_name} from {PACKAGE_PATH}")

    install_package(PACKAGE_PATH)

    print("Update complete. Run this script again when you want to reinstall the package.")


if __name__ == "__main__":
    main()