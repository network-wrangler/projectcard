from setuptools import setup, find_packages

setup(
    name="projectcard",
    version="0.0.1",
    description="",
    packages=find_packages(include=['projectcard']),
    author="Elizabeth Sall",
    install_requires=["jsonschema"],
    scripts=["bin/validate_card","bin/update_projectcard_schema"],
    include_package_data=True,
)
