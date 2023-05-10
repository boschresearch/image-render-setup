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

import ast

import os, glob

_bBeVerbose = False


def _InsertLine(sFilename: str, index: int, sContent: str):
    """Insert string content at line index into source file f
    Args:
        sFilename (str): File to be modified
        index (int): Line number to be inserted at
        sContent (str): Line to be inserted
    """
    with open(sFilename, "r") as f:
        lsContents = f.readlines()
    # EndWith

    lsContents.insert(index, sContent)

    with open(sFilename, "w") as f:
        lsContents = "".join(lsContents)
        f.write(lsContents)
    # EndWith


# EndDef


def _CountLeadingBlanks(s: str):
    """Calculate number of leading blanks
    Args:
        s (str): Input string
    Returns:
        int: Number of leading blanks
    """
    return (len(s) - len(s.lstrip())) if s != "\n" else 0


# EndDef


def _PermutateBlockEnd(_sBlockId):
    sBlockID_lower = f"{_sBlockId[0:1]}".lower() + _sBlockId[1:]
    sBlockID_upper = f"{_sBlockId[0:1]}".upper() + _sBlockId[1:]

    sComment = f"# End{sBlockID_upper}"

    lsAlternatives = [
        f"# end{sBlockID_lower}",
        f"# end{sBlockID_upper}",
        f"# end {sBlockID_lower}",
        f"# end {sBlockID_upper}",
        f"# End{sBlockID_lower}",
        f"# End{sBlockID_upper}",
        f"# End {sBlockID_lower}",
        f"# End {sBlockID_upper}",
    ]

    return {"_sComment": sComment, "_lsAlternatives": lsAlternatives}


# EndDef


class CFormatCodeBlocksAnalyzer(ast.NodeVisitor):
    """Code analyzer class derived from ast.Nodevisitor checking for
    Catharsys Coding Guidelines infractions
    """

    def __init__(self, _sFilename):
        with open(_sFilename, "r") as source:
            self.lsCode = source.readlines()
        # EndWith

        self.sFilename = _sFilename
        # break switch to stop traversing the AST, since adding a line requires reloading
        self.bContinue = True

    # EndDef

    """ Per default the visitor functions for the nodes are ``'visit_'`` +
        class name of the node.  So a `TryFinally` node visit function would
        be `visit_TryFinally`.  This behavior can be changed by overriding
        the `visit` method.  If no visitor function exists for a node
        (return value `None`) the `generic_visit` visitor is used instead.

        see https://docs.python.org/3/library/ast.html#node-classes
    """

    def visit_If(self, _xNode):
        self._VisitGeneric(_xNode, **_PermutateBlockEnd("if"))
        self.generic_visit(_xNode)

    # EndDef

    def visit_For(self, _xNode):
        self._VisitGeneric(_xNode, **_PermutateBlockEnd("for"))
        self.generic_visit(_xNode)

    # EndDef

    def visit_ClassDef(self, _xNode):
        self._VisitGeneric(_xNode, **_PermutateBlockEnd("class"))
        self.generic_visit(_xNode)

    # EndDef

    def visit_FunctionDef(self, _xNode):
        self._VisitGeneric(_xNode, **_PermutateBlockEnd("def"))
        self.generic_visit(_xNode)

    # EndDef

    def visit_While(self, _xNode):
        self._VisitGeneric(_xNode, **_PermutateBlockEnd("while"))
        self.generic_visit(_xNode)

    # EndDef

    def visit_Try(self, _xNode):
        self._VisitGeneric(_xNode, **_PermutateBlockEnd("try"))
        self.generic_visit(_xNode)

    # EndDef

    def visit_With(self, _xNode):
        self._VisitGeneric(_xNode, **_PermutateBlockEnd("with"))
        self.generic_visit(_xNode)

    # EndDef

    def _VisitGeneric(self, _xNode, _sComment: str, _lsAlternatives=None):
        """Generic visit functionality
        Args:
            node (ast.node): Node being visited
            commentstring (str): String that is expected to show up at the end of
            the code belonging to the node.
            altstrings (List of strings): Alternatives to commentstring that are also acceptable.
            Defaults to None.
        """
        if _lsAlternatives is None:
            lsTargets = [_sComment]
        else:
            _lsAlternatives.append(_sComment)
            lsTargets = _lsAlternatives
        # EndIf

        if self.bContinue:
            # skip over potential # Endwhatever comments, till the correct indentation level is reached or EOF

            iCurrentInvestionLineNo = _xNode.end_lineno
            iEndLineNo4Insertion = iCurrentInvestionLineNo
            iMaxLineCnt = len(self.lsCode)
            bExpectedStartFound = False
            while iCurrentInvestionLineNo < iMaxLineCnt:
                sCurrentLine = self.lsCode[iCurrentInvestionLineNo]
                iLeadingBlanks = _CountLeadingBlanks(sCurrentLine)
                if len(sCurrentLine.strip()) > 0 and iLeadingBlanks <= _xNode.col_offset:
                    if len(sCurrentLine) > _xNode.col_offset:
                        bExpectedStartFound = any(
                            [sCurrentLine[_xNode.col_offset :].startswith(sComment) for sComment in lsTargets]
                        )
                    # EndIf
                    break
                # EndIf

                iCurrentInvestionLineNo += 1
                if iLeadingBlanks > _xNode.col_offset:
                    iEndLineNo4Insertion = iCurrentInvestionLineNo
                # EndIf
            # EndWhile

            if not bExpectedStartFound:
                global _bBeVerbose
                if _bBeVerbose:
                    # Endwhatever not found at the correct indent level
                    if hasattr(_xNode, "name"):
                        print(f"{_sComment} in line {_xNode.end_lineno} missing for {_xNode.name}")
                    else:
                        print(f"{_sComment} in line {_xNode.end_lineno} missing")
                    # endif
                # EndIf
                sInsertion = " " * _xNode.col_offset + f"{_sComment}\n"
                _InsertLine(self.sFilename, iEndLineNo4Insertion, sInsertion)
                self.bContinue = False
            # EndIf
        # EndIf

    # EndDef


