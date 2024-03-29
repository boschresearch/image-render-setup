#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \install.py
# Created Date: Wednesday, April 27th 2022, 2:18:33 pm
# Author: Christian Perwass (CR/AEC5)
# <LICENSE id="Apache-2.0">
#
#   Image-Render Setup module
#   Copyright 2022 Robert Bosch GmbH and its subsidiaries
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
###

import sys
import re
import shutil
import platform
from packaging import version

if sys.version_info < (3, 10):
    import importlib_resources as res
else:
    from importlib import resources as res
# endif
from pathlib import Path
import catharsys.setup

# from shutil import unpack_archive
from catharsys.setup import util

g_sCmdDesc = "Installs the Catharsys modules"

try:
    from catharsys.setup import repos

    bHasGit = True
except Exception:
    bHasGit = False
# endtry


####################################################################
def InstallVsCodeModules(*, bForceInstall: bool = False):
    sSystem = platform.system()
    if sSystem == "Windows":
        pathVsCodeAddons = Path(util.NormPath("%USERPROFILE%\.vscode\extensions"))
    elif sSystem == "Linux":
        pathVsCodeAddons = Path(util.NormPath("~/.vscode/extensions"))
    else:
        raise RuntimeError("Unsupported operating system '{}'".format(sSystem))
    # endif

    if not pathVsCodeAddons.exists():
        print("It seems VS-Code is not installed.\n" "VS-Code addons will not be installed.\n")
        return
    # endif

    reDist = re.compile(r"(.*?)-(\d+\.\d+\.\d+)\.zip")
    reInst = re.compile(r"(.*?)-(\d+\.\d+\.\d+)")

    with res.path(catharsys.setup, "dist") as pathDist:
        pathDistCode = pathDist / "vscode"

        if not pathDistCode.exists():
            print("No VS-Code addon modules found")
        else:
            for pathAddOn in pathDistCode.iterdir():
                if not pathAddOn.is_file():
                    continue
                # endif
                xMatch = reDist.match(pathAddOn.name)
                if xMatch is None:
                    continue
                # endif

                sDistName = xMatch.group(1)
                sDistVer = xMatch.group(2)

                # check wether addon is already installed
                bDoInstall = True
                for pathInst in pathVsCodeAddons.iterdir():
                    if not pathInst.is_dir():
                        continue
                    # endif
                    xMatch = reInst.match(pathInst.name)
                    if xMatch is None:
                        continue
                    # endif

                    sInstName = xMatch.group(1)
                    sInstVer = xMatch.group(2)

                    if sInstName == sDistName:
                        if version.parse(sDistVer) <= version.parse(sInstVer) and bForceInstall is not True:
                            bDoInstall = False
                            print(f"VSCode addon '{sDistName} v{sDistVer}', already installed in version '{sInstVer}'")
                            break
                        else:
                            # delete installed version to avoid conflicts
                            print(f"Removing previously installed addon: {sInstName} v{sInstVer}")
                            shutil.rmtree(pathInst)
                        # endif
                    # endif same name
                # endfor

                if bDoInstall is True:
                    print("Unpacking addon '{}' to folder: {}".format(pathAddOn.name, pathVsCodeAddons.as_posix()))
                    # shutil.unpack_archive(pathAddOn.as_posix(), pathVsCodeAddons.as_posix())
                    util.Unzip(pathZipFile=pathAddOn, pathUnpack=pathVsCodeAddons)
                # endif
            # endfor
        # endif has vscode addons
    # endwith "dist" path


# enddef


####################################################################
def _ProvideEmptyUserDocsPath() -> Path:
    pathDocsTrg = util.GetCathUserPath(_bCheckExists=False) / "docs"
    if pathDocsTrg.exists():
        shutil.rmtree(pathDocsTrg.as_posix())
    # endif
    pathDocsTrg.mkdir(parents=True)
    return pathDocsTrg


# enddef


####################################################################
def InstallDocs(*, bForceInstall: bool = False, bForceDist: bool = False, lDocFiles: list = None):
    if lDocFiles is None or len(lDocFiles) == 0:
        with res.path(catharsys.setup, "dist") as pathDist:
            pathDocs = pathDist / "docs"
            if not pathDocs.exists():
                print("WARNING: Documentation not found in distribution")
                return
            # endif

            pathDocsTrg = _ProvideEmptyUserDocsPath()
            print("Installing documentation to: {}".format(pathDocsTrg.as_posix()))

            for pathFile in pathDocs.iterdir():
                if pathFile.is_file() and pathFile.name.endswith(".zip"):
                    shutil.unpack_archive(pathFile.as_posix(), pathDocsTrg.as_posix())
                # endif
            # endfor
            # util.CopyFiles(pathDocs, pathDocsTrg)
        # endwith

    else:
        pathMain = Path.cwd()
        lDocPaths = []
        for sDocFile in lDocFiles:
            pathFile: Path = Path(util.NormPath(sDocFile))

            if not pathFile.is_absolute():
                pathFile = util.NormPath(pathMain / pathFile)
            # endif

            if not pathFile.exists():
                raise RuntimeError(f"Documentation file '{(pathFile.as_posix())}' not found")
            # endif

            if not pathFile.is_file():
                raise RuntimeError(f"Documentation source is not a file: {(pathFile.as_posix())}")
            # endif

            if not pathFile.suffix == ".zip":
                raise RuntimeError(f"Documentation source is not a '.zip' file: {(pathFile.as_posix())}")
            # endif

            lDocPaths.append(pathFile)
        # endfor

        pathDocsTrg = _ProvideEmptyUserDocsPath()
        print("Installing documentation to: {}".format(pathDocsTrg.as_posix()))

        pathFile: Path
        for pathFile in lDocPaths:
            shutil.unpack_archive(pathFile.as_posix(), pathDocsTrg.as_posix())
        # endfor
    # endif


