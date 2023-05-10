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

import re
import sys

if sys.version_info < (3, 10):
    import importlib_resources as res
else:
    from importlib import resources as res
# endif
from pathlib import Path
import catharsys.setup

from shutil import unpack_archive
from typing import Optional
from catharsys.setup import util

g_sCmdDesc = "Installs Catharsys workspaces"


####################################################################
def Run(
    *,
    sWsName: str,
    sPathTrg: Optional[str] = None,
    bForce: bool = False,
    bDoList: bool = False,
):

    if not isinstance(sPathTrg, str):
        pathWsTrg = Path.cwd()
    else:
        pathWsTrg = Path(util.NormPath(sPathTrg))
    # endif

    if not pathWsTrg.exists():
        raise RuntimeError(
            "Target path does not exist: {}".format(pathWsTrg.as_posix())
        )
    # endif

    if sWsName is None:
        bDoList = True
    # endif

    if bDoList is False:
        sWsFullName = "image-render-workspace-{}".format(sWsName)

        with res.path(catharsys.setup, "dist") as pathDist:
            pathDistWs = pathDist / "workspace"

            reDist = re.compile(r"{}-(\d+\.\d+\.\d+)\.zip".format(sWsFullName))
            pathWsSrc = None
            for pathWsZip in pathDistWs.iterdir():
                if pathWsZip.is_file() and reDist.match(pathWsZip.name) is not None:
                    pathWsSrc = pathWsZip
                # endif
            # endfor

            if pathWsSrc is None:
                raise RuntimeError(
                    "Workspace package '{}' not found".format(sWsFullName)
                )
            # endif

            print(
                "Unpacking workspace '{}' to path: {}".format(
                    sWsFullName, pathWsTrg.as_posix()
                )
            )
            # shutil.unpack_archive(pathWsSrc.as_posix(), pathWsTrg.as_posix())
            util.Unzip(pathZipFile=pathWsSrc, pathUnpack=pathWsTrg, bOverwrite=bForce)
        # endwith

    else:
        print("Available workspaces:")
        reDist = re.compile(r"image-render-workspace-([^-]+)-(\d+\.\d+\.\d+)\.zip")
        with res.path(catharsys.setup, "dist") as pathDist:
            pathDistWs = pathDist / "workspace"
            for pathDir in pathDistWs.iterdir():
                xMatch = reDist.match(pathDir.name)
                if xMatch is None:
                    continue
                # endif
                sName = xMatch.group(1)
                sVersion = xMatch.group(2)
                print(f"- '{sName}' (v{sVersion})")
            # endfor
        # endwith
        print("")
    # endif


# enddef
