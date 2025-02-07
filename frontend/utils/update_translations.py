import os
import subprocess
from pathlib import Path
import glob


def update_translations():
    # Create translations directory if it doesn't exist
    Path("translations").mkdir(exist_ok=True)

    # List all Python files in your project
    python_files = (
        glob.glob("pages/*.py")  # Include all Python files in the /pages directory
        + glob.glob(
            "dialogs/*.py"
        )  # Include all Python files in the /dialogs directory
        + ["app6.py"]  # Include the main app file
    )

    # Join the file paths into a single string
    python_files_str = " ".join(python_files)

    # Languages you want to support
    languages = ["fr", "en", "ar"]

    for lang in languages:
        print(f"Generating translations for {lang}...")

        # Generate .ts file
        ts_file = f"translations/app_{lang}.ts"
        pylupdate_command = f"pylupdate5 {python_files_str} -ts {ts_file}"
        subprocess.run(pylupdate_command, shell=True)

        # Generate .qm file
        lrelease_command = f"lrelease {ts_file}"
        subprocess.run(lrelease_command, shell=True)


if __name__ == "__main__":
    update_translations()
