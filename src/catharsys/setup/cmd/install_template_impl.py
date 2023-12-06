#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \install.py
# Created Date: Monday, November 28th 2022, 8:48:36 am
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
import sys

if sys.version_info < (3, 10):
    import importlib_resources as res
else:
    from importlib import resources as res
# endif
from pathlib import Path
import catharsys.setup

import shutil
from anybase import file as anyfile
from anybase import path as anypath
from anybase import config as anycfg
from typing import Optional, NamedTuple
from catharsys.setup import util, module

g_sCmdDesc = "Installs Catharsys workspaces"


####################################################################
class CTemplateModuleInfo(NamedTuple):
    sId: str = None
    sName: str = None
    sVersion: str = None
    pathModule: Path = None
    bIsRepo: bool = True


# endclass


####################################################################
def Run(
    *,
    sTplName: str,
    sNewModuleName: str = None,
    sPathTrg: Optional[str] = None,
    bForce: bool = False,
    bForceDist: bool = False,
    bDoList: bool = False,
    bYes: bool = False,
    lVars: list = None,
):
    pathTplTrg: Path
    if not isinstance(sPathTrg, str):
        pathTplTrg = Path.cwd()
    else:
        pathTplTrg = Path(util.NormPath(sPathTrg))
    # endif

    if not pathTplTrg.exists():
        raise RuntimeError("Target path does not exist: {}".format(pathTplTrg.as_posix()))
    # endif

    if sTplName is None:
        bDoList = True
    # endif

    if bDoList is False:
        InstallTemplate(
            _sId=sTplName,
            _pathTrg=pathTplTrg,
            _bForce=bForce,
            _bForceDist=bForceDist,
            _bYes=bYes,
            _sNewModuleName=sNewModuleName,
            _lVars=lVars,
        )

    else:
        ListTemplates(_bForceDist=bForceDist)
    # endif


# enddef


