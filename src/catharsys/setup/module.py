#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \module.py
# Created Date: Thursday, April 28th 2022, 5:53:19 pm
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

import imp
import re
import sys
import importlib.util

if sys.version_info < (3, 10):
    import importlib_resources as res
else:
    from importlib import resources as res
# endif

from typing import Optional, Callable, Tuple, Union
from pathlib import Path

import catharsys.setup
from catharsys.setup import util
from packaging import version

# Reduce set of installed/uninstalled modules for debug purposes
g_debug_lInstallModules = []  # ["functional-json", "image-render-blender-camera"]


####################################################################
def GetRegExModuleDistFile(*, sType: str = "WHEEL"):
    if sType == "WHEEL":
        reDist = re.compile(r"(.*?)-(\d+\.\d+\.\d+)-(.+)\.whl")

    elif sType == "SOURCE":
        reDist = re.compile(r"(.*?)-(\d+\.\d+\.\d+)\.tar\.gz")

    else:
        raise RuntimeError(f"Invalid distribution file type {sType}")
    # endif

    return reDist


# enddef


####################################################################
def GetModulePath(*, sPathPythonProg: str, sModuleName: str) -> str:
    xScript = res.files(catharsys.setup).joinpath("scripts").joinpath("run-get-module-path.py")
    with res.as_file(xScript) as pathScript:
        bOK, lStdOut = util.ExecShellCmd(
            sCmd='{} "{}" -- {}'.format(sPathPythonProg, pathScript.as_posix(), sModuleName),
            bDoPrint=False,
            bDoPrintOnError=True,
            bReturnStdOut=True,
            sPrintPrefix=">> ",
        )
    # endwith

    return lStdOut[0].strip()


# enddef


####################################################################
def CanPipInstallModule(*, pathModule: Path) -> bool:
    if pathModule.is_dir():
        pathSetupCfg = pathModule / "setup.cfg"
        return pathSetupCfg.exists()

    elif pathModule.is_file():
        return pathModule.suffix == ".whl"
    # endif

    return False


# enddef


####################################################################
def GetRepoVersion(*, pathModule: Path, bGetSource: bool = False) -> Union[str, tuple[str, str, Path]]:
    pathSetupCfg = pathModule / "setup.cfg"
    if not pathSetupCfg.exists():
        raise RuntimeError(
            "File 'setup.cfg' missing in module '{}' at path: {}".format(pathModule.name, pathModule.as_posix())
        )
    # endif

    pathSource = None
    sAttrName = None

    sSetupCfg = pathSetupCfg.read_text()
    # print(pathSetupCfg)
    # print(sSetupCfg)

    xMatch = re.search(r"^\s*version\s*=\s*(\d+\.\d+\.\d+)", sSetupCfg, re.MULTILINE)
    if xMatch is None:
        xMatch = re.search(r"^\s*version\s*=\s*attr:\s*(.+)$", sSetupCfg, re.MULTILINE)
        if xMatch is None:
            raise RuntimeError(
                "Missing or unsupported definition of 'version' element in 'setup.cfg' of module '{}'".format(
                    pathModule.as_posix()
                )
            )
        # endif
        sRef = xMatch.group(1)
        lRef = sRef.split(".")
        pathRef = pathModule / "src"

        for sFolder in lRef[:-2]:
            pathRef = pathRef / sFolder
        # endfor
        if not pathRef.exists():
            raise RuntimeError("Version reference module file not found at: {}".format(pathRef.as_posix()))
        # endif

        sVerModule = ".".join(lRef[:-1])
        sVerModName = lRef[-2]
        sVerAttr = lRef[-1]
        pathVerMod = pathRef / f"{sVerModName}.py"
        try:
            # Loading the module does not always seem to give that latest code,
            # that is in the actual .py file, due to caching.
            # Not sure how to ensure this. importlib.reload() did not work.
            # Instead load .py file as text and expect >{sVerAttr} = "x.y.z"<

            # specVersion = importlib.util.spec_from_file_location(sVerModName, pathVerMod.as_posix())
            # modVersion = importlib.util.module_from_spec(specVersion)
            # specVersion.loader.exec_module(modVersion)

            sPyText = pathVerMod.read_text()
            xMatch = re.search(
                r"^\s*{}\s*=\s*\"(\d+\.\d+\.\d+)\"".format(sVerAttr),
                sPyText,
                re.MULTILINE,
            )
            if xMatch is None:
                raise RuntimeError(f"Cannot find valid version element '{sVerAttr} = x.y.z'")
            # endif
            sVersion = xMatch.group(1)
        except Exception as xEx:
            raise RuntimeError("Cannot get module version from '{}'\n{}".format(pathVerMod.as_posix(), str(xEx)))
        # endtry

        # print(f"Loaded module: {pathVerMod.as_posix()}")
        # print(f"{modVersion.__version__}")
        # sVerText = pathVerMod.read_text()
        # print(sVerText)

        # if not hasattr(modVersion, lRef[-1]):
        #     raise RuntimeError(f"Module '{sVerModule}' does not have attribute '{sVerAttr}'\nLoaded from: {pathVerMod}")
        # # endif
        # sVersion = getattr(modVersion, lRef[-1])
        pathSource = pathVerMod
        sAttrName = sVerAttr
    else:
        sVersion = xMatch.group(1)
        pathSource = pathSetupCfg
        sAttrName = "version"
    # endif

    if bGetSource is True:
        return sVersion, sAttrName, pathSource
    else:
        return sVersion
    # endif


