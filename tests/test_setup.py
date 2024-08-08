"""Test that the package can be setup and imported."""

from projectcard.logger import CardLogger


def test_setup():
    """Create virtual environment and test that projectcard can be installed + imported."""
    import subprocess
    import shutil

    CardLogger.debug("Creating virtual environment...")
    subprocess.run(["python", "-m", "venv", "projectcardtest"], check=True)
    CardLogger.debug("Created virtual environment.\nInstalling ProjectCard...")
    install_process = subprocess.run(["projectcardtest/bin/pip", "install", "-e", "."], check=True)
    CardLogger.debug(f"Installed Wrangler.\n{install_process.stdout}")
    pip_list_process = subprocess.run(
        ["projectcardtest/bin/pip", "list"], capture_output=True, text=True
    )
    CardLogger.debug(f"Venv contents:\n{pip_list_process.stdout}")
    CardLogger.debug("Testing import...")
    subprocess.run(["projectcardtest/bin/python", "-c", "import projectcard"], check=True)
    CardLogger.debug("Projectcard can import.")
    shutil.rmtree("projectcardtest")