####################################################################
def InstallTemplate(
    *,
    _sId: str,
    _pathTrg: Path,
    _bForce: bool,
    _bForceDist: bool,
    _bYes: bool,
    _sNewModuleName: str = None,
    _lVars: list = None,
):
    pathTrg = anypath.MakeNormPath(_pathTrg.absolute())

    lTemplates = GetTemplateInfoList(_bForceDist=_bForceDist)

    xModInfo = None
    xInfo: CTemplateModuleInfo
    for xInfo in lTemplates:
        if xInfo.sId.lower() == _sId.lower():
            if xModInfo is not None:
                raise RuntimeError(
                    f"Template '{_sId}' defined multiple times:\n1. {xModInfo.pathModule}\n2. {xInfo.pathModule}\n"
                )
            # endif
            xModInfo = xInfo
        # endif
    # endfor

    if xModInfo is None:
        ListTemplates(_bForceDist=_bForceDist)
        raise RuntimeError(
            f"Template '{_sId}' not found. Run 'cathy install template --list' to see list of available templates."
        )
    # endif

    print(f"Creating template '{_sId}'")
    if isinstance(_sNewModuleName, str):
        sNewModName: str = _sNewModuleName
    else:
        sNewModName: str = None
    # endif

    #########################################################################################################
    # Parse command line argument variables, if any
    dicUserVarValues: dict[str, str] = {}
    if isinstance(_lVars, list):
        reVarDef = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)=([a-zA-Z_][a-zA-Z0-9_\-]*)")
        for sVarDef in _lVars:
            xMatch = reVarDef.match(sVarDef)
            if xMatch is None:
                raise RuntimeError(f"Variable definition is of incorrect form: {sVarDef}.\n> Expect [Name]=[Value].")
            # endif
            dicUserVarValues[xMatch.group(1)] = xMatch.group(2)
        # endfor
    # endif

    #########################################################################################################
    # Loop until a name for the new module has been found
    while True:
        sMsg: str = None

        # Just an environment which can be exited with a "break"
        while True:
            if sNewModName is None:
                sNewModName = str(input("Enter new module name (press RETURN to abort): "))
                if sNewModName == "":
                    print("User abort of module creation")
                    return
                # endif
            # endif

            xMatch = re.match(r"^[a-zA-Z_][a-zA-Z0-9_\-]*$", sNewModName)
            if xMatch is None:
                sMsg = (
                    f"ERROR: Invalid module name '{sNewModName}'. Allowed characters are [a...z, A...Z, 0...9, -, _]."
                )
                break
            # endif

            pathNewMod = pathTrg / sNewModName

            if pathNewMod.exists():
                if _bForce is False:
                    sMsg = f"ERROR: New module path exists: {(pathNewMod.as_posix())}"
                    break
                else:
                    shutil.rmtree(pathNewMod.as_posix())
                # endif
            # endif

            print(f"New module path: {(pathNewMod.as_posix())}")
            if _bYes is False:
                sYN = str(input("Create module folder [y]/n: "))
                if sYN != "" and sYN != "y":
                    sMsg = "Module folder not accepted by user."
                    break
                # endif
            # endif

            break
        # endwhile environment to break from

        if sMsg is not None:
            sNewModName = None
            if _bYes is False:
                print(sMsg)
                continue
            else:
                raise RuntimeError(sMsg)
            # endif
        # endif
        #
        break
    # endwhile enter module name

    dicUserVarValues["MODULE-NAME"] = sNewModName

    #########################################################################################################
    # Create new folder and copy template files
    try:
        pathNewMod.mkdir(parents=False, exist_ok=False)
    except Exception as xEx:
        raise RuntimeError(f"Error creation module folder:\n{(str(xEx))}\n")
    # endtry

    # print(f"Module name: {sNewModName}")
    if xModInfo.bIsRepo is True:
        lReExcludeDirs = [
            r"\.git",
            r"\.vscode",
            r"__pycache__",
            r"dev",
            r"build",
            r".+\.egg-info",
        ]

        lReExcludeFiles = [
            # r"\.git.+",
            r"\.vscode.+",
            r"stdout_.+\.txt",
            r"action-config-list_.+\.json",
            r"cml-vars_.+\.json",
            r"\.env",
            r".+\.egg-info",
        ]

        util.CopyFiles(
            xModInfo.pathModule,
            pathNewMod,
            pathSrcTop=xModInfo.pathModule,
            pathTrgTop=pathNewMod,
            lReExcludeDirs=lReExcludeDirs,
            lReExcludeFiles=lReExcludeFiles,
        )

    else:
        shutil.unpack_archive(xModInfo.pathModule.as_posix(), pathNewMod.as_posix())

    # endif

    #########################################################################################################
    # Get user input for template variables

    # Load template json
    pathTplInfo = pathNewMod / "template.json5"
    if not pathTplInfo.exists():
        raise RuntimeError(f"Template file 'template.json5' not found at: {(pathTplInfo.as_posix())}")
    # endif

    dicTpl = anyfile.LoadJson(pathTplInfo)
    anycfg.AssertConfigType(dicTpl, "/package/catharsys/template/*:*")

    lTplVars = dicTpl.get("lVars")
    if not isinstance(lTplVars, list):
        raise RuntimeError("Template file 'template.json5' misses element 'lVars'")
    # endif

    iDefCnt = 0
    for dicVar in lTplVars:
        sVarName = dicVar["sName"]
        # Check whether variable has been given in variable list
        sVarValue = dicUserVarValues.get(sVarName)
        if sVarValue is not None:
            dicVar["sValue"] = sVarValue
            iDefCnt += 1
        # endif
    # endfor

    while True:
        bValidVars = True
        if iDefCnt < len(lTplVars):
            print("Please enter values for the following template parameters:")
            print("(Enter empty value to abort)")
            for dicVar in lTplVars:
                if dicVar.get("sValue") is not None:
                    continue
                # endif

                sVarName = dicVar["sName"]
                while True:
                    sVarValue = str(input(f"{sVarName}: "))
                    if sVarValue == "" or sVarValue is None:
                        sMsg = "Template creation aborted by user"
                        bValidVars = False
                        break
                    # endif

                    xMatch = re.match(r"^[a-zA-Z_][a-zA-Z0-9_\-]*$", sVarValue)
                    if xMatch is None:
                        print(
                            f"ERROR: Invalid variable value '{sVarValue}'. Allowed characters are [a...z, A...Z, 0...9, _, -]."
                        )
                        continue
                    # endif
                    break
                # endwhile
                if bValidVars is False:
                    break
                # endif

                dicVar["sValue"] = sVarValue

                ### DEBUG ###
                # break
                #############
            # endfor
        # endif

        if bValidVars is False:
            print(sMsg)
            print(f"Unmodified template can be found at: {(pathNewMod.as_posix())}")
            return
        # endif

        for dicVar in lTplVars:
            sVarName = dicVar["sName"]
            sVarValue = dicVar["sValue"]
            print(f"Using '{sVarName}' = '{sVarValue}'")
        # endfor

        if _bYes is True:
            break
        # endif

        sYNX = str(input("Do you want to use these values [y]/n/x: "))
        if sYNX == "" or sYNX == "y":
            break
        elif sYNX == "x":
            print("Template creation aborted by user.")
            print(f"Unmodified template can be found at: {(pathNewMod.as_posix())}")
            return
        # endif

        for dicVar in lTplVars:
            dicVar["sValue"] = None
        # endfor
    # endwhile

    #########################################################################################################
    # Adapt copied files/folder to template variables
    dicVar: dict
    for dicVar in lTplVars:
        dicFoldernames: dict = dicVar.get("mFoldernames")
        if isinstance(dicFoldernames, dict) and len(dicFoldernames) > 0:
            sReSearch: str = dicFoldernames["sReSearch"]
            sReReplace: str = dicFoldernames["sReReplace"]
            sNewReplace = sReReplace.replace("\\0", dicVar["sValue"])
            # print(f"Replace foldernames: {sReSearch} -> {sNewReplace}")
            RenamePath(_pathMain=pathNewMod, _sReSearch=sReSearch, _sReReplace=sNewReplace, _bFile=False, _bFolder=True)
        # endif

        dicFilenames: dict = dicVar.get("mFilenames")
        if isinstance(dicFilenames, dict) and len(dicFilenames) > 0:
            sReSearch: str = dicFilenames["sReSearch"]
            sReReplace: str = dicFilenames["sReReplace"]
            sNewReplace = sReReplace.replace("\\0", dicVar["sValue"])
            # print(f"Replace foldernames: {sReSearch} -> {sNewReplace}")
            RenamePath(_pathMain=pathNewMod, _sReSearch=sReSearch, _sReReplace=sNewReplace, _bFile=True, _bFolder=False)
        # endif

        lFileContent: list = dicVar.get("lFileContent")
        if isinstance(lFileContent, list) and len(lFileContent) > 0:
            sVarValue: str = dicVar["sValue"]
            dicFileContent: dict
            for dicFileContent in lFileContent:
                if isinstance(dicFileContent, dict) and len(dicFileContent) > 0:
                    lReFiles = dicFileContent["lReFiles"]
                    sReSearch: str = dicFileContent["sReSearch"]
                    sReReplace: str = dicFileContent["sReReplace"]
                    sValueKind = dicFileContent.get("sValueKind")
                    if isinstance(sValueKind, str):
                        if sValueKind == "python/class":
                            sVarValue = f"{sVarValue.upper()[0]}{sVarValue[1:]}"

                        elif sValueKind == "python/function":
                            sVarValue = f"{sVarValue.upper()[0]}{sVarValue[1:]}"
                        # endif
                    # endif
                    sNewReplace = sReReplace.replace("\\0", sVarValue)
                    RenameInFiles(
                        _pathMain=pathNewMod, _lReFiles=lReFiles, _sReSearch=sReSearch, _sReReplace=sNewReplace
                    )
                # endif
            # endfor file content
        # endif is list

        ### DEBUG ###
        # break
        #############
    # endfor

    pathTplInfo.unlink()


