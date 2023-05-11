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


import re
import yaml
import shutil
from typing import Optional, Union
from pathlib import Path

from git import Repo, Commit, Head, Remote

from anybase import file as anyfile
from anybase.cls_any_error import CAnyError, CAnyError_Message
from catharsys.setup import util
from catharsys.setup import module


####################################################################
class CRepoError(CAnyError_Message):
    def __init__(self, *, sMsg: str, xChildEx: Optional[Exception] = None):
        super().__init__(sMsg=sMsg, xChildEx=xChildEx)

    # enddef


# endclass


####################################################################
def FilterPyModules(**kwargs):
    pathModule = kwargs.get("pathModule")

    pathTest = pathModule / "setup.cfg"
    if pathTest.exists():
        return True
    # endif

    pathPackageFile = pathModule / "package.json"
    if not pathPackageFile.exists():
        pathPackageFile = pathModule / "package.json5"
        if not pathPackageFile.exists():
            pathPackageFile = None
        # endif
    # endif

    return pathPackageFile is not None


# enddef


#######################################################6#############
def CannotReleaseFromDist(*, pathDist: Path, pathModule: Path, sName: str, sVersion: str):
    print("===================================================")
    print("Cannot release module from distribution for: {} v{}\n".format(sName, sVersion))


# enddef


####################################################################
def FindHeadForCommit(*, repoMod: Repo, comX: Commit, bLocal: bool = True) -> Head:
    for headX in repoMod.heads:
        if headX.commit == comX:
            return headX
        # endif
    # endfor

    if bLocal is False:
        # find in remotes
        for remX in repoMod.remotes:
            for refX in remX.refs:
                if refX.commit == comX:
                    return refX
            # endfor heads
        # endfor remotes
    # endif

    return None


# enddef


####################################################################
def GetHeadNameForCommit(*, repoMod: Repo, comX: Commit, bLocal: bool = True) -> str:
    headX = FindHeadForCommit(repoMod=repoMod, comX=comX)
    sName = ""
    if headX is not None:
        sName = headX.name
    # endif

    return sName


# enddef


####################################################################
def _RepoTest(*, pathModule):
    sLocalVersion = module.GetRepoVersion(pathModule=pathModule)
    print("Repo: {}, v{}".format(pathModule.name, sLocalVersion))

    repoMod = Repo(pathModule)
    print(repoMod.untracked_files)
    print("Active branch: {}".format(repoMod.active_branch.name))
    print("Heads:")
    for headX in repoMod.heads:
        print("  - {} @{}".format(headX.name, headX.commit))
    # endfor
    print("")

    print("Remotes:")
    for remX in repoMod.remotes:
        print(f"  - {remX.name}")
        for refX in remX.refs:
            print(f"    - {refX.name}")
        # endfor heads
    # endfor remotes
    print("")

    headMaster = repoMod.heads["main"]
    headDev = repoMod.heads["develop"]

    print("Commits before current in {}".format(headDev.name))
    for comX in headDev.commit.parents:
        comY: Commit = comX
        sMsg = comY.message[: min(len(comY.message), 15)]
        print("  - {}: {}".format(comY.name_rev, sMsg))
    # endfor
    print("")

    # comX: Commit = headDev.commit
    # while comX != headMaster.commit:
    #     if len(comX.parents) == 0:
    #         comX = None
    #         break
    #     # endif
    #     comX = comX.parents[0]
    # # endwhile
    # if comX is None:
    #     print("Master head not in develop history")
    # else:
    #     print(f"Last common commit of {headDev.name} and {headMaster.name}:")
    #     print(f" - {comX.name_rev}")
    # # endif
    # print("")

    lComX = repoMod.merge_base(headMaster, headDev)
    if len(lComX) == 0:
        print("No common merge base")
    else:
        comX = lComX[0]
        sName = GetHeadNameForCommit(repoMod=repoMod, comX=comX)
        print("Merge base commit:")
        print(f"  - {comX.name_rev} [{sName}]")

        if comX == headDev.commit:
            print("Master branch more advanced than develop branch")
        elif comX == headMaster.commit:
            print("Can merge Develop into Master")
        else:
            print("Invalid state for merging develop into main")
        # endif
    # endif
    print("")

    # comX: Commit = headDev.commit
    # print("Full dev history")
    # sName = GetHeadNameForCommit(repoMod=repoMod, comX=comX)
    # print(f"{comX.name_rev} ({sName})")
    # while len(comX.parents) > 0:
    #     comX = comX.parents[0]
    #     sName = GetHeadNameForCommit(repoMod=repoMod, comX=comX)
    #     print(f"{comX.name_rev} ({sName})")
    # # endwhile
    # print("")


