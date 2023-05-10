#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \except_util.py
# Created Date: Monday, June 13th 2022, 8:35:55 am
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

from typing import Optional
import traceback


####################################################################
def PrintException(
    *, xEx: Exception, sMsg: Optional[str] = None, bTraceback: bool = False
):

    try:
        from anybase.cls_any_error import CAnyError

        CAnyError.Print(xEx, sMsg=sMsg, bTraceback=bTraceback)

    except Exception:
        print("")
        print("===================================================================")
        if sMsg is not None:
            print(f"ERROR: {sMsg}")
        else:
            print("ERROR")
        # endif
        print(xEx)
        print("")
        if bTraceback:
            print("EXCEPTION ({0})".format(type(xEx)))
            traceback.print_exception(type(xEx), xEx, xEx.__traceback__)
        # endif
        print("===================================================================")
        print("")


# enddef
