#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \dev_repos.py
# Created Date: Wednesday, May 24th 2023, 2:19:03 pm
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

from pathlib import Path
from catharsys.setup import repos

pathRepos = repos.ProvideReposPath()
print(pathRepos)

pathReposListFile = pathRepos / "repos-main.yaml"
lRepos = repos.LoadRepoListFile(_pathRepoList=pathReposListFile)
# print(lRepos)

pathRepoCln = Path(r"C:\Users\prc2hi\Documents\10_Code\tmp\repos")
# repos.CloneRepoListFile(_pathRepoList=pathReposListFile, _pathRepos=pathRepoCln)

repos.PullAll(_pathRepos=pathRepoCln)