# enddef


####################################################################
def Run(
    *,
    bForceDist: bool,
    bForceInstall: bool,
    bSourceDist: bool,
    bVsCodeAddOnsOnly: bool,
    lDocFiles: bool,
    sReposFile: str,
    bUpdate: bool,
):
    from catharsys.setup import module

    # sSystem: str = platform.system()

    bDocsOnly = isinstance(lDocFiles, list)

    if bVsCodeAddOnsOnly is False and bDocsOnly is False:
        pathRepos = util.TryGetReposPath()
        if bUpdate is True:
            if not isinstance(pathRepos, Path):
                raise RuntimeError("Update can only be used on a develop install")
            # endif

            if bHasGit is False:
                raise RuntimeError("'Git' is not installed on this machine")
            # endif

            # pathMain = pathRepos.parent

            # pull "image-render-setup" and install it in current environment
            repos.PullMain()
            # sEnvName = conda.GetActiveEnvName()
            # lCmds = conda.GetShellActivateCommands(sEnvName, bTestActivation=False)
            # lCmds.append("python -m pip install --editable .")
            # shell.ExecPlatformCmds(
            #     lCmds=lCmds,
            #     sCwd=pathMain.as_posix(),
            #     bDoPrint=True,
            #     bDoPrintOnError=True,
            #     sPrintPrefix=">> ",
            # )
        # endif

        if isinstance(pathRepos, Path):
            if bHasGit is False:
                raise RuntimeError("'Git' is not installed on this machine")
            # endif

            lRepoPaths = []
            for pathX in pathRepos.iterdir():
                if pathX.is_dir():
                    pathGit = pathX / ".git"
                    if pathGit.exists() and pathGit.is_dir():
                        lRepoPaths.append(pathX)
                    # endif
                # endif
            # endfor
            if len(lRepoPaths) == 0 or bUpdate is True:
                if sReposFile is None:
                    pathRepoListFile = pathRepos / "repos-main.yaml"
                else:
                    pathRepoListFile = Path(util.NormPath(sReposFile))
                    if not pathRepoListFile.is_absolute():
                        pathRepoListFile = util.NormPath(Path.cwd() / pathRepoListFile)
                    # endif
                # endif
                if pathRepoListFile.exists():
                    print("Cloning repositories...")
                    repos.CloneFromRepoListFile(
                        _pathRepoList=pathRepoListFile, _pathRepos=pathRepos, _bPullIfExists=bUpdate
                    )
                    # if sSystem == "Windows":
                    #     sCmd = f"Get-Content {pathRepoListFile} | vcs import"
                    # else:
                    #     sCmd = "vcs import < {}".format(pathRepoListFile)
                    # # endif
                    # sCwd = pathRepos.as_posix()
                    # shell.ExecPlatformCmds(lCmds=[sCmd], sCwd=sCwd, bDoPrint=True,bDoPrintOnError=True, sPrintPrefix=">> ")
                    # # shell.ExecCmd(
                    # #     sCmd=sCmd,
                    # #     sCwd=sCwd,
                    # #     bDoPrint=True,
                    # #     bDoPrintOnError=True,
                    # #     sPrintPrefix=">> ",
                    # # )
                else:
                    print(
                        f"WARNING: Repository listing file is missing at {(pathRepoListFile.as_posix())}.\nPlease clone the develop repositories manually."
                    )
                # endif
            else:
                print("Found repositories:")
                for pathX in lRepoPaths:
                    print("  - {}".format(pathX.name))
                # endfor
                print("")
            # endif
        # endif

        module.InstallModules(bForceDist=bForceDist, bForceInstall=bForceInstall, bSourceDist=bSourceDist)
    # endif

    if bVsCodeAddOnsOnly is False:
        InstallDocs(bForceInstall=bForceInstall, bForceDist=bForceDist, lDocFiles=lDocFiles)
    # endif

    if bDocsOnly is False:
        InstallVsCodeModules(bForceInstall=bForceInstall)
    # endif

    if bUpdate is True:
        pathRepos = util.TryGetReposPath()
        pathMain = pathRepos.parent
        print("******\n")
        print(
            f"    Run the command 'python -m pip install --editable .' in the following folder to update 'image-render-setup':\n    >> '{(pathMain.as_posix())}\n"
        )
        print("******\n")
    # endif


# enddef
