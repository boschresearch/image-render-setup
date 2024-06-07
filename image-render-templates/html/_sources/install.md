# Installing Templates

You can install templates using the `cathy` command

:::{admonition} Shell
`cathy install template [template name]`
:::

To get a list of available templates use

:::{admonition} Shell
`cathy install template --list`
:::

For example, to install the standard python action template use the following command:

:::{admonition} Shell
`cathy install template std-action-python `
:::

The above command will ask you for a number of inputs, depending on the type of template. These can all be supplied via the command line. For example, a full automatic install of the template `std-action-python` with no user input prompt looks like this:

:::{admonition} Shell
`cathy install template std-action-python --force --yes --name my-act --vars Namespace=hello Name=world`
:::

Note that the set of variables (after the `--vars`) depends on the specfic template. Look at the `template.json5` file in the template's folder to see the list of available variables.

The available command line arguments are:

-   `--force-dist`: The template will be installed from a cloned repository, if this is available. Otherwise, an installed distribution is used. If you want to force installation from a distribution use this command line flag.
-   `--force`: Overwrite any installation of the same name.
-   `--path`: Set the parent path where the module will be installes. By default, the current working directory is used.
-   `--list`: List the set of available templates.
-   `-y` or `--yes`: Answer all yes/no questions with yes.
-   `-n` or `--name`: Set the module name where the template is installed.
-   `-v` or `--vars`: Define values for the template variables. Every element must be of the form `[variable name]=[value]`.
