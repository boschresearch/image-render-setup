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

import os
import platform
from pathlib import Path
from catharsys.setup import shell, conda


####################################################################
def Run(*, sPathWorkspace=None, bDevelop=False, sPrintPrefix=">> "):

    if sPathWorkspace is None:
        pathWS = Path.cwd()
    else:
        pathWS = Path(sPathWorkspace)
    # endif
    sPathWS = pathWS.as_posix()

    ##############################################################################
    # Add default terminal settings that activate the current conda env
    sCondaEnv = conda.GetActiveEnvName()
    if sCondaEnv is None:
        raise RuntimeError(
            "Currently not in an Anaconda Python environment.\n"
            "Create an appropriate environment from within the 'image-render-setup' folder:\n"
            "    python ./scripts/cath-conda.py [environment name]\n\n"
        )
    # endif

    # Check that vscode is available
    sSystem = platform.system()
    pathCode = None
    if sSystem == "Windows":
        pathLocalAppData = Path(os.environ["LOCALAPPDATA"])
        pathPrograms = Path(os.environ["PROGRAMFILES"])
        pathLocalCode = pathLocalAppData / "Programs" / "Microsoft VS Code" / "Code.exe"
        pathSysCode = pathPrograms / "Microsoft VS Code" / "Code.exe"

        if pathLocalCode.exists():
            pathCode = pathLocalCode
        elif pathSysCode.exists():
            pathCode = pathSysCode
        else:
            lCmds = [
                "$cmd = get-command code",
                "if ($?) {",
                "    Write-Host $cmd.Path",
                "} else {",
                "    Write-Host 'None'",
                "}",
            ]
            bOK, lLines = shell.ExecPowerShellCmds(lCmds=lCmds, sCwd=sPathWS, bReturnStdOut=True)
            if bOK is True and not lLines[-1].startswith("None"):
                pathCode = Path("code")
            # endif
        # endif

    elif sSystem == "Linux":
        bOK, lLines = shell.ExecCmd(sCmd="command -v code", sCwd=sPathWS, bReturnStdOut=True)
        if bOK is True and len(lLines) > 0:
            pathCode = Path("code")
        # endif
    else:
        raise RuntimeError("Operating system '{}' not supported".format(sSystem))
    # endif

    if pathCode is None:
        raise RuntimeError("It seems VSCode is not installed")
    # endif

    sName = pathWS.name
    if sName.startswith("image-render-"):
        sName = sName[len("image-render-") :]
    # endif

    sFileWs = f"{sName}-{sCondaEnv}.code-workspace"
    pathWsFile = pathWS / sFileWs
    sPathCodeFile = pathCode.as_posix()
    if " " in sPathCodeFile:
        sPathCodeFile = f'"{sPathCodeFile}"'
    # endif

    if pathWsFile.exists():
        sCmd = f"{sPathCodeFile} ./{pathWsFile.name}"
        print(f"Executing command: {sCmd}")
        shell.ExecCmd(sCmd=sCmd, sCwd=sPathWS)

    else:
        raise RuntimeError(
            f"Workspace file '{pathWsFile.name}' for environment '{sCondaEnv}' not found.\n"
            "Initialize your workspace with: cathy code init\n"
        )
    # endif


# enddef
