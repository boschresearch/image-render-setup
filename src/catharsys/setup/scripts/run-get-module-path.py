#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \run-get-module-path.py
# Created Date: Wednesday, May 4th 2022, 12:01:58 pm
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
import importlib

lArgv = sys.argv
try:
    lArgv = lArgv[lArgv.index("--") + 1 :]
    if len(lArgv) >= 1:
        bValidCall = True
    else:
        sMsg = "Expect name(s) of modules."
    # endif

except ValueError:
    sMsg = "No or invalid command line arguments given."
# endtry

if not bValidCall:
    raise Exception("Invalid call: {0}".format(sMsg))
# endif

for sModule in lArgv:
    try:
        modX = importlib.import_module(sModule)
        sPath = modX.__file__
    except Exception:
        sPath = ""
    # endtry

    sys.stdout.write("{}\n".format(sPath))
# endfor
