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


import re
import os
import sys
import platform
from pathlib import Path


g_pathThis: Path = None
g_pathSetup: Path = None
g_pathModules: Path = None

###############################################################################################
# Prepare Environment
try:
    g_pathThis = Path(__file__).absolute()
    g_pathSetup = g_pathThis.parent.parent
    g_pathModules = g_pathThis.parent.parent / "src" / "catharsys" / "setup"
    if not g_pathModules.exists():
        print("ERROR: Cannot find setup module path: {}".format(g_pathModules.as_posix()))
        sys.exit(1)
    # endif

    sPathModules = g_pathModules.as_posix()
    if sPathModules not in sys.path:
        sys.path.insert(0, sPathModules)
    # endif

    try:
        import shell, conda
    except Exception as xEx:
        raise RuntimeError(
            "ERROR: Cannot import modules 'shell' and 'util' from path: {}\n{}\n".format(
                g_pathModules.as_posix(), str(xEx)
            )
        )
    # endtry

    pathShell = Path(shell.__file__).parent
    if pathShell.as_posix() != g_pathModules.as_posix():
        raise RuntimeError(
            "ERROR: module 'shell' loaded from incorrent path:\n"
            + "> expected: {}\n".format(g_pathModules.as_posix())
            + "> loaded from: {}\n".format(pathShell.as_posix())
        )
    # endif

    # pathUtil = Path(util.__file__).parent
    # if pathUtil.as_posix() != g_pathModules.as_posix():
    #     raise RuntimeError("ERROR: module 'util' loaded from incorrent path:\n"
    #                        + "> expected: {}\n".format(g_pathModules.as_posix())
    #                        + "> loaded from: {}\n".format(pathUtil.as_posix()))
    # # endif

except Exception as xEx:
    print("ERROR initializing catharsys install environment:\n{}\n".format(str(xEx)))
    sys.exit(1)
# endtry

###############################################################################################
# Functions


def RunCmd_Install(_xArgs):
    global g_pathSetup

    conda.Install(
        sEnvName=_xArgs.env_name[0],
        pathSetup=g_pathSetup,
        sDevelopReposFile=_xArgs.develop,
        bEnvOnly=_xArgs.env_only,
        bForceInstall=_xArgs.force_install,
        sShellInitScript=_xArgs.shell_init_script[0],
    )


# enddef


###############################################################################################
# Main function
def RunCli():
    try:
        import argparse

        parseMain = argparse.ArgumentParser(prog="cathy-conda", description="Catharsys Conda Environment install")
        parseMain.add_argument("--debug", dest="debug", action="store_true", default=False)
        parseMain.set_defaults(funcCmd=None)

        parseSub = parseMain.add_subparsers()

        parseCreate = parseSub.add_parser("install", help="create a conda environment and install catharsys")
        parseCreate.add_argument("env_name", nargs=1)
        parseCreate.add_argument("--develop", dest="develop", nargs="?", const="__default__", default=None)
        parseCreate.add_argument("--shell-init-script", dest="shell_init_script", nargs=1, default=[None])
        parseCreate.add_argument("--env-only", dest="env_only", action="store_true", default=False)
        parseCreate.add_argument("--force", dest="force_install", action="store_true", default=False)
        parseCreate.set_defaults(funcCmd=RunCmd_Install)

        xArgs = parseMain.parse_args()
    except Exception as xEx:
        print("ERROR parsing runtime arguments:\n{}\n".format(str(xEx)))
        sys.exit(1)
    # endtry

    try:
        if xArgs.funcCmd is None:
            parseMain.print_help()
            sys.exit(1)
        # endif

        # Call selected command function
        xArgs.funcCmd(xArgs)
    except Exception as xEx:
        print("ERROR running conda install:\n{}\n".format(str(xEx)))
        # util.PrintException("Error running conda install", xEx, bTraceback=xArgs.debug)
        sys.path.remove(sPathModules)
        sys.exit(1)
    # endtry

    sys.exit(0)


# enddef


if __name__ == "__main__":
    RunCli()
# endif
