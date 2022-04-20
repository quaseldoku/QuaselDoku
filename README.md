# QuaselDoku

Deep-Learning based Q&A for the ECU-TEST documentation.

## Overview

This is your new Kedro project, which was generated using `Kedro 0.18.0`.

Take a look at the [Kedro documentation](https://kedro.readthedocs.io) to get started.

## Rules and guidelines

In order to get the best out of the template:

* Don't remove any lines from the `.gitignore` file we provide
* Make sure your results can be reproduced by following a [data engineering convention](https://kedro.readthedocs.io/en/stable/faq/faq.html#what-is-data-engineering-convention)
* Don't commit data to your repository
* Don't commit any credentials or your local configuration to your repository. Keep all your credentials and local configuration in `conf/local/`

## How to install dependencies with Poetry

You can install/update/remove packages via Poetry, a dependency-management & package-manager alternative to pip with the advantage of automatic dependency-resolution. 

### How to use Poetry for my project?

Make sure to have the right python-version installed (Here 3.9.11). 
Then install poetry via Windows-powershell with: 

```
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python 
```

To use poetry within your project simply navigate into your root-directory and start your poetry-shell (poetry will use your virtualenv-python) with:

```
poetry shell
```

Poetry defines it's dependencies within pyproject.toml (like pip does in requirements.txt). If you alreade have a pyproject.toml and poetry.lock defined, you can simply go to your root directory containing both pyproject.toml and poetry.lock and install all dependencies via

```
poetry install
```

When you run the poetry add command, Poetry automatically updates pyproject.toml and pins (makes a snapshot of compatible package-versions) the resolved versions in the poetry.lock file.

To install/update/remove packages simply run:

```
poetry install <package-name>
poetry update (<package-name>)
poetry remove <package-name>
```

For more information on poetry commands, check out:
> https://python-poetry.org/docs/cli/

## PyTorch

For faster computation, it is recommended to use PyTorch together with CUDA installed. CUDA integrates GPU compatibility of your Deep-Learning models, otherwise all computations will be executed on the CPU resulting in much slower inference and training times. Due to it's complicated installation, it is recommended to customize your PyTorch-installation for your system via:

> https://pytorch.org/ > Install PyTorch

and then install it using pip as package manager. Make sure to have the poetry-shell activated in advance by going to your projects root-directory and executing <code>poetry shell</code>, to guarantee that all pytorch-dependencies (modules/libraries etc.) will be saved within your poetry environment.





## How to run your Kedro pipeline

You can run your Kedro project with:

```
kedro run
```

## How to test your Kedro project

Have a look at the file `src/tests/test_run.py` for instructions on how to write your tests. You can run your tests as follows:

```
kedro test
```

To configure the coverage threshold, go to the `.coveragerc` file.

## Project dependencies

To generate or update the dependency requirements for your project:

```
kedro build-reqs
```

This will `pip-compile` the contents of `src/requirements.txt` into a new file `src/requirements.lock`. You can see the output of the resolution by opening `src/requirements.lock`.

After this, if you'd like to update your project requirements, please update `src/requirements.txt` and re-run `kedro build-reqs`.

[Further information about project dependencies](https://kedro.readthedocs.io/en/stable/kedro_project_setup/dependencies.html#project-specific-dependencies)

## How to work with Kedro and notebooks

> Note: Using `kedro jupyter` or `kedro ipython` to run your notebook provides these variables in scope: `context`, `catalog`, and `startup_error`.
>
> Jupyter, JupyterLab, and IPython are already included in the project requirements by default, so once you have run `pip install -r src/requirements.txt` you will not need to take any extra steps before you use them.

### Jupyter
You can start jupyter with:

```
kedro jupyter notebook
```

### JupyterLab
You can start JupyterLab:

```
kedro jupyter lab
```

### IPython
And if you want to run an IPython session:

```
kedro ipython
```

### How to convert notebook cells to nodes in a Kedro project
You can move notebook code over into a Kedro project structure using a mixture of [cell tagging](https://jupyter-notebook.readthedocs.io/en/stable/changelog.html#release-5-0-0) and Kedro CLI commands.

By adding the `node` tag to a cell and running the command below, the cell's source code will be copied over to a Python file within `src/<package_name>/nodes/`:

```
kedro jupyter convert <filepath_to_my_notebook>
```
> *Note:* The name of the Python file matches the name of the original notebook.

Alternatively, you may want to transform all your notebooks in one go. Run the following command to convert all notebook files found in the project root directory and under any of its sub-folders:

```
kedro jupyter convert --all
```

### How to ignore notebook output cells in `git`
To automatically strip out all output cell contents before committing to `git`, you can run `kedro activate-nbstripout`. This will add a hook in `.git/config` which will run `nbstripout` before anything is committed to `git`.

> *Note:* Your output cells will be retained locally.

## Package your Kedro project

[Further information about building project documentation and packaging your project](https://kedro.readthedocs.io/en/stable/tutorial/package_a_project.html)

