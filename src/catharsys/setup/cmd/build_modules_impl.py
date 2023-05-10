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

import re
import os
import shutil
from typing import Optional
from pathlib import Path
from packaging import version
from git import Repo, Commit, Head, Remote

from anybase import file as anyfile
from catharsys.setup import util
from catharsys.setup import module
from catharsys.setup.cmd.repos_release_impl import GitCheckout


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


####################################################################
def TestDoBuild(
    *,
    pathModule: Path,
    sModuleVersion: str,
    pathDist: Path,
    lreDist: list[re.Pattern],
    bCleanDist: bool = True,
) -> bool:

    bDoBuild = False
    for reDist in lreDist:

        bSubDoBuild = True
        for pathDistMod in pathDist.iterdir():
            if not pathDistMod.is_file():
                continue
            # endif

            xMatch = reDist.match(pathDistMod.name)
            if xMatch is None:
                continue
            # endif
            sDistName = xMatch.group(1).replace("_", "-")
            sDistVer = xMatch.group(2)

            if sDistName != pathModule.name:
                continue
            # endif

            verDist = version.parse(sDistVer)
            verModule = version.parse(sModuleVersion)

            if verDist < verModule:
                print("Removing old distribution: {}".format(pathDistMod.name))
                if bCleanDist is True:
                    os.remove(pathDistMod.as_posix())
                # endif

            elif verDist == verModule:
                print("Build for version {} already exists: {}".format(sModuleVersion, pathModule.name))
                bSubDoBuild = False

            else:
                print("Distribution already exists in higher version: {}".format(pathDistMod.name))
                bSubDoBuild = False
            # endif

        # endfor pathDistMod
        if bSubDoBuild is True:
            bDoBuild = True
        # endif
    # endfor reDist

    return bDoBuild


# endif


#####################################################################
def CannotBuildFromDist(*, pathDist: Path, pathModule: Path, sName: str, sVersion: str):

    print("===================================================")
    print("Cannot build module from distribution for: {} v{}\n".format(sName, sVersion))


# enddef


#####################################################################
def SelectBuildBranch(*, pathModule):
    sBranchMain = "master"
    sBranchDev = "develop"
    repoMod = Repo(pathModule)

    if sBranchMain not in repoMod.heads:
        raise RuntimeError(f"Branch '{sBranchMain}' not found")
    # endif

    if sBranchDev not in repoMod.heads:
        raise RuntimeError(f"Branch '{sBranchDev}' not found")
    # endif

    headMain: Head = repoMod.heads[sBranchMain]
    headDev: Head = repoMod.heads[sBranchDev]
    headAct: Head = repoMod.active_branch

    sSwitchBackToBranch: str = None
    if headDev.commit.message.startswith(":cathy:set-version:"):
        print(f"No changes since last release. Switching to release branch...")
        sSwitchBackToBranch = headAct.name
        GitCheckout(repoMod, sBranchMain, sPrintPrefix=">> ")
    else:
        print(f"Changes since last relase. Building with '{headAct.name}' branch version...")
    # endif

    return sSwitchBackToBranch


# endif


#####################################################################
def SelectBranch(*, pathModule, sBranch):
    repoMod = Repo(pathModule)
    print(f"Switching to branch '{sBranch}'")
    GitCheckout(repoMod, sBranch, sPrintPrefix=">> ")


# enddef