# enddef


####################################################################
def PrintStdOut(_sStdOut, *, sPrintPrefix: str = ""):
    if len(_sStdOut) == 0:
        return
    # endif

    lStdOut = _sStdOut.split("\n")
    for sLine in lStdOut:
        print(f"{sPrintPrefix}| {sLine}")
    # endfor


# enddef


####################################################################
def GitCheckout(_repoMod: Repo, _sBranch: str, **kwargs):
    sPrintPrefix = kwargs.pop("sPrintPrefix", "")

    print(f"{sPrintPrefix}Switching to branch '{_sBranch}'")
    sStdOut = _repoMod.git.checkout(f"{_sBranch}", **kwargs)
    lStdOut = sStdOut.split("\n")
    for sLine in lStdOut:
        print(f"{sPrintPrefix}| {sLine}")
    # endfor


# enddef


####################################################################
def GetRepoVersion(*, pathModule: Path) -> str:
    pathSetupCfgFile = pathModule / "setup.cfg"

    pathPackageFile = pathModule / "package.json"
    if not pathPackageFile.exists():
        pathPackageFile = pathModule / "package.json5"
        if not pathPackageFile.exists():
            pathPackageFile = None
        # endif
    # endif

    sModuleType: str = None
    sLocalVersion: str = None

    if pathSetupCfgFile.exists():
        sLocalVersion = module.GetRepoVersion(pathModule=pathModule, bGetSource=False)
        sModuleType = "Python Module"

    elif pathPackageFile is not None:
        # print("Build from package.json")
        dicPkg = anyfile.LoadJson(pathPackageFile)

        if isinstance(dicPkg.get("engines"), dict):
            sLocalVersion = dicPkg.get("version")
            sModuleType = "VS-Code AddOn"

        elif isinstance(dicPkg.get("sDTI"), str):
            sLocalVersion = dicPkg.get("sVersion")
            sModuleType = "Workspace"

        else:
            raise CRepoError(sMsg="Unsupported module package file type.")
        # endif
    else:
        CRepoError(sMsg="Unsupported module type.")
    # endif

    return sLocalVersion, sModuleType


# enddef


####################################################################
def IncRepoVersion(*, pathModule: Path, iVerPart: int, bDoExecute=True):
    pathSetupCfgFile = pathModule / "setup.cfg"

    pathPackageFile = pathModule / "package.json"
    if not pathPackageFile.exists():
        pathPackageFile = pathModule / "package.json5"
        if not pathPackageFile.exists():
            pathPackageFile = None
        # endif
    # endif

    sNewVersion: str = None
    sAttrName: str = None
    pathSource: Path = None
    dicPkg: dict = None

    if pathSetupCfgFile.exists():
        sNewVersion, pathSource = module.IncRepoVersion(
            pathModule=pathModule,
            iVerPart=iVerPart,
            bDoExecute=bDoExecute,
            bGetSource=True,
        )

    elif pathPackageFile is not None:
        # print("Build from package.json")
        dicPkg = anyfile.LoadJson(pathPackageFile)

        if isinstance(dicPkg.get("engines"), dict):
            sAttrName = "version"
            # print("VS-Code AddOn: {}, v{}".format(pathModule.name, sLocalVersion))

        elif isinstance(dicPkg.get("sDTI"), str):
            sAttrName = "sVersion"
            # print("Workspace: {}, v{}".format(pathModule.name, sLocalVersion))

        else:
            raise CRepoError(sMsg="Unsupported module package file type.")
        # endif

        sLocalVersion = dicPkg.get(sAttrName)
        if sLocalVersion is None:
            raise CRepoError(sMsg="Version element '{}' not found in: {}".format(sAttrName, pathPackageFile.as_posix()))
        # endif

        xMatch = re.match(r"(\d+)\.(\d+)\.(\d+)", sLocalVersion)
        if xMatch is None:
            raise RuntimeError(f"Invalid version string '{sLocalVersion}' for module '{pathModule.name}'")
        # endif

        lVersion = [0, 0, 0]
        for i in range(3):
            lVersion[i] = int(xMatch.group(i + 1))
        # endfor

        lVersion[iVerPart] += 1
        for i in range(iVerPart + 1, len(lVersion)):
            lVersion[i] = 0
        # endfor

        sNewVersion = ".".join([str(x) for x in lVersion])
        pathSource = pathPackageFile

        if bDoExecute is True:
            dicPkg[sAttrName] = sNewVersion
            anyfile.SaveJson(pathPackageFile, dicPkg, iIndent=4)
        # endif

    else:
        CRepoError(sMsg="Unsupported module type.")
    # endif

    return sNewVersion, pathSource


