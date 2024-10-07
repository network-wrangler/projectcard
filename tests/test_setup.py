"""Test that the package can be setup and imported."""

import shutil
import subprocess

from projectcard.logger import CardLogger


def test_setup():
    """Create virtual environment and test that projectcard can be installed + imported."""
    CardLogger.debug("Creating virtual environment...")
    subprocess.run(["python", "-m", "venv", "projectcardtest"], check=True)
    CardLogger.debug("Created virtual environment.\nInstalling ProjectCard...")

    try:
        install_process = subprocess.run(
            ["projectcardtest/bin/pip", "install", "-e", "."],
            check=True,
            capture_output=True,
            text=True,
        )
        CardLogger.debug("ProjectCard installed successfully.")
    except subprocess.CalledProcessError as e:
        CardLogger.error(f"Installation failed with error: {e.stderr}")
        raise

    # Clean up the virtual environment after the test
    shutil.rmtree("projectcardtest")
