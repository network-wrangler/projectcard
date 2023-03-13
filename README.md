Project Cards


# Schema

The ProjectCard schema is represented as a [json-schema](https://json-schema.org) in the `/schema` directory and is documented on the [schemas page](schemas.md).

## Example Data

Example project cards can be found in the `/examples` directory and on the [examples page](examples.md)
# Basic Usage

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

# Installation

Generally it is not necessary to install the projectcard package as the main purpose of this repository is to maintain the project card *schema*.

## Development Environment

1. [Fork](https://github.com/network-wrangler/projectcard/fork) and clone repo locally

2. Install dependencies

`conda install --yes --file requirements.txt`
or
`pip install -r requirements.txt`

3. Install from working directory

`pip install -e .`

## Production Environment

To come.