# enddef


####################################################################
# Increment the repository version
def IncRepoVersion(*, pathModule: Path, iVerPart: int, bDoExecute=True, bGetSource: bool = False) -> str:
    if iVerPart < 0 or iVerPart > 2:
        raise RuntimeError(f"Version part index has to be in range [0,1,2], is given as '{iVerPart}'")
    # endif

    sVersion: str = None
    sAttrName: str = None
    pathSource: Path = None

    sVersion, sAttrName, pathSource = GetRepoVersion(pathModule=pathModule, bGetSource=True)

    xMatch = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", sVersion)
    if xMatch is None:
        raise RuntimeError(f"Invalid version string '{sVersion}' for module '{pathModule.name}'")
    # endif

    lVersion = [0, 0, 0]
    for i in range(3):
        lVersion[i] = int(xMatch.group(i + 1))
    # endfor

    lVersion[iVerPart] += 1
    for i in range(iVerPart + 1, len(lVersion)):
        lVersion[i] = 0
    # endfor
    sNewVersion = ".".join([str(x) for x in lVersion])

    if pathSource.suffix == ".cfg":
        sSourceText = pathSource.read_text()
        xMatch = re.search(r"^\s*{}\s*=\s*(\d+\.\d+\.\d+)".format(sAttrName), sSourceText, re.MULTILINE)
        if xMatch is None:
            raise RuntimeError("Cannot find '{}' element in: {}".format(sAttrName, pathSource.as_posix()))
        # endif

    elif pathSource.suffix == ".py":
        sSourceText = pathSource.read_text()
        xMatch = re.search(
            r"^\s*{}\s*=\s*\"(\d+\.\d+\.\d+)\"".format(sAttrName),
            sSourceText,
            re.MULTILINE,
        )
        if xMatch is None:
            raise RuntimeError("Cannot find '{}' element in: {}".format(sAttrName, pathSource.as_posix()))
        # endif

    # endif

    if bDoExecute is True:
        iStartIdx = xMatch.start(1)
        iEndIdx = xMatch.end(1)

        sNewSourceText = sSourceText[:iStartIdx] + sNewVersion + sSourceText[iEndIdx:]
        pathSource.write_text(sNewSourceText)
    # endif

    if bGetSource is True:
        return sNewVersion, pathSource
    else:
        return sNewVersion
    # endif


# enddef


####################################################################
def RepoNeedsInstall(*, sPathPythonProg: str, pathModule: Path) -> bool:
    try:
        sVersion = GetRepoVersion(pathModule=pathModule)
    except Exception as xEx:
        print("ERROR: {}".format(str(xEx)))
        return False
    # endtry

    bInstall = True
    dicInfo = util.GetInstalledModuleInfo(sPathPythonProg=sPathPythonProg, sModuleName=pathModule.name)
    sLoc = dicInfo.get("Location")
    if sLoc is not None:
        if Path(sLoc).is_relative_to(pathModule):
            sInstVer = dicInfo.get("Version")
            if sInstVer is not None:
                if version.parse(sVersion) <= version.parse(sInstVer):
                    bInstall = False
                # endif
            # endif has version
        # endif
    # endif

    return bInstall


# enddef


####################################################################
def DistNeedsInstall(*, sPathPythonProg: str, sName: str, sVersion: str):
    bInstall = True
    sInstVer = None
    dicInfo = util.GetInstalledModuleInfo(sPathPythonProg=sPathPythonProg, sModuleName=sName)
    sLoc = dicInfo.get("Location")
    if sLoc is not None:
        # Check whether the installed module is editable
        pathLoc = Path(sLoc)
        if pathLoc.parts[-1] != "src":
            # if it is not an editable install, then check the version
            sInstVer = dicInfo.get("Version")
            if sInstVer is not None:
                if version.parse(sVersion) <= version.parse(sInstVer):
                    bInstall = False
                # endif
            # endif has version
        # endif not source install
    # endif location available

    return bInstall, sInstVer


# enddef