# enddef InstallTemplate()


####################################################################
def _DoRenameInFiles(_pathMain: Path, _lReFilesComp, _reSearch, _sReReplace: str):
    for pathChild in _pathMain.iterdir():
        if pathChild.is_dir():
            _DoRenameInFiles(
                _pathMain=pathChild, _lReFilesComp=_lReFilesComp, _reSearch=_reSearch, _sReReplace=_sReReplace
            )

        elif pathChild.is_file():
            xMatch = None
            for reFile in _lReFilesComp:
                xMatch = reFile.match(pathChild.name)
                if xMatch is not None:
                    break
                # endif
            # endfor

            if xMatch is None:
                continue
            # endif

            sText = pathChild.read_text()
            sNewText = _reSearch.sub(_sReReplace, sText)
            pathChild.write_text(sNewText)
        # endif
    # endfor


# enddef


####################################################################
def RenameInFiles(*, _pathMain: Path, _lReFiles: list[str], _sReSearch: str, _sReReplace: str):
    reSearch = re.compile(_sReSearch)
    lReFilesComp = [re.compile(x) for x in _lReFiles]

    _DoRenameInFiles(_pathMain=_pathMain, _lReFilesComp=lReFilesComp, _reSearch=reSearch, _sReReplace=_sReReplace)


