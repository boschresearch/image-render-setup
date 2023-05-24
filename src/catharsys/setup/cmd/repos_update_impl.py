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


from typing import Optional, Union
from pathlib import Path

from anybase.cls_any_error import CAnyError, CAnyError_Message
from catharsys.setup import repos, util


####################################################################
class CRepoError(CAnyError_Message):
    def __init__(self, *, sMsg: str, xChildEx: Optional[Exception] = None):
        super().__init__(sMsg=sMsg, xChildEx=xChildEx)

    # enddef


# endclass


####################################################################
def Run():
    pathRepos = util.TryGetReposPath()
    if pathRepos is None:
        raise RuntimeError("Repositories can only be updated from develop install")
    # endif

    # sBranchMain = "stable"
    # sBranchDev = "main"

    repos.PullMain()
    repos.PullRepoCln()


# enddef
