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


try:
    import pytest
except Exception:
    raise RuntimeError("Module 'pytest' not installed in current environment")
# endtry

import re

from contextlib import redirect_stdout
from tabulate import tabulate
from pathlib import Path

from catharsys.setup import util
from catharsys.setup import module


#####################################################################
def CannotTestFromDist(*, pathDist: Path, pathModule: Path, sName: str, sVersion: str):

    print("===================================================")
    print("Cannot test module from distribution for: {} v{}\n".format(sName, sVersion))


# enddef

####################################################################
def FilterPyModules(**kwargs):
    pathModule = kwargs.get("pathModule")

    pathTest = pathModule / "setup.cfg"
    if pathTest.exists():
        return True
    # endif

    return False


# enddef


####################################################################
def RunModuleTests(
    *,
    pathRepos: Path,
    pathModule: Path,
    dicTestResults: dict,
    pathLog: Path,
    bNoLogs: bool = False,
    bBreakOnFailure: bool = False,
):

    # print("\n========================================================================================")

    sMsg = None
    pathLogFile = None
    pathTests = pathModule / "src" / "testing"

    if not pathTests.exists():
        # print(f"WARNING: Module '{pathModule.name}' has no tests to run")
        iRetCode = -1
        sMsg = "no tests available"

    else:
        lPars = []
        if bBreakOnFailure is True:
            lPars.append("-x")
        # endif
        lPars.append(pathTests.as_posix())

        if bNoLogs is True:
            iRetCode = pytest.main(lPars)
            sMsg = "see console output"

        else:
            print(f"Running tests for module '{pathModule.name}'")
            print(">> {}".format(pathModule.as_posix()))

            pathLogFile = pathLog / f"_testlog_{pathModule.name}.txt"
            with pathLogFile.open("w") as xFileLog:
                with redirect_stdout(xFileLog):
                    iRetCode = pytest.main(lPars)
                # endwith
            # endwith

            reSummary = re.compile(r"=+\s+([^=]+)\s+=+")

            sLog = pathLogFile.read_text()
            lLines = sLog.split("\n")
            for sLine in lLines[-1:0:-1]:
                xMatch = reSummary.match(sLine)
                if xMatch is not None:
                    sMsg = xMatch.group(1)
                    break
                # endif
            # endfor
        # endif

    # endif

    dicTestResults[pathModule.name] = {
        "sMsg": sMsg,
        "iRetCode": iRetCode,
        "pathLogFile": pathLogFile,
    }

    if iRetCode != 0 and bBreakOnFailure is True:
        return False
    # endif

    return True


# enddef

####################################################################
def Run(
    *,
    lModules: list[str] = [],
    sLogPath: str = None,
    bNoLogs: bool = False,
    bBreakOnFailure: bool = False,
):

    # Look for documentation virtual environment
    pathRepos = util.TryGetReposPath()
    if pathRepos is None:
        raise RuntimeError("Modules can only be test in source install")
    # endif

    if sLogPath is None:
        pathLog = Path.cwd()

    else:
        pathLog = Path(sLogPath)
        if not pathLog.is_absolute():
            pathLog = Path.cwd() / pathLog
        # endif
        pathLog.mkdir(parents=True, exist_ok=True)
    # endif

    pathSetup = pathRepos.parent

    lIncMods = lModules if isinstance(lModules, list) else []

    def CreateTestFunc(
        *, dicTestResults: dict, pathLog: Path, bNoLogs: bool, bBreakOnFailure: bool
    ):
        def Lambda(*, pathRepos: Path, pathModule: Path):
            return RunModuleTests(
                pathRepos=pathRepos,
                pathModule=pathModule,
                dicTestResults=dicTestResults,
                pathLog=pathLog,
                bNoLogs=bNoLogs,
                bBreakOnFailure=bBreakOnFailure,
            )

        # enddef
        return Lambda

    # enddef

    dicTestResults: dict = {}

    lPathModules = module.ForEach(
        bForceDist=False,
        funcRunDist=CannotTestFromDist,
        funcRunRepo=CreateTestFunc(
            dicTestResults=dicTestResults,
            pathLog=pathLog,
            bNoLogs=bNoLogs,
            bBreakOnFailure=bBreakOnFailure,
        ),
        funcTest=FilterPyModules,
        lIncludeRegEx=lIncMods,
    )

    # for pathModule in lPathModules:
    #     pathLogFile = pathLog / f"_testlog_{pathModule.name}.txt"
    #     sText = pathLogFile.read_text()

    #     sMd = f"# Module {pathModule.name}"

    # print("\n========================================================================================")

    lOutput = []
    for sMod in dicTestResults:
        dicResult = dicTestResults[sMod]
        sResult = None
        iRetCode = dicResult["iRetCode"]
        if iRetCode == 0:
            sResult = "ok"
        elif iRetCode < 0:
            sResult = "invalid"
        else:
            sResult = "failed"
        # endif

        pathLogFile = dicResult["pathLogFile"]
        if pathLogFile is not None:
            pathLogRel = dicResult["pathLogFile"].relative_to(Path.cwd())
            sMsg = "{} ({})".format(dicResult["sMsg"], pathLogRel.as_posix())
        else:
            sMsg = dicResult["sMsg"]
        # endif

        lOutput.append([sMod, sResult, sMsg])
    # endfor

    lHeaders = ["Module", "Result", "Info"]

    print("")
    print(tabulate(lOutput, headers=lHeaders))
    print("")


# enddef