# EndClass


def _FormatCodeBlocks(_sFilename: str):
    """Main formatting loops
    Args:
        filename (str): Code file to be formatted
    """
    global _bBeVerbose
    if _bBeVerbose:
        print(f"opening {_sFilename} to analyse FormatCodeBlocks")
    # EndIf

    # Read file contents
    with open(_sFilename, "r") as source:
        xTree = ast.parse(source.read())
    # EndWith

    # set up Python AST analyzer, set continue flag to False.
    # This flag ensures that only one one code change is performed,
    # since insertion changes the linenumbers.
    # If Analyzer.visit terminates without setting the continue flag,
    # no more changes need to be made to the code
    xAnalyzer = CFormatCodeBlocksAnalyzer(_sFilename)
    xAnalyzer.bContinue = False

    # Fix issues one by one till no findings are left
    while not xAnalyzer.bContinue:
        # Reread the file contents, set up AST and visit
        with open(_sFilename, "r") as source:
            xTree = ast.parse(source.read())
        # EndWith
        xAnalyzer = CFormatCodeBlocksAnalyzer(_sFilename)
        xAnalyzer.visit(xTree)
    # EndWhile
    return


# EndDef


####################################################################
def RunFormat(
    *,
    _bCodeBlocks=False,
    _bVerbose=False,
    _lsFilename=None,
    _lsFolder=None,
    _bFolderRecursive=False,
):
    if not _bCodeBlocks:
        raise RuntimeError("RunFormat expects at least one action [--code-blocks, ]")
    # EndIf

    lsResultingFiles = []

    global _bBeVerbose
    _bBeVerbose = _bVerbose

    if _lsFilename is not None:
        if not isinstance(_lsFilename, list):
            raise ValueError("RunFormat expected a list of filenames as input")
        # EndIf
        for sFilename in _lsFilename:
            if os.path.isfile(sFilename):
                lsResultingFiles.append(os.path.realpath(sFilename))
            # EndIf
        # EndFor
    # EndIf

    if _lsFolder is not None:
        if not isinstance(_lsFolder, list):
            raise ValueError("RunFormat expected a list of folder as input")
        # EndIf

        for sFolder in _lsFolder:
            if _bFolderRecursive:
                lsDirFiles = []
                for sRoot, lsDirectories, lsFiles in os.walk(sFolder):
                    for sFile in lsFiles:
                        if sFile.endswith(".py"):
                            lsDirFiles.append(os.path.realpath(os.path.join(sRoot, sFile)))
                        # EndIf
                    # EndFor
                # EndFor

            else:
                lsDirFiles = [os.path.realpath(sFile) for sFile in glob.glob(sFolder + "/*.py")]
            # EndIf

            for sFile in lsDirFiles:
                lsResultingFiles.append(sFile)
            # EndFor
        # EndFor
    # EndIf

    if _bVerbose:
        print("filenames:")
        for sFile in lsResultingFiles:
            print(sFile)
        # EndFor
    # EndIf

    for sFile in lsResultingFiles:
        if _bCodeBlocks:
            _FormatCodeBlocks(sFile)
        # EndIf
    # EndFor


# enddef

# ------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    # filepath = "D:/TOOLS/common/catharsys/image-render-setup-develop/src/catharsys/setup/cmd/devl_code_format.py"
    if len(sys.argv) >= 2:
        filepath = sys.argv[1]
        if os.path.isfile(filepath):
            _FormatCodeBlocks(filepath)
        # EndIf
    # EndIf
# EndIf
