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

# #  Example on how to obtain file
# xFiles = res.files(catharsys.setup)
# xDist = xFiles.joinpath("dist")
# for xDistFile in xDist.iterdir():
#     print(xDistFile.name)
# # endfor

import shutil
from catharsys.setup import util
from catharsys.setup import module


####################################################################
def _BuildFromRepo(*, pathRepos, pathModule, sOutputType, pathEnv, pathDocMain):
    pathSource = pathModule / "docs" / "source"
    sPathBuild = "build/{}".format(pathModule.name)

    print("===================================================")
    print("Building Documentation for: {}\n---\n".format(pathModule.name))
    sCmd = 'sphinx-build -M {} "{}" {}'.format(sOutputType, pathSource.as_posix(), sPathBuild)
    sCwd = pathDocMain.as_posix()
    util.ExecShellCmd(sCmd=sCmd, sCwd=sCwd, bDoPrint=True, bDoPrintOnError=True, pathVirtEnv=pathEnv)
    print("")


# enddef


#######################################################6#############
def _CannotBuildFromDist(*, pathDist, pathModule, sName, sVersion):
    print("===================================================")
    print("Cannot build documentation from distribution for: {} v{}\n".format(sName, sVersion))


# enddef


####################################################################
def _FilterDocModules(**kwargs):
    pathModule = kwargs.get("pathModule")
    bUseDist = kwargs.get("bUseDist")

    pathTest = pathModule / "docs" / "source" / "conf.py"
    return pathTest.exists()


# enddef


