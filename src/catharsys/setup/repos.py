#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \repos.py
# Created Date: Wednesday, May 24th 2023, 1:13:11 pm
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

import yaml
import json
from tqdm import tqdm
from pathlib import Path
from dataclasses import dataclass
from git import Repo, FetchInfo, RemoteProgress

from catharsys.setup import util


# #####################################################################################################
@dataclass
class CRepoData:
    sName: str = None
    sType: str = None
    sUrl: str = None
    sVersion: str = None


# endclass


# #####################################################################################################
class ProgressPrinter(RemoteProgress):
    def __init__(self):
        super().__init__()
        self._xBar: tqdm = None

    # enddef

    def update(self, op_code, cur_count, max_count=None, message=""):
        if (op_code & 1) != 0:
            self._xBar = tqdm(total=int(max_count))
        elif (op_code & 2) != 0:
            if self._xBar is not None:
                self._xBar.close()
                self._xBar = None
            # endif
        # endif

        if self._xBar is not None:
            self._xBar.update(int(cur_count))
        # endif

        # print(
        #     op_code,
        #     cur_count,
        #     max_count,
        #     cur_count / (max_count or 100.0),
        #     message or "NO MESSAGE",
        # )

    # enddef


# end


# #####################################################################################################
# Load repository data listed in repository listing file
def LoadRepoListFile(*, _pathRepoList: Path) -> list[CRepoData]:
    if not _pathRepoList.exists():
        raise RuntimeError(f"Repository list file not found: {(_pathRepoList.as_posix())}")
    # endif

    lRepos: list = []

    if _pathRepoList.suffix in [".yaml", ".yml"]:
        with _pathRepoList.open("r") as xFile:
            dicYaml = yaml.load(xFile, Loader=yaml.Loader)
            dicRepoList = dicYaml.get("repositories")
            for sRepo in dicRepoList:
                dicRepo = dicRepoList[sRepo]
                lRepos.append(
                    CRepoData(
                        sName=sRepo, sType=dicRepo.get("type"), sUrl=dicRepo.get("url"), sVersion=dicRepo.get("version")
                    )
                )
            # endfor
        # endwith

    elif _pathRepoList.suffix == ".json":
        with _pathRepoList.open("r") as xFile:
            dicRepoCln = json.load(xFile)
        # endwith
        # anycfg.Load(_pathRepoList, sDTI="/catharsys/system/repository-collection:1")
        sDti = dicRepoCln.get("sDTI")
        if sDti is None:
            raise RuntimeError(f"Repository list file has no element 'sDTI': {(_pathRepoList.as_posix())}")
        # endif
        if not sDti.startswith("/catharsys/system/repository-collection:1"):
            raise RuntimeError(f"Repository list file has unsupported DTI: {(_pathRepoList.as_posix())}")
        # endif

        dicRepoList = dicRepoCln.get("mRepositories")
        for sRepo in dicRepoList:
            dicRepo = dicRepoList[sRepo]
            lRepos.append(
                CRepoData(
                    sName=sRepo, sType=dicRepo.get("sType"), sUrl=dicRepo.get("sUrl"), sVersion=dicRepo.get("sVersion")
                )
            )
        # endfor

    else:
        raise RuntimeError(
            f"Unsupported repository list file type '{_pathRepoList.suffix}': {(_pathRepoList.as_posix())}"
        )
    # endif

    return lRepos


# enddef


# #####################################################################################################
def ProvideReposPath(_pathRepos: Path = None, *, _bDoRaise=True) -> Path:
    if not isinstance(_pathRepos, Path):
        pathRepoClnTrg: Path = util.TryGetReposPath()
        if pathRepoClnTrg is None:
            if _bDoRaise is True:
                raise RuntimeError("Repository path only available in develop install")
            else:
                return None
            # endif
        # endif

    else:
        pathRepoClnTrg = _pathRepos
        if not pathRepoClnTrg.exists():
            if _bDoRaise is True:
                raise RuntimeError(f"Repository path does not exist: {(pathRepoClnTrg.as_posix())}")
            else:
                return None
            # endif
        # endif
    # endif

    return pathRepoClnTrg


# endif