#####################################c###############################
def BuildFromRepo(*, pathRepos: Path, pathModule: Path, pathDist: Path, pathSetup: Path):

    print("===================================================")
    sSwitchBackToBranch = SelectBuildBranch(pathModule=pathModule)

    pathSetupCfgFile = pathModule / "setup.cfg"

    pathPackageFile = pathModule / "package.json"
    if not pathPackageFile.exists():
        pathPackageFile = pathModule / "package.json5"
        if not pathPackageFile.exists():
            pathPackageFile = None
        # endif
    # endif

    lreDist = [module.GetRegExModuleDistFile(sType="WHEEL"), module.GetRegExModuleDistFile(sType="SOURCE")]

    if pathSetupCfgFile.exists():
        sRepoVersion = module.GetRepoVersion(pathModule=pathModule)

        if (
            TestDoBuild(
                pathModule=pathModule,
                sModuleVersion=sRepoVersion,
                pathDist=pathDist,
                lreDist=lreDist,
            )
            is True
        ):

            sRelPathDist = os.path.relpath(pathDist.as_posix(), pathModule.as_posix())

            print("Building Module {}\n---\n".format(pathModule.name))
            # print("Path module: {}".format(pathModule.as_posix()))
            # print("Path dist: {}".format(pathDist.as_posix()))
            # print("Rel dist: {}".format(pathRelDist.as_posix()))

            sCmd = 'python -m build --outdir "{}" .'.format(sRelPathDist)
            # sCmd = "python -m build --sdist --outdir \"{}\" .".format(sRelPathDist)
            sCwd = pathModule.as_posix()
            util.ExecShellCmd(
                sCmd=sCmd,
                sCwd=sCwd,
                bDoPrint=True,
                bDoPrintOnError=True,
                sPrintPrefix=">> ",
            )
        # endif

    elif pathPackageFile is not None:
        # print("Build from package.json")

        dicPkg = anyfile.LoadJson(pathPackageFile)
        sPkgDti = dicPkg.get("sDTI")

        if isinstance(dicPkg.get("engines"), dict):
            BuildVsCodePackage(
                pathModule=pathModule,
                pathDist=pathDist / "vscode",
                pathSetup=pathSetup,
                dicPkg=dicPkg,
            )

        elif isinstance(sPkgDti, str):
            if sPkgDti.startswith("/package/catharsys/workspace"):
                BuildWorkspacePackage(
                    pathModule=pathModule,
                    pathDist=pathDist / "workspace",
                    pathSetup=pathSetup,
                    dicPkg=dicPkg,
                )
            elif sPkgDti.startswith("/package/catharsys/templates"):
                BuildTemplatePackages(
                    pathModule=pathModule,
                    pathDist=pathDist / "template",
                    pathSetup=pathSetup,
                    dicPkg=dicPkg,
                )
            else:
                BuildAssetPackage(
                    pathModule=pathModule,
                    pathDist=pathDist / "asset",
                    pathSetup=pathSetup,
                    dicPkg=dicPkg,
                )
            # endif
        else:
            print("WARNING: Unsupported module package file type.")
        # endif
    else:
        print("WARNING: Unsupported module type.")
    # endif

    if sSwitchBackToBranch is not None:
        SelectBranch(pathModule=pathModule, sBranch=sSwitchBackToBranch)
    # endif

    print("")


# enddef


