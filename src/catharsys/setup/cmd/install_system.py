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

g_sCmdDesc = "Installs the Catharsys modules"


####################################################################
def AddArgParseArguments(_xArgParser):
    _xArgParser.add_argument("--force-dist", dest="force_dist", action="store_true", default=False)
    _xArgParser.add_argument("--force", dest="force_install", action="store_true", default=False)
    _xArgParser.add_argument("--vscode-addons", dest="vscode_addons_only", action="store_true", default=False)
    _xArgParser.add_argument("--sdist", dest="sdist", action="store_true", default=False)
    _xArgParser.add_argument("--update", dest="update", action="store_true", default=False)
    _xArgParser.add_argument("--docs", dest="docs", nargs="*", default=None)
    _xArgParser.add_argument("--repos", dest="repos", nargs=1, default=[None])


# enddef


####################################################################
def RunCmd(_argsCmd, _lArgs):
    import catharsys.setup.cmd.install_system_impl as impl
    from catharsys.setup import args

    argsSubCmd = args.ParseCmdArgs(_argsCmd=_argsCmd, _lArgs=_lArgs, _funcAddArgs=AddArgParseArguments)

    impl.Run(
        bForceDist=argsSubCmd.force_dist,
        bForceInstall=argsSubCmd.force_install,
        bVsCodeAddOnsOnly=argsSubCmd.vscode_addons_only,
        bSourceDist=argsSubCmd.sdist,
        lDocFiles=argsSubCmd.docs,
        sReposFile=argsSubCmd.repos[0],
        bUpdate=argsSubCmd.update,
    )


# enddef
