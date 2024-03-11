# Project Cards

Project Cards

## Schema

The ProjectCard schema is represented as a [json-schema](https://json-schema.org) in the `/schema` directory.  More details:  [json-schemas page](json-schemas.md).

## Pydantic Data Models

If you are working in a python environment, you might find it easier to use the [pydantic](https://docs.pydantic.dev/) data models which are synced to the json-schema.  More details: [pydantic-datamodels page](pydantic-datamodels.md).

### Example Data

Example project cards can be found in the `/examples` directory and on the [examples page](examples.md)

## Basic Usage

### Reading cards

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

### Validating a function input conforms to a sub-schema

```python

from pydantic import validate_call
from projectcard.models import SelectSegment

@validate_call
def select_segment_in(data: SelectSegment):
    # Add your function code here which expects taht data conforms to a segment selection
    pass

```

## Installation

Generally it is not necessary to install the projectcard package as the main purpose of this repository is to maintain the project card *schema*.

## Development Environment

1. [Fork](https://github.com/network-wrangler/projectcard/fork) and clone repo locally

2. Install dependencies

```sh
conda install --yes --file requirements.txt
```

or

```sh
pip install -r requirements.txt
```

3. Install from working directory

```sh
pip install -e .
```

## Production Environment

```sh
pip install git+https://github.com/network-wrangler/projectcard@main#egg=projectcard
```