####################################################################
def BuildVsCodePackage(*, pathModule: Path, pathDist: Path, pathSetup: Path, dicPkg: dict):
    print("Building VS-Code package {}\n---\n".format(pathModule.name))

    lReExcludeDirs = [
        r"\.git",
        r"\.vscode",
        r"__pycache__",
        r"unit_test",
        r"_dev",
        r"dev",
        r"_debug",
        r"_render",
        r"build",
        r"dist",
        r"_output",
    ]

    lReExcludeFiles = [
        r"\.srm_.+",
        r"\.git.+",
        r"\.vscode.+",
        r"stdout_.+\.txt",
        r"action-config-list_.+\.json",
        r"cml-vars_.+\.json",
        r".+\.blend1",
        r"\.env",
        r"\.egg-info",
        r"vsc-extension-quickstart.md",
    ]

    reDist = re.compile(r"(.*?)-(\d+\.\d+\.\d+)\.zip")

    sVersion = dicPkg.get("version")
    if not isinstance(sVersion, str):
        raise RuntimeError("Package file does not contain element 'version'")
    # endif

    # Create distribution directory if it does not exist
    pathDist.mkdir(parents=True, exist_ok=True)

    bDoBuild = TestDoBuild(pathModule=pathModule, sModuleVersion=sVersion, pathDist=pathDist, lreDist=[reDist])
    if bDoBuild is False:
        return
    # endif

    pathBuild = pathSetup / "_build"
    pathBuildMod = pathBuild / "{}-{}".format(pathModule.name, sVersion)
    if pathBuildMod.exists():
        shutil.rmtree(pathBuildMod.as_posix())
    # endif
    if pathBuildMod.exists():
        raise RuntimeError("Cannot remove build directory. Please remove manually: {}".format(pathBuildMod.as_posix()))
    # endif

    pathBuildMod.mkdir(parents=True)

    print("Copying package files to build folder: {}".format(pathBuildMod.as_posix()))
    util.CopyFiles(
        pathModule,
        pathBuildMod,
        lReExcludeDirs=lReExcludeDirs,
        lReExcludeFiles=lReExcludeFiles,
        pathSrcTop=pathModule,
        pathTrgTop=pathBuild,
    )

    print("Creating ZIP package")
    pathCwd = Path.cwd()
    os.chdir(pathBuild.as_posix())
    shutil.make_archive(pathBuildMod.name, "zip", ".", pathBuildMod.name)

    sZipFilename = pathBuildMod.name + ".zip"
    pathZipSrcFile = pathBuild / sZipFilename
    pathZipTrg = pathDist
    pathZipTrgFile = pathZipTrg / sZipFilename
    pathZipTrg.mkdir(parents=True, exist_ok=True)

    shutil.move(pathZipSrcFile.as_posix(), pathZipTrgFile.as_posix())
    print("Package stored as: {}".format(pathZipTrgFile.as_posix()))

    os.chdir(pathCwd.as_posix())
    shutil.rmtree(pathBuildMod.as_posix())


# enddef


####################################################################
def BuildWorkspacePackage(*, pathModule: Path, pathDist: Path, pathSetup: Path, dicPkg: dict):
    print("Building Workspace package {}\n---\n".format(pathModule.name))

    lReExcludeDirs = [
        r"\.git",
        r"\.vscode",
        r"__pycache__",
        r"unit_test",
        r"_dev",
        r"dev",
        r"_debug",
        r"_render",
        r"build",
        r"dist",
        r"_output",
        r"_blender",
    ]

    lReExcludeFiles = [
        r"\.srm_.+",
        r"\.git.+",
        r"\.vscode.+",
        r"stdout_.+\.txt",
        r"action-config-list_.+\.json",
        r"cml-vars_.+\.json",
        r".+\.blend1",
        r"Blender-.+\.blend1?",
        r"\.env",
        r"\.egg-info",
        r"vsc-extension-quickstart.md",
    ]

    reDist = re.compile(r"(.*?)-(\d+\.\d+\.\d+)\.zip")

    sVersion = dicPkg.get("sVersion")
    if not isinstance(sVersion, str):
        raise RuntimeError("Package file does not contain element 'sVersion'")
    # endif

    # Create distribution directory if it does not exist
    pathDist.mkdir(parents=True, exist_ok=True)

    bDoBuild = TestDoBuild(pathModule=pathModule, sModuleVersion=sVersion, pathDist=pathDist, lreDist=[reDist])
    if bDoBuild is False:
        return
    # endif

    pathBuild = pathSetup / "_build"
    pathBuildMod = pathBuild / "{}-{}".format(pathModule.name, sVersion)
    if pathBuildMod.exists():
        shutil.rmtree(pathBuildMod.as_posix())
    # endif
    if pathBuildMod.exists():
        raise RuntimeError("Cannot remove build directory. Please remove manually: {}".format(pathBuildMod.as_posix()))
    # endif

    pathBuildMod.mkdir(parents=True)

    print("Copying package files to build folder: {}".format(pathBuildMod.as_posix()))
    util.CopyFiles(
        pathModule,
        pathBuildMod,
        lReExcludeDirs=lReExcludeDirs,
        lReExcludeFiles=lReExcludeFiles,
        pathSrcTop=pathModule,
        pathTrgTop=pathBuild,
    )

    print("Creating ZIP package")
    pathCwd = Path.cwd()
    os.chdir(pathBuild.as_posix())
    shutil.make_archive(pathBuildMod.name, "zip", ".", pathBuildMod.name)

    sZipFilename = pathBuildMod.name + ".zip"
    pathZipSrcFile = pathBuild / sZipFilename
    pathZipTrg = pathDist
    pathZipTrgFile = pathZipTrg / sZipFilename
    pathZipTrg.mkdir(parents=True, exist_ok=True)

    shutil.move(pathZipSrcFile.as_posix(), pathZipTrgFile.as_posix())
    print("Package stored as: {}".format(pathZipTrgFile.as_posix()))

    os.chdir(pathCwd.as_posix())
    shutil.rmtree(pathBuildMod.as_posix())


