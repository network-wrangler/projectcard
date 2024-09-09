# Project Cards

Project Cards represent information about a tranportation infrastructure projects sufficient for usage in a regional travel demand model.

## Schema

The ProjectCard schema is represented as a [json-schema](https://json-schema.org) in the `/schema` directory.  More details:  [json-schemas page](json-schemas.md).

## Pydantic Data Models

If you are working in a python environment, you might find it easier to use the [pydantic](https://docs.pydantic.dev/) data models which are synced to the json-schema.  More details: [pydantic-datamodels page](pydantic-datamodels.md).

### Example Data

Example project cards can be found in the `/examples` directory and on the [examples page](examples.md)

## Basic Usage

This package should generally be used to validate or update project cards.  

There is also a limited object model, `ProjectCard` which can be used to organize and manage project cards.

### Command Line

Validate project card(s) from a directory or specific file path, optionally filtering by a tag.

```sh
validate_card card_search_dir --filter_tags ['tag_to_search_for']
```

Update older project card(s) to current format from a directory or specific file path.  Cards should still be validated afterwards.

```sh
update_projectcard_schema card_search_dir output_dir
```

### Python API

```python
from projectcard.io import read_cards

# Read in cards from a directory with the tag "Baseline 2030"
project_cards = read_cards(directory, filter_tags=["Baseline2030"])

# Iterate through a deck of cards for validity
for project_name,card in project_cards.items():
    print(f"{project_name}: {card.valid}")

# Print out a summary of the card with the project name "4th Ave Busway"
print(project_cards["4th Ave Busway"])
```

## Installation

`pip install projectcard`

!!! tip "Note"

    It is **not generally necessary to install the projectcard package yourself** unless you are using it to do independent validation of project cards. Projects such as `network_wrangler` that use the `projectcard` package to validate project cards usually include `projectcard` as a requirement and install it on their own.

!!! note "Plan on developing in network wrangler?"

    You might want to follow the directions in the [development](development.md) documentation.