####################################################################
def ForEach(
    *,
    bForceDist: bool = False,
    bSourceDist: bool = False,
    funcRunRepo: Optional[Callable] = None,
    funcRunDist: Optional[Callable] = None,
    lExcludeRegEx: list[str] = [],
    lIncludeRegEx: list[str] = [],
    funcTest: Optional[Callable] = None,
    pathReposOverride: Optional[Path] = None,
) -> list[Path]:
    lPathModule = []
    bUseDist = None
    pathModules = None

    if bSourceDist is True:
        reDist = GetRegExModuleDistFile(sType="SOURCE")
    else:
        reDist = GetRegExModuleDistFile(sType="WHEEL")
    # endif

    # Exclude all folders starting with a '.'
    lExcludeRegEx.append(r"^\..+")

    with res.path(catharsys.setup, "dist") as pathDist:
        # print(pathDist)
        if isinstance(pathReposOverride, Path):
            pathRepos = pathReposOverride
        else:
            pathRepos = util.GetReposPath(pathDist)
        # endif

        if pathRepos is None or bForceDist is True:
            bUseDist = True
            pathModules = pathDist
        else:
            bUseDist = False
            pathModules = pathRepos
        # endif

        lExcludeRegExComp = [re.compile(x) for x in lExcludeRegEx]
        lIncludeRegExComp = [re.compile(x) for x in lIncludeRegEx]

        for pathMod in pathModules.iterdir():
            # Test for exclude filter
            bContinue = False
            for reFilter in lExcludeRegExComp:
                if reFilter.fullmatch(pathMod.name) is not None:
                    bContinue = True
                    break
                # endif
            # endfor filter

            if bContinue is True:
                continue
            # endif

            # Test for include filter
            if len(lIncludeRegEx) > 0:
                bContinue = True
                for reFilter in lIncludeRegExComp:
                    if reFilter.fullmatch(pathMod.name) is not None:
                        bContinue = False
                        break
                    # endif
                # endfor filter

                if bContinue is True:
                    continue
                # endif
            # endif

            if funcTest is not None and funcTest(pathModule=pathMod, bUseDist=bUseDist) is False:
                continue
            # endif

            lPathModule.append(pathMod)

            if bUseDist is True:
                if funcRunDist is None:
                    continue
                # endif

                if not pathMod.is_file():
                    continue
                # endif

                xMatch = reDist.fullmatch(pathMod.name)
                if xMatch is None:
                    continue
                # endif

                # In wheel distribution files the '-' are changed into '_'.
                # We need to reverse this here to get the correct name.
                sModuleName = xMatch.group(1).replace("_", "-")

                bResult = funcRunDist(
                    pathModule=pathMod,
                    pathDist=pathDist,
                    sName=sModuleName,
                    sVersion=xMatch.group(2),
                )

            else:
                if funcRunRepo is None:
                    continue
                # endif

                if not pathMod.is_dir():
                    continue
                # endif

                bResult = funcRunRepo(pathModule=pathMod, pathRepos=pathRepos)
            # endif dist or repo

            if bResult is False:
                break
            # endif
        # endfor modules
    # endwith

    return lPathModule


# enddefs


############################################################################
class CRepoHandlerFactory:
    @classmethod
    def CreateUninstall(cls, _sPathPythonProg):
        def Handler(*, pathModule, pathRepos):
            if not CanPipInstallModule(pathModule=pathModule):
                return
            # endif

            print("=================================================================")
            print("Uninstalling (editable): {}\n".format(pathModule.name))
            bOK = util.ExecShellCmd(
                sCmd='"{}" -m pip uninstall {} -y'.format(_sPathPythonProg, pathModule.name),
                sCwd=pathModule.as_posix(),
                bDoPrint=True,
                bDoPrintOnError=True,
                sPrintPrefix=">> ",
            )
            print("")
            if bOK is False:
                print("\n>>>>>>>>>>>>")
                print("ERROR: Cannot uninstall {}.".format(pathModule.name))
                print(">>>>>>>>>>>>\n")
            # endif

        # enddef Handler
        return Handler

    # enddef CreateUninstall

    @classmethod
    def CreateInstall(cls, _sPathPythonProg, _bForceInstall):
        def Handler(*, pathModule, pathRepos):
            if not CanPipInstallModule(pathModule=pathModule):
                return
            # endif

            if _bForceInstall is True:
                print(
                    ">> Installing (editable): {} first removes already installed version=====".format(pathModule.name)
                )
                funcUninstallHandler = cls.CreateUninstall(_sPathPythonProg=_sPathPythonProg)
                funcUninstallHandler(pathModule=pathModule, pathRepos=pathRepos)
            # endif

            print("=================================================================")
            print("Module: {}".format(pathModule.name))
            print(">> Checking installation status...")
            # Check whether module is already installed as editable
            bInstall = True
            if _bForceInstall is False:
                bInstall = RepoNeedsInstall(sPathPythonProg=_sPathPythonProg, pathModule=pathModule)
            # # endif

            if bInstall is True:
                print(">> Installing (editable): {}\n".format(pathModule.name))
                bOK = util.ExecShellCmd(
                    sCmd='"{}" -m pip install --editable .'.format(_sPathPythonProg),
                    sCwd=pathModule.as_posix(),
                    bDoPrint=True,
                    bDoPrintOnError=True,
                    sPrintPrefix=">> >> ",
                )
                print(">> ")
                if bOK is False:
                    print("\n>>>>>>>>>>>>")
                    print(">> ERROR: Cannot install {}.".format(pathModule.name))
                    print(">>>>>>>>>>>>\n")
                # endif
            else:
                print(">> Already installed (editable): {}\n".format(pathModule.name))
            # endif

        # enddef Handler
        return Handler

    # enddef CreateInstall