# enddef


####################################################################
def BuildTemplatePackages(*, pathModule: Path, pathDist: Path, pathSetup: Path, dicPkg: dict):
    print("Building template packages from {}\n---\n".format(pathModule.name))

    lReExcludeDirs = [
        r"\.git",
        r"\.vscode",
        r"__pycache__",
        r"unit_test",
        r"_dev",
        r"dev",
        r"_debug",
        r"_render",
        r"build",
        r"dist",
        r"_output",
        r"_blender",
        r".+\.egg-info",
    ]

    lReExcludeFiles = [
        r"\.srm_.+",
        r"\.git.+",
        r"\.vscode.+",
        r"stdout_.+\.txt",
        r"action-config-list_.+\.json",
        r"cml-vars_.+\.json",
        r".+\.blend1",
        r"Blender-.+\.blend1?",
        r"\.env",
        r"\.egg-info",
        r"vsc-extension-quickstart.md",
    ]

    reDist = re.compile(r"(.*?)-(\d+\.\d+\.\d+)\.zip")

    sVersion = dicPkg.get("sVersion")
    if not isinstance(sVersion, str):
        raise RuntimeError("Package file does not contain element 'sVersion'")
    # endif

    # Create distribution directory if it does not exist
    pathDist.mkdir(parents=True, exist_ok=True)

    # Loop over all templates in the template collection
    lTemplateFolders = dicPkg.get("lTemplateFolders")
    if not isinstance(lTemplateFolders, list):
        raise RuntimeError("Template module package file does not have a 'lTemplates' element")
    # endif

    for sTemplateFolder in lTemplateFolders:
        pathModuleTplSrc = pathModule / f"{sTemplateFolder}"
        pathModuleTplTrg = pathModule / f"image-render-{sTemplateFolder}"

        if not pathModuleTplSrc.exists():
            raise RuntimeError(f"Template source folder does not exist: {(pathModuleTplSrc.as_posix())}")
        # endif

        bDoBuild = TestDoBuild(
            pathModule=pathModuleTplTrg, sModuleVersion=sVersion, pathDist=pathDist, lreDist=[reDist]
        )
        if bDoBuild is False:
            return
        # endif

        pathBuild = pathSetup / "_build"
        pathBuildMod = pathBuild / "{}-{}".format(pathModuleTplTrg.name, sVersion)
        if pathBuildMod.exists():
            shutil.rmtree(pathBuildMod.as_posix())
        # endif
        if pathBuildMod.exists():
            raise RuntimeError(
                "Cannot remove build directory. Please remove manually: {}".format(pathBuildMod.as_posix())
            )
        # endif

        pathBuildMod.mkdir(parents=True)

        print(f"Copying '{sTemplateFolder}' template package files to build folder: {(pathBuildMod.as_posix())}")
        util.CopyFiles(
            pathModuleTplSrc,
            pathBuildMod,
            lReExcludeDirs=lReExcludeDirs,
            lReExcludeFiles=lReExcludeFiles,
            pathSrcTop=pathModuleTplSrc,
            pathTrgTop=pathBuild,
        )

        print("Creating ZIP package")
        pathCwd = Path.cwd()
        os.chdir(pathBuild.as_posix())
        shutil.make_archive(pathBuildMod.name, "zip", pathBuildMod.as_posix())  # , pathBuildMod.name)

        sZipFilename = pathBuildMod.name + ".zip"
        pathZipSrcFile = pathBuild / sZipFilename
        pathZipTrg = pathDist
        pathZipTrgFile = pathZipTrg / sZipFilename
        pathZipTrg.mkdir(parents=True, exist_ok=True)

        shutil.move(pathZipSrcFile.as_posix(), pathZipTrgFile.as_posix())
        print("Package stored as: {}".format(pathZipTrgFile.as_posix()))

        os.chdir(pathCwd.as_posix())
        shutil.rmtree(pathBuildMod.as_posix())
    # endfor


