# Catharsys Development Installation

A development installation installs all Catharsys Python source in `editable` mode. This means, you can use all commands registered in the Python environment by Catharsys, but the code executed is the one in your cloned repositories and not code installed in `site-packages`.

If you just want to have a source installation and do not plan to modify the code, not all the steps described in the following will be necessary. The advantage of a source install is, that you can get the latest (possible buggy) features with the command `cathy repos update`. This pulls the main branch for all repositories in the system. 

The steps that are only needed if you want to contribute code, will be denoted by "**(for contribution install)**". You can leave these out if you just want to use the source install. 

## Contributing

If you want to contribute to any of the repositories, make sure to read and follow the instructions in the repository's `CONTRIBUTION.md` file. Note that the projects have different Open Source licenses. In particular, all Blender related projects are **GPL-v3** licensed, while the other projects are **Apache-2.0** licensed, unless stated otherwise. The documentation is `CC-BY-4.0` and the example configurations `CC-4.0` licensed. In any case, the license file that is included with a project determines its' license. Here is the [CONTRIBUTING.md](CONTRIBUTING.md) file of the `image-render-setup` project.

## Branching Model

This project uses the GitFlow branching model. However, the naming of the branches is adapted to make the workflow with GitHub easier. What would typically be called `develop` branch becomes the `main` branch, which is the default GitHub branch. The `main` or `master` branch of the GitFlow model becomes the `stable` branch. That is, you develop in a feature branch (`feature/[your feature]`) and then create a pull request agains the `main` branch. Pull requests against the `stable` branch will be rejected.

Releases are tagged with a version number in the stable branch. This allows to go back to a specific version from which to create a new release branch, if multiple releases need to be developed or fixed in parallel.

Note that you need to fork this repository if you want to modify it. When forking, it is sufficient to only include the `main` branch in the fork.

## Installation Steps

```{admonition} Windows
For a Windows install, it is assumed that you are using a PowerShell. This should be the default in all current Windows installations. If you are unfamiliar with PowerShell, [here](./powershell.md) is a list of helpful commands and information. Make sure that you have the permissions to run PowerShell scripts. You can enable this locally with the command `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`.
```

**IMPORTANT**: If you just want a source code install without contributing to the code via forked repositories, you only need to do steps 3, 5, 6, 7.

### Step 1

*(for contribution install)*

