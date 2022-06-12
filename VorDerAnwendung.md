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

Make sure to have the right python-version installed (Here 3.8.2). 
Then install poetry via Windows-powershell with: 

```
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python 
```

## How does poetry install dependencies?

### Installing without poetry.lock

If you have never run the command (within the root-directory of your project) before and there is also no poetry.lock file present, Poetry simply resolves all dependencies listed in your pyproject.toml file and downloads the latest version of their files.

When Poetry has finished installing, it writes all of the packages and the exact versions of them that it downloaded to the poetry.lock file, locking the project to those specific versions. You should commit the poetry.lock file to your project repo so that all people working on the project are locked to the same versions of dependencies (more below).

### Installing with poetry.lock

This brings us to the second scenario. If there is already a poetry.lock file as well as a pyproject.toml file when you run poetry install, it means either you ran the install command before, or someone else on the project ran the install command and committed the poetry.lock file to the project (which is good).

Either way, running install when a poetry.lock file is present resolves and installs all dependencies that you listed in pyproject.toml, but Poetry uses the exact versions listed in poetry.lock to ensure that the package versions are consistent for everyone working on your project. As a result you will have all dependencies requested by your pyproject.toml file, but they may not all be at the very latest available versions (some of the dependencies listed in the poetry.lock file may have released newer versions since the file was created). This is by design, it ensures that your project does not break because of unexpected changes in dependencies.

### Poetry within project

To use poetry within your project simply navigate into your root-directory (QuaselDoku) and start your poetry-shell (poetry will use your virtualenv-python) with:

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
poetry install <package-name> # install poetry package
poetry update (<package-name>)
poetry remove <package-name>
```

For more information on poetry commands, check out:
> https://python-poetry.org/docs/cli/

## PyTorch

For faster computation, it is recommended to use PyTorch together with CUDA installed. CUDA integrates GPU compatibility of your Deep-Learning models, otherwise all computations will be executed on the CPU resulting in much slower inference and training times. Due to it's complicated installation, it is recommended to customize your PyTorch-installation for your system via:

> https://pytorch.org/ > Install PyTorch

and then install it using pip as package manager. Make sure to have the poetry-shell activated in advance by going to your projects root-directory and executing <code>poetry shell</code>, to guarantee that all pytorch-dependencies (modules/libraries etc.) will be saved within your poetry environment.

Usually, the following command should be sufficient to install pytorch with CUDA 11.3:

```
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113
```

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

## Important Remarks

### notebook-kernel after 'kedro jupyter notebook' cannot be loaded:

If you can execute 'kedro jupyter notebook' to run your notebooks within the kedro-context (to access the datacatalog via 'catalog.load(...)' f.e.), make sure your ipython kernel is configurated to your python runtime. First find the location of your python-environment by navigating to the root-directory (QuaselDoku) and enter:

```
poetry shell
where python
```

One of the entries is the path to your environment python.exe. Copy the path and navigate to the configuration of your (kedro) ipython-kernel. Simply open the file-explorer and insert %appdata% and press enter. From there navigate to jupyter\kernels\pythonX\kernel.json. This is the configuration-file for your kedro ipython-kernel. Change the first argument to your python.exe-path. The file should then look similar to this:

> {
>  "argv": [
>    "C:\\Users\\<User-Name>\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\quaseldoku-nkif5tvV-py3.8\\Scripts\\python.exe",
>    "-m",
>    "ipykernel_launcher",
>    "-f",
>    "{connection_file}"
>  ],
>  "display_name": "Python 3 (ipykernel)",
>  "language": "python",
>  "metadata": {
>   "debugger": true
>  }
> }

Don't forget two backslashes within the path as separators. Leave the poetry-shell with 'exit' and restart with 'poetry shell'. It should work now. For more information, see the following issues:
> https://github.com/jupyter/notebook/issues/4079
> https://github.com/jupyter/notebook/issues/2301
