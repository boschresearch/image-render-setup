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


g_sCmdDesc = "Releases the Catharsys repositories"


####################################################################
def AddArgParseArguments(_parseArgs):
    _parseArgs.add_argument("-m", "--modules", dest="modules", nargs="*", default=[])
    _parseArgs.add_argument("--execute", dest="do_execute", action="store_true", default=False)
    _parseArgs.add_argument("--push", dest="do_push", action="store_true", default=False)
    _parseArgs.add_argument(
        "--main",
        dest="do_main",
        action="store_true",
        default=False,
        help="Release main image render setup repository",
    )
    _parseArgs.add_argument(
        "--type",
        dest="type",
        nargs=1,
        choices=["major", "minor", "rev"],
        default=["rev"],
    )


# enddef


####################################################################
def RunCmd(_argsCmd, _lArgs):
    from catharsys.setup.cmd.repos_release_impl import Run
    from catharsys.setup import args

    argsSubCmd = args.ParseCmdArgs(_argsCmd=_argsCmd, _lArgs=_lArgs, _funcAddArgs=AddArgParseArguments)

    iVerPart = ["major", "minor", "rev"].index(argsSubCmd.type[0])

    Run(
        lModules=argsSubCmd.modules,
        bDoExecute=argsSubCmd.do_execute,
        bDoPush=argsSubCmd.do_push,
        bDoMain=argsSubCmd.do_main,
        iVerPart=iVerPart,
    )


# enddef
