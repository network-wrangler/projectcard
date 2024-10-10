# Development

## Development Environment

If you plan on developing and changing code within the `projectcard` project, you will likely want to set up your own development environment from a cloned fork.

Helpful prerequisites:

- [github desktop](https://github.com/apps/desktop)
- [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation)
- [VS Code (or another IDE)](https://code.visualstudio.com/)

Fork and Install:

1. [Fork](https://github.com/network-wrangler/projectcard/fork) and clone repo locally

    === "gh cli"
        ``` bash
        gh repo fork network-wrangler/projectcard --clone=true
        cd projectcard
        git remote add upstream https://github.com/network-wrangler/projectcard.git
        ```

    === "github ux"

        - In browser, fork the repository to your github account: <https://github.com/network-wrangler/projectcard/fork>.
        - In the browser with your new fork, click green `code` botton and clone to local disk using Github Desktop.
        - Add the original repo to your upstream remotes to be able to track changes:
          - Make sure the cloned repository is open in GitHub Desktop
          - Click on `Repository` in the menu bar
          - Select Open in Terminal (or Open in Git Bash on Windows).
          - In the terminal window that opens, enter the following command to add the original repository as a remote named upstream:
            ``` bash
            git remote add upstream https://github.com/network-wrangler/projectcard.git
            ```

2. Install dependencies

    === "conda (recommended)"
        ``` sh
        conda install --yes --file requirements.txt
        ```
    === "pip"

        ``` sh
        pip install -r requirements.txt
        ```

3. Install from working directory

    ``` sh
    pip install -e .
    ```

## Keeping your fork updated

To make sure any development and work you are doing takes advantage of and is compatable with the main projectcard repository, you will want to fetch and merge updates.

=== "Using Github Desktop"

    Click on Fetch origin in the top bar of GitHub Desktop to fetch the latest changes from your fork.

=== "In terminal"
    Open the repository in the terminal and run the following command to fetch updates from the upstream repository and merge the udpates into your local branch.

    ```sh
    git fetch upstream
    git merge upstream/main
    ```

    Replace main with the branch of the repository you want to develop towards if it is different.

## Style Guide

- All public modules and functions should be documented using [google-style docstrings](https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html).
- Public modules should be documented with usage examples.
- Public functions should be covered by a test, located in the `/tests` folder.
- Code should be formatted per the [`ruff`](https://docs.astral.sh/ruff/) implementation of PEP8 (which is like `black`, but faster)
- Line width should be no more than 99 characters.
- Document function signatures with [type annotations](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html#) and pass inspection with [`mypy`](https://mypy.readthedocs.io/)

To make sure your code conforms to our style – ensuring that all differences are meaningful and not just fommatting – please use [`pre-commit`](https://pre-commit.com/) before submitting any pull-requests to the main repository:

``` sh
pre-commit run --all-files
```

This will make sure your code conforms to our guidelines as defined in `pyproject.toml`.

## Contributing

Generally we are happy to accept pull-requests directly to the `main` branch which improve documentation or make very minor changes.  If you are making more significant changes, please:

### Before starting

- Create an issue describing the problem you ar solving: Make sure people know what you are working on and that they can let you know sooner rather than later about their opinions (or assign yourself an existing issue).

### Developing

- Follow the [style guide](#style-guide)
- Regularly [update your fork with upstream changes](#keeping-your-fork-updated)

### Incorporating Code to main ProjectCard Repository

- Make sure your code passes all tests
- If you updated documentation, make [sure it properly builds].
- Run `pre-commit`
- Submit a pull-request to the main project card repository and thoroughly describe the problem you are trying to solve, referencing the issue it addresses
- Respond to requests from the code reviewer

## Documentation

Documentation is maintained in the `/docs` repository in [markdown](https://www.markdownguide.org/) text files and is built using the [`mkdocs`](https://www.mkdocs.org/) package.  Public documentation is built using a Github Workflow (`.github/workflows/push.yml`) and published using [`mike`](https://squidfunk.github.io/mkdocs-material/setup/setting-up-versioning/) to [Github Pages](https://pages.github.com/).

### Build the documentation locally

This is useful to make sure that changes you made are rendered as you would expect them.

```sh title="install documentation dependencies"
pip -r docs/requirements.txt
```

```sh title="building documentation locally"
mkdocs serve
```

## Releases

- Releases follow [semantic versioning](https://semver.org/).
- Releases are triggered by project management team via the [github "releases" interface](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).  
- Creating a release in github will trigger a github action to send it to [`pypi`](https://pypi.org) so that users installing it via `pip` will have access to it.

!!! tip

    Releases must have a unique version number in order to be updated on pypi.

## Changelog

{!
    include-markdown "../CHANGELOG.md"
    heading-offset=1
!}
