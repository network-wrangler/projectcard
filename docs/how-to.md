# How To

## Validate Project Cards

Project cards can be validating using the Python API or from the command line – and for a whole directory or just a single card.

!!! example "Using Command Line"

  ```bash title="single card"
  validate_card card_search_dir_or_path_to_single_card --filter_tags ['tag_to_search_for']
  ```

!!! example "Using Python API"

  ```python title="single card"
  from projectcard import read_card
  card = read_card(path_to_single_card, validate=True)
  ```

## Read in project cards

!!! example "Read in Project Cards to ProjectCard object"

  ```python
  from projectcard.io import read_cards

  # Read in cards from a directory with the tag "Baseline 2030"
  project_cards = read_cards(my_directory, filter_tags=["Baseline2030"])

  # Iterate through a deck of cards for validity
  for project_name,card in project_cards.items():
      print(f"{project_name}: {card.valid}")

  # Print out a summary of the card with the project name "4th Ave Busway"
  print(project_cards["4th Ave Busway"])
  ```

## Use Pydantic Data Models to validate all or part of a project card

Because of the necessary structure of the json-schema-based definition of project card format, the errors can be quite overwhelming if it isn't valid.  You might find it easier to navigate the errors if you leverage the [Pydantic](https://pydantic.org) models instead, which you can do for all or part of a project card.  You might also find it useful to use the Project Card [Pydantic](https://pydantic.org) data models in your own code that uses project cards to make sure you are processing valid data.

!!! example "Validate Selection"

  ```python
  from projectcard.models.selections import SelectRoadLinks
  road_selection = {
    "links": {
      "name": ["Main St", "Broadway"],
      "modes": ["drive"],
      "lanes": [2, 3]
    }
  }
  validated_road_selection = SelectRoadLinks(road_selection).model_dump()
  ```
