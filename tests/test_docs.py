"""Test Documentation builds and utilities."""

import subprocess

import markdown
import pytest

from projectcard.docs import card_list_to_table, json_schema_to_md
from projectcard.logger import CardLogger


def test_mkdocs_build(request):
    """Tests that the MkDocs documentation can be built without errors."""
    CardLogger.info(f"--Starting: {request.node.name}")
    subprocess.run(["mkdocs", "build"], capture_output=True, text=True, check=True)
    CardLogger.info(f"--Finished: {request.node.name}")


def test_jsonschema2md(request, test_out_dir):
    CardLogger.info(f"--Starting: {request.node.name}")
    md = json_schema_to_md()
    out_md = test_out_dir / "schema.md"
    with out_md.open("w") as f:
        f.write(md)
    try:
        markdown.markdown(md) 
    except Exception as e:
        pytest.fail(f"json_schema_to_md generated Invalid markdown: {e}")
    CardLogger.info(f"--Finished: {request.node.name}")


def test_examples2md(request, example_dir, test_out_dir):
    CardLogger.info(f"--Starting: {request.node.name}")
    md = card_list_to_table(example_dir)
    out_md = test_out_dir / "examples.md"
    with out_md.open("w") as f:
        f.write(md)
    try:
        markdown.markdown(md) 
    except Exception as e:
        pytest.fail(f"card_list_to_table generated Invalid markdown: {e}")
    CardLogger.info(f"--Finished: {request.node.name}")