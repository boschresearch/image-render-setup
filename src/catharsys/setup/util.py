#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \util.py
# Created Date: Wednesday, April 27th 2022, 3:52:24 pm
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

import re
import io
import os
import sys
import platform
import subprocess
import typing
import json
import pyjson5
from typing import Union, Optional
from pathlib import Path
from tqdm import tqdm
from zipfile import ZipFile
import shutil

if sys.version_info < (3, 10):
    import importlib_resources as res
else:
    from importlib import resources as res
# endif

import catharsys.setup
from . import version
from . import conda


####################################################################
def TryGetReposPath() -> Path:
    pathRepos: Path = None
    with res.path(catharsys.setup, "dist") as pathDist:
        pathRepos = GetReposPath(pathDist)
    # endwith
    return pathRepos


# enddef


####################################################################
def GetDistPath() -> Path:
    pathResult = None
    with res.path(catharsys.setup, "dist") as pathDist:
        pathResult = Path(pathDist.as_posix())
    # endwith
    return pathResult


# enddef


############################################################################
def IsDevelopInstall() -> bool:
    return TryGetReposPath() is not None


# enddef


#################################################################################################################
# IMPORTANT: since image-render-setup is currently not installed in Blender python,
#            need to duplicate this function in image-render-automation, catharsys.util.path.
#
def GetCathUserPath(*, _bCheckExists: bool = False) -> Path:
    sEnvName = conda.GetActiveEnvName()
    if sEnvName is None:
        raise RuntimeError("Conda environment name not set in system environment")
    # endif

    pathUser = Path.home() / ".catharsys" / sEnvName / version.MajorMinorAsString()
    if _bCheckExists is True and not pathUser.exists():
        raise RuntimeError(f"Catharsys user path does not exist: {(pathUser.as_posix())}")
    # endif

    return pathUser


# enddef


#######################################################################
def NormPath(_xPath: Union[str, Path]):
    if isinstance(_xPath, str):
        return Path(os.path.normpath(os.path.expandvars(os.path.expanduser(_xPath)))).as_posix()

    elif isinstance(_xPath, Path):
        return Path(NormPath(_xPath.as_posix()))

    else:
        raise RuntimeError("Path argument has invalid type.")
    # endtry


# enddef


#######################################################################
# Load JSON file from path
def LoadJson(_xFilePath) -> dict:
    pathFile = NormPath(_xFilePath)

    try:
        with pathFile.open("r") as xFile:
            dicData = pyjson5.decode_io(xFile)
        # endwith
    except pyjson5.Json5IllegalCharacter as xEx:
        print(xEx.message)
        xMatch = re.search(r"near\s+(\d+),", xEx.message)
        if xMatch is None:
            raise RuntimeError(
                sMsg="\n".join(
                    [
                        "Illegal character encountered while parsing JSON file",
                        xEx.message,
                        pathFile.as_posix(),
                    ]
                )
            )
        # endif
        iCharPos = int(xMatch.group(1))
        sText = pathFile.read_text()
        lLines = sText.split("\n")
        iCharCnt = 0
        iLinePos = len(lLines) - 1

        for iLineIdx, sLine in enumerate(lLines):
            iCharCnt += len(sLine) + 1
            if iCharCnt >= iCharPos:
                iLinePos = iLineIdx
                break
            # endif
        # endfor

        # From character position, subtract length of line with error and
        # the numer of lines before this line, to subtract the newline characters
        iCharPosInLine = min(
            len(lLines[iLinePos]) - 1,
            max(0, iCharPos - (iCharCnt - len(lLines[iLinePos]))),
        )

        lMsg = [
            "Unexpected character '{}' encountered in line {} at position {}".format(
                xEx.character, iLinePos + 1, iCharPosInLine + 1
            )
        ]
        iLineStart = max(0, iLinePos - 1)
        iLineEnd = min(len(lLines) - 1, iLinePos + 1)
        for iLineIdx in range(iLineStart, iLineEnd + 1):
            sLine = lLines[iLineIdx]
            if iLineIdx == iLinePos:
                sMsg = ">{:3d}<: ".format(iLineIdx + 1)
                sMsg += sLine[0:iCharPosInLine]
                sMsg += ">{}<".format(sLine[iCharPosInLine])
                sMsg += sLine[iCharPosInLine + 1 :]
            else:
                sMsg = " {:3d} :  {}".format(iLineIdx + 1, sLine)
            # endif
            lMsg.append(sMsg)
        # endfor
        raise RuntimeError("Error parsing JSON file: {}{}".format(pathFile.as_posix(), "\n".join(lMsg)))
    # endtry

    return dicData


