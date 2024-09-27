# API

### Basic Usage

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

::: projectcard.projectcard

::: projectcard.io

::: projectcard.validate