# #####################################################################################################
def CloneFromRepoListFile(
    *,
    _pathRepoList: Path,
    _pathRepos: Path = None,
    _bPullIfExists: bool = False,
    _bDoPrint: bool = True,
    _sPrintPrefix: str = ">> ",
):
    pathRepoClnTrg = ProvideReposPath(_pathRepos)
    lRepos = LoadRepoListFile(_pathRepoList=_pathRepoList)

    xRepo: CRepoData
    for xRepo in lRepos:
        try:
            if xRepo.sType == "git":
                pathRepoTrg = pathRepoClnTrg / xRepo.sName
                if pathRepoTrg.exists():
                    if _bPullIfExists is True:
                        PullRepo(pathRepoTrg, _bDoPrint=_bDoPrint, _sPrintPrefix=_sPrintPrefix)
                    elif _bDoPrint is True:
                        print(
                            f"WARNING: Target cloning folder already exists for repository "
                            f"'{xRepo.sName}': {(pathRepoTrg.as_posix())}"
                        )
                    # endif
                else:
                    if _bDoPrint is True:
                        print(f"{_sPrintPrefix}Cloning repository '{xRepo.sName}' from: {xRepo.sUrl}")
                    # endif
                    Repo.clone_from(
                        xRepo.sUrl, pathRepoTrg.as_posix(), branch=xRepo.sVersion, progress=ProgressPrinter()
                    )
                # endif
            else:
                raise RuntimeError(f"Unsupported version control system '{xRepo.sType}' for repository '{xRepo.sName}'")
            # endif
        except Exception as xEx:
            print(f"ERROR cloning repository '{xRepo.sName}':\n{(str(xEx))}")
        # endtry

    # endfor


# enddef


# #####################################################################################################
def GetAvailRepoList(_pathRepos: Path = None) -> list[Path]:
    pathRepoClnTrg = ProvideReposPath(_pathRepos)

    lRepos: list[Path] = []
    pathRepo: Path
    for pathRepo in pathRepoClnTrg.iterdir():
        if not pathRepo.is_dir():
            continue
        # endif
        if not (pathRepo / ".git").exists():
            continue
        # endif

        lRepos.append(pathRepo)
    # endfor

    return lRepos


# enddef


# #####################################################################################################
def PullRepoCln(*, _pathRepos: Path = None, _bDoPrint: bool = True, _sPrintPrefix: str = ">> "):
    lRepos = GetAvailRepoList(_pathRepos)
    for pathRepo in lRepos:
        PullRepo(pathRepo, _bDoPrint=_bDoPrint, _sPrintPrefix=_sPrintPrefix)
        if _bDoPrint is True:
            print("")
        # endif
    # endfor


# enddef


# #####################################################################################################
def PullMain(*, _pathRepos: Path = None, _bDoPrint: bool = True, _sPrintPrefix: str = ">> ") -> bool:
    pathRepoClnTrg = ProvideReposPath(_pathRepos)

    pathRepo: Path = pathRepoClnTrg.parent
    pathGit = pathRepo / ".git"
    if not pathGit.exists():
        if _bDoPrint is True:
            print(f"WARNING: Main install path is not a repository: {(pathRepo.as_posix())}")
        # endif
        return False
    # endif

    PullRepo(pathRepo, _bDoPrint=_bDoPrint, _sPrintPrefix=_sPrintPrefix)
    if _bDoPrint is True:
        print("")
    # endif


# enddef


# #####################################################################################################
def PullRepo(_pathRepo: Path, *, _bDoPrint: bool = True, _sPrintPrefix: str = ">> "):
    try:
        repoX = Repo(_pathRepo.as_posix())
        remX = repoX.remote("origin")
        sActiveBranch = repoX.active_branch

        if _bDoPrint is True:
            print(f"{_sPrintPrefix}[{_pathRepo.name}]: Pulling branch '{sActiveBranch}'")
        # endif

        xInfo: FetchInfo
        for xInfo in remX.pull(refspec=sActiveBranch, progress=ProgressPrinter()):
            if _bDoPrint is True:
                print(f"{_sPrintPrefix}{_sPrintPrefix}ref: {xInfo.ref}, commit: {xInfo.commit}")
            # endif
        # endfor
    except Exception as xEx:
        sError = str(xEx)
        print(f"ERROR pulling branch '{sActiveBranch}' from repository '{_pathRepo.name}':\n{sError}")
    # endtry


# enddef