# enddef


####################################################################
def _DoRenamePath(*, _pathAct: Path, _reSearch, _sReReplace: str, _lRenames: list, _bFile: bool, _bFolder: bool):
    # Recurse first through child folders
    for pathChild in _pathAct.iterdir():
        if pathChild.is_dir():
            _DoRenamePath(
                _pathAct=pathChild,
                _reSearch=_reSearch,
                _sReReplace=_sReReplace,
                _lRenames=_lRenames,
                _bFile=_bFile,
                _bFolder=_bFolder,
            )
        elif pathChild.is_file() and _bFile is True:
            sNewName = _reSearch.sub(_sReReplace, pathChild.name)
            if sNewName != pathChild.name:
                print(f"{pathChild.name} -> {sNewName}")
                pathNew = pathChild.parent / sNewName
                _lRenames.append([pathChild, pathNew])
            # endif
        # endif
    # endfor

    if _bFolder is True:
        sNewName = _reSearch.sub(_sReReplace, _pathAct.name)
        if sNewName != _pathAct.name:
            print(f"{_pathAct.name} -> {sNewName}")
            pathNew = _pathAct.parent / sNewName
            _lRenames.append([_pathAct, pathNew])
        # endif
    # endif


# enddef


####################################################################
def RenamePath(*, _pathMain: Path, _sReSearch: str, _sReReplace: str, _bFile: bool, _bFolder: bool):
    reSearch = re.compile(_sReSearch)
    lRenames = []
    _DoRenamePath(
        _pathAct=_pathMain,
        _reSearch=reSearch,
        _sReReplace=_sReReplace,
        _lRenames=lRenames,
        _bFile=_bFile,
        _bFolder=_bFolder,
    )

    for pathOld, pathNew in lRenames:
        pathOld.rename(pathNew)
        # os.rename(pathOld.as_posix(), pathNew.as_posix())
    # endfor


# enddef


####################################################################
def ListTemplates(*, _bForceDist: bool):
    lTemplates = GetTemplateInfoList(_bForceDist=_bForceDist)

    print("Available templates:")
    xInfo: CTemplateModuleInfo
    for xInfo in lTemplates:
        if xInfo.sName is None:
            print(f"- '{xInfo.sId}' v{xInfo.sVersion}")
        else:
            print(f"- '{xInfo.sId}': {xInfo.sName} v{xInfo.sVersion}")
        # endif
        # print(f"  | {(xInfo.pathModule.as_posix())}")
    # endfor


