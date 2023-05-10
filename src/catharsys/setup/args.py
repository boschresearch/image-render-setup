#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \args.py
# Created Date: Monday, June 13th 2022, 8:18:58 am
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

# import time
from importlib.metadata import entry_points as EntryPoints
from typing import Callable, NamedTuple, Optional


####################################################################
class CCmdArgSplit(NamedTuple):
    lArgs: list[str]
    lRemainder: list[str]
    bHasSubCommand: bool


# endclass

####################################################################
class CCommandSet:
    def __init__(self, _sCommandSetName: str):
        self._sCommandSetName = _sCommandSetName

        # print(f"Loading entry points for: {_sCommandSetName}")
        # find available commands
        self._clnEpGrp = EntryPoints().select(group=_sCommandSetName)
        if len(self._clnEpGrp) == 0:
            raise RuntimeError(f"No commands available for group '{_sCommandSetName}'")
        # endif

        self._dicCmdSet = {}
        self._setCmdNames = set()
        for epCmd in self._clnEpGrp:
            # It seems that sometimes entry points are listed multiple times.
            # Maybe just a bug of pip or the metadata lib.
            # So, ensure here that each entry point is only scanned once.
            if epCmd.name in self._setCmdNames:
                continue
            # endif
            self._setCmdNames.add(epCmd.name)
            self._dicCmdSet[epCmd.name] = epCmd
        # endfor
        # print("done")

    # enddef

    @property
    def sName(self) -> str:
        return self._sCommandSetName

    # enddef

    @property
    def xEntryPoints(self) -> EntryPoints:
        return self._clnEpGrp

    # enddef

    @property
    def setCmdNames(self) -> set:
        return self._setCmdNames

    # enddef

    @property
    def dicCmd(self) -> dict:
        return self._dicCmdSet

    # enddef


# endclass


####################################################################
def GetCurrentCmdArgs(*, _lArgs: list[str], _xCmdSet: CCommandSet) -> CCmdArgSplit:

    lCmdArgs: list = []
    lRemainder: list = []
    bHasSubCommand: bool = False

    for iIdx, sArg in enumerate(_lArgs):
        lCmdArgs.append(sArg)
        if sArg in _xCmdSet.setCmdNames:
            lRemainder = _lArgs[iIdx + 1 :]
            bHasSubCommand = True
            break
        # endif
    # endfor arguments

    return CCmdArgSplit(lCmdArgs, lRemainder, bHasSubCommand)


# enddef

####################################################################
def AddCommandSetArgs(*, _parseMain, _xCmdSet: CCommandSet):  #: argparse.ArgumentParser,

    parseSub = _parseMain.add_subparsers()

    for sCmdName in _xCmdSet.setCmdNames:
        parseCmd = parseSub.add_parser(sCmdName)
        parseCmd.set_defaults(epCmd=_xCmdSet.dicCmd[sCmdName], sCmdName=sCmdName, parseCmd=parseCmd)
    # endfor


# enddef


####################################################################
def RunSubCommand(*, _argsCmd, _lArgs):

    if not hasattr(_argsCmd, "epCmd"):
        raise RuntimeError("Sub-command entry point not set")
    # endif

    try:
        modCmd = _argsCmd.epCmd.load()
    except Exception as xEx:
        raise RuntimeError(f"Error loading module for command {_argsCmd.sCmdName}: {(str(xEx))}")
    # endtry

    if not hasattr(modCmd, "RunCmd"):
        raise RuntimeError(f"Module for command '{_argsCmd.sCmdName}' has no function 'RunCmd()'")
    # endif

    modCmd.RunCmd(_argsCmd, _lArgs)


# enddef


####################################################################
def ProcessSubCommands(*, _argsCmd, _lArgs: list[str], _xCmdSet: CCommandSet) -> bool:

    # Get list of arguments for this command and the remainder
    xCmdArgSplit = GetCurrentCmdArgs(_lArgs=_lArgs, _xCmdSet=_xCmdSet)
    # Parse the arguments for this command
    argsSubCmd = _argsCmd.parseCmd.parse_args(xCmdArgSplit.lArgs, _argsCmd)

    # if a sub-command has been specified, the run the sub-command
    if xCmdArgSplit.bHasSubCommand is True:
        RunSubCommand(_argsCmd=argsSubCmd, _lArgs=xCmdArgSplit.lRemainder)
        return True
    else:
        return False
    # endif


# enddef


####################################################################
def RunCmdGroup(*, _argsCmd, _lArgs: list, _sCommandGroupName: str, _funcAddArgs: Optional[Callable] = None):

    if len(_lArgs) == 0:
        _argsCmd.parseCmd.print_help()

    else:
        if _funcAddArgs is not None:
            _funcAddArgs(_argsCmd.parseCmd)
        # endif

        xCmdSet = CCommandSet(_sCommandGroupName)
        AddCommandSetArgs(_parseMain=_argsCmd.parseCmd, _xCmdSet=xCmdSet)

        bHasSubCommand = ProcessSubCommands(_argsCmd=_argsCmd, _lArgs=_lArgs, _xCmdSet=xCmdSet)
        if bHasSubCommand is False:
            _argsCmd.parseCmd.print_help()
        # endif
    # endif


# enddef


####################################################################
def ParseCmdArgs(*, _argsCmd, _lArgs: list, _funcAddArgs: Optional[Callable] = None):

    if _funcAddArgs is not None:
        _funcAddArgs(_argsCmd.parseCmd)
    # endif

    return _argsCmd.parseCmd.parse_args(_lArgs, _argsCmd)


# enddef
