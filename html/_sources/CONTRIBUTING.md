# Contributing

Want to contribute? Great! You can do so through the standard GitHub pull
request model. For large contributions we do encourage you to file a ticket in
the GitHub issues tracking system prior to any code development to coordinate
with the project development team early in the process. Coordinating up
front helps to avoid frustration later on.  Please follow the [coding guidelines](docs/source/develop/style-guide.md).

Your contribution must be licensed under the Apache-2.0 license, the [license](LICENSE.md)
used by this project. 

## Branching Model

This project uses the GitFlow branching model. However, the naming of the branches is adapted to make the workflow with GitHub easier. What would typically be called `develop` branch is here the `main` branch, which is the default GitHub branch. The `main` or `master` branch of the GitFlow model is here called `stable`. That is, you develop in a feature branch (`feature/[your feature]`) and then create a pull request agains the `main` branch. Pull requests against the `stable` branch will be rejected.

Releases are tagged with a version number in the stable branch. This allows to go back to a specific version from which to create a new release branch, if multiple releases need to be developed or fixed in parallel.

Note that you need to fork this repository if you want to modify it. When forking, it is sufficient to only include the `main` branch in the fork.


## Add / retain copyright notices

Include a copyright notice and license in each new file to be contributed,
consistent with the style used by this project. For python files use this block as template:

```python
# <LICENSE id="Apache-2.0">
#
#   [PROJECT] module
#   Copyright [YYYY] [Your copyright, for corporate developers use your company]
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# </LICENSE>
```

If your contribution contains code under the copyright of a third party, document its origin, license, and
copyright holders in the [3rd-party-licenses](3rd-party-licenses.md) file. See the [3rd-party-licenses-template](3rd-party-licenses-template.txt) file for a template of how to do this. 

## Sign your work

This project tracks patch provenance and licensing using the Developer
Certificate of Origin 1.1 (DCO) from [developercertificate.org][DCO]. In addition it is required that **all commits are signed with a GPG key**, so that they are recognized as verified commits by GitHub. See below for a description of how to do this if you are unsure.

```text
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
1 Letterman Drive
Suite D4700
San Francisco, CA, 94129

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

### Signing Commits with GPG Key

With `gpg` signing a commit message you certify that you authored the patch
or otherwise have the right to submit it under an open source license. 

There is a nice description of how to set this up [here](https://dev.to/devmount/signed-git-commits-in-vs-code-36do). Here is the `TL;DR` version:

- Install `gpg` from [https://www.gnupg.org/download/]().
- Generate a key, e.g. with the newly installed Kleopatra tool. (You can also import keys, of course) Make sure that your key is secured with a password. 
- Check that `gpg` is available with `gpg --version`
- Get the signature of the newly created key: `gpg --list-signatures` (look for a line starting with `sig`)
- Run `git config --global user.signingkey [signature]`
- Run `git config --global commit.gpgsign true`
- On Windows, `git` will likely not find the correct `gpg` install. The easiest way to fix this is with the following command in a PowerShell: `git config --global gpg.program (get-command gpg).source`
- Copy and paste your *public* key to the corresponding GitHub page (Personal -> Settings -> SSH and GPG Keys)
- Enable commit signing in VSCode. Search for `gpg` in the VSCode Settings and enable code signing. 
- You can enable caching of your gpg-key passphrase with the `gpg-agent`. 
    - Set the timeouts for caching the `~/.gnupg/gpg-agent.conf` file with these two lines: `default-cache-ttl 34560000` and `max-cache-ttl 34560000`. See e.g. [this page](https://superuser.com/questions/624343/keep-gnupg-credentials-cached-for-entire-user-session) for more details.
    - For Windows, create the folder with `mkdir ~\.gnupg` and then generate the config file with this one-liner: `Set-Content -Path ~\.gnupg\gpg-agent.conf -Value "default-cache-ttl 34560000$([System.Environment]::NewLine)max-cache-ttl 34560000"` (taken from the page linked above).
    - Now start the agent with `gpg-agent`.


### Individual vs. Corporate Contributors

Often employers or academic institution have ownership over code that is
written in certain circumstances, so please do due diligence to ensure that
you have the right to submit the code.

If you are a developer who is authorized to contribute to this project on
behalf of your employer, then please use your corporate email address in the
Signed-off-by tag. Otherwise please use a personal email address.

## Maintain Copyright holder / Contributor list

Each contributor is responsible for identifying themselves in the
[NOTICE](NOTICE) file, the project's list of copyright holders and authors.
Please add the respective information corresponding to the Signed-off-by tag
as part of your first pull request.

If you are a developer who is authorized to contribute to this project on
behalf of your employer, then add your company / organization to the list of
copyright holders in the [NOTICE](NOTICE) file. As author of a corporate
contribution you can also add your name and corporate email address as in the
Signed-off-by tag.

If your contribution is covered by this project's DCO's clause "(c) The
contribution was provided directly to me by some other person who certified
(a) or (b) and I have not modified it", please add the appropriate copyright
holder(s) to the [NOTICE](NOTICE) file as part of your contribution.

[DCO]: https://developercertificate.org/

[SubmittingPatches]: https://github.com/wking/signed-off-by/blob/7d71be37194df05c349157a2161c7534feaf86a4/Documentation/SubmittingPatches