####################################################################
def Run(*, sOutputType, bInstall, bModulesOnly, bMainOnly, lModules, bInstallOnly=False):
    import ison
    import json

    # Look for documentation virtual environment
    pathRepos = util.TryGetReposPath()
    if pathRepos is None:
        raise RuntimeError("Documentation can only be built from source install")
    # endif

    pathSetup = pathRepos.parent
    pathDocMain = pathSetup / "docs"
    pathEnv = pathSetup / "env" / "docs"
    pathRelEnv = pathEnv.relative_to(pathSetup.as_posix())

    print(f"pathSetup: {pathSetup}")
    print(f"pathDocMain: {pathDocMain}")
    print(f"pathEnv: {pathEnv}")
    print(f"pathRelEnv: {pathRelEnv}")

    if bInstall is True or bInstallOnly is True:
        ##################################################################################
        # Create virtual environment if it does not exist
        if not pathEnv.exists():
            print("Documentation generation python environment not found.")
            print(f"Creating virtual python environment at path\n    {(pathEnv.as_posix())}")
            util.ExecShellCmd(
                sCmd='python -m venv "{}" --system-site-packages'.format(pathRelEnv.as_posix()),
                sCwd=pathSetup.as_posix(),
                bDoPrint=True,
                bDoPrintOnError=True,
                sPrintPrefix=">> ",
            )

            if not pathEnv.exists():
                raise RuntimeError(
                    "Error creating virtual python environment.\n"
                    "Please create manually in path: {}".format(pathEnv.as_posix())
                )
            # endif
        else:
            print("Documentation generation python environment found at: {}".format(pathEnv.as_posix()))
        # endif

        ##################################################################################
        # Installing modules in virtual environment
        util.PipInstallModule(
            sModuleName="sphinx",
            sUserModuleName="Sphinx",
            pathCwd=pathSetup,
            pathVirtEnv=pathEnv,
            sPrintPrefix=">> ",
        )

        util.PipInstallModule(
            sModuleName="myst_parser",
            sUserModuleName="MyST-Parser",
            pathCwd=pathSetup,
            pathVirtEnv=pathEnv,
            sPrintPrefix=">> ",
        )

        util.PipInstallModule(
            sModuleName="myst_nb",
            sUserModuleName="MyST Python Notebook support",
            pathCwd=pathSetup,
            pathVirtEnv=pathEnv,
            sPrintPrefix=">> ",
        )

        util.PipInstallModule(
            sModuleName="sphinx-book-theme",
            sUserModuleName="Sphinx Book Theme",
            pathCwd=pathSetup,
            pathVirtEnv=pathEnv,
            sPrintPrefix=">> ",
        )

    elif not pathEnv.exists():
        raise RuntimeError(
            "Documentation generation python environment not found at: {}\n"
            "Install environment with: cathy build docs -I\n".format(pathEnv.as_posix())
        )
    # endif

    if bInstallOnly is True:
        return
    # endif

    ##################################################################################
    # Loop over all modules that have the basic sphinx documentation structure

    def CreateBuildFunc(_sOutputType, _pathEnv, _pathDocMain):
        def Lambda(*, pathRepos, pathModule):
            _BuildFromRepo(
                pathRepos=pathRepos,
                pathModule=pathModule,
                sOutputType=_sOutputType,
                pathEnv=_pathEnv,
                pathDocMain=_pathDocMain,
            )

        # enddef
        return Lambda

    # enddef

    lIncMods = lModules if isinstance(lModules, list) else []

    if bMainOnly is False:
        lPathModules = module.ForEach(
            bForceDist=False,
            funcRunDist=_CannotBuildFromDist,
            funcRunRepo=CreateBuildFunc(sOutputType, pathEnv, pathDocMain),
            funcTest=_FilterDocModules,
            lIncludeRegEx=lIncMods,
        )
    # endif

    # print(f"lPathModules: {lPathModules}")
    if len(lPathModules) == 0:
        raise RuntimeError("No modules found with documentation structure.")
    # endif

    # Only process modules documentation
    if bModulesOnly is False:
        pathDocSource = pathDocMain / "source"
        pathConfig = pathDocSource / "auto_config.json"
        print("===================================================")
        print("Preprocessing main documentation configuration")

        if bMainOnly is False:
            dicConfig: dict = None
            if pathConfig.exists():
                with pathConfig.open("r") as xFile:
                    dicConfig = json.load(xFile)
                    lModNames = dicConfig.get("lModules")
                # endwith
                for pathMod in lPathModules:
                    if pathMod.name not in lModNames:
                        lModNames.append(pathMod.name)
                    # endif
                # endfor
            else:
                lModNames = [x.name for x in lPathModules]
                dicConfig = {"lModules": lModNames}
            # endif

            with pathConfig.open("w") as xFile:
                json.dump(dicConfig, xFile)
            # endwith

        else:
            with pathConfig.open("r") as xFile:
                dicConfig = json.load(xFile)
                lModNames = dicConfig.get("lModules")
            # endwith
        # endif

        pathIndex = pathDocMain / "index.ison"
        if not pathIndex.exists():
            raise RuntimeError("Missing file: {}".format(pathIndex.as_posix()))
        # endif

        dicVars = {"lModules": lModNames}
        sIndexText = pathIndex.read_text()
        sPathConf = ison.run.Run(
            xData=sIndexText,
            dicConstVars=dicVars,
            sResultKey="result",
            sImportPath=pathDocMain.as_posix(),
        )
        print(">> Index written to: {}".format(sPathConf))
        print("")

        print("===================================================")
        print("Building main documentation...")

        util.ExecShellCmd(
            sCmd="sphinx-build -M {} source build".format(sOutputType),
            sCwd=pathDocMain.as_posix(),
            pathVirtEnv=pathEnv,
            bDoPrint=True,
            bDoPrintOnError=True,
            sPrintPrefix=">> ",
        )

        # pathDocBuild = pathDocMain / "build"
        # pathDocTrg = pathSetup / "src" / "catharsys" / "setup" / "dist" / "docs"
        # if pathDocTrg.exists():
        #     shutil.rmtree(pathDocTrg.as_posix())
        # # endif
        # pathDocTrg.mkdir(parents=True)
        # print("Copying documentation to: {}".format(pathDocTrg.as_posix()))
        # util.CopyFiles(pathSrc=pathDocBuild, pathTrg=pathDocTrg)

    # endif


# enddef