# enddef


####################################################################
def BuildAssetPackage(*, pathModule: Path, pathDist: Path, pathSetup: Path, dicPkg: dict):
    print("Building Asset package {}\n---\n".format(pathModule.name))

    lReExcludeDirs = [
        r"\.git",
        r"\.vscode",
        r"__pycache__",
        r"unit_test",
        r"_dev",
        r"dev",
        r"_debug",
        r"_render",
        r"build",
        r"dist",
        r"_output",
        r"_blender",
    ]

    lReExcludeFiles = [
        r"\.srm_.+",
        r"\.git.+",
        r"\.vscode.+",
        r"stdout_.+\.txt",
        r"action-config-list_.+\.json",
        r"cml-vars_.+\.json",
        r".+\.blend1",
        r"\.env",
        r"\.egg-info",
        r"vsc-extension-quickstart.md",
    ]

    reDist = re.compile(r"(.*?)-(\d+\.\d+\.\d+)\.zip")

    sVersion = dicPkg.get("sVersion")
    if not isinstance(sVersion, str):
        raise RuntimeError("Package file does not contain element 'sVersion'")
    # endif

    # Create distribution directory if it does not exist
    pathDist.mkdir(parents=True, exist_ok=True)

    bDoBuild = TestDoBuild(pathModule=pathModule, sModuleVersion=sVersion, pathDist=pathDist, lreDist=[reDist])
    if bDoBuild is False:
        return
    # endif

    pathBuild = pathSetup / "_build"
    pathBuildMod = pathBuild / "{}-{}".format(pathModule.name, sVersion)
    if pathBuildMod.exists():
        shutil.rmtree(pathBuildMod.as_posix())
    # endif
    if pathBuildMod.exists():
        raise RuntimeError("Cannot remove build directory. Please remove manually: {}".format(pathBuildMod.as_posix()))
    # endif

    pathBuildMod.mkdir(parents=True)

    print("Copying package files to build folder: {}".format(pathBuildMod.as_posix()))
    util.CopyFiles(
        pathModule,
        pathBuildMod,
        lReExcludeDirs=lReExcludeDirs,
        lReExcludeFiles=lReExcludeFiles,
        pathSrcTop=pathModule,
        pathTrgTop=pathBuild,
    )

    print("Creating ZIP package")
    pathCwd = Path.cwd()
    os.chdir(pathBuild.as_posix())
    shutil.make_archive(pathBuildMod.name, "zip", ".", pathBuildMod.name)

    sZipFilename = pathBuildMod.name + ".zip"
    pathZipSrcFile = pathBuild / sZipFilename
    pathZipTrg = pathDist
    pathZipTrgFile = pathZipTrg / sZipFilename
    pathZipTrg.mkdir(parents=True, exist_ok=True)

    shutil.move(pathZipSrcFile.as_posix(), pathZipTrgFile.as_posix())
    print("Package stored as: {}".format(pathZipTrgFile.as_posix()))

    os.chdir(pathCwd.as_posix())
    shutil.rmtree(pathBuildMod.as_posix())


# enddef