# enddef


#######################################################################
# save JSON file from relative path to script path
def SaveJson(_xFilePath, _dicData, iIndent=-1):
    pathFile = NormPath(_xFilePath)

    with pathFile.open("w") as xFile:
        if iIndent < 0 or pathFile.suffix == ".json5" or pathFile.suffix == ".ison":
            pyjson5.encode_io(_dicData, xFile, supply_bytes=False)
        else:
            json.dump(_dicData, xFile, indent=iIndent)
        # endif
    # endwith


# enddef


#################################################################################################################
def ExecShellCmd(
    *,
    sCmd,
    sCwd=None,
    bDoPrint=False,
    bDoPrintOnError=False,
    bDoRaiseOnError=False,
    bReturnStdOut=False,
    sPrintPrefix="",
    dicEnv=None,
    pathVirtEnv=None,
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

    bIsWindows: bool = platform.system() == "Windows"
    sEffCmd = ""
    if pathVirtEnv is not None:
        if bIsWindows is True:
            pathAct = pathVirtEnv / "Scripts" / "activate.bat"
            sEffCmd = "{} & ".format(str(pathAct))
        else:
            pathAct = pathVirtEnv / "bin" / "activate"
            pathAct = pathAct.relative_to(Path(sEffCwd))
            sEffCmd = "source {} && ".format(pathAct.as_posix())
        # endif
    # endif

    sEffCmd += sCmd

    print(f"Effective Command:\n{sEffCmd}")
    sExecutable: str = None
    if bIsWindows is False:
        sExecutable = "/bin/bash"
        print(f"Using Executable: {sExecutable}")
    # endif

    procChild = subprocess.Popen(
        sEffCmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        executable=sExecutable,
        cwd=sEffCwd,
        # universal_newlines=True,
        env=dicEnviron,
    )

    lLines = []
    # for sLine in iter(procChild.stdout.readline, ""):
    for sLine in io.TextIOWrapper(procChild.stdout, encoding="utf-8", errors="ignore"):
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


####################################################################
def GetReposPath(_pathDist, bDoRaise=False):
    if "src" not in _pathDist.parts:
        if bDoRaise:
            raise RuntimeError("Unable to install as 'editable', because this is not a source repository")
        else:
            return None
        # endif
    # endif
    pathRepos = _pathDist
    while pathRepos.name != "src":
        pathRepos = pathRepos.parent
    # endwhile
    pathRepos = pathRepos.parent / "repos"

    if not pathRepos.exists():
        if bDoRaise:
            raise RuntimeError("Unable to install as 'editable', because source repository folder cannot be found")
        else:
            return None
        # endif
    # endif

    return pathRepos


# enddef


############################################################################
def GetInstalledModuleInfo(
    *, sPathPythonProg: str, sModuleName: str, pathVirtEnv: typing.Optional[Path] = None
) -> dict:
    bOK, lStdOut = ExecShellCmd(
        sCmd="{} -m pip show {}".format(sPathPythonProg, sModuleName),
        pathVirtEnv=pathVirtEnv,
        bDoPrint=False,
        bDoPrintOnError=False,
        bDoRaiseOnError=False,
        sPrintPrefix=">> ",
        bReturnStdOut=True,
    )

    dicInfo = {}

    if bOK is False:
        return dicInfo
        # raise RuntimeError("Error obtaining installed version of package '{}'".format(sModuleName))
    # endif

    reElement = re.compile(r"([^:]+):\s*(.+)")
    xMatch = None
    for sLine in lStdOut:
        xMatch = reElement.match(sLine)
        if xMatch is not None:
            dicInfo[xMatch.group(1)] = xMatch.group(2)
        # endif
    # endfor

    return dicInfo


# enddef


####################################################################
def PipInstallModule(
    *,
    sModuleName,
    pathCwd=None,
    sUserModuleName=None,
    sPathPythonProg="python",
    pathVirtEnv=None,
    bDoPrint=True,
    bDoPrintOnError=True,
    sPrintPrefix="",
):
    if sUserModuleName is None:
        sUserModuleName = sModuleName
    # endif

    if pathCwd is None:
        pathCwd = Path.cwd()
    # endif

    if bDoPrint is True:
        print("==========================================================")
        print(f"Checking whether {sUserModuleName} is installed...")
    # endif

    dicInfo = GetInstalledModuleInfo(
        sPathPythonProg=sPathPythonProg,
        sModuleName=sModuleName,
        pathVirtEnv=pathVirtEnv,
    )
    sVersion = dicInfo.get("Version")
    if sVersion is None:
        if bDoPrint is True:
            print(sPrintPrefix + f"Installing {sUserModuleName}...")
        # endif

        ExecShellCmd(
            sCmd="{} -m pip install -U {}".format(sPathPythonProg, sModuleName),
            sCwd=pathCwd.as_posix(),
            pathVirtEnv=pathVirtEnv,
            bDoPrint=bDoPrint,
            bDoPrintOnError=bDoPrintOnError,
            sPrintPrefix=sPrintPrefix + ">> ",
        )

        dicInfo = GetInstalledModuleInfo(
            sPathPythonProg=sPathPythonProg,
            sModuleName=sModuleName,
            pathVirtEnv=pathVirtEnv,
        )
        sVersion = dicInfo.get("Version")
        if sVersion is None:
            raise RuntimeError(sPrintPrefix + f"Error installing {sUserModuleName}")
        # endif
    # endif
    if bDoPrint is True:
        print(sPrintPrefix + f"Using {sUserModuleName} v{sVersion}\n")
    # endif


# enddef


####################################################################
def Unzip(*, pathZipFile: Path, pathUnpack: Path, bOverwrite: bool = False):
    with ZipFile(pathZipFile.as_posix(), "r") as zipFile:
        lNames = zipFile.namelist()
        sMainFolder = lNames[0].split("/")[0]
        pathExtract = pathUnpack / sMainFolder

        if pathExtract.exists():
            if bOverwrite is False:
                raise RuntimeError("Unzip target path already exists: {}".format(pathExtract.as_posix()))
            else:
                shutil.rmtree(pathExtract.as_posix())
            # endif
        # endif

        sPathUnpack: str = pathUnpack.as_posix()

        for xMember in tqdm(zipFile.infolist(), desc="Extracting "):
            try:
                zipFile.extract(xMember, sPathUnpack)
            except Exception as xEx:
                raise RuntimeError(
                    "Error extracting file: {}".format(pathZipFile.as_posix()),
                    xChildEx=xEx,
                )
            # endtry
        # endfor zip members
    # endwith


# enddef


###############################################################################################
def CopyFiles(
    pathSrc: Path,
    pathTrg: Path,
    *,
    bRecursive: bool = True,
    lReExcludeDirs: list[str] = [],
    lReExcludeFiles: list[str] = [],
    _lReCmpExclDirs: list[re.Pattern] = [],
    _lReCmpExclFiles: list[re.Pattern] = [],
    pathSrcTop: Optional[Path] = None,
    pathTrgTop: Optional[Path] = None,
):
    if len(_lReCmpExclDirs) > 0:
        lReExclDirs = _lReCmpExclDirs
    else:
        lReExclDirs = [re.compile(x) for x in lReExcludeDirs]
    # endif

    if len(_lReCmpExclFiles) > 0:
        lReExclFiles = _lReCmpExclFiles
    else:
        lReExclFiles = [re.compile(x) for x in lReExcludeFiles]
    # endif

    if pathSrcTop is None:
        pathSrcTop = pathSrc
    # endif

    if pathTrgTop is None:
        pathTrgTop = pathTrg
    # endif

    for pathSrcX in pathSrc.glob("*"):
        if pathSrcX.is_file():
            sName = pathSrcX.name

            if len(lReExclFiles) > 0 and any(test.match(sName) for test in lReExclFiles) is True:
                print("Exclude file: {}".format(pathSrcX.relative_to(pathSrcTop).as_posix()))
            else:
                pathTrgX = pathTrg / sName
                # print("Copy file: {}".format(pathSrcX.relative_to(pathSrcTop).as_posix()))
                shutil.copy(pathSrcX, pathTrgX)
            # endif

        elif pathSrcX.is_dir():
            if bRecursive is True:
                sName = pathSrcX.name

                if len(lReExclDirs) > 0 and any(test.match(sName) for test in lReExclDirs) is True:
                    print("Exclude folder: {}".format(pathSrcX.relative_to(pathSrcTop).as_posix()))
                else:
                    pathTrgX = pathTrg / sName
                    pathTrgX.mkdir(exist_ok=True)
                    # print("Copy folder: {}".format(pathSrcX.relative_to(pathSrcTop).as_posix()))
                    CopyFiles(
                        pathSrcX,
                        pathTrgX,
                        pathSrcTop=pathSrcTop,
                        pathTrgTop=pathTrgTop,
                        _lReCmpExclDirs=lReExclDirs,
                        _lReCmpExclFiles=lReExclFiles,
                    )
                # endif
            # endif recursive
        # endif file | dir
    # endfor


# enddef