To install the Catharsys system from the Python sources, you first need to create forks from all repositories starting with `image-render` in the [github.com/boschresearch](https://github.com/boschresearch) organization. In addition you also need forks of `functional-json` and `functional-json-vscode` also in `boschresearch`.

To be precise, you only really need to fork those repositories that you want to modify. The others can be used directly from the `boschresearch` organization. This may, however, become quite confusing later on.

### Step 2

*(for contribution install)*

Pull requests can only be merged with the repositories on `boschresearch`, if **all** commits are signed with a GPG key **and** the commit message contains a 'signed-off-by' statement. With `gpg` signing a commit message you certify that you authored the patch or otherwise have the right to submit it under an open source license. You also agree with the DCO that is given in the `CONTRIBUTION` file. 

To automatically add a 'signed-off-by' text in your commit message you can use the `-s` flag for the `git commit` command. If you are using VS Code, enable the setting `git.alwaysSignOff` to sign all commits in this way. Note that this is not the same as GPG signing your commits, which will be discussed in the following.

There is a nice description of how to set this up [here](https://dev.to/devmount/signed-git-commits-in-vs-code-36do). Here is the `TL;DR` version:

- Install `gpg` from [https://www.gnupg.org/download/]().
- Generate a key, e.g. with the newly installed Kleopatra tool. (You can also import keys, of course) Make sure that your key is secured with a password. 
- Check that `gpg` is available with `gpg --version`
- Get the signature of the newly created key: `gpg --list-signatures` (look for a line starting with `sig`)
- Run `git config --global user.signingkey [signature]`
- Run `git config --global commit.gpgsign true`
- On Windows, `git` will likely not find the correct `gpg` install. The easiest way to fix this is with the following command in a PowerShell: `git config --global gpg.program (get-command gpg).source`
- Copy and paste your *public* key to the corresponding GitHub page (Personal -> Settings -> SSH and GPG Keys)
- Adapt VSCode settings to:
    - Enable commit signing by searching for `gpg` in the VSCode Settings and enable code signing. 
    - Enable automatic addition of "signed-off by" to commit messages in VSCode, by searching for "git always sign off" in the settings and enabling it.
- You can enable caching of your gpg-key passphrase with the `gpg-agent`. 
    - Set the timeouts for caching the `~/.gnupg/gpg-agent.conf` file with these two lines: `default-cache-ttl 34560000` and `max-cache-ttl 34560000`. See e.g. [this page](https://superuser.com/questions/624343/keep-gnupg-credentials-cached-for-entire-user-session) for more details.
    - For Windows, create the folder with `mkdir ~\.gnupg` and then generate the config file with this one-liner: `Set-Content -Path ~\.gnupg\gpg-agent.conf -Value "default-cache-ttl 34560000$([System.Environment]::NewLine)max-cache-ttl 34560000"` (taken from the page linked above).
    - Now start the agent with `gpg-agent`.

### Step 3

Clone the `image-render-setup` repository to your local machine and open the cloned folder with VSCode. 

### Step 4

*(for contribution install)*

Within the `image-render-setup` folder, copy and **rename** the file `repos/repos-main.yaml` to a new folder `_local/repos-main-fork.yaml`. We will use this copy to specify which repositories should be cloned from where. If you have forked all repositories simply replace `boschresearch` with your GitHub user name. For example, `https://github.com/boschresearch/functional-json.git` becomes `https://github.com/<user>/functional-json.git`.

### Step 5

Open a terminal in the `image-render-setup` folder. 

:::{admonition} Windows
If the base Conda environment is not active run `.\scripts\CondaActivate.ps1` if `conda activate base` does not work.
:::

Now install the Catharsys system with one of the following commands. If you forked any repository and created a new repository list `./_local/repos-main-fork.yaml`, then use this command:

:::{admonition} Shell
`python ./scripts/cathy-conda.py install [new environment name] --develop ./_local/repos-main-fork.yaml`
:::

If you didn't fork any repositories and just want to get a source install, run this command:

:::{admonition} Shell
`python ./scripts/cathy-conda.py install [new environment name] --develop`
:::

In the remainder of the installation documentation it is assumed that the environment name is `cex1`, short for *Catharsys Example 1*.

The script will create a new Conda environment with the given name. You can install different Catharsys versions side-by-side on your system, as long as they are in different Conda environments.

### Step 6

Switch to the new environment with:
:::{admonition} Shell
`conda activate [new environment name]`
:::

Go to the latest [release](https://github.com/boschresearch/image-render-setup/releases) for `image-render-setup` and download the ISON language VS-Code addon. This should be a `.vsix` file. You can [install](https://vscode-docs.readthedocs.io/en/stable/extensions/install-extension/) this directly via VS-Code.
In VSCode select the `ISON language` extension as the default syntax highlighting for `.json5` and `.ison` files.

### Step 7

To start working with the Catharsys system, you can create a VSCode workspace file, that contains references to all repositories and sets parameters for the `black`-formatter etc. You generate a workspace file by running the following command in the `image-render-setup` folder:

:::{admonition} Shell
`cathy code init`
:::

:::{note}
This command only works either inside the `image-render-setup` folder or in a workspace (as discussed later).
:::

You should now see a `.code-workspace` file. If you open this file with VSCode, all repositories should be listed in the file explorer. Also, when you open a terminal, the conda environment that was active when you executed the `cathy code init` command, will be activated again. It is also the default environment for all debugging calls.

## Next Steps

Now go back to the [main setup document](setup.md#catharsys-system) for the next steps.
