#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \version.py
# Created Date: Thursday, June 2nd 2022, 11:21:05 am
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


__version__ = "3.2.29"


def AsString() -> str:
    return __version__


# enddef


def AsList() -> list:
    return __version__.split(".")


# enddef


def AsIntList() -> list[int]:
    return [int(x) for x in AsList()]


# enddef


def MajorAsString() -> str:
    return AsList()[0]


# enddef


def MajorMinorAsString() -> str:
    return ".".join(AsList()[0:2])


# enddef
