#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \start.py
# Created Date: Thursday, May 5th 2022, 11:51:37 am
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


g_sCmdDesc: str = "Repository commands"


####################################################################
def AddArgParseArguments(_parseArgs):
    # from catharsys.setup import args
    # No additional arguments apart from sub-commands
    pass


# enddef


####################################################################
def RunCmd(_argsCmd, _lArgs):
    from catharsys.setup import args

    args.RunCmdGroup(_argsCmd=_argsCmd, _lArgs=_lArgs, _sCommandGroupName="catharsys.commands.repos")


# enddef