####################################################################
def BuildSetupPackage(*, pathSetupSrc: Path, pathDist: Path, pathTop: Path):
    print("Building Setup package {}\n---\n".format(pathSetupSrc.name))

    lReExcludeDirs = [
        r"\.git",
        r"\.vscode",
        r"__pycache__",
        r"unit_test",
        r"_dev",
        r"dev",
        r"_debug",
        r"_render",
        r"build",
        r"_build",
        r"_output",
        r"_blender",
        r"env",
        r".+\.egg-info",
    ]

    lReExcludeFiles = [
        r"\.srm_.+",
        r"\.git.+",
        r"\.vscode.+",
        r"stdout_.+\.txt",
        r"action-config-list_.+\.json",
        r"cml-vars_.+\.json",
        r".+\.blend1",
        r"\.env",
        r"\.egg-info",
        r"vsc-extension-quickstart.md",
        r".+\.code-workspace",
    ]

    sSwitchBackToBranch = SelectBuildBranch(pathModule=pathSetupSrc)

    sVersion = module.GetRepoVersion(pathModule=pathSetupSrc)

    pathBuild = pathTop / "_build"
    pathBuildMod = pathBuild / "{}-{}".format(pathSetupSrc.name, sVersion)
    if pathBuildMod.exists():
        shutil.rmtree(pathBuildMod.as_posix())
    # endif
    if pathBuildMod.exists():
        raise RuntimeError("Cannot remove build directory. Please remove manually: {}".format(pathBuildMod.as_posix()))
    # endif

    pathBuildMod.mkdir(parents=True)

    print("Copying package files to build folder: {}".format(pathBuildMod.as_posix()))

    # ################################################################
    print("Packing documentation...")

    pathDocsSrc = pathSetupSrc / "docs"
    pathDocsTrg = pathSetupSrc / "src" / "catharsys" / "setup" / "dist" / "docs"
    sDocsZipName = f"{pathSetupSrc.name}-docs"

    pathCwd = Path.cwd()
    os.chdir(pathDocsSrc.as_posix())
    shutil.make_archive(sDocsZipName, "zip", "build")

    sZipFilename = sDocsZipName + ".zip"
    pathZipSrcFile = pathDocsSrc / sZipFilename
    pathZipTrgFile = pathDocsTrg / sZipFilename
    pathDocsTrg.mkdir(parents=True, exist_ok=True)

    if pathZipTrgFile.exists():
        os.unlink(pathZipTrgFile.as_posix())
    # endif

    shutil.move(pathZipSrcFile.as_posix(), pathZipTrgFile.as_posix())
    print("Docs packed to: {}".format(pathZipTrgFile.as_posix()))

    os.chdir(pathCwd.as_posix())
    # ##################################################################

    pathReposSrc = pathSetupSrc / "repos"
    pathReposTrg = pathBuildMod / "repos"
    pathReposTrg.mkdir(exist_ok=True)
    pathReposFileTrg = pathReposTrg / "repos-develop.yaml"
    pathReposFileSrc = pathReposSrc / "repos-develop.yaml"
    shutil.copy(pathReposFileSrc.as_posix(), pathReposFileTrg.as_posix())

    pathReposFileTrg = pathReposTrg / "repos-release.yaml"
    pathReposFileSrc = pathReposSrc / "repos-release.yaml"
    shutil.copy(pathReposFileSrc.as_posix(), pathReposFileTrg.as_posix())

    pathScriptsSrc = pathSetupSrc / "scripts"
    pathScriptsTrg = pathBuildMod / "scripts"
    pathScriptsTrg.mkdir(exist_ok=True)
    util.CopyFiles(
        pathScriptsSrc,
        pathScriptsTrg,
        lReExcludeDirs=lReExcludeDirs,
        lReExcludeFiles=lReExcludeFiles,
        pathSrcTop=pathSetupSrc,
        pathTrgTop=pathBuildMod,
    )

    pathCodeSrc = pathSetupSrc / "src"
    pathCodeTrg = pathBuildMod / "src"
    pathCodeTrg.mkdir(exist_ok=True)
    util.CopyFiles(
        pathCodeSrc,
        pathCodeTrg,
        lReExcludeDirs=lReExcludeDirs,
        lReExcludeFiles=lReExcludeFiles,
        pathSrcTop=pathSetupSrc,
        pathTrgTop=pathBuildMod,
    )

    shutil.copy((pathSetupSrc / "setup.cfg").as_posix(), (pathBuildMod / "setup.cfg").as_posix())
    shutil.copy(
        (pathSetupSrc / "pyproject.toml").as_posix(),
        (pathBuildMod / "pyproject.toml").as_posix(),
    )

    print("Creating ZIP package")
    pathCwd = Path.cwd()
    os.chdir(pathBuild.as_posix())
    shutil.make_archive(pathBuildMod.name, "zip", ".", pathBuildMod.name)

    sZipFilename = pathBuildMod.name + ".zip"
    pathZipSrcFile = pathBuild / sZipFilename
    pathZipTrg = pathDist
    pathZipTrgFile = pathZipTrg / sZipFilename
    pathZipTrg.mkdir(parents=True, exist_ok=True)

    shutil.move(pathZipSrcFile.as_posix(), pathZipTrgFile.as_posix())
    print("Package stored as: {}".format(pathZipTrgFile.as_posix()))

    os.chdir(pathCwd.as_posix())
    shutil.rmtree(pathBuildMod.as_posix())

    if sSwitchBackToBranch is not None:
        SelectBranch(pathModule=pathSetupSrc, sBranch=sSwitchBackToBranch)
    # endif