# end class


class CDistHandlerFactory:
    @classmethod
    def CreateInstall(cls, _sPathPythonProg, _bForceInstall):
        def Handler(*, pathModule, pathDist, sName, sVersion):
            if not CanPipInstallModule(pathModule=pathModule):
                return
            # endif

            print("=================================================================")
            print("Module: {} v{}".format(sName, sVersion))
            print(">> Checking installation status...")

            # Check whether module is already installed as distribution
            bInstall = True
            if _bForceInstall is False:
                bInstall, sInstVer = DistNeedsInstall(sPathPythonProg=_sPathPythonProg, sName=sName, sVersion=sVersion)
            # endif

            print("=================================================================")
            if bInstall is True:
                print(">> Installing: {} v{}\n".format(sName, sVersion))
                bOK = util.ExecShellCmd(
                    sCmd='"{}" -m pip install --upgrade "{}"'.format(_sPathPythonProg, pathModule.as_posix()),
                    sCwd=pathDist.as_posix(),
                    bDoPrint=True,
                    bDoPrintOnError=True,
                    sPrintPrefix=">> >> ",
                )
                print(">> ")
                if bOK is False:
                    print("\n>>>>>>>>>>>>")
                    print(">> ERROR: Cannot install {}.".format(pathModule.name))
                    print(">>>>>>>>>>>>\n")
                # endif
            else:
                print(">> Already installed: {} v{}\n".format(sName, sInstVer))
            # endif

        # enddef Handler
        return Handler

    @classmethod
    def CreateUninstall(cls, _sPathPythonProg):
        def Handler(*, pathModule, pathDist, sName, sVersion):
            print("=================================================================")
            print("Uninstalling: {} v{}\n".format(sName, sVersion))
            bOK = util.ExecShellCmd(
                sCmd='"{}" -m pip uninstall {} -y'.format(_sPathPythonProg, sName),
                sCwd=pathDist.as_posix(),
                bDoPrint=True,
                bDoPrintOnError=True,
                sPrintPrefix=">> ",
            )
            print("")
            if bOK is False:
                print("\n>>>>>>>>>>>>")
                print("ERROR: Cannot install {}.".format(pathModule.name))
                print(">>>>>>>>>>>>\n")
            # endif

        # enddef Handler
        return Handler

    # enddef Factory


# end class


############################################################################
def InstallModules(
    *,
    sPathPythonProg: str = "python",
    bForceDist: bool,
    bForceInstall: bool,
    bSourceDist: bool,
):
    ForEach(
        bForceDist=bForceDist,
        bSourceDist=bSourceDist,
        # funcRunRepo=CreateInstallRepoHandler(sPathPythonProg, bForceInstall),
        # funcRunDist=CreateInstallDistHandler(sPathPythonProg, bForceInstall),
        funcRunRepo=CRepoHandlerFactory.CreateInstall(sPathPythonProg, bForceInstall),
        funcRunDist=CDistHandlerFactory.CreateInstall(sPathPythonProg, bForceInstall),
        lIncludeRegEx=g_debug_lInstallModules,
        lExcludeRegEx=["image-render-workspace-.+"],
    )


# enddef


############################################################################
def UninstallModules(
    *,
    sPathPythonProg: str = "python",
):
    ForEach(
        bForceDist=False,
        # funcRunRepo=CreateUninstallRepoHandler(sPathPythonProg),
        # funcRunDist=CreateUninstallDistHandler(sPathPythonProg),
        funcRunRepo=CRepoHandlerFactory.CreateUninstall(sPathPythonProg),
        funcRunDist=CDistHandlerFactory.CreateUninstall(sPathPythonProg),
        lIncludeRegEx=g_debug_lInstallModules,
        lExcludeRegEx=["image-render-workspace-.+"],
    )


# enddef