# enddef


####################################################################
def GetTemplateInfoList(*, _bForceDist: bool) -> list[CTemplateModuleInfo]:
    lTemplates: list[CTemplateModuleInfo] = []

    if util.IsDevelopInstall() and _bForceDist is False:
        # develop install
        pathRepos: Path = util.TryGetReposPath()
        lTemplates = GetRepoTemplateList(pathRepos)

    else:
        reDist = re.compile(r"image-render-(.+)-(\d+\.\d+\.\d+)\.zip")
        with res.path(catharsys.setup, "dist") as pathDist:
            pathDistWs = pathDist / "template"
            for pathDir in pathDistWs.iterdir():
                xMatch = reDist.match(pathDir.name)
                if xMatch is None:
                    continue
                # endif
                sId = xMatch.group(1)
                sVersion = xMatch.group(2)
                lTemplates.append(
                    CTemplateModuleInfo(sId=sId, sName=None, sVersion=sVersion, pathModule=pathDir, bIsRepo=False)
                )
            # endfor
        # endwith
    # endif

    return lTemplates


# enddef


####################################################################
def _CreateRepoTemplateListHandler(_lTemplateNameList: list):
    def Handler(*, pathModule, pathRepos):
        pathPkgFile: Path = pathModule / "package.json"
        if not pathPkgFile.exists():
            return
        # endif

        dicPkg: dict = anyfile.LoadJson(pathPkgFile)
        sPkgDti: str = dicPkg.get("sDTI")

        if not isinstance(sPkgDti, str) or not sPkgDti.startswith("/package/catharsys/templates"):
            return
        # endif

        sTplVersion: str = dicPkg.get("sVersion")
        if not isinstance(sTplVersion, str):
            print(
                f"ERROR: Template collection '{pathModule.name}' misses 'sVersion' element in: {(pathPkgFile.as_posix())}"
            )
            return
        # endif

        lTemplateFolders: list[str] = dicPkg.get("lTemplateFolders")
        if not isinstance(lTemplateFolders, list):
            print(
                f"ERROR: Template collection '{pathModule.name}' misses 'lTemplateFolders' element in: {(pathPkgFile.as_posix())}"
            )
            return
        # endif

        sTemplateFolder: str
        for sTemplateFolder in lTemplateFolders:
            pathTpl: Path = pathModule / sTemplateFolder
            pathTplFile: Path = pathTpl / "template.json5"
            if not pathTplFile.exists():
                print(f"ERROR: Template '{sTemplateFolder}' misses file: {(pathTplFile.as_posix())}")
                continue
            # endif

            dicTpl: dict = anyfile.LoadJson(pathTplFile)
            sTplName: str = dicTpl.get("sName")
            if not isinstance(sTplName, str):
                print(f"ERROR: Template '{sTemplateFolder}' misses element 'sName' in: {(pathTplFile.as_posix())}")
                continue
            # endif

            sVersion: str = dicTpl.get("sVersion", sTplVersion)

            _lTemplateNameList.append(
                CTemplateModuleInfo(
                    sId=sTemplateFolder,
                    sName=sTplName,
                    sVersion=sVersion,
                    pathModule=pathTpl,
                    bIsRepo=True,
                )
            )

        # endfor

    # enddef

    return Handler


# enddef


####################################################################
def _CreateInvalidHandler():
    def Handler(*, pathModule, pathDist, sName, sVersion):
        raise RuntimeError("Processing distribution modules invalid in this context")

    # enddef
    return Handler


# enddef


####################################################################
def GetRepoTemplateList(pathRepos: Path) -> list[str]:
    lTemplateNameList: list[str] = []

    module.ForEach(
        bForceDist=False,
        funcRunRepo=_CreateRepoTemplateListHandler(lTemplateNameList),
        funcRunDist=_CreateInvalidHandler(),
    )

    return lTemplateNameList


# enddef
