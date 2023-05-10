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


g_sCmdDesc = "Builds the Catharsys documentation"


####################################################################
def AddArgParseArguments(_parseArgs):
    _parseArgs.add_argument("output_type", nargs="?", default="html")
    _parseArgs.add_argument("-I", "--install", dest="install", action="store_true", default=False)
    _parseArgs.add_argument("-M", "--modules-only", dest="modules_only", action="store_true", default=False)
    _parseArgs.add_argument("-N", "--main-only", dest="main_only", action="store_true", default=False)
    _parseArgs.add_argument("-m", "--modules", dest="modules", nargs="*", default=[])


# enddef


####################################################################
def RunCmd(_argsCmd, _lArgs):
    from catharsys.setup.cmd import build_docs_impl as impl
    from catharsys.setup import args

    argsSubCmd = args.ParseCmdArgs(_argsCmd=_argsCmd, _lArgs=_lArgs, _funcAddArgs=AddArgParseArguments)

    impl.Run(
        sOutputType=argsSubCmd.output_type,
        bInstall=argsSubCmd.install,
        bModulesOnly=argsSubCmd.modules_only,
        bMainOnly=argsSubCmd.main_only,
        lModules=argsSubCmd.modules,
    )


# enddef


####################################################################
def RunCli():
    import sys
    import argparse
    from catharsys.setup import except_util

    try:
        xArgParse = argparse.ArgumentParser(description="Build Catharsys Documentation")
        xArgParse.add_argument("--debug", dest="debug", action="store_true", default=False)
        AddArgParseArguments(xArgParse)
        xArgs = xArgParse.parse_args()
    except Exception as xEx:
        print("ERROR parsing runtime arguments:\n{}\n".format(str(xEx)))
        sys.exit(1)
    # endtry

    try:
        RunCmd(xArgs)
    except Exception as xEx:
        except_util.PrintException(sMsg="Error running documentation build", xEx=xEx, bTraceback=xArgs.debug)
        sys.exit(1)
    # endtry

    sys.exit(0)


# enddef


####################################################################
if __name__ == "__main__":
    RunCli()
# endif
