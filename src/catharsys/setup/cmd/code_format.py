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

from anybase.dec.cls_const_keyword_namespace import constKeywordNamespace

g_sCmdDesc = "formatting some code catharsys coding convention for the catharsys modules inside repo folder"


@constKeywordNamespace
class NsKeys:
    code_blocks: str
    verbose: str
    file: str
    folder: str
    recursive: str


####################################################################
def AddArgParseArguments(_xArgParser):

    _xArgParser.add_argument(
        "--code-blocks",
        dest=NsKeys.code_blocks,
        action="store_true",
        default=False,
        help="coding convention requires for each structural element a closing #end  if/for/try.....",
    )

    _xArgParser.add_argument(
        "-v",
        "--verbose",
        dest=NsKeys.verbose,
        action="store_true",
        default=False,
        help="shows the changes that will be done",
    )

    _xArgParser.add_argument(
        "--file",
        nargs="+",
        dest=NsKeys.file,
        default=None,
        help="use only that file for coding convention formatting",
    )

    _xArgParser.add_argument(
        "--folder",
        nargs="+",
        dest=NsKeys.folder,
        default=None,
        help="use only that folder and any python (*.py) file for coding convention formatting",
    )

    _xArgParser.add_argument(
        "--recursive",
        dest=NsKeys.recursive,
        action="store_true",
        default=False,
        help="when folder given go recursively into sub-folders",
    )


# enddef

####################################################################
def RunCmd(_argsCmd, _lArgs):
    from . import code_format_impl as impl
    from catharsys.setup import args

    argsSubCmd = args.ParseCmdArgs(_argsCmd=_argsCmd, _lArgs=_lArgs, _funcAddArgs=AddArgParseArguments)

    impl.RunFormat(
        _bCodeBlocks=argsSubCmd.code_blocks,
        _bVerbose=argsSubCmd.verbose,
        _lsFilename=argsSubCmd.file,
        _lsFolder=argsSubCmd.folder,
        _bFolderRecursive=argsSubCmd.recursive,
    )


# enddef
