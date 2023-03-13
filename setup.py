"""Installation script for projectcard_validator package."""

import os

from setuptools import setup

version = "0.0.1"

classifiers = [
    "Development Status :: 1 - Planning",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
]

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.readlines()
install_requires = [r.strip() for r in requirements]

setup(
    name="projectcard",
    version=version,
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/network-wrangler/projectcard",
    license="Apache 2",
    platforms="any",
    packages=["projectcard"],
    include_package_data=True,
    install_requires=install_requires,
    scripts = [bin/validate_card],
)