# enddef


####################################################################
def ReleaseFromRepo(
    *,
    pathRepos: Path,
    pathModule: Path,
    pathSetup: Path,
    bDoExecute: bool,
    bDoPush: bool,
    iVerPart: int,
):
    print("===================================================")
    sResultMsg = "ok"

    try:
        sBranchMain = "main"
        sBranchDev = "develop"

        sLocalVersion, sModuleType = GetRepoVersion(pathModule=pathModule)
        sTagName = f"v{sLocalVersion}"
        print("{}: {}, v{}".format(sModuleType, pathModule.name, sLocalVersion))
        sPrintPrefix = ">> "

        repoMod = Repo(pathModule)

        if repoMod.is_dirty():
            sMsg = "There are modified files in the repository"

            if len(repoMod.untracked_files) > 0:
                sMsg += "\nThere are untracked files in the repository:" + CAnyError.ListToString(
                    repoMod.untracked_files
                )
            # endif

            raise CRepoError(sMsg=sMsg)
        # endif

        if sBranchMain not in repoMod.heads:
            raise CRepoError(sMsg=f"Branch '{sBranchMain}' not found")
        # endif

        if sBranchDev not in repoMod.heads:
            raise CRepoError(sMsg=f"Branch '{sBranchDev}' not found")
        # endif

        headMain: Head = repoMod.heads[sBranchMain]
        headDev: Head = repoMod.heads[sBranchDev]
        headAct: Head = repoMod.active_branch

        bForceReleaseNewVersion = iVerPart == 0 or iVerPart == 1

        if headDev.commit.message.startswith(":cathy:set-version:") and not bForceReleaseNewVersion:
            print(f"{sPrintPrefix}No changes since last release")

        else:
            if headAct != headMain and headAct != headDev:
                raise CRepoError(sMsg=f"Active branch is neither '{headDev.name}' nor '{headMain.name}'")
            # endif

            if bForceReleaseNewVersion is True:
                if headAct != headDev:
                    # Checkout develop branch
                    GitCheckout(repoMod, headDev.name, sPrintPrefix=sPrintPrefix + ">> ")
                # endif

                sNewVersion, pathSource = IncRepoVersion(
                    pathModule=pathModule, iVerPart=iVerPart, bDoExecute=bDoExecute
                )
                print(
                    f"{sPrintPrefix}Incrementing version of module '{pathModule.name}' from '{sLocalVersion}' to '{sNewVersion}'"
                )

                sPathVerFile = pathSource.relative_to(pathModule).as_posix()
                print(f"{sPrintPrefix}Committing version file: {sPathVerFile}")
                if bDoExecute is True:
                    repoMod.index.add([sPathVerFile])
                    repoMod.index.commit(f":cathy:set-version:{sNewVersion}: Increment version to {sNewVersion}")
                # endif

                sLocalVersion = sNewVersion
                sTagName = f"v{sLocalVersion}"
                # After incrementing a major or minor version,
                # increment the revision version for the next commits.
                iVerPart = 2
            # endif

            # If develop differs from main, then try a merge.
            # Otherwise, only increment version of module in develop and commit
            if headMain.commit != headDev.commit:
                lComX = repoMod.merge_base(headMain, headDev)
                if len(lComX) == 0:
                    raise CRepoError(sMsg=f"No common merge basis for branches '{headDev.name}' and '{headMain.name}'")
                # endif

                comX: Commit = lComX[0]
                sName = GetHeadNameForCommit(repoMod=repoMod, comX=comX)
                print(f"{sPrintPrefix}Merge base commit:")
                print(f"{sPrintPrefix}  - {comX.name_rev} [{sName}]")

                if comX == headDev.commit:
                    raise CRepoError(
                        sMsg=f"Target branch '{headMain.name}' is more advanced than '{headDev.name}' branch"
                    )
                elif comX == headMain.commit:
                    print(f"{sPrintPrefix}Will merge branch '{headDev.name}' into branch '{headMain.name}'")
                else:
                    raise CRepoError(sMsg=f"Invalid state for merging '{headDev.name}' into '{headMain.name}'")
                # endif

                if bDoExecute is True:
                    GitCheckout(repoMod, headMain.name, sPrintPrefix=sPrintPrefix + ">> ")

                    print(f"{sPrintPrefix}Merging branch '{headDev.name}' into branch '{headMain.name}'")
                    sStdOut = repoMod.git.merge(f"{headDev.name}")
                    PrintStdOut(sStdOut, sPrintPrefix=sPrintPrefix)

                    headMain = repoMod.heads[sBranchMain]
                    if repoMod.is_dirty():
                        raise RuntimeError(
                            f"Resolve merge problems and commit {sBranchMain}. Then run this command again."
                        )
                    # endif
                # endif do execute
            # endif Main differs from develop

            bDoTag = True
            for tagX in repoMod.tags:
                if tagX.name == sTagName:
                    if tagX.commit != headMain.commit:
                        raise CRepoError(
                            sMsg=f"Release tag '{sTagName}' already used for different commit: {tagX.commit.name_rev}"
                        )
                    # endif
                    bDoTag = False
                # endif
            # endfor

            if bDoTag is True:
                print(f"{sPrintPrefix}Tagging branch '{headMain.name}' with '{sTagName}'")
                if bDoExecute is True:
                    if repoMod.active_branch != headMain:
                        GitCheckout(repoMod, headMain.name, sPrintPrefix=sPrintPrefix + ">> ")
                    # endif
                    repoMod.create_tag(sTagName, message=f"Release {sTagName}")
                # endif
            # endif

            GitCheckout(repoMod, headDev.name, sPrintPrefix=sPrintPrefix + ">> ")

            sNewVersion, pathSource = IncRepoVersion(pathModule=pathModule, iVerPart=iVerPart, bDoExecute=bDoExecute)
            print(
                f"{sPrintPrefix}Incrementing version of module '{pathModule.name}' from '{sLocalVersion}' to '{sNewVersion}'"
            )

            sPathVerFile = pathSource.relative_to(pathModule).as_posix()
            print(f"{sPrintPrefix}Committing version file: {sPathVerFile}")
            if bDoExecute is True:
                repoMod.index.add([sPathVerFile])
                repoMod.index.commit(f":cathy:set-version:{sNewVersion}: Increment version to {sNewVersion}")
            # endif
        # endif needs release

        sTagRelName = None
        for tagX in repoMod.tags:
            if tagX.commit == headMain.commit:
                sTagRelName = tagX.name
            # endif
        # endfor
        if sTagRelName is None:
            raise CRepoError(sMsg=f"WARNING: Branch '{headMain.name}' is not at any release commit")
        # endif

        if bDoPush is True and bDoExecute is True:
            print(f"{sPrintPrefix}Pushing branch '{sBranchMain}' to 'origin'")
            sStdOut = repoMod.git.push("origin", sBranchMain)
            PrintStdOut(sStdOut, sPrintPrefix=sPrintPrefix)

            print(f"{sPrintPrefix}Pushing branch '{sBranchDev}' to 'origin'")
            sStdOut = repoMod.git.push("origin", sBranchDev)
            PrintStdOut(sStdOut, sPrintPrefix=sPrintPrefix)

            print(f"{sPrintPrefix}Pushing tags to 'origin'")
            sStdOut = repoMod.git.push("origin", "--tags")
            PrintStdOut(sStdOut, sPrintPrefix=sPrintPrefix)
        # endif

    except CRepoError as xEx:
        sResultMsg = f"CANNOT RELEASE:\n{xEx}\n"
        print(f"{sPrintPrefix}{sResultMsg}")
        sTagRelName = None
    # endtry

    print("")
    return pathModule, sTagRelName, sResultMsg


