"""Functions for mkdocs documentation."""

from pathlib import Path

from projectcard.docs import card_list_to_table

SCHEMA_DIR = Path("projectcard") / "schema"


def define_env(env):
    """This is the hook for defining variables, macros and filters.

    - variables: the dictionary that contains the environment variables
    - macro: a decorator function, to declare a macro.
    """

    @env.macro
    def document_schema(**kwargs) -> str:
        """Generate Markdown documentation for a JSON schema."""
        from projectcard.docs import json_schema_to_md

        return json_schema_to_md(**kwargs)

    @env.macro
    def list_examples(data_dir: Path) -> str:
        """Outputs a simple list of the directories in a folder in markdown.

        Args:
            data_dir: directory to search in
        Returns: markdown-formatted list
        """
        return card_list_to_table(Path(env.project_dir) / data_dir)


def _get_html_between_tags(content: str, tag: str = "body") -> str:
    """Returns string that is between tags if they are found. If not, returns whole string.

    Args:
        content (str): Content
        tag: tag to get content for. Note if multiple sets of the tag extist, will return the
            first set of content wrapped by the tag if the tag exists. Defaults to "body" tag.
    """
    if f"</{tag}>" not in content:
        return content
    content = content[content.index(f"<{tag}") :]
    content = content[content.index(">") :]

    content = content[: content.index(f"</{tag}>")]
    return content


def _rm_html_between_tags(content: str, tag: str = "footer") -> str:
    """Returns string without the tags if they are found. If not, returns whole string.

    Only removes first found instance.

    Args:
        content (str): Content
        tag: tag to get content for. Note if multiple sets of the tag extist, will return the
            first set of content wrapped by the tag if the tag exists. Defaults to "body" tag.
    """
    if f"</{tag}>" not in content:
        return content

    content_a, content_b = content.split(f"<{tag}", 1)
    content_b, content_c = content_b.split(f"</{tag}>", 1)

    return content_a + content_c
