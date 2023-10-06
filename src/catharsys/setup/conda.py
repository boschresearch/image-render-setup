#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \conda.py
# Created Date: Friday, June 3rd 2022, 12:25:13 pm
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

import os
import re
import platform
from pathlib import Path

try:
    from . import shell
except Exception:
    import shell
# endtry


###############################################################################################
def GetInfo(*, lPreCmds=[]) -> dict:
    lCmds = lPreCmds.copy()
    lCmds.append("conda info")

    bOK, lLines = shell.ExecPlatformCmds(lCmds=lCmds, bReturnStdOut=True, bDoPrintOnError=False)
    # print(lLines)

    if bOK is False:
        raise RuntimeError(
            "It seems anaconda is not installed, because command 'conda info' is not available:\n| {}\n".format(
                "\n| ".join(lLines)
            )
        )
    # endif

    reLine = re.compile(r"^\s*(.+?)\s:\s(.+?)\s*$")
    reList = re.compile(r"^\s*(.+?)\s*$")
    dicInfo = {}
    iLineIdx = 0
    iLineCnt = len(lLines)
    while iLineIdx < iLineCnt:
        sLine = lLines[iLineIdx]
        # print("{}: {}".format(iLineIdx, sLine), flush=True)
        xMatch = reLine.match(sLine)
        if xMatch is None:
            iLineIdx += 1
            continue
        # endif

        if iLineIdx + 1 < iLineCnt and reLine.match(lLines[iLineIdx + 1]) is None:
            lList = [xMatch.group(2)]
            while iLineIdx + 1 < iLineCnt and reLine.match(lLines[iLineIdx + 1]) is None:
                sLine = lLines[iLineIdx + 1]
                # print("| {}: {}".format(iLineIdx+1, sLine))
                xListMatch = reList.match(sLine)
                if xListMatch is None:
                    break
                # endif
                lList.append(xListMatch.group(1))
                iLineIdx += 1
            # endwhile
            # print("|>> {}".format(lList))
            dicInfo[xMatch.group(1)] = lList
        else:
            dicInfo[xMatch.group(1)] = xMatch.group(2)
        # endif

        iLineIdx += 1
    # endwhile

    dicInfo["CONDA_DEFAULT_ENV"] = os.environ.get("CONDA_DEFAULT_ENV")

    ######################################################################
    lCmds = lPreCmds.copy()
    lCmds.append("conda env list")

    bOK, lLines = shell.ExecPlatformCmds(lCmds=lCmds, bReturnStdOut=True, bDoPrintOnError=False)

    if bOK is False:
        raise RuntimeError("Error executing 'conda env list':\n| {}\n".format("\n| ".join(lLines)))
    # endif

    dicEnv = {}
    reEnvList = re.compile(r"^([^\s]+)\s+(\*?)\s*(.+)$")
    for sLine in lLines:
        if sLine.startswith("#"):
            continue
        # endif
        xMatch = reEnvList.match(sLine)
        if xMatch is None:
            continue
        # endif

        dicEnv[xMatch.group(1)] = xMatch.group(3)
    # endfor
    dicInfo["dicEnv"] = dicEnv

    return dicInfo


# enddef


###############################################################################################
def GetActiveEnvName():
    return os.environ.get("CONDA_DEFAULT_ENV")


# enddef


###############################################################################################
def GetShellActivateCommands(
    _sEnvName: str, *, sSystem: str = platform.system(), bTestActivation: bool = False, pathShellInitScript: Path = None
) -> "list[str]":
    lSysCmds = []
    if sSystem == "Linux":
        if pathShellInitScript is not None:
            lSysCmds.append(f"source {(pathShellInitScript.as_posix())}")
        # endif
        lSysCmds.append(f"conda activate {_sEnvName}")

    elif sSystem == "Windows":
        if pathShellInitScript is not None:
            pathHook = pathShellInitScript
        else:
            pathHook: Path = None

            sUserCondaPath = os.environ.get("CATHARSYS_CONDA_PATH")
            if sUserCondaPath is not None:
                pathTest = Path(sUserCondaPath) / "shell/condabin/conda-hook.ps1"
                if not pathTest.exists():
                    raise RuntimeError(
                        f"Conda hook script cannot be found using main conda path set by environment variable 'CATHARSYS_CONDA_PATH': {sUserCondaPath}\n"
                        f"> Testing for script at path: {(pathTest.as_posix())}"
                    )
                # endif
                pathHook = pathTest

            else:
                # It seems that on some systems the environment variable "HOME" is not defined.
                # On the command prompt is may be available as '$HOME' directly.
                # Using '~' and expanding it works, however.
                lPaths: list[str] = []
                for sType in ["Anaconda3", "Miniconda3"]:
                    lPaths.extend(
                        [
                            os.path.expanduser(f"~/{sType}/shell/condabin/conda-hook.ps1"),
                            "{}/{}/shell/condabin/conda-hook.ps1".format(os.environ.get("PROGRAMFILES"), sType),
                            "{}/{}/shell/condabin/conda-hook.ps1".format(os.environ.get("LOCALAPPDATA"), sType),
                        ]
                    )
                # endfor

                for sTestPath in lPaths:
                    pathTest = Path(sTestPath)
                    if pathTest.exists():
                        pathHook = pathTest
                        break
                    # endif
                # endfor
            # endif

            if pathHook is None:
                raise RuntimeError(
                    "Cannot find conda activation script 'conda-hook.ps1'.\n"
                    "You may need to set the main conda installation path with the environment variable 'CATHARSYS_CONDA_PATH'.\n"
                    "Tested for the script in the following paths:\n" + "\n".join(lPaths)
                )
            # endif
        # endif

        lSysCmds = [
            "invoke-expression -Command \"& '{}'\"".format(pathHook.as_posix()),
            f"conda activate {_sEnvName}",
        ]
    # endif

    if bTestActivation is True:
        bOK, lLines = shell.ExecPlatformCmds(lCmds=lSysCmds, bReturnStdOut=True, bDoPrintOnError=False)
        if bOK is False:
            sCmds = "\n|> ".join(lSysCmds)
            sError = "|> ".join(lLines)
            raise RuntimeError(
                f"Cannot activate conda environment '{_sEnvName}' with commands:\n|\n|> {sCmds}\n"
                f"|\n| Received this error message:\n| {sError}\n"
            )
        # endif
    # endif

    return lSysCmds