# enddef

####################################################################
def Run(*, lModules: list[str] = []):

    # Check whether "build" is installed
    dicInfo = util.GetInstalledModuleInfo(sPathPythonProg="python", sModuleName="build")
    if dicInfo.get("Version") is None:
        raise RuntimeError(
            "Module 'build' from setuptools not installed.\n"
            "Please install it with: pip install build\n"
            "You may need to download a version >= 0.7.0 manually from: https://github.com/pypa/build/tags\n"
        )
    # endif

    # Look for documentation virtual environment
    pathRepos = util.TryGetReposPath()
    if pathRepos is None:
        raise RuntimeError("Modules can only be built from source install")
    # endif

    pathSetup = pathRepos.parent
    pathDist = util.GetDistPath()

    def CreateBuildFunc(_pathDist: Path, _pathSetup: Path):
        def Lambda(*, pathRepos: Path, pathModule: Path):
            BuildFromRepo(
                pathRepos=pathRepos,
                pathModule=pathModule,
                pathDist=_pathDist,
                pathSetup=_pathSetup,
            )

        # enddef
        return Lambda

    # enddef

    lIncMods = lModules if isinstance(lModules, list) else []

    lPathModules = module.ForEach(
        bForceDist=False,
        funcRunDist=CannotBuildFromDist,
        funcRunRepo=CreateBuildFunc(pathDist, pathSetup),
        funcTest=FilterPyModules,
        lIncludeRegEx=lIncMods,
    )


# enddef


####################################################################
def RunWorkspace(*, pathWorkspace: Optional[Path] = None):

    # Build workspace package
    print("===================================================")

    if isinstance(pathWorkspace, Path):
        pathModule = pathWorkspace
    else:
        pathModule = Path.cwd()
    # endif

    pathPackageFile = pathModule / "package.json"
    if not pathPackageFile.exists():
        pathPackageFile = pathModule / "package.json5"
        if not pathPackageFile.exists():
            pathPackageFile = None
        # endif
    # endif

    if pathPackageFile is None:
        raise RuntimeError("Current directory does not contain a 'package.json[5]' file")
    # endif

    pathDist = pathModule.parent
    pathSetup = pathDist
    dicPkg = anyfile.LoadJson(pathPackageFile)

    BuildWorkspacePackage(pathModule=pathModule, pathDist=pathDist, pathSetup=pathSetup, dicPkg=dicPkg)


# enddef


####################################################################
def RunBuildSetup(*, pathSetup: Optional[Path] = None):

    # Build workspace package
    print("===================================================")

    if isinstance(pathSetup, Path):
        pathSetupSrc = pathSetup
    else:
        pathSetupSrc = Path.cwd()
    # endif

    pathSetupCfg = pathSetupSrc / "setup.cfg"

    if pathSetupCfg is None:
        raise RuntimeError("Directory does not contain a 'setup.cfg' file")
    # endif

    pathDist = pathSetupSrc.parent

    BuildSetupPackage(pathSetupSrc=pathSetupSrc, pathDist=pathDist, pathTop=pathDist)


# enddef
