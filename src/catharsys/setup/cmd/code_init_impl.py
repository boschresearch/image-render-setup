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
import json
from pathlib import Path

if sys.version_info < (3, 10):
    import importlib_resources as res
else:
    from importlib import resources as res
# endif
import platform

import catharsys.setup
from catharsys.setup import module, conda

from anybase import file as anyfile


####################################################################
def GetRepoPaths() -> list[Path]:
    lPathModules: list[Path] = []

    def CreateHandler_GetRepoPath(_lPathModules):
        def Handler(*, pathModule, pathRepos):
            _lPathModules.append(pathModule)

        # enddef
        return Handler

    # enddef

    module.ForEach(funcRunRepo=CreateHandler_GetRepoPath(lPathModules))

    return lPathModules


# enddef


####################################################################
def Run(*, sPathWorkspace=None, sPrintPrefix=">> "):
    try:
        from catharsys.config.cls_project import CProjectConfig
    except Exception:
        print(
            "ERROR: It seems module 'image-render-automation' is not installed."
            "       Please run 'cathy install' before using this command."
        )
    # endtry

    if sPathWorkspace is None:
        pathWS = Path.cwd()
    else:
        pathWS = Path(sPathWorkspace)
    # endif

    pathSetupCfg = pathWS / "setup.cfg"
    bIsCodeWs = pathSetupCfg.exists()

    if bIsCodeWs is True:
        print(f"{sPrintPrefix}Initializing VSCode for python module at path: {(pathWS.as_posix())}")
    else:
        print("{}Initializing VSCode for workspace at path: {}".format(sPrintPrefix, pathWS.as_posix()))

        pathConfig = pathWS / "config"
        if not pathConfig.exists():
            raise RuntimeError("Configuration folder 'config' not found in workspace: {}".format(pathConfig.as_posix()))
        # endif

        ##############################################################################
        # Search for launch files
        lLaunchFiles = [
            x
            for x in pathConfig.rglob("launch.*")
            if (x.is_file() and ".vscode" not in x.as_posix() and x.suffix in [".json", ".json5", ".ison"])
        ]

        # Get list of valid project configurations in workspace
        lPrjCfg: list[CProjectConfig] = []
        for pathLaunchFile in lLaunchFiles:
            xPrjCfg = CProjectConfig()
            try:
                xPrjCfg.FromLaunchPath(pathLaunchFile)
            except Exception as xEx:
                print(
                    "{}! Invalid launch file for configuraton: {}\n{}\n".format(
                        sPrintPrefix, pathLaunchFile.as_posix(), str(xEx)
                    )
                )
            # endtry
            lPrjCfg.append(xPrjCfg)
        # endfor

        # Print valid configurations found
        print(f"{sPrintPrefix}Configurations found:")
        for xPrjCfg in lPrjCfg:
            print("{}- {}".format(sPrintPrefix, xPrjCfg.sLaunchFolderName))
        # endfor

    # endif

    ##############################################################################
    lPathModules = GetRepoPaths()
    bIsDevelop = len(lPathModules) > 0

    dicWS = {}

    bHasPwd = False
    lFolders = dicWS["folders"] = []
    for pathModule in lPathModules:
        if pathModule.is_relative_to(pathWS):
            sPath = pathModule.relative_to(pathWS).as_posix()
            if sPath == ".":
                bHasPwd = True
            # endif
        else:
            sPath = pathModule.as_posix()
        # endif

        lFolders.append({"path": sPath})
    # endfor

    if bHasPwd is False:
        lFolders.append({"path": "."})
    # endif

    if bIsDevelop is True:
        ##############################################################################
        # add default settings if this is a develop workspace
        xSettings = res.files(catharsys.setup).joinpath("data").joinpath("default-settings.json")
        with res.as_file(xSettings) as pathSettings:
            dicSettings = anyfile.LoadJson(pathSettings)
            dicWS["settings"] = dicSettings
            # dicWS["settings"] = json.loads(pathSettings.read_text())
        # endwith

        ##############################################################################
        # Launch configuration for debugging
        dicWS["launch"] = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Current Python File",
                    "type": "python",
                    "request": "launch",
                    "program": "${file}",
                    "args": ["--debug"],
                    "cwd": f"${{workspaceFolder:{pathWS.name}}}",
                    "console": "integratedTerminal",
                    "justMyCode": True,
                    "subProcess": True,
                }
            ],
        }
    else:
        dicWS["launch"] = {}
        dicWS["settings"] = {}
    # endif

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

    print(f"{sPrintPrefix}Using conda environemnt '{sCondaEnv}' as default environment for VSCode")

    # Write conda env Settings for Catharsys Painkiller preconfiguration in generated workspaces
    dicWS["settings"].update({"Image-Render-Automation.condaenv": sCondaEnv})

    pathWsCath = pathWS / ".catharsys" / sCondaEnv
    pathWsCath.mkdir(parents=True, exist_ok=True)

    lActCmdsLinux = conda.GetShellActivateCommands(sCondaEnv, sSystem="Linux")

    # Only create windows shell script, if we are in Windows, because
    # GetShellActivateCommands() looks for files that only exist in Windows
    if platform.system() == "Windows":
        lActCmdsWindows = conda.GetShellActivateCommands(sCondaEnv, sSystem="Windows")
        pathWsCathPs = pathWsCath / "init-shell.ps1"
        pathRelCathPs = pathWsCathPs.relative_to(pathWS)
        sRelPathCathPs = str(pathRelCathPs)

        sPsScript = 'param (\n\t[string]$Command = ""\n)\n\n'
        sPsScript += "\n".join(lActCmdsWindows)
        sPsScript += (
            "\n\n"
            "if (![string]::IsNullOrWhitespace($Command)) {\n"
            '\tinvoke-expression -Command "$Command $args"\n'
            "\texit\n}\n"
        )
        pathWsCathPs.write_text(sPsScript)
        dicWS["settings"].update(
            {
                "terminal.integrated.profiles.windows": {
                    "Catharsys PS": {
                        "source": "PowerShell",
                        "icon": "terminal-powershell",
                        "args": [
                            "-ExecutionPolicy",
                            "ByPass",
                            "-NoExit",
                            "-Command",
                            f"${{workspaceFolder:{pathWS.name}}}\\{sRelPathCathPs}",
                        ],
                    }
                },
                "terminal.integrated.defaultProfile.windows": "Catharsys PS",
            }
        )
    # endif

    # Always create Linux shell script
    pathWsCathBash = pathWsCath / "init-shell.sh"
    pathRelCathBash = pathWsCathBash.relative_to(pathWS)
    sRelPathCathBash = pathRelCathBash.as_posix()

    sBashScript = "source ~/.bashrc\n" + "\n".join(lActCmdsLinux) + "\n"
    pathWsCathBash.write_text(sBashScript)

    dicWS["settings"].update(
        {
            "terminal.integrated.profiles.linux": {
                "Catharsys Bash": {
                    "path": "/bin/bash",
                    "args": [
                        "--init-file",
                        f"${{workspaceFolder:{pathWS.name}}}/{sRelPathCathBash}",
                    ],
                }
            },
            "terminal.integrated.defaultProfile.linux": "Catharsys Bash",
        }
    )

    dicWS["settings"].update(
        {
            # Ensure that conda environment set by scripts above, is not overwritten by VSCode
            "python.terminal.activateEnvironment": False,
            # Ensure that all commit messages contain a "signed-off-by" line.
            "git.alwaysSignOff": True,
        }
    )

    ##############################################################################
    # write workspace file
    sName = pathWS.name
    if bIsCodeWs is False and sName.startswith("image-render-"):
        sName = sName[len("image-render-") :]
    # endif

    sCodeWsName = f"{sName}-{sCondaEnv}.code-workspace"
    pathCodeWs = pathWS / sCodeWsName

    with pathCodeWs.open("w") as xFile:
        json.dump(dicWS, xFile, indent=4)
    # endwith
    print(f"{sPrintPrefix}VSCode workspace file written to: {pathCodeWs.as_posix()}")


# enddef
