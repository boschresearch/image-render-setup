# Catharsys Distribution Installation

The installation starts with an image render setup archive. The filename is of the form `image-render-setup-[X.Y.Z].zip`, where `[X.Y.Z]` stands for a three digit version number. For this tutorial, we assume that the image render setup archive is located at `~/code/image-render-setup-3.0.28.zip`. 

```{admonition} Windows
For a Windows install, it is assumed that you are using a PowerShell. This should be the default in all current Windows installations. If you are unfamiliar with PowerShell, [here](./powershell.md) is a list of helpful commands and information.
```

## Step 0

Open a standard PowerShell (Windows) or Bash (Linux) prompt.

## Step 1

Unpack the zip-file directly in the `code` folder. 

```{admonition} PowerShell
`expand-archive .\image-render-setup-3.0.28.zip -DestinationPath .`
```

```{admonition} Linux
`unzip image-render-setup-3.0.28.zip`
```

## Step 2

Change to the newly created folder with 

```{admonition} Shell
`cd image-render-setup-3.0.28`
```

Now activate the base anaconda environment. 

```{admonition} PowerShell
If you started the default PowerShell, Anaconda will not be activated, even if it is installed. The image render setup comes with a helpful script that does that for you. Execute:

`.\scripts\CondaActivate.ps1`
```

```{admonition} Linux
Under Linux, you have probably already initialized anaconda with the command `conda init`, which will modify your `~/.bashrc`. You can therefore activate conda from any bash prompt with:

`conda activate`
```

## Step 3

Make sure that the command `pip` can access the internet. You can test this by trying to upgrade pip (which is a sensible thing to do anyway):

```{admonition} Shell
`python -m pip install --upgrade pip`
```

If `pip` cannot access the module archive, you may need to install and configure a proxy.

## Step 4

Run the image render installation. This will create an anaconda environment for you, where everything is installed. We will choose `cex1` as the environment name, but you can choose any valid name you like.

```{admonition} Shell
`python ./scripts/cathy-conda.py install cex1`
```
This command will create a *distribution* install, which is sufficient, if you just want to use Catharsys. If you want to develop Catharsys code or Catharsys add-ons, you should do a *develop* install. In a develop install, the source code of all modules is cloned from a `git` server, and the code is installed such that you can edit and debug everything, while still using the standard execution commands. If you execute the following command for a develop install, all other commands will recognize this type of install and act accordingly. For example, the VS-Code initialization described later, creates a workspace file that maps all source repositories.

```{admonition} Shell *(develop install)*
`python ./scripts/cathy-conda.py install cex1 --develop`
```

## Step 5

To test whether the system installed successfully, you first of all need to switch to the Anaconda environment that was just created:

```{admonition} Shell
`conda activate cex1`
```

Now let's run the main Catharsys management command `cathy`:

```{admonition} Shell
`cathy -h`
```

This should print the usage and available sub-commands of `cathy`. The set of available commands depends on the Catharsys modules and add-ons installed. If you write your own Catharsys module, you can also define your own sub-commands.

Now try to open the HTML documentation in a web browser, with the command:

```{admonition} Shell
`cathy --docs`
```

This should open the default web browser and show this documentation.

## Next Steps

Now go back to the [main setup document](setup.md#catharsys-system) for the next steps.