# enddef


###############################################################################################
# Prepare Conda
def Install(
    *,
    sEnvName: str,
    pathSetup: Path,
    bForceInstall: bool = False,
    sDevelopReposFile: str = None,
    bEnvOnly: bool = False,
    sShellInitScript: str = None,
    sPrintPrefix=">> ",
):
    # sSystem = platform.system()
    bDevelop: bool = sDevelopReposFile is not None

    pathShellInitScript: Path = None
    if isinstance(sShellInitScript, str):
        pathShellInitScript = Path(sShellInitScript).absolute()

        if not pathShellInitScript.exists():
            raise RuntimeError(f"Shell initialization script not found: {(pathShellInitScript.as_posix())}")
        # endif
    # endif
    # print(pathShellInitScript)

    sActEnvName: str = None
    lSysCmds = GetShellActivateCommands(" ", pathShellInitScript=pathShellInitScript)
    # print(lSysCmds)

    dicInfo = GetInfo(lPreCmds=lSysCmds)
    # print(dicInfo)

    sActEnvName = dicInfo.get("active environment", dicInfo.get("CONDA_DEFAULT_ENV"))
    if sActEnvName is None:
        raise RuntimeError(
            "The active environment name cannot be determined from conda info\n"
            "and conda cannot be activated. It seems anaconda python is not installed."
        )
    # endif
    print(f"{sPrintPrefix}Currently in conda environment '{sActEnvName}'")

    dicEnv = dicInfo["dicEnv"]
    # print(dicEnv)

    if sEnvName not in dicEnv:
        print(f"{sPrintPrefix}Creating conda environment '{sEnvName}'")
        lCmds = GetShellActivateCommands(" ", bTestActivation=True, pathShellInitScript=pathShellInitScript)
        lCmds.append(f"conda create --name {sEnvName} -y python=3.10")
        bOK = shell.ExecPlatformCmds(
            lCmds=lCmds,
            sCwd=pathSetup.as_posix(),
            bDoPrint=True,
            bDoPrintOnError=True,
            sPrintPrefix=sPrintPrefix + ">> ",
        )

        if bOK is False:
            raise RuntimeError("Error installing conda environment")
        # endif

    elif sEnvName != sActEnvName:
        print(f"{sPrintPrefix}Try switching to conda environment '{sEnvName}'...")
        lCmds = GetShellActivateCommands(sEnvName, bTestActivation=True, pathShellInitScript=pathShellInitScript)

        dicRunInfo = GetInfo(lPreCmds=lCmds)
        # print(dicRunInfo)
        sRunEnvName = dicRunInfo.get("active environment", dicInfo.get("CONDA_DEFAULT_ENV"))
        if sRunEnvName != sEnvName:
            raise RuntimeError(f"Error switching to conda environment '{sEnvName}' in shell")
        # endif
        print(f"{sPrintPrefix}>> conda environment '{sEnvName}' available.")
    # endif

    # Get environment activation commands and test whether activation works
    lSysCmds = GetShellActivateCommands(sEnvName, bTestActivation=True, pathShellInitScript=pathShellInitScript)

    # Install conda packages
    print(f"{sPrintPrefix}Installing necessary packages in conda environment '{sEnvName}'...")

    sInstallCath = "cathy install system"
    if bDevelop is True and sDevelopReposFile != "__default__":
        sInstallCath += f" --repos {sDevelopReposFile}"
    # endif

    if bDevelop is True:
        sInstallSetup = "python -m pip install --editable ."
    else:
        sInstallSetup = "python -m pip install ."
        sInstallCath += " --force-dist"
    # endif

    if bForceInstall is True:
        sInstallCath += " --force"
    # endif

    # Modules to install
    lModules = [
        "vcstool",
        "ipykernel",
        "opencv-python==4.6.0.66",
        "scikit-image",
        "jupyter",
        "notebook",
        "tabulate",
        "psutil",
    ]

    # Modules to install for develop version
    if bDevelop is True:
        lModules.extend(["GitPython", "pytest", "flake8", "black", "black[jupyter]", "blender-stubs"])
    # endif

    lCmds = lSysCmds.copy()
    lCmds.append("python -m pip install --upgrade {}".format(" ".join(lModules)))

    if bEnvOnly is False:
        lCmds.extend([sInstallSetup, sInstallCath])
    # endif

    shell.ExecPlatformCmds(
        lCmds=lCmds,
        sCwd=pathSetup.as_posix(),
        bDoPrint=True,
        bDoPrintOnError=True,
        sPrintPrefix=sPrintPrefix + ">> ",
    )

    print(f"\n{sPrintPrefix}Switch to the new environment with: conda activate {sEnvName}\n")


# enddef
