"""Setup script for projectcard package."""

from setuptools import setup, find_packages

setup(
    name="projectcard",
    version="0.1.2",
    description="",
    packages=find_packages(include=["projectcard"]),
    author="Elizabeth Sall",
    scripts=["bin/validate_card", "bin/update_projectcard_schema"],
    include_package_data=True,
)
