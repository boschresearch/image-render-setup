#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \shell.py
# Created Date: Friday, May 6th 2022, 10:13:25 am
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
import subprocess
import platform
import tempfile
from pathlib import Path


#################################################################################################################
def ExecCmd(
    *,
    sCmd,
    sCwd=None,
    bDoPrint=False,
    bDoPrintOnError=False,
    bDoRaiseOnError=False,
    bReturnStdOut=False,
    sPrintPrefix="",
    dicEnv=None,
):

    if sCwd is None:
        sEffCwd = os.getcwd()
    else:
        sEffCwd = sCwd
    # endif

    dicEnviron = os.environ.copy()
    if dicEnv is not None:
        dicEnviron.update(dicEnv)
    # endif

    procChild = subprocess.Popen(
        sCmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        cwd=sEffCwd,
        universal_newlines=True,
        env=dicEnviron,
    )

    lLines = []
    for sLine in iter(procChild.stdout.readline, ""):
        lLines.append(sLine)
        if bDoPrint:
            print(sPrintPrefix + sLine, end="", flush=True)
        # endif
    # endfor

    procChild.stdout.close()
    iReturnCode = procChild.wait()

    if iReturnCode != 0:
        if bDoRaiseOnError:
            raise subprocess.CalledProcessError(iReturnCode, sCmd)
        elif not bDoPrint and bDoPrintOnError is True:
            sMsg = sPrintPrefix + "ERROR:\n"
            for sLine in lLines:
                sMsg += sPrintPrefix + "! " + sLine
            # endfor
            print(sMsg)
        # endif
    # endif

    if bReturnStdOut is True:
        return iReturnCode == 0, lLines
    else:
        return iReturnCode == 0
    # endif


# enddef


#################################################################################################################
def ExecShellCmds(
    *,
    sShellPath,
    lCmds,
    lShellArgs=None,
    sCwd=None,
    bDoPrint=False,
    bDoPrintOnError=False,
    bDoRaiseOnError=False,
    bReturnStdOut=False,
    sPrintPrefix="",
    dicEnv=None,
):

    if not isinstance(lCmds, list):
        raise RuntimeError("Argument 'lCmds' must be a list. Received: {}".format(lCmds))
    # endif

    if sCwd is None:
        sEffCwd = os.getcwd()
    else:
        sEffCwd = sCwd
    # endif

    dicEnviron = os.environ.copy()
    if dicEnv is not None:
        dicEnviron.update(dicEnv)
    # endif

    sCmd = "\n".join(lCmds)

    pathScript = None
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ps1") as xFile:
        pathScript = Path(xFile.name)
        xFile.write(sCmd)
    # endwith

    lCmd = [sShellPath]
    if isinstance(lShellArgs, list):
        lCmd.extend(lShellArgs)
    # endif
    lCmd.append(pathScript.as_posix())

    procChild = subprocess.Popen(
        lCmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False,
        cwd=sEffCwd,
        universal_newlines=True,
        env=dicEnviron,
    )

    lLines = []
    for sLine in iter(procChild.stdout.readline, ""):
        lLines.append(sLine)
        if bDoPrint:
            print(sPrintPrefix + sLine, end="", flush=True)
        # endif
    # endfor

    procChild.stdout.close()
    iReturnCode = procChild.wait()
    pathScript.unlink()

    if iReturnCode != 0:
        if bDoRaiseOnError:
            raise subprocess.CalledProcessError(iReturnCode, sCmd)
        elif not bDoPrint and bDoPrintOnError is True:
            sMsg = sPrintPrefix + "ERROR:\n"
            for sLine in lLines:
                sMsg += sPrintPrefix + "! " + sLine
            # endfor
            print(sMsg)
        # endif
    # endif

    if bReturnStdOut is True:
        return iReturnCode == 0, lLines
    else:
        return iReturnCode == 0
    # endif


# enddef


#################################################################################################################
def ExecPowerShellCmds(
    *,
    lCmds,
    sCwd=None,
    bDoPrint=False,
    bDoPrintOnError=False,
    bDoRaiseOnError=False,
    bReturnStdOut=False,
    sPrintPrefix="",
    dicEnv=None,
):

    return ExecShellCmds(
        sShellPath="powershell.exe",
        lCmds=lCmds,
        sCwd=sCwd,
        bDoPrint=bDoPrint,
        bDoPrintOnError=bDoPrintOnError,
        bDoRaiseOnError=bDoRaiseOnError,
        bReturnStdOut=bReturnStdOut,
        sPrintPrefix=sPrintPrefix,
        dicEnv=dicEnv,
    )


# enddef


#################################################################################################################
def ExecBashCmds(
    *,
    lCmds,
    sCwd=None,
    bDoPrint=False,
    bDoPrintOnError=False,
    bDoRaiseOnError=False,
    bReturnStdOut=False,
    sPrintPrefix="",
    dicEnv=None,
):
    # Run bash shell in interactive mode,
    # so that .bashrc is parsed automatically.
    # This also removes problems with .bashrc files,
    # that explicitly avoid execution in non-interactive mode.

    return ExecShellCmds(
        sShellPath="/bin/bash",
        lShellArgs=["-i"],
        lCmds=lCmds,
        sCwd=sCwd,
        bDoPrint=bDoPrint,
        bDoPrintOnError=bDoPrintOnError,
        bDoRaiseOnError=bDoRaiseOnError,
        bReturnStdOut=bReturnStdOut,
        sPrintPrefix=sPrintPrefix,
        dicEnv=dicEnv,
    )


# enddef


#################################################################################################################
def ExecPlatformCmds(
    *,
    lCmds,
    sCwd=None,
    bDoPrint=False,
    bDoPrintOnError=False,
    bDoRaiseOnError=False,
    bReturnStdOut=False,
    sPrintPrefix="",
    dicEnv=None,
):

    sSystem = platform.system()
    if sSystem == "Windows":
        return ExecPowerShellCmds(
            lCmds=lCmds,
            sCwd=sCwd,
            bDoPrint=bDoPrint,
            bDoPrintOnError=bDoPrintOnError,
            bDoRaiseOnError=bDoRaiseOnError,
            bReturnStdOut=bReturnStdOut,
            sPrintPrefix=sPrintPrefix,
            dicEnv=dicEnv,
        )

    elif sSystem == "Linux":
        return ExecBashCmds(
            lCmds=lCmds,
            sCwd=sCwd,
            bDoPrint=bDoPrint,
            bDoPrintOnError=bDoPrintOnError,
            bDoRaiseOnError=bDoRaiseOnError,
            bReturnStdOut=bReturnStdOut,
            sPrintPrefix=sPrintPrefix,
            dicEnv=dicEnv,
        )

    else:
        raise RuntimeError(f"Unsupported system '{sSystem}'")
    # endif


# enddef