# enddef


####################################################################
def Run(
    *,
    lModules: list[str] = [],
    bDoExecute: bool,
    bDoPush: bool,
    iVerPart: int,
    bDoMain: bool,
):
    # Look for documentation virtual environment
    pathRepos = util.TryGetReposPath()
    if pathRepos is None:
        raise RuntimeError("Modules can only be built from source install")
    # endif

    sBranchMain = "main"
    sBranchDev = "develop"

    #########################################
    # For debugging
    # pathSetup = pathRepos / "dev-test-01"
    # pathRepos = pathSetup / "repos"
    #########################################

    pathSetup = pathRepos.parent

    lModRelTag = []

    def CreateReleaseFunc(
        _pathSetup: Path,
        _bDoExecute: bool,
        _bDoPush: bool,
        _iVerPart: int,
        _lModRelTag: list,
    ):
        def Lambda(*, pathRepos: Path, pathModule: Path):
            tData = ReleaseFromRepo(
                pathRepos=pathRepos,
                pathModule=pathModule,
                pathSetup=_pathSetup,
                bDoExecute=_bDoExecute,
                bDoPush=_bDoPush,
                iVerPart=_iVerPart,
            )
            _lModRelTag.append(tData)

        # enddef
        return Lambda

    # enddef

    lIncMods = lModules if isinstance(lModules, list) else []

    bDoExecMods = not bDoMain and bDoExecute

    # if a main release is created, use the iVerType only for the
    # main repository.
    if bDoMain is True:
        iModVerPart = 2
    else:
        iModVerPart = iVerPart
    # endif

    module.ForEach(
        bForceDist=False,
        funcRunDist=CannotReleaseFromDist,
        funcRunRepo=CreateReleaseFunc(pathSetup, bDoExecMods, bDoPush, iModVerPart, lModRelTag),
        funcTest=FilterPyModules,
        lIncludeRegEx=lIncMods,
        pathReposOverride=pathRepos,
    )

    print("\n===================================================")
    sHeader = "Modules Summary"
    print(sHeader)
    print("-" * len(sHeader))

    bAllReleasesAvailable = True
    for pathMod, sTagRelName, sResultMsg in lModRelTag:
        sModName = pathMod.name
        if sTagRelName is None:
            lResultMsg = sResultMsg.split("\n")
            sSep = "\n" + " " * len(sModName) + "  "
            sTag = sSep.join(lResultMsg)
            bAllReleasesAvailable = False
        else:
            sTag = sTagRelName
        # endif
        print(f"{sModName}: {sTag}")
    # endfor
    print("")

    # sPrintPrefix = ""

    if bDoMain is True and bAllReleasesAvailable is False:
        print(
            "ERROR: Cannot release main repo, "
            "if not all module repositories have their main branches at a release tag\n"
        )

    elif bDoMain is True:
        print("\n===================================================")
        print(f"Release main repo: {pathSetup.name}\n")

        repoMain = Repo(pathSetup)
        if sBranchMain not in repoMain.heads:
            raise CRepoError(sMsg=f"Branch '{sBranchMain}' not found")
        # endif

        if sBranchDev not in repoMain.heads:
            raise CRepoError(sMsg=f"Branch '{sBranchDev}' not found")
        # endif

        headMain = repoMain.heads[sBranchMain]
        sTagRelName = None
        for tagX in repoMain.tags:
            if tagX.commit == headMain.commit:
                sTagRelName = tagX.name
            # endif
        # endfor
        if sTagRelName is None:
            print(f"WARNING: Branch '{headMain.name}' is not at any release commit")
        else:
            print(f"Previous release: {sTagRelName}")
        # endif

        # Checkout develop branch to ensure that we are reading the correct version file
        GitCheckout(repoMain, sBranchDev)

        pathPrevRepoListFile = pathRepos / f"repos-release.yaml"
        # pathPrevRepoListFile = pathRepos / f"repos-{sTagRelName}.yaml"
        bCreateNewRepoList = False
        bCopyRepoList = False

        if not pathPrevRepoListFile.exists():
            print(f"No repository list file found for version {sTagRelName}: {pathPrevRepoListFile.as_posix()}")
            bCreateNewRepoList = True
        else:
            print(
                f"Checking previous repo list file for differences to repo versions: {pathPrevRepoListFile.as_posix()}"
            )
            with pathPrevRepoListFile.open("r") as xFile:
                dicYaml = yaml.load(xFile, Loader=yaml.Loader)
                dicRepoList = dicYaml.get("repositories")
                for pathMod, sTagRelName, sResultMsg in lModRelTag:
                    print(f"Repository '{pathMod.name}', {sTagRelName}:")
                    dicRepo = dicRepoList.get(pathMod.name)
                    if dicRepo is None:
                        print("  - not found in previous repo list")
                        bCreateNewRepoList = True
                        break
                    # endif
                    sRepoTag = dicRepo.get("version")
                    xMatch = re.match(r"tags\/(v\d+\.\d+\.\d+)", sRepoTag)
                    if xMatch is None:
                        print(f"  - repository list version has invalid form: {sRepoTag}")
                        bCreateNewRepoList = True
                        break
                    # endif
                    sPrevTagRelName = xMatch.group(1)
                    if sPrevTagRelName != sTagRelName:
                        print(
                            f"  - previous repository tag '{sPrevTagRelName}' differs from current one '{sTagRelName}'"
                        )
                        bCreateNewRepoList = True
                        break
                    # endif
                    print(f"  - same previous version: {sPrevTagRelName}")
                # endfor
            # endwith

            # Check whether the repository versions stayed the same but the main repo has modifictions.
            # In this case, the old repo list file is copied to the new version.
            headDev = repoMain.heads[sBranchDev]
            bMainRepoChanged = not headDev.commit.message.startswith(":cathy:set-version:")

            bCopyRepoList = bCreateNewRepoList is False and bMainRepoChanged

        # endif
        print("")

        sLocalVersion, sModType = GetRepoVersion(pathModule=pathSetup)
        print(f"Local version: {sLocalVersion}")
        pathRepoListFile = pathPrevRepoListFile
        # pathRepoListFile = pathRepos / f"repos-v{sLocalVersion}.yaml"

        if bCopyRepoList is True:
            print("Keeping repository list file the same")
            # print(f"Copying repository list file '{pathPrevRepoListFile.name}' to '{pathRepoListFile.name}'")
            # if bDoExecute is True:
            #     shutil.copy(pathPrevRepoListFile.as_posix(), pathRepoListFile.as_posix())
            # # endif

        elif bCreateNewRepoList is True:
            print(f"Creating new repository list for version: {sLocalVersion}")

            dicYaml = {}
            dicRepoList = dicYaml["repositories"] = {}
            for pathMod, sTagRelName, sResultMsg in lModRelTag:
                dicRepo = dicRepoList[pathMod.name] = {}
                dicRepo["type"] = "git"
                repoMod = Repo(pathMod)
                remMod = repoMod.remote()
                sUrl = remMod.url
                dicRepo["url"] = sUrl
                dicRepo["version"] = f"tags/{sTagRelName}"
            # endfor

            print("Writing repo list file: {}".format(pathRepoListFile.as_posix()))
            if bDoExecute is True:
                with pathRepoListFile.open("w") as xFile:
                    # yaml.dump(dicYaml, xFile, Dumper=yaml.Dumper, encoding="utf-8")
                    yaml.safe_dump(dicYaml, xFile, encoding="utf-8", allow_unicode=True, indent=4)
                # endwith
            # endif
        # endif

        if bDoExecute and bCreateNewRepoList:
            print(f"Committing new repo list file: {pathRepoListFile.name}")
            sPathRepoListFile = pathRepoListFile.relative_to(pathSetup).as_posix()
            repoMain.index.add([sPathRepoListFile])
            repoMain.index.commit(
                f":cathy:new-repo-list:{sLocalVersion}: Create new repo list file for {sLocalVersion}"
            )
        # endif

        print("")

        # Release main repo
        print("Releasing main module")
        ReleaseFromRepo(
            pathRepos=pathRepos,
            pathModule=pathSetup,
            pathSetup=pathSetup,
            bDoExecute=bDoExecute,
            bDoPush=bDoPush,
            iVerPart=iVerPart,
        )
        print("")

        # if bDoPush is True and bDoExecute is True:
        #     print(f"{sPrintPrefix}Pushing branch '{sBranchMain}' to 'origin'")
        #     sStdOut = repoMain.git.push("origin", sBranchMain)
        #     PrintStdOut(sStdOut, sPrintPrefix=sPrintPrefix)

        #     print(f"{sPrintPrefix}Pushing branch '{sBranchDev}' to 'origin'")
        #     sStdOut = repoMain.git.push("origin", sBranchDev)
        #     PrintStdOut(sStdOut, sPrintPrefix=sPrintPrefix)

        #     print(f"{sPrintPrefix}Pushing tags to 'origin'")
        #     sStdOut = repoMain.git.push("origin", "--tags")
        #     PrintStdOut(sStdOut, sPrintPrefix=sPrintPrefix)
        # # endif
        # print("")

    # endif


# enddef
