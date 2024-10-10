# Project Cards

Project Cards represent information about a tranportation infrastructure projects sufficient for usage in a regional travel demand model. The dream is that by coding a project once(ish) in a project card, it can be re-used over and over again in various scenarios – and even be shared across agencies.

## Schema

The ProjectCard schema is represented as a [json-schema](https://json-schema.org) in the `/schema` directory.  More details:  [json-schemas page](json-schemas.md).

The rendering of json-schema leaves a wee bit to be desired, so you might prefer revieweing the schema in [datamodels](datamodels.md).

## Data Model

If you are working in a python environment, you might find it easier to use the [pydantic](https://docs.pydantic.dev/) data models which are synced to the json-schema.  More details: [datamodels page](datamodels.md).

### Example Data

Example project cards can be found in the `/examples` directory and on the [examples page](examples.md) as well as within the [datamodels](datamodels.md) documentation.

## Basic Usage

This package should generally be used to validate or update project cards.  

There is also a limited object model, `ProjectCard` and Python API which can be used to read and write project cards.

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

For more examples and detail, pleae see the [API](api.md) page.

## Installation

```bash
pip install projectcard
```

!!! tip "Note"

    It is **not generally necessary to install the projectcard package yourself** unless you are using it to do independent validation of project cards. Projects such as `network_wrangler` that use the `projectcard` package to validate project cards usually include `projectcard` as a requirement and install it on their own.

!!! note "Plan on developing in network wrangler?"

    You might want to follow the directions in the [development](development.md) documentation.

## Companion Software

[NetworkWrangler](https://wsp-sag.github.io/network_wrangler): While ProjectCard can stand alone, it was initially developed to be used with the NetworkWrangler network scenario management software.

[ProjectCardRegistry](https://github.com/BayAreaMetro/project_card_registry): Example project card registries can be useful for storing collections of project cards, tracking their changes, and making sure project names are not duplicated.

## Having an issue?

🪲 ProjectCard may contain bugs.

🤔 Also, since it has primarily been used by its developers, the documentation may contain some omissions or not be entirely clear.

But we'd love to make it better! Please report bugs or incorrect/unclear/missing documentation with a [GitHub Issue](https://github.com/network-wrangler/projectcard/issues) -  or fix them yourself with a pull request!

## Who-dat?

ProjectCard was developed using resources from the [Metropolitan Transportation Commission](https://www.bayareametro.gov), [Metropolitan Council MN](https://metrocouncil.org/), and in-kind time from [UrbanLabs LLC](https://urbanlabs.io) and [WSP](https://www.wsp.com).  It is currently maintained using in-kind time...so please be patient.

## Release History

{!
    include-markdown "../CHANGELOG.md"
    heading-offset=1
!}
